from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class GetCourseDetails(BaseModel):
    course_id: str


class AddNewCourse(BaseModel):
    course_name: str
    level: str
    image_uri: str
    description: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.now)

    @classmethod
    def __get_validators__(cls):
        yield from super().__get_validators__()
        yield cls.clean_description

    @staticmethod
    def clean_description(values):
        import re
        if 'description' in values and isinstance(values['description'], str):
            v = values['description']
            v = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', v)
            v = re.sub(r'\n+', '\n', v).strip()
            values['description'] = v
        return values

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EditTrendingPopularCourse(BaseModel):
    course_id: str
    is_trending: bool
    is_popular: bool


class EditCourse(BaseModel):
    course_id: str
    course_name: str
    level: str
    image_uri: str
    description: str
    
    class Config:
        # Allow arbitrary types for handling multi-line strings and other complex data
        arbitrary_types_allowed = True


class DeleteCourse(BaseModel):
    course_id: str


class AddSegmentsToCourse(BaseModel):
    course_id: str
    segment_ids: List[str]


class RemoveSegmentsFromCourse(BaseModel):
    course_id: str
    segment_ids: List[str]
