from pymongo import MongoClient
# pprint library is used to make the outpu look more pretty
from pprint import pprint

# connect to MongoDB cluster
# remember to configure IP addr access in mongoDB cloud management
# connected through pem certificates (create new)
client = MongoClient()

class ConnectToMongoDB:
    def __init__(self):
        pass

    def is_mongodb_installed(self):
        # TODO check for working MongoDB installation
        pass

    def setup(self):
        pass
