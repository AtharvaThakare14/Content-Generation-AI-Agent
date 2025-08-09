import sys
from langgraph.graph import StateGraph, START, END

from src.exception import CustomException

from src.ai.course_generation.agent_states.states import *
from src.ai.course_generation.agents.course_module_generator import CourseModuleGenerator
from src.ai.course_generation.agents.lesson_content_generator import LessonContentGenerator

class CourseModuleGraphBuilder:
    def generate_graph(self):
        try:

            course_module_generator = CourseModuleGenerator().course_module_generator
            lesson_content_generator = LessonContentGenerator().lesson_content_generator

            graph_builder = StateGraph(
                input=Course, state_schema=CourseModules)

            graph_builder.add_node(
                "course_module_generator_node", course_module_generator)
            graph_builder.add_node(
                "lesson_content_generator_node", lesson_content_generator)

            graph_builder.add_edge(START, "course_module_generator_node")
            graph_builder.add_edge(
                "course_module_generator_node", "lesson_content_generator_node")
            graph_builder.add_edge("lesson_content_generator_node", END)

            graph = graph_builder.compile()
            return graph
        except Exception as e:
            return CustomException(e, sys)
