import sys
from typing import List, Any

from src.logging import logging
from src.constants.mongodb import *
from src.exception import CustomException
from src.db.mongodb_singleton import mongodb
from src.utils.mongo_insert_one import MongoUtils
from src.utils.add_new_field_dict import add_fields_to_dict
from src.utils.unique_id_generator import unique_id_generator


class Lessons:
    def __init__(self):
        try:
            # Use the MongoDB singleton instead of creating a new connection
            self.domain_collection = mongodb.domain_collection
            self.courses_collection = mongodb.courses_collection
            self.modules_collection = mongodb.modules_collection
            self.lessons_collection = mongodb.lessons_collection
            
        except Exception as e:
            return CustomException(e, sys)

    def get_lessons(self, course_id: str, module_id: str):
        try:
            course_doc = self.lessons_collection.find_one(
                {"course_id": course_id, "modules.module_id": module_id},
                {"modules.$": 1, "_id": 0}  # Project only the matching module
            )

            if not course_doc or 'modules' not in course_doc:
                return []

            return course_doc['modules'][0]['lessons']

        except Exception as e:
            return CustomException(e, sys)
