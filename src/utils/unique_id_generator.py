import uuid

def unique_id_generator(prefix: str) -> str:
    """
    Generate a unique course ID with a prefix.

    Args:
        prefix (str): A prefix for the course ID (default: "COURSE").

    Returns:
        str: A unique course ID string.
    """
    unique_id = uuid.uuid4().hex[:8].upper()  # Shortened and uppercase
    return f"{prefix}_{unique_id}"