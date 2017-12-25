import pprint
from pymongo import MongoClient

def get_db(db_name):
    '''
    Setting Up MongoDB Connections
    :param db_name:
    :return db:
    '''
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def make_pipeline():
    pipeline = [{"$match":{"NHD:way_id":{"$exists":1}}}]
    return pipeline

def aggregate(db, pipeline):
    return [doc for doc in db.aurora_il.aggregate(pipeline)]


if __name__ == '__main__':
    db = get_db('opendata')
    pipeline = make_pipeline()
    result = aggregate(db, pipeline)
    pprint.pprint(result)