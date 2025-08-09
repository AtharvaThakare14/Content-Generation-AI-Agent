import sys
from collections import OrderedDict
from fastapi import APIRouter, Query


from src.logging import logging
from src.schemas.modules import *
from src.exception import CustomException
from src.components.modules import Modules


# Ai Modules
# import src.ai.mcq_generator.global_vars as gv
from src.ai.course_generation.agent_states.states import *
from src.utils.unique_id_generator import unique_id_generator
from src.ai.course_generation.schema.course_generation import *


router = APIRouter()
modules = Modules()


# @router.post("/add-domain")
# def add_new_domain(data: AddNewDomain):
#     try:
#         results = domains.add_new_domain(data)
#         return results
#     except Exception as e:
#         return CustomException(e, sys)


# @router.post("/add-courses")
# def add_courses_to_domain(data: AddCoursesDomain):
#     try:
#         results = domains.add_courses_to_domain(data)
#         return results
#     except Exception as e:
#         return CustomException(e, sys)


@router.get("/get-modules")
def get_all_modules(course_id: str = Query(None)):
    try:
        response = modules.get_modules(course_id)
        return response
    except Exception as e:
        return CustomException(e, sys)
    
@router.put("/update/module")
def update_module(data: UpdateModules):
    try:
        response = modules.update_module(data)
        return response
    except Exception as e:
        return CustomException(e, sys)
    
@router.put("/update/module-content")
def update_module_content(data: UpdateModulesContent):
    try:
        response = modules.update_module_content(data)
        return response
    except Exception as e:
        return CustomException(e, sys)


# @router.get("/get-courses")
# def get_all_course_details(course_id: List[str] = Query(None)):
#     try:
#         logging.info("Getting courses details")
#         results = domains.get_domain_courses(course_id)
#         return results
#     except Exception as e:
#         return CustomException(e, sys)
