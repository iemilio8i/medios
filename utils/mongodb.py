import pymongo, tweepy, json, datetime, unidecode, re
import pymongo.errors
from tweepy.auth import OAuthHandler
from bson import json_util

from os import listdir
from os.path import isfile, join


CONSUMER_KEY = "CONSUMER_KEY"
CONSUMER_SECRET = "CONSUMER_SECRET"
ACCESS_TOKEN = "ACCESS_TOKEN"
ACCESS_TOKEN_SECRET = "ACCESS_TOKEN_SECRET"


# Class for listening to twitter
class StreamListener(tweepy.StreamListener):
    # This is a class provided by tweepy to access the Twitter Streaming API.

    def on_connect(self):
        # Called initially to connect to the Streaming API
        print("You are now connected to the streaming API.")

    def on_error(self, status_code):
        # On error - if an error occurs, display the error / status code
        print('An Error has occured: ' + repr(status_code))
        return False

    def on_data(self, data):
        # This is the meat of the script...it connects to your mongoDB and stores the tweet
        try:
            client = pymongo.MongoClient()

            # Use twitterdb database. If it doesn't exist, it will be created.
            db = client.tweet_test_db

            # Decode the JSON from Twitter
            datajson = json.loads(data)

            # grab the 'created_at' data from the Tweet to use for display
            created_at = datajson['created_at']

            # print out a message to the screen that we have collected a tweet
            print("Tweet collected at " + str(created_at))

            # insert the data into the mongoDB into a collection called twitter_search
            # if twitter_search doesn't exist, it will be created.
            db.twitter_search.insert(datajson)
        except Exception as e:
            print(e)

def setup_listener(MEDIOS):
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    # Set up the listener. The 'wait_on_rate_limit=True' is needed to help with Twitter API rate limiting.
    listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
    streamer = tweepy.Stream(auth=auth, listener=listener)
    print("Tracking: " + str(MEDIOS))
    streamer.filter(track=MEDIOS)

def limpiar_nombre_medio(nombre):
    nombre = nombre.lower()
    nombre = unidecode.unidecode(nombre)
    pattern = re.compile('[\W_]+')
    return pattern.sub('', nombre)

def test_connection():

    try:
        client = pymongo.MongoClient(serverSelectionTimeoutMS=1)  # default ('localhost', 27017)

        print(client.server_info())  # Saca error si no conecta
        print('hola esto no ha explotado')


        db = client.tweet_test_db
        collection = db.tweets_test2
        print(client.database_names())
        try:
            post_id = collection.insert_one({'medio':'olaktal'})
        except pymongo.errors.DuplicateKeyError:
            print('hola k tal')
        result = collection.create_index([('medio', pymongo.ASCENDING)], unique=True, )
        #db.collection.ensure_index([("medio", pymongo.ASCENDING), ("unique", 1), ("dropDups", 1)])
        posts = db.posts
        #print(db.collection_names())
        #for collection in db.collection_names():
        #    print(db[collection].count())
        #cursor = collection.find({})
        #print(pd.DataFrame(list(cursor)))
        #print(cursor[0].pop('user'))
        #print(cursor[0])

        #print(post_id)

        # force connection on a request as the
        # connect=True parameter of MongoClient seems
        # to be useless here
    except pymongo.errors.ServerSelectionTimeoutError as err:
        # do whatever you need
        print(err)
    '''
    db = client.test_database  # test_database = nombre base de datos
    collection = db.test_collection
    # Insertar documento en collection
    posts = db.posts
    data={}
    post_id = posts.insert_one(data).inserted_id

    # Coger documento
    # data = {ekis=peke}
    posts.find_one(data)

    posts.insert_many([data])
    # returns all found
    posts.find(data)
    d = datetime.datetime(2009, 11, 12, 12)
    for post in posts.find({"date": {"$lt": d}}).sort("author"):
        print('hola')

    #Indexes
    result = db.profiles.create_index([('user_id', pymongo.ASCENDING)], unique = True)
    sorted(list(db.profiles.index_information()))
    '''

def json_upload_to_collection(file, medio_name):
    try:
        client = pymongo.MongoClient(serverSelectionTimeoutMS=1)  # default ('localhost', 27017)

        client.server_info() # Saca error si no conecta

        json_data = file.read()
        data = json_util.loads(json_data)

        db = client.tweet_test_db
        if 'medios' not in db.collection_names():
            db.create_collection('medios')
        index_name = 'nombre_medio'
        if index_name not in db.medios.index_information():
            db.medios.create_index(index_name, unique=True)

        collection_name=limpiar_nombre_medio(medio_name)
        for collection in db.collection_names():
            original = collection_name
            if collection == original  or original in collection or collection in original:
                collection_name = collection
                break

        collection = db[collection_name]

        try:
            post_id = db.medios.insert_one({'medio':collection})
        except pymongo.errors.DuplicateKeyError:
            pass

        post_id = collection.insert_many(data)
        db.medios.insert_one({ 'nombre_medio': medio_name })
        return 'Archivo subido satisfactoriamente'


    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(err)
        return 'Error en la base de datos'

def json_file_to_collection(path, collection_name):
    try:
        client = pymongo.MongoClient(serverSelectionTimeoutMS=1)  # default ('localhost', 27017)

        client.server_info() # Saca error si no conecta

        collection_name = limpiar_nombre_medio(collection_name)
        json_data = open(path, encoding='utf-8').read()
        data = json_util.loads(json_data)

        db = client.tweet_test_db
        collection = db[collection_name]

        post_id = collection.insert_many(data)
        print(post_id.inserted_ids)

        # Extra Info
        # Select whole collection: cursor = collection.find({})
        #print(pd.DataFrame(list(cursor)))
        #print(client.database_names())
        #print(db.collection_names())

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(err)

def update_medio(user, medio):
    fecha = user['created_at']
    try:
        medio = limpiar_nombre_medio(medio)
        client = pymongo.MongoClient(serverSelectionTimeoutMS=1)  # default ('localhost', 27017)

        client.server_info()  # Saca error si no conecta

        db = client.tweet_test_db
        medios = db['medios']

        consulta_medio_db = medios.find()
        medio_db =  None
        for aux_medio_db in list(consulta_medio_db):
            if limpiar_nombre_medio(aux_medio_db) in medio or medio in limpiar_nombre_medio(aux_medio_db):
                medio_db = aux_medio_db
                break
        try:
            if medio_db['fecha'] < fecha:
                medio_db.update({'user': user, 'fecha': fecha})
        except:
            medio_db.update({'user':user, 'fecha':fecha})

        medios.update_one({'nombre_medio':medio}, {"$set": medio_db}, upsert=False)

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(err)

def folder_json(folder_path):
    onlyfiles = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    json_files = [ f for f in onlyfiles if not f.endswith('2000.json')]
    nombres = [ f.replace('.json','') for f in json_files ]
    for i,f in enumerate(json_files):
        json_file_to_collection(folder_path+'/'+f, limpiar_nombre_medio(nombres[i]))

# Sacar lista de medios a partir del nombre de las collecciones
def get_collection_list():
    try:
        client = pymongo.MongoClient(serverSelectionTimeoutMS=1)  # default ('localhost', 27017)
        client.server_info() # Saca error si no conecta
        db = client.tweet_test_db
        # Limpiar lista
        resul = []
        for collection in list(db.collection_names()):
            consulta = db[collection].find()
            resul.append((collection, consulta.count()))
        resul = sorted(resul, reverse=True, key=lambda tup: tup[1])
        return resul

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(err)

# Sacar lista de medios a partir del nombre de las collecciones
def get_medios_destacados():
    try:
        client = pymongo.MongoClient(serverSelectionTimeoutMS=1)  # default ('localhost', 27017)
        client.server_info() # Saca error si no conecta
        db = client.tweet_test_db
        # Limpiar lista
        resul = []
        for collection in list(db.collection_names()):
            consulta = db[collection].find()
            resul.append((collection, consulta.count()))
        resul = [x[0] for x in sorted(resul, reverse=True, key=lambda tup: tup[1])]
        return resul

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(err)

def get_medio_list():
    try:
        client = pymongo.MongoClient(serverSelectionTimeoutMS=1)  # default ('localhost', 27017)
        client.server_info() # Saca error si no conecta
        db = client.tweet_test_db
        medio_db = db.medios.find()
        print(medio_db.count())

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(err)

def check_medio_in_medios(medio):
    try:
        client = pymongo.MongoClient(serverSelectionTimeoutMS=1)  # default ('localhost', 27017)
        client.server_info() # Saca error si no conecta
        db = client.tweet_test_db
        # Limpiar lista
        medio = limpiar_nombre_medio(medio)
        if 'medios' in list(db.collection_names()):
            medio_db = db.medios.find({'nombre_medio':medio})
            if medio_db.count()>0:
                for encontrado in list(medio_db):
                    if 'user' in encontrado.keys():
                        return encontrado['user']
                    else:
                        return False
            else:
                return False

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(err)

def consulta_medio_fecha(medio_collection, fecha_i=datetime.datetime(2010, 2, 15), fecha_f=datetime.datetime.now(), limit=None):
    try:
        client = pymongo.MongoClient(serverSelectionTimeoutMS=1)  # default ('localhost', 27017)
        client.server_info() # Saca error si no conecta
        db = client.tweet_test_db
        medio_collection = limpiar_nombre_medio(medio_collection)
        for medio in db.collection_names():
            medio_limpio = limpiar_nombre_medio(medio)
            if medio_limpio in medio_collection or medio_collection in medio_limpio:
                medio_collection = medio
        # Limpiar lista
        collection = db[medio_collection]
        fecha_i = fecha_i.strftime('%Y-%m-%d %H:%M:%S')
        fecha_f = fecha_f.strftime('%Y-%m-%d %H:%M:%S')
        if limit:
            cursor = collection.find( {'created_at': {'$lt': fecha_f, '$gte': fecha_i}} ).sort("created_at", pymongo.DESCENDING).limit(limit)
        else:
            cursor = collection.find( {'created_at': {'$lt': fecha_f, '$gte': fecha_i}} )
        return list(cursor)

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(err)


def sacar_intervalo_fecha(medio_collection):
    try:
        client = pymongo.MongoClient(serverSelectionTimeoutMS=1)  # default ('localhost', 27017)
        client.server_info() # Saca error si no conecta
        db = client.tweet_test_db
        medio_collection = limpiar_nombre_medio(medio_collection)
        for medio in db.collection_names():
            medio_limpio = limpiar_nombre_medio(medio)
            if medio_limpio in medio_collection or medio_collection in medio_limpio:
                medio_collection = medio
        # Limpiar lista
        collection = db[medio_collection]
        try:
            fecha_i = list(collection.find().sort("created_at", pymongo.ASCENDING).limit(1))[0]
            fecha_i = fecha_i['created_at'].split()[0]
            fecha_f = list(collection.find().sort("created_at", pymongo.DESCENDING).limit(1))[0]
            fecha_f = fecha_f['created_at'].split()[0]
            return fecha_i, fecha_f
        except:
            return 'hola','mundo'

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(err)


def main():
    #test_connection()
    folder_path = 'F:\Desktop\TFG\Medios_Emilio'
    #folder_json(folder_path)
    MEDIOS = ['elpais_espana']
    #setup_listener(MEDIOS)
    #print(get_medios_list())

    #fecha_i = datetime.datetime(2016, 2, 15)
    #fecha_f = datetime.datetime(2016, 2, 16)
    #print(consulta_medio_fecha('ELPAIS', fecha_i, fecha_f))
    #print(consulta_medio_fecha('ELPAIS'))
    limpiar_nombre_medio('El_País')

if __name__ == '__main__':
    main()
