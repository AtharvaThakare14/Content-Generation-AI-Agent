import sys
from typing import List, Any

from src.logging import logging
from src.constants.mongodb import *
from src.exception import CustomException
from src.db.mongodb_singleton import mongodb
from src.utils.mongo_insert_one import MongoUtils
from src.utils.add_new_field_dict import add_fields_to_dict
from src.utils.unique_id_generator import unique_id_generator


class Segments:
    def __init__(self):
        try:
            # Use the MongoDB singleton instead of creating a new connection
            self.segments_collection = mongodb.segments_collection
            self.domain_collection = mongodb.domain_collection
            self.courses_collection = mongodb.courses_collection

        except Exception as e:
            return CustomException(e, sys)

    def add_segments(self, data):
        try:
            # Check if a segment with the same name already exists
            existing_segment = self.segments_collection.find_one({
                "segment_name": data.segment_name
            })

            if existing_segment:
                return {"success": False, "message": "Segment with this name already exists."}

            # Generate unique ID and insert new segment
            unique_id = unique_id_generator("segment")

            self.segments_collection.insert_one({
                "segment_id": unique_id,
                "segment_name": data.segment_name,
                "segment_description": data.description,
            })

            return {"success": True, "segment_id": unique_id}

        except Exception as e:
            return CustomException(e, sys)

    def get_segment(self, segment_id):
        try:
            segement = self.segments_collection.find_one(
                {"segment_id": segment_id},{"_id": 0})
        
            return segement  # Segment not found
        except Exception as e:
            return CustomException(e, sys)

    def get_all_segments(self):
        try:
            segments = list(self.segments_collection.find({}, {"_id": 0}))
            return segments
        except Exception as e:
            return CustomException(e, sys)

    def update_segment(self, data):
        try:
            # Check if the segment exists
            existing_segment = self.segments_collection.find_one({
                "segment_id": data.segment_id
            })

            if not existing_segment:
                return {"success": False, "message": "Segment not found."}

            # Proceed with update
            self.segments_collection.update_one(
                {"segment_id": data.segment_id},
                {
                    "$set": {
                        "segment_name": data.segment_name,
                        "segment_description": data.description,
                    }
                }
            )
            return {"success": True, "message": "Segment updated successfully."}

        except Exception as e:
            return CustomException(e, sys)

    def delete_segment(self, data):
        try:

            # Check if the segment exists
            existing_segment = self.segments_collection.find_one({
                "segment_id": data.segment_id
            })

            if not existing_segment:
                return {"success": False, "message": "Segment not found."}

            # Delete segment from segments_collection
            result = self.segments_collection.delete_one(
                {"segment_id": data.segment_id}
            )

            if result.deleted_count > 0:
                # Remove references from domain_collection
                self.domain_collection.update_many(
                    {},
                    {"$pull": {"segment_ids": data.segment_id}}
                )

                # Remove references from courses_collection
                self.courses_collection.update_many(
                    {},
                    {"$pull": {"segment_ids": data.segment_id}}
                )

                return {"success": True, "message": "Segment and references deleted successfully."}
            else:
                return {"success": False, "message": "Segment could not be deleted."}

        except Exception as e:
            return CustomException(e, sys)
