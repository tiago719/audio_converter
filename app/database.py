from pymongo import MongoClient
from gridfs import GridFS
from settings import MONGO


database = MongoClient(**MONGO)['db']
gridfs = GridFS(database, 'storage')