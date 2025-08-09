import sys
from typing import List, Any, Dict

from src.logging import logging
from src.constants.mongodb import *
from src.exception import CustomException
from src.utils.mongo_insert_one import MongoUtils
from src.utils.add_new_field_dict import add_fields_to_dict
from src.utils.unique_id_generator import unique_id_generator
from src.db.mongodb_singleton import mongodb


class Modules:
    def __init__(self):
        try:
            # Use the MongoDB singleton instead of creating a new connection
            self.domain_collection = mongodb.domain_collection
            self.courses_collection = mongodb.courses_collection
            self.modules_collection = mongodb.modules_collection
            self.lessons_collection = mongodb.lessons_collection
            
        except Exception as e:
            return CustomException(e, sys)

    def get_modules(self, course_id: str) -> Dict:
        try:
            # 1. Fetch course metadata + modules
            course_doc = self.modules_collection.find_one(
                {"course_id": course_id},
                {"_id": 0, "course_id": 1, "level": 1, "course": 1,
                    "duration": 1, "tools": 1, "modules": 1}
            )

            if not course_doc:
                return {}

            # 2. Fetch lesson document and count lessons by module_id
            lessons_doc = self.lessons_collection.find_one(
                {"course_id": course_id},
                {"_id": 0, "modules": 1}
            )

            lesson_counts = {
                mod["module_id"]: len(mod.get("lessons", []))
                for mod in lessons_doc.get("modules", []) if "module_id" in mod
            } if lessons_doc else {}

            # 3. Enrich each module with lesson_count and ensure no nested module structure
            enriched_modules = []
            for mod in course_doc["modules"]:
                # Handle case where module might have a nested 'module' structure
                if "module" in mod and isinstance(mod["module"], dict):
                    # Extract nested module content and merge with top level
                    nested_module = mod.pop("module")
                    # Keep original title and description if they exist
                    nested_module["title"] = mod.get(
                        "title", nested_module.get("title", ""))
                    nested_module["description"] = mod.get(
                        "description", nested_module.get("description", ""))
                    # Merge other fields from top level
                    for key, value in mod.items():
                        if key not in ["title", "description"]:
                            nested_module[key] = value
                    enriched = nested_module
                else:
                    enriched = mod.copy()

                # Add lesson count
                enriched["lesson_count"] = lesson_counts.get(
                    enriched.get("module_id", ""), 0)
                enriched_modules.append(enriched)

            # 4. Return full course structure
            course_details = self.courses_collection.find_one(
                {"course_id": course_id}, {"_id": 0,"course_name":0,"course_id":0,"created_at":0})
            return {
                "course_id": course_doc["course_id"],
                "course_details": course_details,
                "level": course_doc["level"],
                "course": course_doc["course"],
                "duration": course_doc["duration"],
                "tools": course_doc["tools"],
                "modules": enriched_modules
            }

        except Exception as e:
            raise CustomException(e, sys)

    def update_module(self, data):
        try:
            self.modules_collection.update_one(
                {"course_id": data.course_id},
                {
                    "$set": {
                        "course": data.course_name,
                        "level": data.level,
                        "duration": data.duration,
                        "tools": data.tools
                    }
                }
            )
            return {"message": "Module updated successfully"}
        except Exception as e:
            raise CustomException(e, sys)

    def update_module_content(self, data):
        try:
            self.modules_collection.update_one(
                # Find the module inside the array
                {"modules.module_id": data.module_id},
                {
                    "$set": {
                        "modules.$.title": data.module_title,
                        "modules.$.description": data.description,
                        "modules.$.estimated_completion_time": data.estimated_completion_time,
                        "modules.$.prerequisites.knowledge": data.prerequisites_knowledge,
                        "modules.$.prerequisites.technical": data.prerequisites_technical,
                        "modules.$.key_topics": data.key_topics,
                        "modules.$.practical_applications": data.practical_applications,
                        "modules.$.learning_objectives": data.learning_objectives
                    }
                }
            )
            return {"message": "Module updated successfully"}
        except Exception as e:
            raise CustomException(e, sys)
