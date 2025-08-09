import uuid


from src.logging import logging
import src.ai.course_generation.global_vars as gv
from src.configurations.mongodb import MongoDBConnection
from src.constants.mongodb import *


class InsertData:
    def __init__(self):
        self.mongodb_client = MongoDBConnection(database_name=AI_TUTOR_IQAN_DATABASE_NAME)
        self.collection = self.mongodb_client.db[DOMAIN_COLLECTION_NAME]

    def insert_data(self, data):
        try:
            logging.info(f"Data recieved for inserting")
            logging.info(data)
            insert_result = self.collection.insert_one(dict(data))
            return {
                "status": True,
                "inserted_document_id:": insert_result.inserted_id,
                "message": f"Course inserted successfully"
            }
        except Exception as e:
            logging.error(f"Error inserting Course: {str(e)}")
            return {
                "status": False,
                "message": f"Error inserting Course: {str(e)}"
            }
