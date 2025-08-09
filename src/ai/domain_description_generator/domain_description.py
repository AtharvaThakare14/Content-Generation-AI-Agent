import sys
from typing import Dict, Any

from src.logging import logging
from src.constants.mongodb import *
from src.exception import CustomException
from src.configurations.openai import OpenAIChatModel
from src.configurations.mongodb import MongoDBConnection
from src.utils.add_new_field_dict import add_fields_to_dict

from src.ai.course_description_generator.states.states import domain_description


class DomainQualityChecker:
    """Agent responsible for checking and improving the quality of domain descriptions."""

    def __init__(self):
        try:
            self.chat_open_ai = OpenAIChatModel()
            self.model = self.chat_open_ai.get_chat_model()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            self.logger.error(
                f"Failed to initialize DomainQualityChecker: {str(e)}")
            raise CustomException(e, sys)

    def check_description_quality(self, description: str) -> Dict[str, Any]:
        """Check the quality of a domain description."""
        # Check length (should be 1-2 sentences)
        words = description.split()
        sentences = description.split('.')
        sentences = [s for s in sentences if s.strip()]

        length_score = 1.0 if 15 <= len(
            words) <= 50 and 1 <= len(sentences) <= 2 else 0.5

        # Check for clarity and focus
        clarity_terms = ['focuses on', 'covers', 'encompasses',
                         'includes', 'explores', 'specializes in']
        has_clarity = any(term in description.lower()
                          for term in clarity_terms)
        clarity_score = 1.0 if has_clarity else 0.5

        # Check for domain specificity
        tech_terms = ['technology', 'development', 'programming',
                      'science', 'engineering', 'design', 'analytics', 'business']
        has_specificity = any(term in description.lower()
                              for term in tech_terms)
        specificity_score = 1.0 if has_specificity else 0.5

        # Calculate overall score
        overall_score = (length_score + clarity_score +
                         specificity_score) / 3 * 100

        return {
            "quality_score": round(overall_score, 2),
            "passes_threshold": overall_score >= 80,
            "feedback": {
                "length": "Good" if length_score >= 0.8 else "Description should be 1-2 concise sentences (15-50 words)",
                "clarity": "Good" if clarity_score >= 0.8 else "Add terms that clearly define the domain's focus",
                "specificity": "Good" if specificity_score >= 0.8 else "Include specific field or technology areas covered"
            }
        }

    def improve_description(self, description: str, feedback: Dict[str, str]) -> str:
        """Improve a domain description based on quality feedback."""
        if all(value == "Good" for value in feedback.values()):
            return description

        system_message = f"""
        You are an expert copywriter specializing in creating concise, clear domain descriptions.
        
        Improve the following domain description based on this feedback:
        
        CURRENT DESCRIPTION:
        "{description}"
        
        FEEDBACK:
        {', '.join([f"{key}: {value}" for key, value in feedback.items() if value != "Good"])}
        
        Create a new 1-2 sentence description (15-50 words) that is concise, specific, and clear.
        Focus on what the domain encompasses and include specific field or technology areas where appropriate.
        Use clear language that precisely defines the domain's scope and focus.
        
        Return ONLY the improved description text with no additional commentary.
        """

        try:
            response = self.model.invoke(system_message)
            improved_description = response.content.strip().strip('"')
            return improved_description
        except Exception as e:
            self.logger.error(f"Error improving description: {str(e)}")
            return description


class DomainDescriptionGenerator:
    """Main class responsible for generating high-quality domain descriptions."""

    def __init__(self):
        try:
            self.chat_open_ai = OpenAIChatModel()
            self.model = self.chat_open_ai.get_chat_model()
            self.structured_llm = self.model.with_structured_output(
                domain_description)
            self.mongodb_client = MongoDBConnection(
                database_name=AI_TUTOR_IQAN_DATABASE_NAME)
            self.collection = self.mongodb_client.db[DOMAIN_COLLECTION_NAME]
            self.quality_checker = DomainQualityChecker()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            self.logger.error(
                f"Failed to initialize DomainDescriptionGenerator: {str(e)}")
            raise CustomException(e, sys)

    def generate_description(self, data, unique_id):
        """Generate a high-quality, concise 1-2 sentence domain description."""
        try:
            # Generate initial description
            system_message = f"""
            You are an expert copywriter specializing in creating concise, clear educational content descriptions.
            
            Create a powerful 1-2 sentence description for a domain on "{data['domain_name']}".
            
            Your description should:
            - Be exactly 1-2 sentences (15-50 words total)
            - Clearly define what the domain encompasses
            - Use precise language that communicates the domain's focus
            - Include specific field or technology areas where appropriate
            - Be informative and educational
            
            Return ONLY the description text with no additional commentary.
            """

            self.logger.info(
                f"Generating description for domain: {data['domain_name']}")
            response = self.model.invoke(system_message)
            initial_description = response.content.strip().strip('"')

            # Check and improve description quality
            quality_report = self.quality_checker.check_description_quality(
                initial_description)
            self.logger.info(
                f"Description quality score: {quality_report['quality_score']}/100")

            final_description = initial_description
            if not quality_report['passes_threshold']:
                self.logger.info("Improving description quality")
                final_description = self.quality_checker.improve_description(
                    initial_description, quality_report['feedback'])

            # Create structured output
            structured_response = domain_description(
                description=final_description)

            # Add additional fields
            new_fields = {
                'domain_id': unique_id,
                'domain_name': data['domain_name'],
                'created_at': data.get('created_at'),
                'on_demand': False
            }

            updated_dict = add_fields_to_dict(
                structured_response.model_dump(), new_fields, insert_at_top=True)

            self.logger.info(f"Final domain description: {final_description}")
            return updated_dict

        except Exception as e:
            self.logger.error(f"Error generating domain description: {str(e)}")
            raise CustomException(e, sys)
