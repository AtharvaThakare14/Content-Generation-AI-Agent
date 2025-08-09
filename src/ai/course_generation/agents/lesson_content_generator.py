from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


from src.logging import logging
from src.configurations.openai import OpenAIChatModel
from src.ai.course_generation.agent_states.states import *


class LessonContentGenerator:
    def __init__(self):
        self.chat_open_ai = OpenAIChatModel()
        self.model = self.chat_open_ai.get_chat_model()

    def lesson_content_generator(self, state: CourseModules) -> dict:
        description_context = f"\nCourse Description: {getattr(state, 'description', '')}" if getattr(state, 'description', '') else ""
        system_prompt = f"""
        You are a highly knowledgeable Course Lesson Generator with expertise in instructional design and programming education.
        {description_context}
        For each lesson, generate:
        1. Clear and detailed instructional content.
        2. A relevant coding question (if applicable) to reinforce the concept.
        3. A complete and correct Python solution for that question.
        4. The expected output of that solution.

        Make use of tool to get the knowledge to generate content

        Return your output in **JSON format** as:
        {{
            "lesson_title": str,
            "lesson_objective": str,
            "estimated_duration": str,
            "lesson_content": str,
            "coding_question": str (optional),
            "coding_solution": str (optional),
            "coding_output": str (optional)
        }}

        Important:
        - Use double quotes for all keys and string values.
        - Do not include trailing commas.
        - Escape all special characters (like newlines and quotes).
        - Do not return markdown or code blocks.
        """

        for module in state.modules:
            for lesson in module.lessons:
                message = HumanMessage(
                    content=f"""
                            LESSON CONTENT SHOULD BE IN DETAIL EXPLANATION
                            
                            Lesson Title: {lesson.lesson_title}
                            Objective: {lesson.lesson_objective}
                            Estimated Duration: {lesson.estimated_duration}

                            Generate the full instructional lesson with optional coding exercise as JSON.
                            Return a strict JSON object as described earlier.
                            """
                )
                response = self.model.invoke(
                    [SystemMessage(content=system_prompt), message])
    #             print(response)
                import re

                def extract_field(field_name: str, content: str) -> str:
                    pattern = fr'"{field_name}"\s*:\s*(".*?"|null)'
                    match = re.search(pattern, content, re.DOTALL)
                    if not match:
                        return ""
                    value = match.group(1)
                    if value == "null":
                        return ""
                    return value.strip('"').replace('\\"', '"').replace('\\n', '\n')

                try:
                    content_str = response.content
                    lesson.lesson_content = extract_field(
                        "lesson_content", content_str)
                    lesson.coding_question = extract_field(
                        "coding_question", content_str)
                    lesson.coding_solution = extract_field(
                        "coding_solution", content_str)
                    lesson.coding_output = extract_field(
                        "coding_output", content_str)
                except Exception as e:
                    raise ValueError(
                        f"Error extracting lesson content: {e}\nRaw:\n{response.content}")
        print("Response from Course Lesson Generator")
        print( state.model_dump())
        return state.model_dump()  