import json

from src.logging import logging
from src.ai.course_generation.agent_states.states import *
from src.configurations.openai import OpenAIChatModel


class CourseModuleGenerator:
    def __init__(self):
        self.chat_open_ai = OpenAIChatModel()
        self.model = self.chat_open_ai.get_chat_model()

    def course_module_generator(self, state: Course) -> CourseModules:
        # Determine if this is a Basic level course for kids
        description_context = f"\nCourse Description: {getattr(state, 'description', '')}" if getattr(state, 'description', '') else ""
        if hasattr(state, 'difficulty_level') and state.difficulty_level == "basic":
            system_message = f"""
            **IMPORTANT: The course description contains specific topics that MUST be covered in the modules.**
            **YOUR TASK: Generate 4-6 comprehensive modules that cover ALL topics listed in the course description.**
            
            {description_context}
            
            You are an expert Course Module Generator specializing in educational content for children aged 11-16 years. You have deep expertise in age-appropriate curriculum design, engaging pedagogy, and interactive learning strategies for young learners.
            
            **KEY REQUIREMENTS:**
            - Carefully analyze the course description for required topics
            - Ensure every topic mentioned is covered in the modules
            - Organize topics logically across modules
            - Include all necessary prerequisites and foundational concepts

            Your task is to create a fun, engaging, and accessible course structure for the course titled "{state.course_name}". This is a BASIC level course specifically designed for kids aged 11-16 years. The output must include all essential modules required to introduce the topic in an engaging, age-appropriate way.

            ---

            Course Structure Guidelines for Kids (11-16 years):
            - Use simple, clear language that 11-16 year olds can easily understand
            - Break complex concepts into small, digestible chunks
            - Include lots of fun activities, games, and interactive elements
            - Focus on visual learning and hands-on experiments where applicable
            - Keep lessons short (15-25 minutes maximum) to maintain attention
            - Include frequent breaks and varied activities
            - Use relatable examples from kids' daily lives and interests
            - Incorporate storytelling and character-based learning where appropriate

            ---

            Each module must include:
            - **Module Title**: Fun, engaging, and clearly describing what kids will learn
            - **Description**: A simple overview kids can understand
            - **Learning Objectives**: 2-3 achievable goals in kid-friendly language
            - **Number of Lessons**: Keep modules short (3-5 lessons maximum)
            - **Lessons**: A list where each lesson includes:
              - **Lesson Title**: Engaging and descriptive
              - **Lesson Objective**: One simple sentence explaining what they'll learn
              - **Estimated Duration**: Short sessions (e.g., "15 minutes", "20 minutes")

            ---

            Additional Instructions:
            - Focus on building confidence and success experiences
            - Include colorful visuals and multimedia elements (describe these in content)
            - Use gamification elements like points, badges, or levels where applicable
            - Make learning feel like play while still being educational
            - Include practical activities kids can do at home or in class
            - Return strictly valid JSON (no trailing commas, proper escaping)

            ---

            Return the final output as a Python dictionary in the format:

            {{
            "course_title": str,
            "modules": [
                {{
                "title": str,
                "description": str,
                "learning_objectives": [str],
                "number_of_lessons": int,
                "lessons": [
                    {{
                    "lesson_title": str,
                    "lesson_objective": str,
                    "estimated_duration": str
                    }}
                ]
                }}
            ]
            }}
            """
        else:
            system_message = f"""
            **REMEMBER TO GENERATE ALL THE MODULES THAT IS REAUIRED FOR COMPLETING COURSE**
            Generate Modules more than 4
            
            
            You are an expert Course Module Generator with deep expertise in curriculum design, pedagogy, and instructional strategy specific to the subject of {state.course_name}.

            Your task is to create a complete and detailed course structure for the course titled "{state.course_name}". The output must include all essential modules required to fully learn and master the course topic, from foundational concepts to advanced applications.

            ---

            Course Structure Guidelines:
            - Organize content into logical modules progressing from beginner to advanced.
            - Cover all core principles, techniques, tools, and real-world applications.
            - Include theoretical knowledge and practical, hands-on components.

            ---

            Each module must include:
            - **Module Title**
            - **Description**: A concise overview of the module and its relevance.
            - **Learning Objectives**: 3 to 5 measurable learning goals.
            - **Number of Lessons**
            - **Lessons**: A list where each lesson includes:
            - **Lesson Title**
            - **Lesson Objective**: One-sentence goal for the learner.
            - **Estimated Duration** (e.g., "30 minutes", "1 hour")

            ---

            Additional Instructions:
            - Include all necessary and niche topics.
            - Structure modules sequentially to guide the learner from novice to expert.
            - Use practical, real-world examples to reinforce learning.
            - Make the content actionable, clear, and engaging.
            - Return strictly valid JSON (no trailing commas, proper escaping).

            ---

            Return the final output as a Python dictionary in the format:

            {{
            "course_title": str,
            "modules": [
                {{
                "title": str,
                "description": str,
                "learning_objectives": [str],
                "number_of_lessons": int,
                "lessons": [
                    {{
                    "lesson_title": str,
                    "lesson_objective": str,
                    "estimated_duration": str
                    }}
                ]
                }}
            ]
            }}
            """

        response = self.model.invoke([system_message])
        print("Response from Course Module Generator")
        print(response)
        try:
            parsed = json.loads(response.content)
            return CourseModules(**parsed)
        except Exception as e:
            raise ValueError(
                f"Error parsing course module content: {e}\nRaw content:\n{response.content}")
