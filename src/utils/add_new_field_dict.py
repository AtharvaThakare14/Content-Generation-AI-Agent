def add_fields_to_dict(base_dict: dict, new_fields: dict, insert_at_top: bool = True) -> dict:
    """
    Add new fields to a dictionary. Optionally insert at the top.
    
    Args:
        base_dict (dict): Original dictionary
        new_fields (dict): Fields to be added
        insert_at_top (bool): If True, prepends new fields; else appends
    
    Returns:
        dict: Updated dictionary
    """
    if insert_at_top:
        return {**new_fields, **base_dict}
    else:
        return {**base_dict, **new_fields}
