import sys
from typing import List, Any

from src.logging import logging
from src.constants.mongodb import *
from src.exception import CustomException
from src.utils.mongo_insert_one import MongoUtils
from src.utils.add_new_field_dict import add_fields_to_dict
from src.utils.unique_id_generator import unique_id_generator
from src.db.mongodb_singleton import mongodb

from src.ai.course_description_generator.course_description import CourseDescriptionGenerator
from src.ai.domain_description_generator.domain_description import DomainDescriptionGenerator


class Domains:
    def __init__(self):
        try:
            # Use the MongoDB singleton instead of creating a new connection
            self.domain_collection = mongodb.domain_collection
            self.courses_collection = mongodb.courses_collection
            self.modules_collection = mongodb.modules_collection
            self.on_demand_domains_collection = mongodb.on_demand_domains_collection

        except Exception as e:
            return CustomException(e, sys)

    def add_new_domain(self, data):
        try:
            data = dict(data)
            unique_id = unique_id_generator("DOMAIN")
            # data['domain_id'] = unique_id
            # data['on_demand'] = False

            # Generate domain description
            domain_description_generator = DomainDescriptionGenerator()
            domain_data = domain_description_generator.generate_description(
                data, unique_id)

            # Insert domain with description into collection
            result = MongoUtils.insert_one_document(
                self.domain_collection, domain_data)
            return result
        except Exception as e:
            return CustomException(e, sys)

    def get_domains(self):
        try:
            results = list(self.domain_collection.find({}, {'_id': 0}))
            return results
        except Exception as e:
            return CustomException(e, sys)

    def update_on_demand_domain(self, data):
        try:
            self.domain_collection.update_one(
                {'domain_id': data.domain_id},
                {'$set': {'on_demand': data.on_demand}}
            )
            return True
        except Exception as e:
            return CustomException(e, sys)

    def get_on_demand_domain(self):
        try:
            results = list(
                self.domain_collection.find({"on_demand": True}, {'_id': 0, }))
            return results
        except Exception as e:
            return CustomException(e, sys)

    def add_courses_to_domain(self, data):
        try:
            domain_id = data.domain_id
            courses_ids = data.courses_ids

            # Check if domain exists
            domain = self.domain_collection.find_one({"domain_id": domain_id})
            if not domain:
                return False

            # Filter out course IDs that are already in the domain
            existing_course_ids = domain.get("courses_ids", [])
            new_course_ids = [
                course_id for course_id in courses_ids if course_id not in existing_course_ids]

            # If there are new courses to add, update the domain
            if new_course_ids:
                self.domain_collection.update_one(
                    {"domain_id": domain_id},
                    {
                        "$addToSet": {
                            "courses_ids": {"$each": new_course_ids}
                        }
                    }
                )

            # Return True to maintain backward compatibility
            return True

        except Exception as e:
            return CustomException(e, sys)

    def get_domain_courses(self, course_ids: list):
        try:
            # self.courses_collection = self.mongodb_client.db[COURSES_COLLECTION_NAME]

            # Query all courses where course_id is in the provided list
            results = list(self.courses_collection.find(
                {"course_id": {"$in": course_ids}},
                {"_id": 0}  # Optional: Exclude MongoDB's internal _id field
            ))
            return results
        except Exception as e:
            raise CustomException(e, sys)

    def add_on_demand_domains(self):
        try:
            data = dict(data)
            data['domain_id'] = unique_id_generator("DEMAND")
            self.domain_collection.insert_one(dict(data))
            # Get all on-demand domains
        except Exception as e:
            return CustomException(e, sys)

    def delete_domain(self, domain_id):
        try:
            self.domain_collection.delete_one({"domain_id": domain_id})
            return True
        except Exception as e:
            return CustomException(e, sys)

    def update_domain(self, data):
        try:
            self.domain_collection.update_one({"domain_id": data.domain_id},
                                              {'$set': {"domain_name": data.domain_name,
                                                        "description": data.description}
                                               })
            return True
        except Exception as e:
            return CustomException(e, sys)

    def delete_course(self, domain_id, course_id):
        try:
            self.domain_collection.update_one(
                {"domain_id": domain_id},
                {"$pull": {"courses_ids": course_id}}
            )
            return {"message": "Course removed from domain successfully"}
        except Exception as e:
            raise CustomException(e, sys)

    def add_segments_to_domain(self, data):
        try:
            domain_id = data.domain_id
            segment_ids = data.segment_ids  # List of segment IDs to add

            # Check if domain exists
            domain = self.domain_collection.find_one({"domain_id": domain_id})
            if not domain:
                return False

            # Filter out segment IDs that are already in the domain
            existing_segment_ids = domain.get("segment_ids", [])
            new_segment_ids = [
                seg_id for seg_id in segment_ids if seg_id not in existing_segment_ids
            ]

            # If there are new segments to add, update the domain
            if new_segment_ids:
                self.domain_collection.update_one(
                    {"domain_id": domain_id},
                    {
                        "$addToSet": {
                            "segment_ids": {"$each": new_segment_ids}
                        }
                    }
                )

            return True

        except Exception as e:
            return CustomException(e, sys)

    def remove_segments_from_domain(self, data):
        try:
            domain_id = data.domain_id
            segment_ids = data.segment_ids  # List of segment IDs to remove

            # Check if domain exists
            domain = self.domain_collection.find_one({"domain_id": domain_id})
            if not domain:
                return False

            # Update the domain by pulling the segment IDs
            self.domain_collection.update_one(
                {"domain_id": domain_id},
                {
                    "$pull": {
                        "segment_ids": {"$in": segment_ids}
                    }
                }
            )

            return True

        except Exception as e:
            return CustomException(e, sys)
