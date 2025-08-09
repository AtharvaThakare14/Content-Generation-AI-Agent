import sys
from langgraph.graph import StateGraph, MessagesState, START, END

from src.exception import CustomException
from src.utils.add_new_field_dict import add_fields_to_dict
from src.utils.unique_id_generator import unique_id_generator


from src.ai.module_generator.states.states import *
from src.ai.module_generator.agents.module_generator import ModuleGenerator


class ModuleGraphgenerator:
    def __init__(self):
        try:
            self.course_generater = ModuleGenerator().module_generater
        except Exception as e:
            return CustomException(e, sys)

    def generate_graph(self):
        try:
            builder = StateGraph(state_schema=Module, output=ModuleOutput)
            builder.add_node("course_generater", self.course_generater)
            builder.set_entry_point("course_generater")
            builder.add_edge("course_generater", END)
            graph = builder.compile()
            return graph
        except Exception as e:
            return CustomException(e, sys)

    def generate_module(self, data):
        try:
            graph = self.generate_graph()
            response = graph.invoke(data)

            # Add course-level fields
            new_fields = {
                'course_id': data['course_id'],
                'level': data['level'],
            }
            updated_dict = add_fields_to_dict(
                response, new_fields, insert_at_top=True)

            # Add module_id to each module
            for module in updated_dict.get('modules', []):
                module['module_id'] = unique_id_generator(prefix="MODULE")

            return dict(updated_dict)

        except Exception as e:
            return CustomException(e, sys)