import pymongo
import time

while(True):

    client = pymongo.MongoClient("localhost", 26543)

    database_name = "client_system_limit_error"
    database = client[database_name]
    collection_name = "cpu_over_limit"

    collection = database[collection_name]
    cursor = collection.find()

    for document in cursor:
        print(document)

    time.sleep(60)