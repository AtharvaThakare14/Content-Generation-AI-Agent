import os
from pathlib import Path

def load_lesson_prompt(prompt_type: str, level: str, **kwargs) -> str:
    """
    Load a lesson prompt template for the given level and format it with the provided kwargs.
    
    Args:
        prompt_type: The type of prompt ('outline' or 'content')
        level: The difficulty level ('basic', 'beginner', 'intermediate', 'advance')
        **kwargs: Variables to format into the prompt template
        
    Returns:
        str: The formatted prompt
    """
    # Define the base directory for prompts
    base_dir = Path(__file__).parent / "lessons_generator" / "levels"
    
    # Map level and type to filename
    filename = f"{level.lower()}_{prompt_type.lower()}.txt"
    
    # Build the full file path
    filepath = base_dir / filename
    
    # Read the template
    try:
        with open(filepath, 'r') as f:
            template = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Lesson prompt file not found: {filepath}")
    
    # Format the template with the provided variables
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise KeyError(f"Missing required variable in lesson prompt template: {e}")
