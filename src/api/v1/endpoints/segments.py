import sys
from fastapi import APIRouter, Query


from src.logging import logging
from src.schemas.segments import *
from src.exception import CustomException
from src.components.segments import Segments


from src.ai.course_generation.schema.course_generation import *


router = APIRouter()
segments = Segments()


@router.post("/add-segments")
def get_all_lessons(data: AddSegments):
    try:
        results = segments.add_segments(data)
        return results
    except Exception as e:
        return CustomException(e, sys)


@router.put("/update-segment")
def update_segment(data: UpdateSegments):
    try:
        return segments.update_segment(data)
    except Exception as e:
        return CustomException(e, sys)


@router.delete("/delete-segment")
def delete_segment(data: DeleteSegment):
    try:
        return segments.delete_segment(data)
    except Exception as e:
        return CustomException(e, sys)


@router.get("/get-segment")
def get_segment(segment_id: str = Query(None)):
    try:
        return segments.get_segment(segment_id)
    except Exception as e:
        return CustomException(e, sys)


@router.get("/get-all-segments")
def get_all_segments():
    try:
        return segments.get_all_segments()
    except Exception as e:
        return CustomException(e, sys)
