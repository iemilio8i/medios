from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

import datetime

# Bokeh
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from numpy import pi
import matplotlib.pyplot as plt


from .forms import ListaAparicionForm
from .models import Choice, Question

from utils.tweet_test import Tweet, Entities, User, Media, read_json_file,\
        tweet_to_dataframe, test_df_plot, filtrar_df_fecha,\
        buscar_palabra_df, n_palabras_comun, uniq_usuarios_df, filtrar_df_user, sacar_hastags


global_list_tweet = read_json_file('F:\Desktop\TFG\Datos\ELPAIS_2000.json')
global_df = tweet_to_dataframe(global_list_tweet)


class IndexView(generic.ListView):
    template_name = 'medios/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'medios/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'medios/results.html'




# Plots
def pie_chart(percents):
    # define starts/ends for wedges from percentages of a circle
    percents = [0, 0.3, 0.4, 0.6, 0.9, 1]
    starts = [p * 2 * pi for p in percents[:-1]]
    ends = [p * 2 * pi for p in percents[1:]]

    # a color for each pie piece
    colors = ["red", "green", "blue", "orange", "yellow"]

    p = figure(x_range=(-2, 2), y_range=(-2, 2))

    p.wedge(x=0, y=0, radius=1, start_angle=starts, end_angle=ends, color=colors)

    return p


def index(request):
    x= [1,3,5,7,9,11,13]
    y= [1,2,3,4,5,6,7]
    title = 'y = f(x)'

    plot = figure(title= title,
        x_axis_label= 'X-Axis',
        y_axis_label= 'Y-Axis',
        plot_width= 400,
        plot_height= 400,
        )
    plot.line(x, y, legend= 'f(x)', line_width = 2)

    percents = [0, 0.3, 0.4, 0.6, 0.9, 1]
    starts = [p * 2 * pi for p in percents[:-1]]
    ends = [p * 2 * pi for p in percents[1:]]

    # a color for each pie piece
    colors = ["red", "green", "blue", "orange", "yellow"]

    p = figure(x_range=(-1, 1), y_range=(-1, 1))

    p.wedge(x=0, y=0, radius=1, start_angle=starts, end_angle=ends, color=colors)


    # Store Components
    script, div = components(p)

    # Feed them to the Django Template.
    return render(request, 'medios/bokeh_test.html', {'script' : script, 'div' : div } )

def bokeh_prueba_tweet(request):
    list_tweet = read_json_file('F:\Desktop\TFG\Datos\ELPAIS_2000.json')
    df = tweet_to_dataframe(list_tweet)
    series = test_df_plot(df).fillna(0) # fillna para pasar nan values a 0
    print(series)

    # Test uso filtro por fechas
    nuevo_df = filtrar_df_fecha(df, '2016-02-16', datetime.datetime.now())
    nuevo_series = test_df_plot(nuevo_df).fillna(0)

    bseries = buscar_palabra_df(df,'la')
    df2 = df[bseries]

    counter = n_palabras_comun(df, 100)
    print(counter)

    #uniq_usuarios_df(df)

    categorias = list(series.keys())
    plot = figure(x_axis_type='datetime', plot_width=1000, plot_height=600, x_axis_label='Fecha', y_axis_label='Retweets')#, x_range=categorias
    bar_width = 150000000/len(categorias)
    plot.vbar(categorias, top=list(series.values), width=bar_width, line_color='green', bottom=0)


    #Store Components
    script, div = components(plot)

    titulo = 'Gráfica Número de Retweets por Día'
    # Feed them to the Django Template.
    return render(request, 'medios/bokeh_test.html', {'script' : script, 'div' : div, 'titulo': titulo } )


def grafica_palabras(request, n=10, column='texto', titulo='Gráfica Palabras más Frequentes', fecha1=datetime.date(2016,1,1) ,fecha2=datetime.date.today()):

    initial = { 'tipo_busqueda': column, 'numero_resultados':n, 'fecha_inicio': fecha1, 'fecha_final':fecha2 }
    form = ListaAparicionForm(initial=initial)

    df = global_df
    df = filtrar_df_fecha(df, fecha1, fecha2)
    counter = n_palabras_comun(df, n, column=column)
    categorias = [ x[0] for x in counter ]
    top = [ x[1] for x in counter ]
    plot = figure(x_range=categorias, plot_width=1000, plot_height=600, x_axis_label='Palabra', y_axis_label='Frecuencia')#, x_range=categorias
    bar_width = 1
    plot.vbar(x=categorias, top=top, width=bar_width, line_color='green', bottom=0)


    #Store Components
    script, div = components(plot)
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
            if column == 'texto':
                titulo = 'Gráfica de Palabras más Frecuentes'
            else:
                titulo = 'Gráfica frecuencia de %s'%(busqueda_map[column])

            # TODO Mirar como poner los títulos y filtro por fechas
            return grafica_palabras(request, n=n, column=column, fecha1=fecha_i, fecha2=fecha_f, titulo=titulo )

    else: # Si es GET
        return grafica_palabras(request)



# Pagina Indice de un medio de comunicacion con sus datos mas relevantes
def index_medio(medio, df):
    # TODO Se necesita una clara distinción de medios relevantes (lista de ellos)
    user_df = filtrar_df_user(df, user=medio)
    counter_hastags = sacar_hastags(user_df)
    # TODO poner aqui gráfica de palabras Nota: Se debería excluir el nombre del medio
    #
    # TODO lista de ultimos tweets (incluir busqueda de tweets por fecha)
    # TODO Idea: dividir lista de tweets entre tweets propios y menciones/RTs
    # TODO Mirar clasificacion de medios por categorias (deporte, politica...)


    return





def medio_index(request, medio_id=0):

    # El Pais User ID: 7996082 || 7996082
    list_tweet = read_json_file('F:\Desktop\TFG\Datos\ELPAIS_2000.json')
    medio = 'El País'
    medio_user = 'No se ha encontrado el medio.'
    #imagen_medio = 'http://pbs.twimg.com/profile_images/2284174872/7df3h38zabcvjylnyfe3_bigger.png'
    imagen_medio = 'No hay imagen'
    medio_test_id = list_tweet[0].usuario.id

    # TODO Terminar Esto: Mirar como contar los tweets de entidad

    for indice, tweet in enumerate(list_tweet):
        print(tweet.usuario.id)
        # Test TODO: Añadir base de datos de medios y elegir medio segun criterio
        #if 'el país' in tweet.usuario.nombre.lower():
        if tweet.usuario.id == medio_test_id:
            medio = tweet.usuario.nombre
            medio_user = tweet.usuario
            imagen_medio = medio_user.imagen_http.replace('normal', 'bigger')

    # Creacion nueva lista tweet a partir del id de medio
    nueva_lista_tweet = []
    for tweet in list_tweet:
        if (medio_test_id in [ide for ide, nombre in tweet.entidades.user_mentions]) or medio_test_id == tweet.usuario.id:
            nueva_lista_tweet.append(tweet)

    # TODO Ahora mismo: Filtrar tweets por usuario

    context = {
        'tweet_list':nueva_lista_tweet,
        'titulo':medio,
        'medio':medio_user,
        'imagen_medio':imagen_medio,
    }
    return render(request,'medios/medio_index.html', context)





# Prueba mostrar lista tweets
def list_tweets(request):
    list_tweet = read_json_file('F:\Desktop\TFG\Datos\ELPAIS_2000.json')
    return render(request,'medios/index_tweets.html', {'tweet_list' : list_tweet } )


# Prueba mostrar atributos tweet
def detail_tweet(request, tweet_id):
    list_tweet = read_json_file('F:\Desktop\TFG\Datos\ELPAIS_2000.json')
    tweet = None
    for x in list_tweet:
        if x.tweet_id ==tweet_id:
            tweet=x
            break
    return render(request, 'medios/detail_tweet.html', {'tweet' : tweet })


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'medios/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('medios:results', args=(question.id,)))