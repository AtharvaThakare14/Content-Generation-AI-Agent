from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UpdateModules(BaseModel):
    course_id: str
    course_name: str
    level: str
    duration: str
    tools: List[str]


class UpdateModulesContent(BaseModel):
    module_id: str
    module_title: str
    description: str
    estimated_completion_time: str
    prerequisites_knowledge: str
    prerequisites_technical: str
    learning_objectives: List[str]
    key_topics: List[str]
    practical_applications: List[str]