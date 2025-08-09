from pydantic import Field,BaseModel
from typing import Optional,Literal

class CourseGenerationInput(BaseModel):
    """Input schema."""
    # user_id : Optional[str]
    course_name : str
    difficulty_level : Literal["basic", "beginner","intermediate","advance"]
