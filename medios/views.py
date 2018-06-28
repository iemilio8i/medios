from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

import datetime
from threading import Thread

# Graphs
from utils.graph import test_pie_chart, test_graph, n_words_graph, linear_plot, mean_linear_plot, locations_graph
from utils.mongodb import json_upload_to_collection, update_medio, get_collection_list, get_medios_destacados, sacar_intervalo_fecha

from .forms import ListaAparicionForm, SubirArchivoForm, BuscarMedioForm, FiltrarFechaForm
from .models import Choice, Question

from utils.tweet_test import filtrar_df_fecha,\
        buscar_palabra_df, n_palabras_comun, uniq_usuarios_df, filtrar_df_user, procces_data_db, sacar_df_y_user_medio


def lista_medios(request):
    list_title = 'Medios de Comunicación'
    table_title = 'Resumen Medios'
    lista_medio_count = get_collection_list()
    lista_medio = [ x[0] for x in lista_medio_count]
    lista_count = [ x[1] for x in lista_medio_count]
    lista_medios_destacados = get_medios_destacados()[:5]
    max_tweets_medio = max(lista_count)

    intervalo_medio = []
    for medio in lista_medio:
        fecha_i, fecha_f = sacar_intervalo_fecha(medio)
        intervalo_medio.append((fecha_i, fecha_f))

    lista_medio = [ [lista_medio[i], lista_count[i], intervalo_medio[i]] for i in range(len(lista_medio)) ]

    table_head = [('Medio',20), ('algo',None), ('Tweets Almacenados',None), ('Ver Medio',None), ('Añadir Tweets', 20)]


    return render(request, 'medios/lista_medios.html', {
                'table_title':table_title,
                'list_title':list_title,
                'lista_medios':lista_medio,
                'lista_medios_destacados':lista_medios_destacados,
                'max_tweets_medio':max_tweets_medio,
                'table_head':table_head,
                })

def subir_archivo(request, medio_nombre=''):
    form_title = 'Subir Medio'
    lista_medios_destacados = get_medios_destacados()[:5]

    if request.method == 'POST':
        form = SubirArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            nombre_medio = form.cleaned_data['nombre_medio']
            file = request.FILES['archivo_json']
            if file.name.endswith('.json'):
                subido = json_upload_to_collection(file, nombre_medio)
                df, user = sacar_df_y_user_medio(nombre_medio)
                if user:
                    update_medio(user, nombre_medio)
            else:
                subido = 'Error: El archivo no es json'
            return render(request, 'medios/subir_archivo.html', {'form': form, 'form_title':form_title,'subido':subido, 'lista_medios_destacados':lista_medios_destacados,})
    else:
        form = SubirArchivoForm(initial={'nombre_medio': medio_nombre})
    return render(request, 'medios/subir_archivo.html', {'form': form, 'form_title':form_title, 'lista_medios_destacados':lista_medios_destacados, })

# Test: Plot pie chart
def index(request):
    # Call test pie chart from graph.py
    script, div = test_pie_chart()
    # Feed them to the Django Template.
    return render(request, 'medios/bokeh_test.html', {'script' : script, 'div' : div } )

def bokeh_prueba_tweet(request):
    df = procces_data_db()

    script, div = test_graph(df)

    titulo = 'Gráfica Número de Retweets por Día'
    # Feed them to the Django Template.
    return render(request, 'medios/bokeh_test.html', {'script' : script, 'div' : div, 'titulo': titulo } )

def grafica_palabras(request, n=10, column='text', titulo='Gráfica Palabras más Frequentes', fecha1=datetime.date(2016,1,1) ,fecha2=datetime.date.today()):

    initial = { 'tipo_busqueda': column, 'numero_resultados':n, 'fecha_inicio': fecha1, 'fecha_final':fecha2 }
    form = ListaAparicionForm(initial=initial)

    df = procces_data_db()
    df = filtrar_df_fecha(df, fecha1, fecha2)
    script, div = n_words_graph(df, n, column)
    # Feed them to the Django Template.
    return render(request, 'medios/bokeh_test.html', {'script' : script, 'div' : div, 'titulo': titulo, 'form':form } )

def grafica_palabras_form(request):
    if request.method== 'POST':
        form = ListaAparicionForm(request.POST)
        if form.is_valid():
            n = form.cleaned_data['numero_resultados']
            print(n)
            column = form.cleaned_data['tipo_busqueda']
            fecha_i = form.cleaned_data['fecha_inicio']
            fecha_f = form.cleaned_data['fecha_final']

            busqueda_map = {
                'texto':'Texto Tweet',
                'user_nombre': 'Nombre Usuario',
                'retweets': 'Retweets',
                'user_id': 'Id Usuario',
            }
            if column == 'text':
                titulo = 'Gráfica de Palabras más Frecuentes'
            else:
                titulo = 'Gráfica frecuencia de %s'%(busqueda_map[column])

            # TODO Mirar como poner los títulos y filtro por fechas
            return grafica_palabras(request, n=n, column=column, fecha1=fecha_i, fecha2=fecha_f, titulo=titulo )

    else: # Si es GET
        return grafica_palabras(request)

# Submethod of medio index for managing list of tweets
def medio_index_tweets_tab(medio_nombre, fecha_i, fecha_f):
    df = procces_data_db(medio_nombre, fecha_i, fecha_f, limit=100)
    modified_df = df[['user_screen_name', 'user_name', 'id_str', 'text', 'retweet_count', 'favorite_count', 'created_at']]
    return modified_df.values.tolist()

# Looks for medio in db and returns its data
def medio_index_get_medio(df, medio_tweet, nombre):
    try:
        medio = medio_tweet['user_name']
        medio_user = medio_tweet['user_screen_name']
        #imagen_medio = 'http://pbs.twimg.com/profile_images/2284174872/7df3h38zabcvjylnyfe3_bigger.png'
        imagen_medio = medio_tweet['user_profile_image_url']
        imagen_medio = imagen_medio.replace('_normal', '_bigger')
        user_id_str = medio_tweet['user_id_str']
        try:
            n_medio_tweets = len(df.loc[df['user_id_str']==user_id_str ])
        except Exception as e:
            n_medio_tweets = 0
        medio_dict = medio_tweet.to_dict()
    except Exception as e:
        medio, medio_user = nombre, nombre
        imagen_medio = None
        medio_dict = {}
        n_medio_tweets = 0

    return medio, medio_user, imagen_medio, medio_dict, n_medio_tweets

# Medio Overview, generates a bunch of bokeh graphs and returns context to show it
def medio_index_overview(df):
    # Start a thread for every graph
    linear_resul = [None]*2
    t_linear = Thread(target=linear_plot, args=(df[['created_at', 'retweet_count']],linear_resul))
    t_linear.start()

    mean_linear_resul = [None] * 2
    mean_t_linear = Thread(target=mean_linear_plot, args=(df[['created_at', 'retweet_count']], mean_linear_resul))
    mean_t_linear.start()

    n_words_resul = [None] * 2
    n_words_t = Thread(target=n_words_graph, args=(df[['created_at', 'text']], 5, 'text', n_words_resul))
    n_words_t.start()

    loca_list = list(df['user_location'])
    location_resul = [None] * 2
    location_t = Thread(target=locations_graph, args=(loca_list, 5, location_resul))
    location_t.start()

    pie_chart_resul = [None] * 2
    pie_chart_t = Thread(target=test_pie_chart, args=(df, pie_chart_resul))
    pie_chart_t.start()

    return t_linear, mean_t_linear, n_words_t, location_t, pie_chart_t, linear_resul, mean_linear_resul, n_words_resul, location_resul, pie_chart_resul

def overview_context(df):
    info_title = 'Información Extra'
    n_reply_tweets = df.loc[df['in_reply_to_screen_name'].notnull()].shape[0]
    n_rt_tweets = len(df[df['text'].str.startswith('RT')])
    total_tweets = df.shape[0]
    rest_tweets = total_tweets - n_rt_tweets - n_reply_tweets

    return {
        'info_title': info_title,
        'reply_tweets': n_reply_tweets,
        'rt_tweets': n_rt_tweets,
        'rest_tweets':rest_tweets,
        'total_tweets': total_tweets,
        }

def medio_index(request, medio_nombre='elpais', fecha_i=datetime.datetime(2010, 2, 15), fecha_f=datetime.datetime.now()):
    tweet_user = None
    df, tweet_user = sacar_df_y_user_medio(medio_nombre, fecha_i, fecha_f)
    medio, medio_user, imagen_medio, medio_tweet, n_medio_tweets = medio_index_get_medio(df, tweet_user, medio_nombre)


    # Overview
    linear_title = 'Número de Tweets por Hora'
    mean_title = 'Media de Retweets por Hora'
    n_title = 'Palabras más frecuentes'
    location_title = 'Localizaciones'
    pie_title = 'Hashtags más utilizados'
    lista_medios_destacados = get_medios_destacados()[:5]


    context = {
        'titulo': medio.title(),
        'medio':medio_user.title(),
        'imagen_medio':imagen_medio,
        'medio_tweet': medio_tweet,
        'n_medio_tweets':n_medio_tweets,
        ## Overview
        # Graph context
        ##### Linear Graph
        'linear_title':linear_title,

        ##### Mean Linear Graph
        'mean_title': mean_title,

        ###### N Words Graph
        'n_title': n_title,

        ###### Pie chart Hastags
        'pie_title': pie_title,

        ###### Localizations
        'location_title': location_title,

        # FORMS
        'buscarmedioform':BuscarMedioForm(),
        'filtrarfechaform': FiltrarFechaForm(),
        'lista_medios_destacados': lista_medios_destacados,
    }
    try:
        t_linear, mean_t_linear, n_words_t, location_t, pie_chart_t, linear_resul, mean_linear_resul, n_words_resul, location_resul, pie_chart_resul = medio_index_overview(df)
    except Exception as e:
        return render(request, 'medios/medio_index.html', context)

    over_context = overview_context(df)
    over_context['rest_tweets']-= n_medio_tweets

    # Tweet list tab proccesing
    df_list = medio_index_tweets_tab(medio_nombre, fecha_i, fecha_f)
    uniq_users = len(set(df['user_screen_name']))

    # Wait for every thread to finish his jon
    t_linear.join()
    mean_t_linear.join()
    n_words_t.join()
    location_t.join()
    pie_chart_t.join()

    # Assign resuls to respective return values
    location_script, location_div = location_resul
    linear_script, linear_div = linear_resul
    mean_script, mean_div = mean_linear_resul
    n_script, n_div = n_words_resul
    pie_script, pie_div = pie_chart_resul

    context = {
        'tweet_list':df_list,
        'titulo': medio.title(),
        'medio':medio_user.title(),
        'imagen_medio':imagen_medio,
        'medio_tweet': medio_tweet,
        'n_medio_tweets':n_medio_tweets,
        ## Overview
        # Graph context
        ##### Linear Graph
        'linear_title':linear_title,
        'linear_script':linear_script,
        'linear_div':linear_div,
        ##### Mean Linear Graph
        'mean_title': mean_title,
        'mean_script': mean_script,
        'mean_div': mean_div,
        ###### N Words Graph
        'n_title': n_title,
        'n_script': n_script,
        'n_div': n_div,
        ###### Pie chart Hastags
        'pie_title': pie_title,
        'pie_script': pie_script,
        'pie_div': pie_div,
        ###### Localizations
        'location_title': location_title,
        'location_script': location_script,
        'location_div': location_div,
        # Some info
        'uniq_users':uniq_users,
        # FORMS
        'buscarmedioform':BuscarMedioForm(),
        'filtrarfechaform': FiltrarFechaForm(),
        'lista_medios_destacados': lista_medios_destacados,
    }
    context = { **context, **over_context}

    return render(request,'medios/medio_index.html', context)

def control_flow_medio_index(request, medio_nombre):
    if request.method=="POST":
        if 'buscarmedio' in request.POST:
            buscarmedioform = BuscarMedioForm(request.POST, prefix='buscar')
            try:
                medio_nombre = buscarmedioform.data['nombre_medio']
            except Exception as e:
                print(e)
            return HttpResponseRedirect(reverse('medios:medio_index', args=(medio_nombre,)))
        elif 'filtrarfecha' in request.POST:
            filtrarfechaform = FiltrarFechaForm(request.POST, prefix='filtrar')
            try:
                fecha_inicial_day = int(filtrarfechaform.data['fecha_inicial_day'])
                fecha_inicial_month = int(filtrarfechaform.data['fecha_inicial_month'])
                fecha_inicial_year = int(filtrarfechaform.data['fecha_inicial_year'])
                fecha_final_day = int(filtrarfechaform.data['fecha_final_day'])
                fecha_final_month = int(filtrarfechaform.data['fecha_final_month'])
                fecha_final_year = int(filtrarfechaform.data['fecha_final_year'])
                fecha_inicial = datetime.datetime(fecha_inicial_year, fecha_inicial_month, fecha_inicial_day)
                fecha_final = datetime.datetime(fecha_final_year, fecha_final_month, fecha_final_day)
            except Exception as e:
                raise e
            return medio_index(request, medio_nombre, fecha_inicial, fecha_final)

        else:
            return HttpResponseRedirect(reverse('medios:medio_index', args=(medio_nombre,)))
    else:
       return medio_index(request, medio_nombre)