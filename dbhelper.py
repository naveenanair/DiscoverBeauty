# Author: Naveena Nair
# Description: mongodb helper module

import pymongo, json
from pymongo import MongoClient

################################################################################
def init_mongo_client(dbName, collNames=[]):
    client = pymongo.MongoClient()
    db = client[dbName]

    collections = {}
    for collName in collNames:
        collections[collName] = db[collName]
    return (db, collections)


################################################################################
def insertRow(db, collName, dataDict):
    db[collName].insert(dataDict)
