import sys
import json
from bson import ObjectId
from datetime import datetime
from src.logging import logging
from src.exception import CustomException
from src.db.mongodb_singleton import mongodb
from src.utils.unique_id_generator import unique_id_generator
from src.schemas.combined_courses import ModuleReference, CourseReference, CombinedCourseSchema
from src.components.modules import Modules


def convert_objectid_to_str(obj):
    """
    Recursively convert all ObjectId objects to strings in a document.
    Works with nested dictionaries and lists.
    """
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    else:
        return obj

# Custom JSON encoder to handle ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

class CombinedCourses:
    def __init__(self):
        try:
            self.courses_collection = mongodb.courses_collection
            self.modules_collection = mongodb.modules_collection
            self.lessons_collection = mongodb.lessons_collection
            self.combined_courses_collection = mongodb.combined_courses_collection
            self.modules_component = Modules()
            
        except Exception as e:
            raise CustomException(e, sys)

    def create_combined_course(self, request):
        try:
            # Generate a unique ID for the combined course
            combined_course_id = unique_id_generator(prefix="COMBO")
            
            # Extract course IDs from the request
            course_ids = request.course_ids
            
            # Fetch all courses to be combined
            courses_to_combine = list(self.courses_collection.find({"course_id": {"$in": course_ids}}))
            
            # Check if all courses were found
            if len(courses_to_combine) != len(course_ids):
                # Find which course IDs are missing
                found_course_ids = [course["course_id"] for course in courses_to_combine]
                missing_course_ids = [course_id for course_id in course_ids if course_id not in found_course_ids]
                raise Exception(f"The following course IDs were not found in the database: {missing_course_ids}")
            
            # Prepare the courses list with their modules
            courses_list = []
            for i, course in enumerate(courses_to_combine):
                course_id = course["course_id"]
                course_name = course["course_name"]
                
                # Use the Modules component to fetch modules for this course
                course_data = self.modules_component.get_modules(course_id)
                module_refs = []
                
                # Extract modules from the course data
                if course_data and "modules" in course_data:
                    for module in course_data["modules"]:
                        if "module_id" in module and "title" in module:
                            module_ref = ModuleReference(
                                module_id=module["module_id"],
                                module_name=module["title"]
                            )
                            module_refs.append(module_ref)
                
                course_ref = CourseReference(
                    course_id=course_id,
                    course_name=course_name,
                    order=i+1,  # Order based on the sequence in the request
                    modules=module_refs
                )
                courses_list.append(course_ref)
            
            # Create the combined course document
            # Convert Pydantic models to dictionaries manually to handle ObjectId
            courses_data = []
            for course in courses_list:
                course_dict = {
                    "course_id": course.course_id,
                    "course_name": course.course_name,
                    "order": course.order,
                    "modules": []
                }
                
                for module in course.modules:
                    module_dict = {
                        "module_id": module.module_id,
                        "module_name": module.module_name
                    }
                    course_dict["modules"].append(module_dict)
                
                courses_data.append(course_dict)
            
            combined_course = {
                "combined_course_id": combined_course_id,
                "title": request.course_name,
                "description": request.description,
                "image_uri": request.image_url,
                "level": request.level,
                "topics": request.topics if hasattr(request, 'topics') else [],
                "is_trending": False,
                "is_popular": False,
                "courses": courses_data,
                "created_at": request.created_at,
                "updated_at": request.created_at
            }
            
            # Insert the combined course into the database
            result = self.combined_courses_collection.insert_one(combined_course)
            
            # Convert ObjectId to string and return the created combined course
            return convert_objectid_to_str(combined_course)
            
        except Exception as e:
            logging.error(f"Error creating combined course: {str(e)}")
            raise CustomException(e, sys)
            
    def combine_courses(self, request):
        try:
            # Extract parameters from request
            course_ids = request.course_ids
            course_name = request.course_name
            level = request.level
            image_url = request.image_url
            description = request.description
            created_at = request.created_at
            
            # 1. Fetch all courses to be combined
            courses_to_combine = list(self.courses_collection.find({"course_id": {"$in": course_ids}}))
            if len(courses_to_combine) != len(course_ids):
                raise Exception("One or more course IDs are invalid.")

            # 2. Create a new course
            new_course_id = unique_id_generator(prefix="COURSE")
            new_course = {
                "course_id": new_course_id,
                "course_name": course_name,
                "description": description,
                "level": level,
                "image_uri": image_url,
                "is_popular": False,
                "is_trending": False,
                "segment_ids": [],
                "modules": [],
                "created_at": created_at,
                "is_combined": True,
                "source_course_ids": course_ids
            }

            # 3. Combine modules and lessons
            all_modules = []
            all_lessons = []
            for course in courses_to_combine:
                course_id = course["course_id"]
                # Find all modules for this course
                modules = list(self.modules_collection.find({"course_id": course_id}))
                for module in modules:
                    try:
                        # Print module keys for debugging
                        module_keys = list(module.keys())
                        logging.info(f"Module keys: {module_keys}")
                        
                        # Check if module_id exists
                        if "module_id" not in module:
                            logging.error("module_id not found in module")
                            # Try to log a safe representation of the module
                            try:
                                safe_module = {k: str(v) for k, v in module.items()}
                                logging.error(f"Module content: {safe_module}")
                            except Exception as e:
                                logging.error(f"Could not log module content: {str(e)}")
                            continue
                            
                        # Create a safe copy of the module by converting to dict and back
                        module_dict = {}
                        for key in module:
                            if key == '_id':
                                # Skip the MongoDB _id field when copying
                                continue
                            # Convert ObjectId to string if needed
                            if isinstance(module[key], ObjectId):
                                module_dict[key] = str(module[key])
                            else:
                                module_dict[key] = module[key]
                                
                        module_dict["course_id"] = new_course_id
                        all_modules.append(module_dict)
                        
                        # Find all lessons for this module
                        module_id = module["module_id"]
                        lessons = list(self.lessons_collection.find({"module_id": module_id}))
                        for lesson in lessons:
                            # Create a safe copy of the lesson
                            lesson_dict = {}
                            for key in lesson:
                                if key == '_id':
                                    # Skip the MongoDB _id field when copying
                                    continue
                                # Convert ObjectId to string if needed
                                if isinstance(lesson[key], ObjectId):
                                    lesson_dict[key] = str(lesson[key])
                                else:
                                    lesson_dict[key] = lesson[key]
                                    
                            lesson_dict["course_id"] = new_course_id
                            all_lessons.append(lesson_dict)
                    except KeyError as ke:
                        logging.error(f"KeyError in module processing: {ke}")
                        continue

            # Add all module IDs to the new course - ensure they're strings, not ObjectId
            new_course["modules"] = []
            for module in all_modules:
                if module.get("module_id"):
                    module_id = module.get("module_id")
                    # Convert to string if it's an ObjectId
                    if isinstance(module_id, ObjectId):
                        module_id = str(module_id)
                    new_course["modules"].append(module_id)

            # 4. Insert new data into the database
            self.courses_collection.insert_one(new_course)
            
            # 5. Update modules collection with bulk write operation if there are modules
            if all_modules:
                module_operations = []
                for module in all_modules:
                    try:
                        # Create an update operation for each module
                        if "module_id" not in module:
                            logging.error("module_id not found in module during update")
                            continue
                        
                        # Get the module_id and ensure it's properly formatted
                        module_id = module["module_id"]
                        # If it's already a string representation of ObjectId, use it as is
                        
                        filter_criteria = {"module_id": module_id}
                        update_data = {"$set": {"course_id": new_course_id}}
                        module_operations.append({
                            "update_one": {
                                "filter": filter_criteria,
                                "update": update_data
                            }
                        })
                    except KeyError as ke:
                        logging.error(f"KeyError in module update: {ke}")
                        continue
                
                # Execute the bulk update if there are operations
                if module_operations:
                    self.modules_collection.bulk_write(module_operations)
            
            # 6. Update lessons if needed
            if all_lessons:
                lesson_operations = []
                for lesson in all_lessons:
                    try:
                        # Create an update operation for each lesson
                        if "lesson_id" not in lesson:
                            logging.error("lesson_id not found in lesson during update")
                            continue
                        
                        # Get the lesson_id and ensure it's properly formatted
                        lesson_id = lesson["lesson_id"]
                        # If it's already a string representation of ObjectId, use it as is
                        
                        filter_criteria = {"lesson_id": lesson_id}
                        update_data = {"$set": {"course_id": new_course_id}}
                        lesson_operations.append({
                            "update_one": {
                                "filter": filter_criteria,
                                "update": update_data
                            }
                        })
                    except KeyError as ke:
                        logging.error(f"KeyError in lesson update: {ke}")
                        continue
                
                # Execute the bulk update if there are operations
                if lesson_operations:
                    self.lessons_collection.bulk_write(lesson_operations)

            return new_course

        except Exception as e:
            raise CustomException(e, sys)
            
    def get_all_combined_courses(self):
        try:
            # Retrieve all combined courses from the database
            combined_courses = list(self.combined_courses_collection.find())
            
            # Convert all ObjectId objects to strings recursively
            combined_courses = convert_objectid_to_str(combined_courses)
            
            return combined_courses
            
        except Exception as e:
            logging.error(f"Error retrieving combined courses: {str(e)}")
            raise CustomException(e, sys)
    
    def get_combined_course_by_id(self, combined_course_id):
        try:
            # Find the combined course by ID
            combined_course = self.combined_courses_collection.find_one({"combined_course_id": combined_course_id})
            
            if not combined_course:
                raise Exception(f"Combined course with ID {combined_course_id} not found.")
            
            # Convert all ObjectId objects to strings recursively
            combined_course = convert_objectid_to_str(combined_course)
            
            return combined_course
            
        except Exception as e:
            logging.error(f"Error retrieving combined course: {str(e)}")
            raise CustomException(e, sys)
            
    def update_combined_course(self, request):
        try:
            # Extract the combined course ID and other fields to update
            combined_course_id = request.combined_course_id
            
            # Check if the combined course exists
            existing_course = self.combined_courses_collection.find_one({"combined_course_id": combined_course_id})
            if not existing_course:
                raise Exception(f"Combined course with ID {combined_course_id} not found.")
            
            # Prepare the update data
            update_data = {}
            if hasattr(request, 'title') and request.title is not None:
                update_data["title"] = request.title
            if hasattr(request, 'description') and request.description is not None:
                update_data["description"] = request.description
            if hasattr(request, 'image_uri') and request.image_uri is not None:
                update_data["image_uri"] = request.image_uri
            if hasattr(request, 'level') and request.level is not None:
                update_data["level"] = request.level
            if hasattr(request, 'topics') and request.topics is not None:
                update_data["topics"] = request.topics
            
            # Always update the updated_at timestamp
            update_data["updated_at"] = datetime.now()
            
            # Update the combined course in the database
            result = self.combined_courses_collection.update_one(
                {"combined_course_id": combined_course_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                logging.warning(f"No changes made to combined course {combined_course_id}")
            
            # Return the updated combined course
            return self.get_combined_course_by_id(combined_course_id)
            
        except Exception as e:
            logging.error(f"Error updating combined course: {str(e)}")
            raise CustomException(e, sys)
    
    def update_trending_popular(self, request):
        try:
            # Extract the combined course ID and trending/popular flags
            combined_course_id = request.combined_course_id
            is_trending = request.is_trending
            is_popular = request.is_popular
            
            # Check if the combined course exists
            existing_course = self.combined_courses_collection.find_one({"combined_course_id": combined_course_id})
            if not existing_course:
                raise Exception(f"Combined course with ID {combined_course_id} not found.")
            
            # Update the trending and popular flags
            update_data = {
                "is_trending": is_trending,
                "is_popular": is_popular,
                "updated_at": datetime.now()
            }
            
            # Update the combined course in the database
            result = self.combined_courses_collection.update_one(
                {"combined_course_id": combined_course_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                logging.warning(f"No changes made to combined course {combined_course_id}")
            
            # Return the updated combined course
            return self.get_combined_course_by_id(combined_course_id)
            
        except Exception as e:
            logging.error(f"Error updating trending/popular status: {str(e)}")
            raise CustomException(e, sys)
    
    def delete_combined_course(self, combined_course_id):
        try:
            # Check if the combined course exists
            existing_course = self.combined_courses_collection.find_one({"combined_course_id": combined_course_id})
            if not existing_course:
                raise Exception(f"Combined course with ID {combined_course_id} not found.")
            
            # Delete the combined course from the database
            result = self.combined_courses_collection.delete_one({"combined_course_id": combined_course_id})
            
            if result.deleted_count == 0:
                raise Exception(f"Failed to delete combined course with ID {combined_course_id}.")
            
            return {"message": f"Combined course with ID {combined_course_id} successfully deleted."}
            
        except Exception as e:
            logging.error(f"Error deleting combined course: {str(e)}")
            raise CustomException(e, sys)
