from pydantic import BaseModel
from typing import List, Literal
import json

# Define lesson structure
class LessonItem(BaseModel):
    lesson_id: str  # NEW FIELD
    title: str
    type: Literal["read", "read_and_execute"]
    content: str
    instruction: str | None = None
    expected_output: str | None = None
    answer: str | None = None
    outline: str | None = None  # Added outline field with proper Pydantic typing


class ModuleLessonContent(BaseModel):
    module_id: str
    lessons: List[LessonItem]

class ModulesLessonOutput(BaseModel):
    course_id: str
    modules: List[ModuleLessonContent]