import sys
from typing import List, Any

from src.logging import logging
from src.constants.mongodb import *
from src.exception import CustomException
from src.db.mongodb_singleton import mongodb
from src.utils.mongo_insert_one import MongoUtils
from src.utils.add_new_field_dict import add_fields_to_dict
from src.utils.unique_id_generator import unique_id_generator


from src.ai.module_generator.graph import ModuleGraphgenerator
from src.ai.lessons_generator.agents.lessons_generator import LessonsGenerator
from src.ai.course_description_generator.course_description import CourseDescriptionGenerator


class Courses:
    def __init__(self):
        try:
            # Use the MongoDB singleton instead of creating a new connection
            self.domain_collection = mongodb.domain_collection
            self.courses_collection = mongodb.courses_collection
            self.modules_collection = mongodb.modules_collection
            self.lessons_collection = mongodb.lessons_collection
            self.segments_collection = mongodb.segments_collection

        except Exception as e:
            return CustomException(e, sys)

    def get_courses_with_course_count(self):
        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": MODULES_COLLECTION_NAME,
                        "localField": "course_id",
                        "foreignField": "course_id",
                        "as": "course_data"
                    }
                },
                {
                    "$addFields": {
                        "num_courses": {
                            "$ifNull": [{"$arrayElemAt": ["$course_data.num_modules", 0]}, 0]
                        }
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "course_id": 1,
                        "segment_ids":1,
                        "course_name": 1,
                        "level": 1,
                        "description": 1,
                        "image_uri": 1,
                        "created_at": 1,
                        "num_courses": 1,
                        "is_popular": 1,
                        "is_trending": 1
                    }
                }
            ]

            results = list(self.courses_collection.aggregate(pipeline))
            return results

        except Exception as e:
            raise CustomException(e, sys)

    def get_courses_by_segment_id(self,segment_id):
        try:
            pipeline = [
                {
                    "$match": {
                        "segment_ids": segment_id
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "course_id": 1,
                        "segment_ids":1,
                        "course_name": 1,
                        "level": 1,
                        "description": 1,
                        "image_uri": 1,
                        "created_at": 1,
                        "num_courses": 1,
                        "is_popular": 1,
                        "is_trending": 1
                    }
                }
            ]

            results = list(self.courses_collection.aggregate(pipeline))
            return results

        except Exception as e:
            return CustomException(e, sys)

    def get_course_details(
            self, course_id: str
    ) -> dict:
        try:
            result = self.collection.find_one(
                {"course_id": course_id},
                {"_id": 0}
            )
            return result
        except Exception as e:
            return CustomException(e, sys)

    def generate_course(self, data):
        try:
            # Check if course with the same name already exists
            existing_course = self.courses_collection.find_one(
                {"course_name": data.course_name})
            if existing_course:
                logging.info(f"Course '{data.course_name}' already exists.")
                return {"message": f"Course '{data.course_name}' already exists."}

            # Generate Unique ID for the Course
            unique_id = unique_id_generator(prefix="COURSE")

            # Generate The Descriptions for the course and save to MongoDB
            course_description_generator = CourseDescriptionGenerator()
            description = course_description_generator.generate_description(
                data, unique_id)
            result = MongoUtils.insert_one_document(
                self.courses_collection, description)
            logging.info(f"Generated Course Description: {description}")

            # Generate Course Modules and save to mongodb
            module_generator = ModuleGraphgenerator()
            generated_modules = module_generator.generate_module(description)
            logging.info(f"Generated Modules: {generated_modules['modules']}")
            result = MongoUtils.insert_one_document(
                self.modules_collection, generated_modules)

            # Generate Lessons for each Modules and save to mongodb
            lesson_generator = LessonsGenerator()
            lessons = lesson_generator.generate_lessons_for_each_module(
                generated_modules['modules'], unique_id)

            # final = dict(result.model_dump())
            # final = final['modules']
            # final = final['course_id'] = unique_id

            result = MongoUtils.insert_one_document(
                self.lessons_collection, dict(lessons.model_dump()))

            return result

        except Exception as e:
            raise CustomException(e, sys)

    def edit_trending_popular_course(self, data):
        try:
            self.courses_collection.update_one(
                {"course_id": data.course_id},
                {
                    "$set": {
                        "is_popular": data.is_popular,
                        "is_trending": data.is_trending
                    }
                }
            )
            return {"message": "Course Updated Successfully"}
        except Exception as e:
            raise CustomException(e, sys)

    def edit_course(self, data):
        try:
            existing_course = self.courses_collection.find_one(
                {"course_id": data.course_id})
            if existing_course:
                logging.info(f"Course '{data.course_name}' already exists.")
                self.courses_collection.update_one(
                    {"course_id": data.course_id},
                    {
                        "$set": {
                            "level": data.level,
                            "image_uri": data.image_uri,
                            "description": data.description,
                            "course_name": data.course_name
                        }
                    }
                )
                return {"message": "Course Updated Successfully"}
            else:
                return {"message": "No Course Found"}

        except Exception as e:
            raise CustomException(e, sys)

    def delete_course(self, data):
        try:
            course_id = data.course_id

            # 1. Delete course from courses collection
            self.courses_collection.delete_one({"course_id": course_id})

            # 2. Delete related modules
            self.modules_collection.delete_many({"course_id": course_id})

            # 3. Delete related lessons
            self.lessons_collection.delete_many({"course_id": course_id})

            # 4. Remove course_id from all domain documents (if exists)
            self.domain_collection.update_many(
                {"courses_ids": course_id},
                {"$pull": {"courses_ids": course_id}}
            )

            return {"message": "Course and associated data deleted successfully"}

        except Exception as e:
            raise CustomException(e, sys)


########################   ADD Segment to course ############################

    def add_segment_to_course(self, data):
        try:
            course_id = data.course_id
            segment_ids = data.segment_ids  # Expecting a list of segment IDs

            # Check if course exists
            course = self.courses_collection.find_one({"course_id": course_id})
            if not course:
                return False

            # Get existing segment IDs from the course
            existing_segment_ids = course.get("segment_ids", [])
            new_segment_ids = [
                segment_id for segment_id in segment_ids if segment_id not in existing_segment_ids
            ]

            # If there are new segments to add, update the course
            if new_segment_ids:
                self.courses_collection.update_one(
                    {"course_id": course_id},
                    {
                        "$addToSet": {
                            "segment_ids": {"$each": new_segment_ids}
                        }
                    }
                )

            return True

        except Exception as e:
            return CustomException(e, sys)

    def remove_segments_from_course(self, data):
        try:
            course_id = data.course_id
            segment_ids = data.segment_ids  # Expecting a list of segment IDs to remove

            # Check if course exists
            course = self.courses_collection.find_one({"course_id": course_id})
            if not course:
                return False

            # Update the course by pulling the segment IDs
            self.courses_collection.update_one(
                {"course_id": course_id},
                {
                    "$pull": {
                        "segment_ids": {"$in": segment_ids}
                    }
                }
            )

            return True

        except Exception as e:
            return CustomException(e, sys)
