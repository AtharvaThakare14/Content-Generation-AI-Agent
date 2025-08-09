import sys
from typing import List, Dict, Any
import json

from src.logging import logging
from src.constants.mongodb import *
from src.exception import CustomException
from src.configurations.openai import OpenAIChatModel
from src.configurations.mongodb import MongoDBConnection

from src.ai.module_generator.states.states import *


class CurriculumStructureGenerator:
    """Agent responsible for generating the high-level curriculum structure."""

    def __init__(self):
        try:
            self.chat_open_ai = OpenAIChatModel()
            self.model = self.chat_open_ai.get_chat_model()
            self.structured_llm = self.model.with_structured_output(
                ModuleOutput)
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            self.logger.error(
                f"Failed to initialize CurriculumStructureGenerator: {str(e)}")
            raise CustomException(e, sys)

    def generate_curriculum_structure(self, course_name: str) -> Dict[str, Any]:
        """Generate a high-level curriculum structure with modules."""
        system_message = f"""
        You are an expert curriculum architect with extensive experience in designing comprehensive educational programs.
        
        Your task is to create a structured curriculum blueprint for "{course_name}".
        
        Guidelines for a professional-grade curriculum:
        - Design 6-10 modules in a logical progression from fundamentals to advanced concepts
        - Each module must have:
          * A clear, action-oriented title that communicates value to the learner
          * A comprehensive description (3-5 sentences) explaining what will be covered and why it matters
        - Provide a realistic timeline for completion (e.g., "8 weeks at 10 hours/week")
        - Include a complete list of tools, technologies, and prerequisites students will need
        - Ensure modules build upon each other in a coherent learning path
        - Consider both theoretical knowledge and practical skills development
        
        Your curriculum should be suitable for a professional educational platform and follow industry best practices.
        
        Return structured data in this format:
        - course: The name of the course
        - duration: Realistic timeframe to complete the curriculum
        - num_modules: Number of modules generated
        - tools: Comprehensive list of all tools and technologies used
        - modules: List of modules with title and description
        """

        self.logger.info(f"Generating curriculum structure for: {course_name}")
        structured_model = self.model.with_structured_output(
            ModuleOutput, method="function_calling")
        response = structured_model.invoke(system_message)
        return response.model_dump()


class ModuleEnhancer:
    """Agent responsible for enhancing module descriptions with learning objectives and prerequisites."""

    def __init__(self):
        try:
            self.chat_open_ai = OpenAIChatModel()
            self.model = self.chat_open_ai.get_chat_model()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            self.logger.error(f"Failed to initialize ModuleEnhancer: {str(e)}")
            raise CustomException(e, sys)

    def enhance_module(self, module: Dict[str, str], course_context: Dict[str, Any], module_index: int) -> Dict[str, Any]:
        """Enhance a module with learning objectives, prerequisites, and detailed content outline."""
        system_message = f"""
        You are an expert instructional designer specializing in creating detailed, high-quality course modules.
        
        Enhance the following module with professional-grade details:
        
        COURSE CONTEXT:
        - Course Title: {course_context['course']}
        - Tools Used: {', '.join(course_context['tools'])}
        - Module Position: {module_index + 1} of {course_context['num_modules']}
        
        MODULE TO ENHANCE:
        - Title: {module['title']}
        - Description: {module['description']}
        
        Create a comprehensive enhancement that includes:
        
        1. LEARNING OBJECTIVES (4-6 specific, measurable outcomes using Bloom's Taxonomy verbs)
           Example: "Implement error handling strategies in asynchronous JavaScript functions"
        
        2. PREREQUISITES
           - Knowledge prerequisites (what students should already know)
           - Technical prerequisites (tools, software, etc. needed)
        
        3. KEY TOPICS (8-12 specific topics that will be covered in this module)
           Provide a bullet list of specific concepts, techniques, or skills
        
        4. PRACTICAL APPLICATIONS (3-5 real-world scenarios where these skills apply)
           Brief descriptions of how these skills are used professionally
        
        5. ESTIMATED COMPLETION TIME
           Realistic time to complete this specific module (e.g., "5-7 hours")
        
        IMPORTANT: Do NOT create a nested 'module' structure inside the module. Keep all properties at the top level.
        For example, DO NOT structure your response like this:
        {{"title": "Title", "description": "Description", "module": {{...}}}}.
        
        Instead, keep all properties at the top level like this:
        {{"title": "Title", "description": "Description", "learning_objectives": [...], ...}}
        
        Format your response as a JSON object with these fields. Ensure all content is educational, professional, and aligned with industry best practices.
        """

        self.logger.info(f"Enhancing module: {module['title']}")

        try:
            response = self.model.invoke(system_message)
            enhanced_content = json.loads(response.content)

            # Merge the original module with enhanced content
            enhanced_module = {
                "title": module['title'],
                "description": module['description'],
                **enhanced_content
            }

            return enhanced_module

        except Exception as e:
            self.logger.error(f"Error enhancing module: {str(e)}")
            # Return original module if enhancement fails
            return {
                "title": module['title'],
                "description": module['description'],
                "learning_objectives": ["Unable to generate learning objectives"],
                "prerequisites": {"knowledge": [], "technical": []},
                "key_topics": ["Unable to generate key topics"],
                "practical_applications": ["Unable to generate practical applications"],
                "estimated_completion_time": "Unknown"
            }


class ModuleQualityChecker:
    """Agent responsible for checking and improving the quality of modules."""

    def __init__(self):
        try:
            self.chat_open_ai = OpenAIChatModel()
            self.model = self.chat_open_ai.get_chat_model()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            self.logger.error(
                f"Failed to initialize ModuleQualityChecker: {str(e)}")
            raise CustomException(e, sys)

    def check_module_quality(self, module: Dict[str, Any]) -> Dict[str, Any]:
        """Check the quality of a module and provide improvement suggestions."""
        # Define quality criteria
        criteria = {
            "title_quality": self._check_title_quality(module.get('title', '')),
            "description_quality": self._check_description_quality(module.get('description', '')),
            "learning_objectives_quality": self._check_learning_objectives(module.get('learning_objectives', [])),
            "key_topics_quality": self._check_key_topics(module.get('key_topics', [])),
            "practical_relevance": self._check_practical_relevance(module.get('practical_applications', []))
        }

        # Calculate overall quality score
        quality_score = sum(criteria.values()) / len(criteria) * 100

        return {
            "quality_score": round(quality_score, 2),
            "passes_threshold": quality_score >= 80,
            "criteria": criteria,
            "improvement_suggestions": self._generate_improvement_suggestions(criteria, module)
        }

    def _check_title_quality(self, title: str) -> float:
        """Check the quality of the module title."""
        if not title:
            return 0.0

        # Check length (not too short, not too long)
        length_score = 0.5 if 4 <= len(title.split()) <= 8 else 0.3

        # Check for action verbs
        action_verbs = ['build', 'create', 'develop',
                        'implement', 'master', 'learn', 'understand', 'explore']
        has_action_verb = any(verb in title.lower() for verb in action_verbs)
        action_score = 0.5 if has_action_verb else 0.2

        return length_score + action_score

    def _check_description_quality(self, description: str) -> float:
        """Check the quality of the module description."""
        if not description:
            return 0.0

        # Check length
        words = description.split()
        length_score = 0.4 if len(words) >= 30 else 0.2

        # Check for specific details
        specificity_score = 0.3 if any(tech_word in description.lower() for tech_word in [
                                       'javascript', 'python', 'code', 'function', 'api']) else 0.1

        # Check for learning value indicators
        value_score = 0.3 if any(value_word in description.lower() for value_word in [
                                 'learn', 'skill', 'practice', 'understand', 'master']) else 0.1

        return length_score + specificity_score + value_score

    def _check_learning_objectives(self, objectives: List[str]) -> float:
        """Check the quality of learning objectives."""
        if not objectives:
            return 0.0

        # Check number of objectives
        count_score = 0.3 if 4 <= len(objectives) <= 8 else 0.1

        # Check for Bloom's taxonomy verbs
        bloom_verbs = ['analyze', 'apply', 'assess', 'build', 'calculate', 'categorize', 'compare', 'compile', 'compose', 'construct', 'create',
                       'critique', 'define', 'demonstrate', 'design', 'develop', 'differentiate', 'evaluate', 'explain', 'identify', 'implement', 'integrate']

        verb_scores = [0.1 for obj in objectives if any(
            verb in obj.lower() for verb in bloom_verbs)]
        verb_score = min(sum(verb_scores), 0.7)  # Cap at 0.7

        return count_score + verb_score

    def _check_key_topics(self, topics: List[str]) -> float:
        """Check the quality of key topics."""
        if not topics:
            return 0.0

        # Check number of topics
        count_score = 0.4 if 6 <= len(topics) <= 15 else 0.2

        # Check specificity (length of topics as a proxy)
        specificity_score = min(
            0.6, sum(0.05 for topic in topics if len(topic.split()) >= 3))

        return count_score + specificity_score

    def _check_practical_relevance(self, applications: List[str]) -> float:
        """Check the practical relevance of the module."""
        if not applications:
            return 0.0

        # Check number of applications
        count_score = 0.4 if len(applications) >= 3 else 0.2

        # Check for industry relevance indicators
        industry_terms = ['industry', 'professional', 'workplace',
                          'company', 'business', 'production', 'real-world']
        relevance_score = min(0.6, sum(0.15 for app in applications if any(
            term in app.lower() for term in industry_terms)))

        return count_score + relevance_score

    def _generate_improvement_suggestions(self, criteria: Dict[str, float], module: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on quality criteria."""
        suggestions = []

        if criteria['title_quality'] < 0.7:
            suggestions.append(
                "Make the title more action-oriented and specific about what learners will achieve.")

        if criteria['description_quality'] < 0.7:
            suggestions.append(
                "Enhance the description with more specific details about technologies and skills covered.")

        if criteria['learning_objectives_quality'] < 0.7:
            suggestions.append(
                "Improve learning objectives using specific, measurable action verbs from Bloom's taxonomy.")

        if criteria['key_topics_quality'] < 0.7:
            suggestions.append(
                "Expand key topics to be more comprehensive and specific.")

        if criteria['practical_relevance'] < 0.7:
            suggestions.append(
                "Add more industry-relevant practical applications with specific examples.")

        return suggestions

    def improve_module(self, module: Dict[str, Any], quality_report: Dict[str, Any]) -> Dict[str, Any]:
        """Improve a module based on quality evaluation."""
        if quality_report['passes_threshold']:
            return module

        suggestions = quality_report.get('improvement_suggestions', [])
        if not suggestions:
            return module

        system_message = f"""
        You are an expert curriculum designer specializing in creating high-quality educational modules.
        
        Improve the following module based on these suggestions:
        
        SUGGESTIONS:
        {chr(10).join(f'- {suggestion}' for suggestion in suggestions)}
        
        CURRENT MODULE:
        {json.dumps(module, indent=2)}
        
        IMPORTANT: Do NOT create a nested 'module' structure inside the module. Keep all properties at the top level.
        For example, DO NOT structure your response like this:
        {{"title": "Title", "description": "Description", "module": {{...}}}}.
        
        Instead, keep all properties at the top level like this:
        {{"title": "Title", "description": "Description", "learning_objectives": [...], ...}}
        
        Provide an improved version of this module addressing all the suggestions.
        Return your response as a JSON object with the same structure as the original module.
        """

        try:
            response = self.model.invoke(system_message)
            improved_module = json.loads(response.content)
            return improved_module
        except Exception as e:
            self.logger.error(f"Error improving module: {str(e)}")
            return module


class ModuleGenerator:
    """Main class responsible for generating high-quality course modules."""

    def __init__(self):
        try:
            self.chat_open_ai = OpenAIChatModel()
            self.model = self.chat_open_ai.get_chat_model()
            self.structured_llm = self.model.with_structured_output(
                ModuleOutput)
            self.mongodb_client = MongoDBConnection(
                database_name=AI_TUTOR_IQAN_DATABASE_NAME)
            self.collection = self.mongodb_client.db[COURSES_COLLECTION_NAME]
            self.curriculum_generator = CurriculumStructureGenerator()
            self.module_enhancer = ModuleEnhancer()
            self.quality_checker = ModuleQualityChecker()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            self.logger.error(
                f"Failed to initialize ModuleGenerator: {str(e)}")
            raise CustomException(e, sys)

    def module_generater(self, state: Module):
        """Generate high-quality course modules using a multi-phase approach."""
        try:
            # Phase 1: Generate high-level curriculum structure
            self.logger.info(
                f"Generating curriculum for: {state['course_name']}")
            curriculum = self.curriculum_generator.generate_curriculum_structure(
                state['course_name'])

            # Phase 2: Enhance each module with detailed content
            enhanced_modules = []
            for i, module in enumerate(curriculum['modules']):
                # Create module context for the enhancer
                module_context = {
                    'course': curriculum['course'],
                    'tools': curriculum['tools'],
                    'num_modules': curriculum['num_modules']
                }

                # Enhance the module with detailed content
                enhanced_module = self.module_enhancer.enhance_module(
                    module, module_context, i)

                # Check and improve module quality
                quality_report = self.quality_checker.check_module_quality(
                    enhanced_module)
                self.logger.info(
                    f"Module quality score: {quality_report['quality_score']}/100")

                if not quality_report['passes_threshold']:
                    self.logger.info(
                        f"Improving module: {enhanced_module['title']}")
                    enhanced_module = self.quality_checker.improve_module(
                        enhanced_module, quality_report)

                enhanced_modules.append(enhanced_module)

            # Update the curriculum with enhanced modules
            curriculum['modules'] = enhanced_modules

            # Log a sample of the generated content for verification
            if enhanced_modules:
                sample_module = enhanced_modules[0]
                self.logger.info(
                    f"Sample module title: {sample_module['title']}")
                self.logger.info(
                    f"Sample learning objectives: {sample_module.get('learning_objectives', [])[:2]}")

            return curriculum

        except Exception as e:
            self.logger.error(f"Error generating modules: {str(e)}")
            raise CustomException(e, sys)
