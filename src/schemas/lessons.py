from pydantic import BaseModel



class LessonBot(BaseModel):
    question: str
    context: str

