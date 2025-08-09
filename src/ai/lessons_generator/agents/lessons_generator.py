import sys
from typing import List, Dict, Any
import json
import re

from src.logging import logging
from src.constants.mongodb import *
from src.exception import CustomException
from src.configurations.openai import OpenAIChatModel
from src.configurations.mongodb import MongoDBConnection
from src.utils.unique_id_generator import unique_id_generator
from src.ai.lessons_generator.states.states import *
from src.ai.lessons_generator.agents.lesson_quality_checker import LessonQualityChecker


class ContentOutlineGenerator:
    """Agent responsible for generating detailed lesson outlines."""
    
    def __init__(self):
        try:
            self.chat_open_ai = OpenAIChatModel()
            self.model = self.chat_open_ai.get_chat_model()
            self.structured_llm = self.model.with_structured_output(ModuleLessonContent)
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            self.logger.error(f"Failed to initialize ContentOutlineGenerator: {str(e)}")
            raise CustomException(e, sys)
    
    def generate_lesson_outlines(self, module: dict) -> ModuleLessonContent:
        """Generate detailed outlines for each lesson in a module."""
        # Check if this is a basic level course for kids (11-16 years)
        level = module.get('level', '').lower()
        
        if level == 'basic':
            system_prompt = f"""
            You are an expert curriculum architect specializing in creating educational content for children aged 11-16 years.
            
            Your task is to create a fun, engaging, and age-appropriate outline for 3-5 lessons covering the following module:
            - Title: {module['title']}
            - Description: {module['description']}
            - Module ID: {module['module_id']}
            
            This is a BASIC level course specifically designed for kids aged 11-16 years.
            
            For each lesson, provide:
            1. A fun, engaging title that will appeal to kids aged 11-16
            2. A type: either "read" (for theory) or "read_and_execute" (for hands-on practice)
            3. A detailed outline with age-appropriate content that's easy to understand
            
            For "read_and_execute" lessons, also outline:
            - instruction: Clear, simple steps that kids can follow
            - expected_output: What kids should achieve (make it fun and rewarding)
            - answer: Key components of the solution (in very simple terms)
            
            Ensure your outline:
            - Uses simple language that 11-16 year olds can easily understand
            - Breaks complex concepts into small, digestible chunks
            - Includes fun activities, games, and interactive elements
            - Focuses on visual learning and hands-on experiments where applicable
            - Keeps content short to maintain attention (15-25 minutes per lesson maximum)
            - Uses relatable examples from kids' daily lives and interests
            - Incorporates storytelling and character-based learning where appropriate
            
            Format your response as a structured ModuleLessonContent object with module_id and a list of lesson outlines.
            """
        else:
            system_prompt = f"""
            You are an expert curriculum architect with 10+ years of experience in creating high-quality educational content.
            
            Your task is to create a comprehensive outline for 4-6 lessons covering the following module:
            - Title: {module['title']}
            - Description: {module['description']}
            - Module ID: {module['module_id']}
            
            For each lesson, provide:
            1. A clear, action-oriented title that speaks directly to the learner
            2. A type: either "read" (for theory) or "read_and_execute" (for hands-on practice)
            3. A detailed outline with relevant content for the module topic
            
            For "read_and_execute" lessons, also outline:
            - instruction: The main task and objectives
            - expected_output: What students should achieve
            - answer: Key components of the solution
            
            Ensure your outline:
            - Progresses logically from fundamentals to advanced concepts
            - Includes at least two practical exercises with increasing complexity
            - Covers every important sub-topic implied by the module title
            - Addresses different learning styles
            
            Format your response as a structured ModuleLessonContent object with module_id and a list of lesson outlines.
            """
        
        self.logger.info(f"Generating lesson outlines for module: {module['title']}")
        result = self.structured_llm.invoke(system_prompt)
        
        # Add lesson IDs
        for lesson in result.lessons:
            lesson.lesson_id = unique_id_generator("LESSON")

        return result


class DetailedContentGenerator:
    """Agent responsible for expanding lesson outlines into comprehensive content."""
    
    def __init__(self):
        try:
            self.chat_open_ai = OpenAIChatModel()
            self.model = self.chat_open_ai.get_chat_model()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            self.logger.error(f"Failed to initialize DetailedContentGenerator: {str(e)}")
            raise CustomException(e, sys)
    
    def _ensure_markdown_consistency(self, content: str) -> str:
        """Ensures markdown formatting is consistent throughout the content."""
        if not content:
            return content
            
        # Fix inconsistent headers (ensure space after ##)
        content = re.sub(r'##(?=[^\s#])', '## ', content)
        content = re.sub(r'###(?=[^\s#])', '### ', content)
        
        # Ensure code blocks have language specification
        content = re.sub(r'```\s*\n', '```text\n', content)
        
        # Ensure blank lines between sections
        content = re.sub(r'(\n##[^\n]+)\n(?=[^\n])', r'\1\n\n', content)
        
        # Ensure blank lines after code blocks
        content = re.sub(r'```\s*\n(?=[^\n])', '```\n\n', content)
        
        # Standardize bullet points
        content = re.sub(r'^\s*-\s', '* ', content, flags=re.MULTILINE)
        
        return content
    
    def expand_lesson_content(self, lesson: LessonItem, module_context: dict) -> LessonItem:
        """Expand a lesson outline into comprehensive, frontend-friendly content."""
        # Initialize lesson with a copy of the original to preserve ID
        expanded_lesson = LessonItem(
            lesson_id=lesson.lesson_id,
            title=lesson.title,
            type=lesson.type,
            content="",
            instruction=lesson.instruction,
            expected_output=lesson.expected_output,
            answer=lesson.answer
        )
        
        # Check if this is a basic level course for kids (11-16 years)
        level = module_context.get('level', '').lower()
        
        # Construct system message based on lesson type and level
        if level == 'basic':
            base_message = f"""
            You are an expert educational content creator specializing in creating engaging, fun content for children aged 11-16 years.
            
            Your task is to expand the following lesson outline into age-appropriate, engaging content for kids:
            
            LESSON TITLE: {lesson.title}
            LESSON TYPE: {lesson.type}
            
            MODULE CONTEXT:
            - Title: {module_context['title']}
            - Description: {module_context['description']}
            
            Create content that is:
            - Written in simple, clear language that 11-16 year olds can easily understand
            - Fun, engaging, and visually stimulating (describe visuals where appropriate)
            - Broken down into small, digestible chunks
            - Full of relatable examples from kids' daily lives
            - Interactive with activities, games, and challenges
            - Incorporates storytelling elements and characters where appropriate
            - Keeps kids' attention with varied content types
            
            FORMAT REQUIREMENTS:
            - Use ## for main section headers (keep these fun and engaging)
            - Use ### for subsection headers
            - Use emojis where appropriate to add visual interest
            - Use simple bullet points for lists
            - Keep paragraphs very short (2-3 sentences maximum)
            - Include simple diagrams or illustrations (describe them in the content)
            - Use bold and colors for emphasis (describe where colors should be used)
            
            ADDITIONAL GUIDELINES:
            - Include 1-2 mini-activities or experiments that kids can do
            - Use metaphors and stories that relate to kids' experiences
            - Provide frequent encouragement and positive reinforcement
            - Keep technical terms to a minimum, and when used, explain them simply
            - Total reading time should be no more than 15-20 minutes
            
            Your content should be fun, educational, and keep kids engaged throughout the lesson.
            """
        else:
            base_message = f"""
            You are an expert educational content creator with a specialty in {module_context['title']}.
            
            Your task is to expand the following lesson outline into comprehensive, engaging content:
            
            LESSON TITLE: {lesson.title}
            LESSON TYPE: {lesson.type}
            
            MODULE CONTEXT:
            - Title: {module_context['title']}
            - Description: {module_context['description']}
            
            Create comprehensive content that is:
            - Well-structured with clear headings and subheadings
            - Engaging and conversational in tone
            - Rich with examples, analogies, and practical applications
            - Designed to accommodate multiple learning styles
            - Formatted in clean, consistent Markdown
            
            FORMAT REQUIREMENTS:
            - Use ## for main section headers
            - Use ### for subsection headers
            - Use appropriate formatting for code blocks, bullet points, etc.
            - Include 2-3 practical examples where appropriate
            - For code examples, include explanatory comments
            - Use bold and italic formatting to emphasize key points
            - Keep paragraphs short (3-5 sentences)
            
            Your content should flow naturally between topics and maintain a consistent narrative.
            """
        
        system_prompt = base_message + f"""
        
        LESSON OUTLINE:
        - Title: {lesson.title}
        - Type: {lesson.type}
        - Content Outline: {lesson.content}
        {f'- instruction Outline: {lesson.instruction}' if lesson.instruction else ''}
        {f'- expected_output Outline: {lesson.expected_output}' if lesson.expected_output else ''}
        {f'- answer Outline: {lesson.answer}' if lesson.answer else ''}
        
        Create extensive, comprehensive content with these requirements:
        
        1. FORMAT THE CONTENT IN CONSISTENT MARKDOWN for proper frontend rendering:
           - Section headers MUST use ## format (e.g., ## Introduction)
           - Subsection headers MUST use ### format (e.g., ### Key Principles)
           - Code blocks MUST use triple backticks with language specification (```python, ```javascript, etc.)
             ```python
             def example_function():
                 return "This is how code should be formatted"
             ```
           - Use **bold** for important terms and emphasis
           - Use *italic* for secondary emphasis
           - Use `inline code` for variable names, functions, and short code snippets
           - Lists MUST use proper Markdown formatting:
             * Unordered lists with asterisks (prefer this format)
             1. Ordered lists with numbers followed by periods
           - Tables MUST use proper Markdown table syntax:
             | Header 1 | Header 2 |
             |----------|----------|
             | Cell 1   | Cell 2   |
           - Include blank lines between paragraphs and sections
           - Use > for blockquotes to highlight important notes
           - Use --- for horizontal rules to separate major content areas
           - Links MUST use [text](URL) format
        
        2. For the CONTENT field, create SUBSTANTIAL (at least 2000-3000 words) content with:
           - Create YOUR OWN well-structured sections with clear headers (use ## for headers)
           - In-depth explanations with theoretical foundations and principles
           - Multiple comprehensive examples for each main concept
           - Detailed code samples where appropriate (with line-by-line explanations)
           - Practical applications with step-by-step walkthroughs
           - Historical context and evolution of key concepts
           - Visual descriptions (tables, diagrams described in text)
           - Common misconceptions and how to avoid them
           - Advanced tips and techniques for mastery
           - References to industry standards and best practices
        
        3. ORGANIZE THE CONTENT FREELY with your own creativity and expertise:
           - You are NOT limited to any specific sections or structure
           - Create any sections that best communicate the material
           - Organize the content in whatever way makes the most pedagogical sense
           - Feel free to create unique section titles that engage learners
           - Consider different learning styles and approaches
           - The goal is comprehensive, engaging, and thorough content
        
        4. If the type is "read_and_execute", also provide these comprehensive sections:
           - ## Instruction
             Extremely detailed step-by-step task with clear objectives
             Number each step (at least 10-15 steps) and provide context for why each step matters
             Include preparation steps, setup requirements, and validation checks
           
           - ## Expected Output
             Precise description of what the student should see/achieve
             Include detailed visual descriptions or representations of expected results
             Explain how to interpret the results and verify correctness
           
           - ## Answer
             A complete solution with thorough explanations
             Include explanations before and after any examples or code
             Provide alternative approaches and optimization suggestions
        
        Ensure your content is engaging, conversational, and academically rigorous. The content should be SUBSTANTIAL - imagine writing a detailed chapter in a textbook, not just a brief overview.
        """
        
        self.logger.info(f"Expanding content for lesson: {lesson.title}")
        
        try:
            response = self.model.invoke(system_prompt)
            expanded_content = response.content
            
            # Parse the expanded content
            content_sections = self._parse_markdown_sections(expanded_content)
            
            # Update the lesson with expanded content and ensure consistent markdown
            lesson.content = self._ensure_markdown_consistency(self._extract_main_content(content_sections))
            
            if lesson.type == "read_and_execute":
                lesson.instruction = self._ensure_markdown_consistency(content_sections.get("instruction", ""))
                lesson.expected_output = self._ensure_markdown_consistency(content_sections.get("expected_output", ""))
                lesson.answer = self._ensure_markdown_consistency(content_sections.get("answer", ""))
            
            return lesson
            
        except Exception as e:
            self.logger.error(f"Error expanding lesson content: {str(e)}")
            return lesson
    
    def _parse_markdown_sections(self, markdown_text: str) -> Dict[str, str]:
        """Parse markdown text into sections based on ## headers."""
        sections = {}
        current_section = None
        current_content = []
        
        for line in markdown_text.split('\n'):
            if line.startswith('## '):
                # Save previous section if it exists
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Save the last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _extract_main_content(self, sections: Dict[str, str]) -> str:
        """Combine all content sections into a single comprehensive markdown string.
        Preserves all generated content with no filtering."""
        # Skip instruction, expected_output, and answer as they're handled separately
        excluded_sections = ["instruction", "expected_output", "answer"]
        
        # Include ALL sections from the generated content, preserving the original order
        content_parts = []
        for section, content in sections.items():
            if section.lower() not in excluded_sections:
                content_parts.append(f"## {section}\n{content}")
        
        return '\n\n'.join(content_parts)


class LessonsGenerator:
    def __init__(self):
        try:
            self.chat_open_ai = OpenAIChatModel()
            self.model = self.chat_open_ai.get_chat_model()
            self.structured_llm = self.model.with_structured_output(ModuleLessonContent)
            self.mongodb_client = MongoDBConnection(database_name=AI_TUTOR_IQAN_DATABASE_NAME)
            self.collection = self.mongodb_client.db[COURSES_COLLECTION_NAME]
            self.quality_checker = LessonQualityChecker()
            self.outline_generator = ContentOutlineGenerator()
            self.content_generator = DetailedContentGenerator()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            self.logger.error(f"Failed to initialize LessonsGenerator: {str(e)}")
            raise CustomException(e, sys)

    def generate_lessons_for_each_module(self, modules: List[dict], course_id: str) -> ModulesLessonOutput:
        """Generate comprehensive lessons for each module using a two-phase approach."""
        final_results = []

        for module in modules:
            self.logger.info(f"Generating lessons for module: {module['title']}")
            
            # Phase 1: Generate lesson outlines using the ContentOutlineGenerator
            module_outline = self.outline_generator.generate_lesson_outlines(module)
            
            # Phase 2: Expand each lesson outline into detailed content
            expanded_lessons = []
            for lesson_outline in module_outline.lessons:
                # Create module context for the content generator
                module_context = {
                    'title': module['title'],
                    'description': module['description'],
                    'module_id': module['module_id']
                }
                
                # Expand the lesson outline into comprehensive content
                expanded_lesson = self.content_generator.expand_lesson_content(lesson_outline, module_context)
                expanded_lessons.append(expanded_lesson)
            
            # Update the module with expanded lessons
            module_outline.lessons = expanded_lessons
            
            # Check and improve lesson quality
            self._check_and_improve_module_quality(module_outline)
            
            final_results.append(module_outline)

        course_output = ModulesLessonOutput(course_id=course_id, modules=final_results)
        
        # Perform final course-level quality check
        quality_report = self.quality_checker.check_course_quality(course_output)
        self.logger.info(f"Course quality score: {quality_report['overall_quality_score']}/100")
        
        # Log a sample of the generated content for verification
        if final_results and final_results[0].lessons:
            sample_lesson = final_results[0].lessons[0]
            self.logger.info(f"Sample lesson title: {sample_lesson.title}")
            self.logger.info(f"Sample lesson content preview: {sample_lesson.content[:200]}...")
        
        return course_output
        
    def _check_and_improve_module_quality(self, module: ModuleLessonContent) -> None:
        """Check and improve the quality of lessons in a module."""
        try:
            # Evaluate module quality
            module_quality = self.quality_checker.check_module_quality(module)
            self.logger.info(f"Module {module.module_id} quality score: {module_quality['average_quality_score']}/100")
            
            # Improve low-quality lessons
            improved_lessons = []
            for lesson_eval in module_quality['lesson_evaluations']:
                lesson_id = lesson_eval['lesson_id']
                lesson = next((l for l in module.lessons if l.lesson_id == lesson_id), None)
                
                if lesson and not lesson_eval['evaluation']['passes_threshold']:
                    self.logger.info(f"Improving lesson: {lesson.title} (Score: {lesson_eval['evaluation']['quality_score']}/100)")
                    improved_lesson = self.quality_checker.improve_lesson(lesson, lesson_eval['evaluation'])
                    improved_lessons.append(improved_lesson)
                else:
                    improved_lessons.append(lesson)
            
            # Replace lessons with improved versions
            module.lessons = improved_lessons
            
        except Exception as e:
            self.logger.error(f"Error checking module quality: {str(e)}")
            # Continue with original lessons if quality check fails
