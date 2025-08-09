
import sys
from collections import OrderedDict
from fastapi import APIRouter, Query


from src.logging import logging
from src.schemas.lessons import *
from src.exception import CustomException
from src.components.lessons import Lessons


# Ai Modules
# import src.ai.mcq_generator.global_vars as gv
from src.ai.course_generation.agent_states.states import *
from src.utils.unique_id_generator import unique_id_generator
from src.ai.course_generation.schema.course_generation import *
from src.ai.lesson_chatbot.lesson_chatbot import ContextBoundQABot


router = APIRouter()
lessons = Lessons()
context_bound_bot = ContextBoundQABot()

@router.get("/get-lessons")
def get_all_lessons(course_id: str = Query(None), module_id: str = Query(None)):
    try:
        logging.info("Getting courses details")
        results = lessons.get_lessons(course_id,module_id)
        return results
    except Exception as e:
        return CustomException(e, sys)
    


@router.post("/ai/bot")
def get_all_lessons(data: LessonBot):
    try:
        logging.info("Getting courses details")
        results = context_bound_bot.answer_question(data)
        return results
    except Exception as e:
        return CustomException(e, sys)
    
