from pydantic import BaseModel, Field


class CourseModules(BaseModel):
    course_title: str
    description: str


class Course(BaseModel):
    course_name: str


class domain_description(BaseModel):
    description: str = Field(description="description of the domain")
