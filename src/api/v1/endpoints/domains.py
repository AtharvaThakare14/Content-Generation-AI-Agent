import sys
from fastapi import APIRouter, Query


from src.logging import logging
from src.schemas.domains import *
from src.exception import CustomException
from src.components.domains import Domains


router = APIRouter()
domains = Domains()


@router.post("/add-domain")
def add_new_domain(data: AddNewDomain):
    try:
        results = domains.add_new_domain(data)
        return results
    except Exception as e:
        return CustomException(e, sys)


@router.get("/get-domains")
def get_all_domains():
    try:
        response = domains.get_domains()
        return response
    except Exception as e:
        return CustomException(e, sys)


@router.put("/update-demand")
def update_on_demaind_domain(data: UpdateOnDemandDomain):
    try:
        response = domains.update_on_demand_domain(data)
        return response
    except Exception as e:
        return CustomException(e, sys)


@router.get("/demand/get-domains")
def get_on_demand_all_domains():
    try:
        response = domains.get_on_demand_domain()
        return response
    except Exception as e:
        return CustomException(e, sys)


@router.post("/add-courses")
def add_courses_to_domain(data: AddCoursesDomain):
    try:
        results = domains.add_courses_to_domain(data)
        return results
    except Exception as e:
        return CustomException(e, sys)


@router.get("/get-courses")
def get_all_domain_course_details(course_id: List[str] = Query(None)):
    try:
        logging.info("Getting courses details")
        results = domains.get_domain_courses(course_id)
        return results
    except Exception as e:
        return CustomException(e, sys)


@router.delete("/delete-domain")
def delete_domain(domain_id: str = Query(None)):
    try:
        results = domains.delete_domain(domain_id)
        return results
    except Exception as e:
        return CustomException(e, sys)


@router.put("/update-domain")
def update_domain(data: UpdateDomain):
    try:
        results = domains.update_domain(data)
        return results
    except Exception as e:
        return CustomException(e, sys)


@router.delete("/delete-course")
def delete_domain_course(domain_id: str = Query(None), course_id: str = Query(None)):
    try:
        results = domains.delete_course(domain_id, course_id)
        return results
    except Exception as e:
        return CustomException(e, sys)


@router.post("/add-segments-to-domain")
def add_segments_to_domain(data: AddSegmentsToDomain):
    try:
        return domains.add_segments_to_domain(data)
    except Exception as e:
        return CustomException(e, sys)


@router.post("/remove-segments-from-domain")
def remove_segments_from_domain(data: RemoveSegmentFromDomain):
    try:
        return domains.remove_segments_from_domain(data)
    except Exception as e:
        return CustomException(e, sys)
