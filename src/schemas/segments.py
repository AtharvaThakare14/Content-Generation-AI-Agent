from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UpdateSegments(BaseModel):
    course_id: str
    course_name: str
    level: str
    duration: str
    tools: List[str]


class AddSegments(BaseModel):
    segment_name: str
    description: str


class UpdateSegments(BaseModel):
    segment_id :  str
    segment_name: str
    description: str

class DeleteSegment(BaseModel):
    segment_id :  str