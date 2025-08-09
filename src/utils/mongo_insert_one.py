from pymongo.collection import Collection
from typing import Dict, Any
import logging
import sys
from datetime import datetime


class MongoUtils:
    @staticmethod
    def insert_one_document(collection: Collection, document):
        """
        Insert a single document into a MongoDB collection with error handling.
        
        Args:
            collection (Collection): The MongoDB collection object.
            document (dict): The document to insert.
        
        Returns:
            InsertOneResult or raises exception
        """
        try:
            logging.info(f"Inserting document into MongoDB: {document}")
            result = collection.insert_one(document)
            # logging.info(f"Insert successful, ID: {result.inserted_id}")
            return {"udpated": True}
        except Exception as e:
            logging.error(f"Error inserting document: {e}")
            raise Exception(f"Mongo insert failed: {e}") from e
