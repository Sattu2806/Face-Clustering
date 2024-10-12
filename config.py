from flask_pymongo import PyMongo

# mongo = None

def init_mongo(app):
    global mongo
    mongo = PyMongo(app, serverSelectionTimeoutMS=10000, socketTimeoutMS=120000)
    return mongo