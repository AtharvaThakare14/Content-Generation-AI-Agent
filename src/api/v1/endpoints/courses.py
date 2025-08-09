import sys
# from collections import OrderedDict
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from bson import ObjectId
import json

from src.logging import logging
from src.schemas.courses import *
from src.schemas.combined_courses import (
    CombineCoursesRequest, 
    EditCombinedCourse, 
    EditTrendingPopularCombinedCourse,
    DeleteCombinedCourse,
    GetCombinedCourseDetails
)
from src.exception import CustomException
from src.components.courses import Courses
from src.components.combined_courses import CombinedCourses, convert_objectid_to_str


# Ai Modules
# import src.ai.mcq_generator.global_vars as gv
from src.ai.course_generation.agent_states.states import *
# from src.utils.unique_id_generator import unique_id_generator
from src.ai.course_generation.schema.course_generation import *
# from src.ai.mcq_generator.graph import McqGeneratorGraphBuilder
# from src.ai.course_generation.graph import CourseModuleGraphBuilder
from src.ai.course_generation.insertion.mongodb_insertion import InsertData
# from src.ai.course_description_generator.course_description import CourseDescriptionGenerator


courses = Courses()
combined_courses = CombinedCourses()
router = APIRouter()
insert = InsertData()


@router.post("/ai/add-course")
def add_new_course_using_ai(data: AddNewCourse):
    try:
        results = courses.generate_course(data)
        return results
    except Exception as e:
        return CustomException(e, sys)


@router.post("/combine-courses")
def combine_courses_endpoint(data: CombineCoursesRequest):
    try:
        logging.info(f"Combining courses: {data.course_ids} into new course: {data.course_name}")
        # Use the new create_combined_course method to save to the combined_courses collection
        result = combined_courses.create_combined_course(data)
        # Convert any ObjectId objects to strings for JSON serialization
        result = convert_objectid_to_str(result)
        return {"message": "Courses combined successfully", "combined_course": result}
    except Exception as e:
        return CustomException(e, sys)


@router.get("/get-courses")
def get_all_courses():
    try:
        logging.info("Getting courses")
        results = courses.get_courses_with_course_count()
        return results
    except Exception as e:
        return CustomException(e, sys)
        
        
# Combined Courses Endpoints
@router.get("/combined-courses")
def get_all_combined_courses():
    try:
        logging.info("Getting all combined courses")
        results = combined_courses.get_all_combined_courses()
        return {"combined_courses": results}
    except Exception as e:
        return CustomException(e, sys)


@router.get("/combined-courses/{combined_course_id}")
def get_combined_course(combined_course_id: str):
    try:
        logging.info(f"Getting combined course with ID: {combined_course_id}")
        result = combined_courses.get_combined_course_by_id(combined_course_id)
        return result
    except Exception as e:
        return CustomException(e, sys)


@router.put("/combined-courses")
def update_combined_course(data: EditCombinedCourse):
    try:
        logging.info(f"Updating combined course with ID: {data.combined_course_id}")
        result = combined_courses.update_combined_course(data)
        return {"message": "Combined course updated successfully", "combined_course": result}
    except Exception as e:
        return CustomException(e, sys)


@router.put("/combined-courses/trending-popular")
def update_trending_popular(data: EditTrendingPopularCombinedCourse):
    try:
        logging.info(f"Updating trending/popular status for combined course: {data.combined_course_id}")
        result = combined_courses.update_trending_popular(data)
        return {"message": "Trending/popular status updated successfully", "combined_course": result}
    except Exception as e:
        return CustomException(e, sys)


@router.delete("/combined-courses/{combined_course_id}")
def delete_combined_course(combined_course_id: str):
    try:
        logging.info(f"Deleting combined course with ID: {combined_course_id}")
        result = combined_courses.delete_combined_course(combined_course_id)
        return result
    except Exception as e:
        return CustomException(e, sys)


@router.get("/get-courses-by-segments")
def get_courses_by_segment_id(segment_id: str = Query(None)):
    try:
        logging.info("Getting courses")
        results = courses.get_courses_by_segment_id(segment_id)
        return results
    except Exception as e:
        return CustomException(e, sys)


@router.put("/edit-trending")
def edit_trending_popular_course(data: EditTrendingPopularCourse):
    try:
        logging.info("Editing trending and popular course")
        results = courses.edit_trending_popular_course(data)
        return results
    except Exception as e:
        return CustomException(e, sys)


@router.put("/update-courses")
def update_course(data: EditCourse):
    try:
        logging.info("Editing  course")
        results = courses.edit_course(data)
        return results
    except Exception as e:
        return CustomException(e, sys)


@router.delete("/delete-courses")
def delete_course(data: DeleteCourse):
    try:
        logging.info("deleting  course")
        results = courses.delete_course(data)
        return results
    except Exception as e:
        return CustomException(e, sys)


@router.post("/add-segment-to-course")
def add_segment_to_course(data: AddSegmentsToCourse):
    try:
        return courses.add_segment_to_course(data)
    except Exception as e:
        return CustomException(e, sys)


@router.post("/remove-segment-from-course")
def remove_segment_from_course(data: RemoveSegmentsFromCourse):
    try:
        return courses.remove_segments_from_course(data)
    except Exception as e:
        return CustomException(e, sys)


# @router.get("/details")
# def get_course_details(course_id: str = Query(None)):
#     try:
#         logging.info("Getting courses details")
#         results = courses.get_course_details(course_id)
#         return results
#     except Exception as e:
#         return CustomException(e, sys)


# @router.post("/generate")
# def generate_course(data: CourseGenerationInput):
#     try:
#         logging.info("Generating courses")
#         graph_builder = CourseModuleGraphBuilder()

#         graph = graph_builder.generate_graph()

#         course = Course(course_name=data.course_name)

#         course_data = graph.invoke(course)

#         output = CourseModules(**course_data)
#         dict_output = output.model_dump()

#         course_id = unique_id_generator()
#         num_modules = len(dict_output.get("modules", []))

#         ordered_output = OrderedDict([
#             ("domain_id", course_id),
#             ("difficulty_level", data.difficulty_level),
#             ("number_of_modules", num_modules),
#         ])
#         ordered_output.update(dict_output)

#         response = insert.insert_data(ordered_output)

#         return ordered_output
#     except Exception as e:
#         return CustomException(e, sys)


# def generate_mcqs(self,data):
#     try:
#         gv.set_primary_skills(data.primary_skills)
#         gv.set_difficulty_level(data.difficulty_level)
#         gv.set_primary_skill_id(data.primary_skills_id)


#         graph_builder = McqGeneratorGraphBuilder()

#         graph = graph_builder.generate_graph()


#         mcqs_data = graph.invoke({"primary_skills": data.primary_skills,
#                              "difficulty": data.difficulty_level})

#         # response = insert_mcqs.insert_data(mcqs_data)

#         return mcqs_data
#     except Exception as e:
#         return CustomException(e, sys)
