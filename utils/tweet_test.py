import json, os, sys
import pandas as pd
from datetime import datetime
from collections import Counter
'''
from pymongo import MongoClient

def _connect_mongo(host, port, username, password, db):
    """ A util for making a connection to mongo """

    if username and password:
        mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
        conn = MongoClient(mongo_uri)
    else:
        conn = MongoClient(host, port)


    return conn[db]


def read_mongo(db, collection, query={}, host='localhost', port=27017, username=None, password=None, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Connect to MongoDB
    db = _connect_mongo(host=host, port=port, username=username, password=password, db=db)

    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)

    # Expand the cursor and construct the DataFrame
    df =  pd.DataFrame(list(cursor))

    # Delete the _id
    if no_id:
        del df['_id']

    return df
'''
'''
#mongodb_id = _id --> Parece ser Mongodbid no util
#truncated?
#texto = text

## Mirar esto mejor
quote = is_quote_status
quoted_status ---> entities

#tweet_id_int = id
#id_str --> Se supone k hay k usar este id

#created_at

# Tweet respuesta
#in_reply_to_status_id
#in_reply_to_screen_name
#in_reply_to_user_id
#in_reply_to_user_id_str
#in_reply_to_status_id_str

#retuiteado = retweeted # no util
#retweet_count

#favorited # no util
#favoritos = 'favorite_count'

#alomejor es util miarma
possibly_sensitive

# No parece tener siempre datos
place:{ bounding_box: {coordinates:{}}, contained_within:{}, attributes:{} } 
coordenadas = coordinates
geo:{}
metadata:{ iso_language_code:es, result_type : popular }

lang


#fuente = source  # fuente de cogida de tuit probablemente no util


# Creo que son entidades mencionadas en el tweet
entidades = entities {
            symbols,
            user_mentions:[{id:123, indices:[1,2], id_str:2937634, screen_name:el_pais, name:EL PAIS}],
            hashtags,
            urls:[url, indices, expanded_url, display_url],
            media:{}
            }

# Crear otra clase para esto
user:{ has_extended_profile , profile_use_background_image, default_profile_image, id, profile_background_image_url_https,
    verified, profile_text_color, profile_image_url_https, profile_sidebar_fill_color,
    entities:{
        url:{ urls:[igual k arriba] },
        description{}
    },
    followers_count, profile_sidebar_border_color,
    id_str, profile_background_color, listed_count, is_translation_enabled, utc_offset, statuses_count, description,
    friends_count, location, profile_link_color, profile_image_url, geo_enabled, profile_banner_url, profile_background_image_url,
    screen_name, lang, profile_background_tile, favourites_count name, url, created_at, contributors_enabled, time_zone, protected,
    default_profile, is_translator
    }

#Hacer que esto sea otro objeto tweet
retweeted_status:{ # Bucle entities# }

}

'''

# Clase entidades mencionadas en el tweet, se encuentra dentro de Tweet
class Entities():
    def __init__(self, tweet_id, entities_dic):
        self.referenced_tweet = tweet_id
        self.hastags = [ x['text'] for x in entities_dic['hashtags'] ]
        self.media = [ Media(x) for x in entities_dic['media'] ]
        self.urls = [ x['url'] for x in entities_dic['urls'] ]
        self.user_mentions = [ (mencion['id_str'], mencion['name']) for mencion in entities_dic['user_mentions'] ]
        self.polls =[]
        # Mirar si puede ser util
        # if 'polls' in entities_dic.keys():
    def __str__(self):
        hastags_str = 'Hastags: '+ ', '.join(self.hastags) + '\n'
        media_str = 'Media: '+ ', '.join(self.media.__str__()) + '\n'
        urls_str = 'Urls: '+ ', '.join(self.urls) + '\n'
        mentions_str = 'Menciones: '+ ', '.join([x[1] for x in self.user_mentions]) + '\n'
        str_retorno = hastags_str + media_str + urls_str + mentions_str
        return str_retorno

# Clase media del tweet , se encuentra en Entities
class Media():
    def __init__(self, media_dic):
        self.tipo = media_dic['type']
        self.indices = media_dic['indices']
        self.url = media_dic['url']
        self.id = media_dic['id_str']
    def __str__(self):
        str_media = 'Tipo: '+self.tipo+', url: '+ self.url
        return str_media

class User():
    def __init__(self, user_dic):
        '''
        ['has_extended_profile', 'profile_use_background_image', 'default_profile_image', 'id',
         'profile_background_image_url_https', 'verified', 'profile_text_color', 'profile_image_url_https',
         'profile_sidebar_fill_color', 'entities', 'followers_count', 'profile_sidebar_border_color', 'id_str',
         'profile_background_color', 'listed_count', 'is_translation_enabled', 'statuses_count', 'description',
         'friends_count', 'location', 'profile_link_color', 'profile_image_url', 'geo_enabled', 'profile_banner_url',
         'profile_background_image_url', 'screen_name', 'lang', 'profile_background_tile', 'favourites_count', 'name',
         'created_at', 'contributors_enabled', 'protected', 'default_profile', 'is_translator']
        '''
        self.id = user_dic['id_str']
        self.nombre = user_dic['name']
        self.nombre_pantalla = user_dic['screen_name']
        self.location = user_dic['location']
        self.url = None
        if 'url' in user_dic.keys():
            self.url = user_dic['url']
        self.descripcion = user_dic['description']
        self.verificada = user_dic['verified']
        self.seguidores = user_dic['followers_count']
        self.amigos = user_dic['friends_count']
        self.numero_tweets = user_dic['statuses_count']
        self.fecha_creacion = user_dic['created_at']
        self.imagen = user_dic['profile_image_url']
        self.imagen_http = user_dic['profile_image_url_https']
        # Mirar si me quedo con las imagenes para ponerlas en la pagina
    def sacar_url(self):
        url = 'https://twitter.com/intent/user?user_id={user_id}'
        url = url.replace('{user_id}', self.id)
        return url

class Tweet():

    def __init__(self, dic):
        self.mongodb_id = dic['_id']
        self.texto = dic['text']
        self.tweet_id = dic['id_str']
        self.fecha = datetime.strptime(dic['created_at'], '%Y-%m-%d %H:%M:%S') #2016-02-17  12:26:19 Formato de estos datos pero se supone que es diferente
        #self.fecha = datetime.strftime('%Y-%m-%d %H:%M:%S', datetime.strptime(dic['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
        # Obtener del otro formato
        #ts = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
        if 'in_reply_to_status_id_str' in dic.keys():
            self.tweet_respuesta_id = dic['in_reply_to_status_id_str']
            self.usuario_respuesta_id = dic['in_reply_to_user_id_str']
            self.usuario_respuesta_nombre = dic['in_reply_to_screen_name']
        self.retweets = dic['retweet_count']
        self.favoritos = dic['favorite_count']

        self.entidades = Entities(self.tweet_id, dic['entities'])
        self.usuario = User(dic['user'])

    def sacar_url(self):
        url = 'https://twitter.com/statuses/{ID}'
        url = url.replace('{ID}', self.tweet_id )
        return url

# link para cuenta usuario by user_id
# https://twitter.com/intent/user?user_id={user_id}

# Link para tweet by id
# https://twitter.com/statuses/{ID}


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

# Procesa json a DF actualmente recibe path luego habra k añadir mongodb
def procces_data(path):
    df = pd.read_json(path)

    # Mirar user y entities
    df = df [[
        '_id',
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
    return df


def tweet_to_dataframe(list_tweet):
    # Columnas del objeto para formar el DataFrame
    columns = ['texto', 'tweet_id', 'fecha', 'retweets', 'favoritos', 'user_mentions', 'user_id', 'user_nombre' ]
    # Lista a tratar de forma especial
    excluir_entidades = ['user_mentions' ]
    excluir_user = [('user_id','id'), ('user_nombre','nombre')]
    # Diccionario con el data para formar DataFrame
    dict = { atributo : [] for atributo in columns }
    for tweet in list_tweet:
        for key, lista in dict.items():
            if key in excluir_entidades:
                lista.append(getattr(tweet.entidades, key))
            elif key in [x[0] for x in excluir_user]:
                n_key = [x[1] for x in excluir_user if x[0]==key][0]
                lista.append(getattr(tweet.usuario, n_key))
            else:
                lista.append(getattr(tweet, key))

    # Construir DataFrame
    df = pd.DataFrame.from_dict(dict)
    return df


def test_df_plot(df):
    plot =  df.set_index('fecha').groupby(pd.Grouper(freq='D'))['retweets'].mean()#.plot()
    return plot

def filtrar_df_fecha(df, fecha1, fecha2):
    aux_df = df.loc[ (fecha1 <= df['fecha']) & (df['fecha'] <= fecha2) ]
    return aux_df

def buscar_palabra_df(df, palabra):
    return df['texto'].str.contains(palabra)

# Hay dos datos relevantes del User, su id y su nombre, mirar por cual buscarlo
# Suponemos que ahora se filtra por nombre
def filtrar_df_user(df, user, user_column='user_nombre'):
    new_df = df.loc[df[user_column] == user]
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

# Funcion Apply para sacar hastags
def sacar_hastags(df, column='texto'):
    df['hastags'] = df['texto'].apply(hastags_texto)
    return Counter( df['hastags'] )



def n_palabras_comun(df, n, column='texto', stopwords=True, separator=' '):
    aux_df = df[column]
    aux_df = aux_df.apply(tratar_texto_df)
    aux_df = aux_df.apply(lambda x: x.lower())
    lstopwords = []
    if stopwords:
        lstopwords = leer_stopwords()
    return Counter([x for x in " ".join(aux_df).split(separator) if x not in lstopwords]).most_common(n)


def uniq_usuarios_df(df):
    print(len(list(set(df['user_nombre']))))
    print( Counter(" ".join(df['user_id']).split()).most_common(10))
    test_df = df[df['user_id']=='3309112245']


# TEST PANDAS
def test_pandas(path):
    df = pd.read_json(path)
    tupla = df.shape # (nrows, ncolums)
    columnas = df.columns
    tipos = df.dtypes
    # df['columna']
    # subset = df[['user','id_str','place']]
    # df.loc[numero]acceder lineas "objetos" -> Series
    # df.iloc[nombre] --> mismo loc pero nombre Series
    # df.ix[valor] --> Busco primero por nombre y luego por numero row
    # df.ix[ rows , columns ]
    # df.groupby(columnname)[columns a mostrar].mean().plot()
    '''
    df = pd.DataFrame.from_dict(dict) # dict to df
    dict = df.to_dict() # df to dict
    '''
    # Iterar por filas de DF
    # for index, row in df.iterrows():
    #   print row[column]

    # Group by days
    # df.set_index('fecha').groupby(pd.Grouper(freq='D'))['retweets'].mean()
    # Sacar lista
    # df.set_index('created_at').groupby(pd.TimeGrouper('D'))['retweet_count'].apply(list)
    # df.loc[df['column_name'] == some_value]
    # df.loc[df['column_name'].isin(lista_valores)]
    # df.loc[(df['column_name'] == some_value) & df['other_column'].isin(some_values)] Multiples condiciones
    # isin retorna Series de bool --- ~ Para negarlo
    # df.loc[~df['column_name'].isin(some_values)]

    # Serie bool de los tweets k contienen 'la'
    x = df['text'].str.contains('la')
    df['entities'].apply(lambda x: len(x.keys()))

# Lee archivo json con tweets y retorna diccionario
def read_json_file(path):
    tweets = []
    dic_test = {}
    with open(path, encoding='utf-8-sig') as json_file:
        json_data = json.load(json_file)

        #for i in range(2000):
        for tweet in json_data:
            tweets.append(Tweet(tweet))
            #print( tweets[-1].sacar_url() )
            usuario = tweets[-1].usuario.nombre
            if usuario in dic_test.keys():
                dic_test.update({usuario:dic_test[usuario]+1})
            else:
                dic_test.update({usuario:1})
    #for usuario in sorted(dic_test, key=dic_test.get, reverse=False):
    #    print (usuario, dic_test[usuario])
    return tweets

def leer_stopwords():
    with open('utils/stopwords.json', encoding='utf-8-sig') as json_file:
        json_data = json.load(json_file)
    return  json_data

def main():
    '''
    argumentos = sys.argv
    if (len(argumentos)<2):
        print('Argumentos insuficientes: ruta a archivo json...' + ''.join(argumentos))
        return
    else:
        path = argumentos[-1]
    '''
    path = 'F:\Desktop\TFG\Datos\ELPAIS_2000.json'
    read_json_file(path)

if __name__ == '__main__':
    main()
