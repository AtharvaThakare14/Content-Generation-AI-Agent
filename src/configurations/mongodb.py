import pymongo
import certifi
import os
import sys
from src.logging import logging
from src.exception import CustomException
from src.constants.mongodb import  MONGODB_URI


class MongoDBConnection:
    '''
    MongoDB Connection Class
    '''
    client = None

    logging.info("Started MongoDB Connection >>>")

    def __init__(self, database_name=None) -> None:
        try:
            self.mongo_url = MONGODB_URI
            if MongoDBConnection.client is None:
                MongoDBConnection.client = pymongo.MongoClient(
                    self.mongo_url, tlsCAFile=certifi.where())

            self.client = MongoDBConnection.client
            self.db = self.client[database_name]
            logging.info("MongoDB Connection Successfull >>>")
        except Exception as e:
            raise CustomException(e, sys)