import sys
from typing import Dict, Any

from src.logging import logging
from src.constants.mongodb import *
from src.exception import CustomException
from src.configurations.openai import OpenAIChatModel
from src.configurations.mongodb import MongoDBConnection
from src.utils.add_new_field_dict import add_fields_to_dict

from src.ai.course_description_generator.states.states import *


class DescriptionQualityChecker:
    """Agent responsible for checking and improving the quality of course descriptions."""
    
    def __init__(self):
        try:
            self.chat_open_ai = OpenAIChatModel()
            self.model = self.chat_open_ai.get_chat_model()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            self.logger.error(f"Failed to initialize DescriptionQualityChecker: {str(e)}")
            raise CustomException(e, sys)
    
    def check_description_quality(self, description: str) -> Dict[str, Any]:
        """Check the quality of a course description."""
        # Check length (should be 1-2 sentences)
        words = description.split()
        sentences = description.split('.')
        sentences = [s for s in sentences if s.strip()]
        
        length_score = 1.0 if 15 <= len(words) <= 50 and 1 <= len(sentences) <= 2 else 0.5
        
        # Check for marketing appeal
        marketing_terms = ['master', 'learn', 'discover', 'develop', 'build', 'create', 'transform', 'unlock']
        has_marketing_appeal = any(term in description.lower() for term in marketing_terms)
        marketing_score = 1.0 if has_marketing_appeal else 0.5
        
        # Check for specificity
        tech_terms = ['javascript', 'python', 'react', 'node', 'web', 'app', 'data', 'code', 'programming', 'development']
        has_specificity = any(term in description.lower() for term in tech_terms)
        specificity_score = 1.0 if has_specificity else 0.5
        
        # Calculate overall score
        overall_score = (length_score + marketing_score + specificity_score) / 3 * 100
        
        return {
            "quality_score": round(overall_score, 2),
            "passes_threshold": overall_score >= 80,
            "feedback": {
                "length": "Good" if length_score >= 0.8 else "Description should be 1-2 concise sentences (15-50 words)",
                "marketing_appeal": "Good" if marketing_score >= 0.8 else "Add action-oriented terms that motivate learners",
                "specificity": "Good" if specificity_score >= 0.8 else "Include specific technologies or skills covered"
            }
        }
    
    def improve_description(self, description: str, feedback: Dict[str, str]) -> str:
        """Improve a course description based on quality feedback."""
        if all(value == "Good" for value in feedback.values()):
            return description
        
        system_message = f"""
        You are an expert course copywriter specializing in creating concise, compelling course descriptions.
        
        Improve the following course description based on this feedback:
        
        CURRENT DESCRIPTION:
        "{description}"
        
        FEEDBACK:
        {', '.join([f"{key}: {value}" for key, value in feedback.items() if value != "Good"])}
        
        Create a new 1-2 sentence description (15-50 words) that is concise, specific, and motivating.
        Focus on what learners will gain and include specific technologies or skills where appropriate.
        Use action-oriented language that appeals to potential students.
        
        Return ONLY the improved description text with no additional commentary.
        """
        
        try:
            response = self.model.invoke(system_message)
            improved_description = response.content.strip().strip('"')
            return improved_description
        except Exception as e:
            self.logger.error(f"Error improving description: {str(e)}")
            return description


class CourseDescriptionGenerator:
    """Main class responsible for generating high-quality course descriptions."""
    
    def __init__(self):
        try:
            self.chat_open_ai = OpenAIChatModel()
            self.model = self.chat_open_ai.get_chat_model()
            self.structured_llm = self.model.with_structured_output(domain_description)
            self.mongodb_client = MongoDBConnection(database_name=AI_TUTOR_IQAN_DATABASE_NAME)
            self.collection = self.mongodb_client.db[DOMAIN_COLLECTION_NAME]
            self.quality_checker = DescriptionQualityChecker()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            self.logger.error(f"Failed to initialize CourseDescriptionGenerator: {str(e)}")
            raise CustomException(e, sys)

    def generate_description(self, data, unique_id):
        """Generate a high-quality, concise 1-2 sentence course description."""
        try:
            # Check if user provided a description
            if hasattr(data, 'description') and data.description:
                self.logger.info(f"Using user-provided description for course: {data.course_name}")
                # Format multi-line description to a single line with proper spacing
                final_description = " ".join(data.description.replace('\r', '').split('\n'))
            else:
                # Generate initial description
                formatted_description = ""
                if hasattr(data, 'description') and data.description:
                    # Format multi-line description to a single line with proper spacing
                    formatted_description = " ".join(data.description.replace('\r', '').split('\n'))
                    description_context = f"\nAdditional context/notes from the course creator: {formatted_description}"
                else:
                    description_context = ""
                system_message = f"""
                You are an expert course copywriter specializing in creating concise, compelling educational content.
                
                Create a powerful 1-2 sentence description for a course on "{data.course_name}".
                {description_context}
                Your description should:
                - Be exactly 1-2 sentences (15-50 words total)
                - Clearly communicate the value proposition to potential students
                - Use action-oriented language (e.g., "Master", "Build", "Develop")
                - Include specific technologies or skills where appropriate
                - Focus on outcomes and what learners will gain
                - Be engaging and motivational
                
                Return ONLY the description text with no additional commentary.
                """
                
                self.logger.info(f"Generating description for course: {data.course_name}")
                response = self.model.invoke(system_message)
                initial_description = response.content.strip().strip('"')
                
                # Check and improve description quality
                quality_report = self.quality_checker.check_description_quality(initial_description)
                self.logger.info(f"Description quality score: {quality_report['quality_score']}/100")
                
                final_description = initial_description
                if not quality_report['passes_threshold']:
                    self.logger.info("Improving description quality")
                    final_description = self.quality_checker.improve_description(
                        initial_description, quality_report['feedback'])
            
            # Create structured output
            structured_response = domain_description(description=final_description)
            
            # Add additional fields
            new_fields = {
                'course_id': unique_id,
                'course_name': data.course_name,
                'level': data.level,
                'image_uri': data.image_uri,
                'created_at': data.created_at,
                'is_popular': False,
                'is_trending': False
            }
            
            updated_dict = add_fields_to_dict(
                structured_response.model_dump(), new_fields, insert_at_top=True)
            
            self.logger.info(f"Final description: {final_description}")
            return updated_dict

        except Exception as e:
            self.logger.error(f"Error generating description: {str(e)}")
            raise CustomException(e, sys)
