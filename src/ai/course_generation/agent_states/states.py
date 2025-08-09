from pydantic import BaseModel
from typing import List, Optional


class Lesson(BaseModel):
    lesson_title: str
    lesson_objective: str
    estimated_duration: str
    lesson_content: Optional[str] = None
    coding_question: Optional[str] = None
    coding_solution: Optional[str] = None
    coding_output: Optional[str] = None


class Module(BaseModel):
    title: str
    description: str
    learning_objectives: List[str]
    number_of_lessons: int
    lessons: List[Lesson]


class CourseModules(BaseModel):
    course_title: str
    modules: List[Module]


class Course(BaseModel):
    course_name: str
    difficulty_level: Optional[str] = None