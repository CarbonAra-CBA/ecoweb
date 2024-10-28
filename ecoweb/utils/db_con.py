from pymongo import MongoClient
def db_connect():
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client['ecoweb']
    collection_traffic = db['lighthouse_traffic']
    collection_resource = db['lighthouse_resource']

    return client, db, collection_traffic, collection_resource
