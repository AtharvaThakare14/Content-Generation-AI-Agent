from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ModuleReference(BaseModel):
    module_id: str
    module_name: str


class CourseReference(BaseModel):
    course_id: str
    course_name: str
    order: int
    modules: List[ModuleReference]


class CombinedCourseSchema(BaseModel):
    combined_course_id: str
    title: str
    description: str
    image_uri: str
    level: str
    topics: List[str]
    is_trending: bool = False
    is_popular: bool = False
    courses: List[CourseReference]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GetCombinedCourseDetails(BaseModel):
    combined_course_id: str


class CombineCoursesRequest(BaseModel):
    course_ids: List[str] = Field(..., min_items=2, description="A list of course IDs to combine.")
    course_name: str = Field(..., description="The name for the new combined course.")
    level: str = Field(..., description="The difficulty level of the course")
    image_url: str = Field(..., description="URL for the course image")
    topics: List[str] = Field(default=[], description="List of topics covered in the combined course")
    created_at: datetime = Field(default_factory=datetime.now, description="Course creation timestamp")
    description: str = Field(default="This is a combined course.", description="Course description")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EditCombinedCourse(BaseModel):
    combined_course_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    image_uri: Optional[str] = None
    level: Optional[str] = None
    topics: Optional[List[str]] = None
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EditTrendingPopularCombinedCourse(BaseModel):
    combined_course_id: str
    is_trending: bool
    is_popular: bool


class DeleteCombinedCourse(BaseModel):
    combined_course_id: str
