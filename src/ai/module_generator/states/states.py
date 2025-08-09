from typing import List
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState


class Module(MessagesState):
    course_name: str


class ModuleItem(BaseModel):
    title: str
    description: str


class ModuleOutput(BaseModel):
    course: str
    duration: str
    num_modules: int
    tools: List[str]
    modules: List[ModuleItem]
