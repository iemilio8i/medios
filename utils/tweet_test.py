import json, os, sys
import pandas as pd
from datetime import datetime
from collections import Counter


# Busca palabra en tweet_df
def buscar_palabra(tweet_df, palabra):
    bool_series = tweet_df['text'].str.contains(palabra)
    resul = tweet_df[bool_series.values]
    return resul

# Busca usuario en tweet_df
def buscar_usuario(tweet_df, usuario):
    return

# Recibe tweets[] y intervalo = datetime(fechainicio, fechafinal)?-> saca tweets que se encuentran en esa fecha(orden ascendente)
def filtrar_fecha(tweets, intervalo):
    resul = []
    for tweet in tweets:
        if intervalo[0] <= tweet.fecha <= intervalo[1]:
            resul.append(tweet)
    resul1 = sorted(resul, key=lambda x: x.fecha, reverse=False)
    return resul1


# Group DF by date given a freq and a column to show
def group_by_date(df, freq='D', column='retweet_count'):
    # freq values = (D day, H hour, M month, Y year)
    plot_data =  df.set_index('created_at').groupby(pd.Grouper(freq=freq))
    if column!='':
        plot_data=plot_data[column]
    return plot_data


def filtrar_df_fecha(df, fecha1, fecha2):
    aux_df = df.loc[ (fecha1 <= df['created_at']) & (df['created_at'] <= fecha2) ]
    return aux_df

def buscar_palabra_df(df, palabra):
    return df['text'].str.contains(palabra)

# Suponemos que ahora se filtra por nombre
def filtrar_df_user(df, user, user_column='user'):
    new_df = df.loc[df[user_column]['name'] == user]
    return new_df

# Tratamiento de texto de df para quitar RT @entidad:
def tratar_texto_df(texto):
    texto=texto.strip()
    if texto.startswith('RT'):
        pos = texto.find(':')
        texto = texto[pos+2:]
    return texto

def hastags_texto(texto):
    hastags = []
    for palabra in texto.split():
        if palabra.startswith('#'):
            hastags.append(palabra)
    return hastags

# Get needed data for pie chart
def hashtags_pie(df, most_common=5):
    hashtag_series = df.loc[df['hashtags'].apply(lambda x: True if len(x) > 0 else False)]['hashtags']
    hashtagslist = [ item for sublist in (hashtag_series.values) for item in sublist  ]
    # Number of uniq hastags
    h_counter = Counter(hashtagslist)
    return h_counter.most_common(most_common)


def count_locations(lista, n=5):
    return Counter(list(filter(None, lista)) ).most_common(n)

def n_palabras_comun(df, n, column='text', stopwords=True, separator=' '):
    aux_df = df[column]
    aux_df = aux_df.apply(tratar_texto_df)
    aux_df = aux_df.apply(lambda x: x.lower().strip())
    lstopwords = []
    if stopwords:
        lstopwords = leer_stopwords()
    return Counter([x for x in " ".join(aux_df).split(separator) if x not in lstopwords]).most_common(n)


def uniq_usuarios_df(df):
    print(len(list(set(df['user_nombre']))))
    print( Counter(" ".join(df['user_id']).split()).most_common(10))
    test_df = df[df['user_id']=='3309112245']


def leer_stopwords():
    with open('utils/stopwords.json', encoding='utf-8-sig') as json_file:
        json_data = json.load(json_file)
    return  json_data

def clean_entities(dentity):
    # Delete not required fields from entity
    dentity.pop('symbols', None)
    dentity.pop('media', None)
    dentity.pop('symbols', None)
    dentity.pop('hashtags', None)
    # Delete not required fields from user_mentions
    for duser_mention in dentity['user_mentions']:
        duser_mention.pop('id', None)
        duser_mention.pop('indices', None)
    # Delete not required fields from urls
    dentity['urls'] = [ durl['url'] for durl in dentity['urls']]
#    for durl in dentity['urls']:
#        durl.pop('indices', None)
#        durl.pop('expanded_url', None)
#        durl.pop('display_url', None)
    return dentity

'''
# INFO FILTERED ENTITIES
 KEYS:
    'user_mentions': 
        LIST[DICT{
                'id_str',
                'screen_name',
                'name'
                }
    'hastags'
    'urls': LIST[]
    
'''

# Take user fields from user column and pass it to main df with user_key format
def user_dict_to_df(df):
    user_keys = ['id_str', 'name', 'screen_name', 'location', 'description', 'verified', 'followers_count', 'statuses_count', 'created_at', 'profile_image_url', 'friends_count']
    for key in user_keys:
        df_key = 'user_'+key
        df[df_key] = df['user'].apply(lambda x: x[key])
    del df['user']
    return df

# Procesa json a DF actualmente recibe path luego habra k añadir mongodb
def procces_data(path='F:\Desktop\TFG\Medios_Emilio\ELPAIS.json'):
    df = pd.read_json(path, encoding='utf-8')
    # Mirar user y entities
    df = df [[
        'text',
        'id_str',
        'created_at',
        'in_reply_to_status_id_str',
        'in_reply_to_user_id_str',
        'in_reply_to_screen_name',
        'retweet_count',
        'favorite_count',
        'entities',
        'user',
    ]]

    df['hashtags'] = df['entities'].apply(lambda x: [ y['text'] for y in  x['hashtags']])
    # Procces entities fields
    df['entities'] = df['entities'].apply(clean_entities)
    # Procces user fields
    df = user_dict_to_df(df)
    return df



def main():
    path = 'F:\Desktop\TFG\Medios_Emilio\ELPAIS.json'
    df = procces_data(path)
    print(df)


if __name__ == '__main__':
    main()
