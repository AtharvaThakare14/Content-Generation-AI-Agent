import sys
from typing import List, Dict, Any
import re

from src.logging import logging
from src.exception import CustomException
from src.configurations.openai import OpenAIChatModel
from src.ai.lessons_generator.states.states import ModulesLessonOutput, ModuleLessonContent, LessonItem


class LessonQualityChecker:
    """
    Agent responsible for checking the quality of generated lessons.
    Ensures lessons meet educational standards and contain all required components.
    """
    
    def __init__(self):
        """Initialize the LessonQualityChecker with required configurations."""
        try:
            self.chat_open_ai = OpenAIChatModel()
            self.model = self.chat_open_ai.get_chat_model()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            self.logger.error(f"Failed to initialize LessonQualityChecker: {str(e)}")
            raise CustomException(e, sys)
    
    def check_content_structure(self, content: str) -> Dict[str, bool]:
        """
        Check the structure of lesson content without requiring specific sections.
        
        Args:
            content: The lesson content to check
            
        Returns:
            Dictionary with structure quality metrics
        """
        # Check for presence of any section headers
        has_sections = bool(re.findall(r'##\s+\w+', content))
        
        # Check for content length and paragraphs
        content_length = len(content)
        paragraphs = content.count('\n\n')
        
        # Check for formatting elements
        has_formatting = any(marker in content for marker in ['**', '*', '```', '- ', '1. '])
        
        return {
            "has_sections": has_sections,
            "content_length": content_length,
            "paragraph_count": paragraphs,
            "has_formatting": has_formatting,
            "structure_quality": "good" if has_sections and content_length > 500 and paragraphs >= 3 and has_formatting else "needs_improvement"
        }
    
    def check_code_quality(self, code: str, is_technical: bool = True) -> Dict[str, Any]:
        """
        Check the quality of code examples in the lesson.
        
        Args:
            code: The code to check
            is_technical: Whether this is a technical subject requiring code
            
        Returns:
            Dictionary with quality metrics
        """
        if not code or not is_technical:
            return {"has_code": False}
            
        # Check for comments (supporting multiple languages)
        has_comments = any(comment_marker in code for comment_marker in ['//', '/*', '#', '<!--', '"""', "'''"])
        
        # Check for proper indentation (generic approach)
        lines = code.split('\n')
        if len(lines) > 1:
            # Check if subsequent lines have consistent indentation
            indentation_levels = [len(line) - len(line.lstrip()) for line in lines[1:] if line.strip()]
            has_proper_indentation = len(set(indentation_levels)) <= 3  # Allow up to 3 different indentation levels
        else:
            has_proper_indentation = True
        
        # Check for error handling (supporting multiple languages)
        error_handling_patterns = [
            'try', 'catch', 'except', 'finally', 'rescue', 'raise', 'throw', 'error', 
            'handle', 'on error', 'if err', 'error handling'
        ]
        has_error_handling = any(pattern in code.lower() for pattern in error_handling_patterns)
        
        return {
            "has_code": True,
            "has_comments": has_comments,
            "has_proper_indentation": has_proper_indentation,
            "has_error_handling": has_error_handling
        }
    
    def check_exercise_quality(self, lesson: LessonItem) -> Dict[str, Any]:
        """
        Check the quality of exercises in read_and_execute lessons.
        
        Args:
            lesson: The lesson to check
            
        Returns:
            Dictionary with quality metrics
        """
        if lesson.type != "read_and_execute":
            return {"is_exercise": False}
            
        # Check instruction clarity
        has_clear_steps = bool(lesson.instruction and 
                              (re.search(r'\b\d+[\.\)]\s', lesson.instruction) or 
                               "Step" in lesson.instruction))
        
        # Check expected output clarity
        has_clear_output = bool(lesson.expected_output and len(lesson.expected_output) > 20)
        
        # Check solution quality
        code_quality = self.check_code_quality(lesson.answer or "")
        
        return {
            "is_exercise": True,
            "has_clear_steps": has_clear_steps,
            "has_clear_output": has_clear_output,
            "code_quality": code_quality
        }
    
    def evaluate_lesson(self, lesson: LessonItem, module_context: dict = None) -> Dict[str, Any]:
        """
        Evaluate the quality of a single lesson.
        
        Args:
            lesson: The lesson to evaluate
            module_context: Optional context about the module this lesson belongs to
            
        Returns:
            Dictionary with quality metrics and improvement suggestions
        """
        # Check content structure
        structure_check = self.check_content_structure(lesson.content)
        
        # Check code quality if code blocks are present
        code_blocks = re.findall(r'```([\s\S]*?)```', lesson.content)
        code_quality = self.check_code_quality('\n'.join(code_blocks)) if code_blocks else {"has_code": False}
        
        # Check exercise quality for practical lessons
        exercise_quality = self.check_exercise_quality(lesson) if lesson.type == "read_and_execute" else {"is_exercise": False}
        
        # Check module relevance if context is provided
        module_relevance = self._check_module_relevance(lesson, module_context) if module_context else {"is_relevant": True}
        
        # Calculate overall quality score
        quality_score = 100
        
        # Deduct points for structure issues
        if structure_check.get("structure_quality") == "needs_improvement":
            quality_score -= 20
        if structure_check.get("content_length", 0) < 300:
            quality_score -= 15
        if not structure_check.get("has_sections", False):
            quality_score -= 15
        if not structure_check.get("has_formatting", False):
            quality_score -= 10
        
        # Deduct points for code quality issues
        if code_quality.get("has_code", False):
            if not code_quality.get("has_comments", False):
                quality_score -= 10
            if not code_quality.get("has_proper_indentation", False):
                quality_score -= 10
            if not code_quality.get("has_error_handling", False):
                quality_score -= 5
        
        # Deduct points for exercise quality issues
        if exercise_quality.get("is_exercise", False):
            if not exercise_quality.get("has_clear_steps", False):
                quality_score -= 15
            if not exercise_quality.get("has_clear_output", False):
                quality_score -= 10
        
        # Deduct points for module relevance issues
        if not module_relevance.get("is_relevant", True):
            quality_score -= 25  # Major penalty for irrelevant content
        
        # Ensure score is within bounds
        quality_score = max(0, min(100, quality_score))
        
        # Generate improvement suggestions
        suggestions = []
        
        # Structure improvement suggestions
        if structure_check.get("structure_quality") == "needs_improvement":
            if not structure_check.get("has_sections", False):
                suggestions.append("Add section headers to organize content")
            if structure_check.get("content_length", 0) < 300:
                suggestions.append("Expand the content with more detailed explanations")
            if structure_check.get("paragraph_count", 0) < 3:
                suggestions.append("Break content into more paragraphs for readability")
            if not structure_check.get("has_formatting", False):
                suggestions.append("Add formatting elements like bold, italic, lists, or code blocks")
        
        if code_quality.get("has_code", False):
            if not code_quality.get("has_comments", False):
                suggestions.append("Add comments to code examples")
            if not code_quality.get("has_proper_indentation", False):
                suggestions.append("Fix code indentation")
            if not code_quality.get("has_error_handling", False):
                suggestions.append("Add error handling to code examples")
        
        if exercise_quality.get("is_exercise", False):
            if not exercise_quality.get("has_clear_steps", False):
                suggestions.append("Add numbered steps to exercise instructions")
            if not exercise_quality.get("has_clear_output", False):
                suggestions.append("Provide clearer description of expected output")
        
        # Add module relevance suggestions
        if not module_relevance.get("is_relevant", True):
            suggestions.append("Rewrite content to focus specifically on the module topic")
            if module_relevance.get("irrelevant_sections", []):
                sections = ', '.join(module_relevance.get("irrelevant_sections", []))
                suggestions.append(f"Revise these sections to be more module-specific: {sections}")
        
        return {
            "lesson_id": lesson.lesson_id,
            "quality_score": quality_score,
            "passes_threshold": quality_score >= 70,
            "structure_check": structure_check,
            "code_quality": code_quality,
            "exercise_quality": exercise_quality,
            "module_relevance": module_relevance,
            "improvement_suggestions": suggestions
        }
    
    def _check_module_relevance(self, lesson: LessonItem, module_context: dict) -> Dict[str, Any]:
        """
        Check if the lesson content is relevant to the module topic.
        
        Args:
            lesson: The lesson to check
            module_context: Context about the module this lesson belongs to
            
        Returns:
            Dictionary with relevance metrics
        """
        if not module_context:
            return {"is_relevant": True}
            
        try:
            # Extract key terms from module title and description
            module_title = module_context.get('title', '')
            module_description = module_context.get('description', '')
            
            # Simple keyword matching for quick relevance check
            title_keywords = self._extract_keywords(module_title)
            desc_keywords = self._extract_keywords(module_description)
            all_keywords = set(title_keywords + desc_keywords)
            
            # Check for keyword presence in lesson content
            content_text = lesson.title + ' ' + lesson.content
            keyword_matches = sum(1 for keyword in all_keywords if keyword.lower() in content_text.lower())
            keyword_relevance = keyword_matches / max(1, len(all_keywords))
            
            # Check for relevance in each section
            sections = self._parse_markdown_sections(lesson.content)
            irrelevant_sections = []
            
            for section_name, section_content in sections.items():
                section_relevance = sum(1 for keyword in all_keywords 
                                      if keyword.lower() in section_content.lower()) / max(1, len(all_keywords))
                if section_relevance < 0.2:  # Threshold for section relevance
                    irrelevant_sections.append(section_name)
            
            # Overall relevance assessment
            is_relevant = keyword_relevance >= 0.3 and len(irrelevant_sections) <= 1
            
            return {
                "is_relevant": is_relevant,
                "keyword_relevance": keyword_relevance,
                "irrelevant_sections": irrelevant_sections
            }
        except Exception as e:
            self.logger.error(f"Error checking module relevance: {str(e)}")
            return {"is_relevant": True}  # Default to relevant on error
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from text.
        
        Args:
            text: The text to extract keywords from
            
        Returns:
            List of keywords
        """
        # Remove common stop words and punctuation
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'when',
                      'at', 'from', 'by', 'for', 'with', 'about', 'against', 'between',
                      'into', 'through', 'during', 'before', 'after', 'above', 'below',
                      'to', 'of', 'in', 'on', 'is', 'are', 'was', 'were', 'be', 'been',
                      'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did',
                      'doing', 'this', 'that', 'these', 'those', 'will', 'would', 'shall',
                      'should', 'can', 'could', 'may', 'might'}
        
        # Clean text and extract words
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = [word for word in clean_text.split() if word not in stop_words and len(word) > 2]
        
        # Return unique words
        return list(set(words))
        
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
        
    def check_module_quality(self, module: ModuleLessonContent) -> Dict[str, Any]:
        """
        Check the quality of all lessons in a module.
        
        Args:
            module: The module to check
            
        Returns:
            Dictionary with quality metrics for the module
        """
        lesson_evaluations = []
        total_score = 0
        lessons_below_threshold = 0
        
        # Create module context for relevance checking
        module_context = {
            'module_id': module.module_id,
            'title': '',  # Will be filled from database if possible
            'description': ''  # Will be filled from database if possible
        }
        
        # Try to get module details from database
        try:
            module_data = self.mongodb_client.db[MODULES_COLLECTION_NAME].find_one(
                {"module_id": module.module_id}
            )
            if module_data:
                module_context['title'] = module_data.get('title', '')
                module_context['description'] = module_data.get('description', '')
        except Exception as e:
            self.logger.error(f"Error fetching module data: {str(e)}")
        
        # Check if module has a good mix of lesson types
        read_count = sum(1 for lesson in module.lessons if lesson.type == "read")
        practice_count = sum(1 for lesson in module.lessons if lesson.type == "read_and_execute")
        has_good_type_mix = read_count > 0 and practice_count > 0
        
        for lesson in module.lessons:
            # Evaluate lesson with module context for relevance checking
            evaluation = self.evaluate_lesson(lesson, module_context)
            lesson_evaluations.append({
                "lesson_id": lesson.lesson_id,
                "title": lesson.title,
                "evaluation": evaluation
            })
            
            total_score += evaluation["quality_score"]
            if not evaluation["passes_threshold"]:
                lessons_below_threshold += 1
        
        # Calculate average quality score
        avg_score = total_score / max(1, len(module.lessons))
        
        # Generate improvement suggestions
        suggestions = []
        
        if lessons_below_threshold > 0:
            suggestions.append(f"Improve {lessons_below_threshold} lessons below quality threshold")
            
        if not has_good_type_mix:
            if practice_count == 0:
                suggestions.append("Add practical exercises to the module")
            elif read_count == 0:
                suggestions.append("Add theoretical lessons to the module")
        
        return {
            "module_id": module.module_id,
            "average_quality_score": avg_score,
            "passes_threshold": avg_score >= 70,
            "lessons_below_threshold": lessons_below_threshold,
            "has_good_type_mix": has_good_type_mix,
            "improvement_suggestions": suggestions,
            "lesson_evaluations": lesson_evaluations
        }
    
    def check_course_quality(self, course: ModulesLessonOutput) -> Dict[str, Any]:
        """
        Check the quality of an entire course.
        
        Args:
            course: The course to check
            
        Returns:
            Dictionary with quality metrics and improvement suggestions for the course
        """
        module_evaluations = []
        overall_score = 0
        
        for module in course.modules:
            evaluation = self.check_module_quality(module)
            module_evaluations.append(evaluation)
            overall_score += evaluation["average_quality_score"]
        
        # Calculate average score
        avg_score = overall_score / len(course.modules) if course.modules else 0
        
        # Generate overall improvement suggestions
        suggestions = []
        if avg_score < 70:
            suggestions.append("The overall course quality needs improvement")
            
        low_quality_modules = [
            eval["module_id"] for eval in module_evaluations 
            if not eval["passes_threshold"]
        ]
        
        if low_quality_modules:
            suggestions.append(f"Modules that need improvement: {', '.join(low_quality_modules)}")
        
        modules_without_mix = [
            eval["module_id"] for eval in module_evaluations 
            if not eval["has_good_type_mix"]
        ]
        
        if modules_without_mix:
            suggestions.append(f"Add more practical exercises to modules: {', '.join(modules_without_mix)}")
        
        return {
            "course_id": course.course_id,
            "overall_quality_score": avg_score,
            "passes_threshold": avg_score >= 70,
            "improvement_suggestions": suggestions,
            "module_evaluations": module_evaluations
        }
    
    def improve_lesson(self, lesson: LessonItem, evaluation: Dict[str, Any], module_context: dict = None) -> LessonItem:
        """
        Improve a lesson based on quality evaluation.
        
        Args:
            lesson: The lesson to improve
            evaluation: Quality evaluation of the lesson
            module_context: Optional context about the module this lesson belongs to
            
        Returns:
            Improved lesson
        """
        if evaluation["passes_threshold"]:
            return lesson
            
        # Use the model to improve the lesson based on suggestions
        suggestions = evaluation.get("improvement_suggestions", [])
        if not suggestions:
            return lesson
        
        # Get module context if not provided
        if not module_context and "module_relevance" in evaluation:
            # Try to get module details from database
            try:
                module_data = self.mongodb_client.db[MODULES_COLLECTION_NAME].find_one(
                    {"module_id": lesson.module_id if hasattr(lesson, 'module_id') else ''}
                )
                if module_data:
                    module_context = {
                        'module_id': module_data.get('module_id', ''),
                        'title': module_data.get('title', ''),
                        'description': module_data.get('description', '')
                    }
            except Exception as e:
                self.logger.error(f"Error fetching module data: {str(e)}")
        
        # Add module context to the prompt
        module_context_str = ""
        if module_context:
            module_context_str = f"""
            MODULE CONTEXT (IMPORTANT - LESSON MUST BE RELEVANT TO THIS):
            Title: {module_context.get('title', '')}
            Description: {module_context.get('description', '')}
            """
            
        prompt = f"""
        You are an expert curriculum architect with 10+ years of experience in creating high-quality educational content. Improve the following lesson based on these suggestions:
        
        SUGGESTIONS:
        {chr(10).join(f"- {suggestion}" for suggestion in suggestions)}
        {module_context_str}
        ORIGINAL LESSON:
        Title: {lesson.title}
        Type: {lesson.type}
        Content: {lesson.content}
        
        {f"Instruction: {lesson.instruction}" if lesson.instruction else ""}
        {f"Expected Output: {lesson.expected_output}" if lesson.expected_output else ""}
        {f"Answer: {lesson.answer}" if lesson.answer else ""}
        
        IMPORTANT REQUIREMENTS:
        1. The lesson MUST be focused on the module topic and directly relevant to it
        2. All examples and explanations must relate to concepts from the module
        3. Make sure all sections (Why This Matters, Core Concepts, etc.) directly relate to the module
        4. Include appropriate examples that illustrate the concepts effectively
        
        Provide an improved version of this lesson addressing all the suggestions and requirements.
        Format your response with these exact headings:
        Title: (improved title)
        Content: (improved content with markdown formatting)
        
        For read_and_execute lessons, also include:
        Instruction: (improved instructions)
        Expected Output: (improved expected output)
        Answer: (improved answer/solution)
        """
        
        try:
            # Use a longer timeout for improvement as it's a complex task
            response = self.model.invoke(prompt, timeout=60)
            
            # Extract improved content from response
            improved_content = response.content
            
            # Update the lesson with improved content
            if "Title:" in improved_content:
                title_match = re.search(r"Title:\s*(.*?)(?:\n|$)", improved_content)
                if title_match:
                    lesson.title = title_match.group(1).strip()
            
            if "Content:" in improved_content:
                content_match = re.search(r"Content:\s*(.*?)(?:\n\n(?:Instruction:|Expected Output:|Answer:)|$)", improved_content, re.DOTALL)
                if content_match:
                    lesson.content = content_match.group(1).strip()
            
            if lesson.type == "read_and_execute":
                if "Instruction:" in improved_content:
                    instruction_match = re.search(r"Instruction:\s*(.*?)(?:\n\n(?:Expected Output:|Answer:)|$)", improved_content, re.DOTALL)
                    if instruction_match:
                        lesson.instruction = instruction_match.group(1).strip()
                
                if "Expected Output:" in improved_content:
                    output_match = re.search(r"Expected Output:\s*(.*?)(?:\n\n(?:Answer:)|$)", improved_content, re.DOTALL)
                    if output_match:
                        lesson.expected_output = output_match.group(1).strip()
                
                if "Answer:" in improved_content:
                    answer_match = re.search(r"Answer:\s*(.*?)(?:\n\n|$)", improved_content, re.DOTALL)
                    if answer_match:
                        lesson.answer = answer_match.group(1).strip()
            
            # Log improvement success
            self.logger.info(f"Successfully improved lesson: {lesson.title}")
            return lesson
            
        except Exception as e:
            self.logger.error(f"Error improving lesson: {str(e)}")
            return lesson
