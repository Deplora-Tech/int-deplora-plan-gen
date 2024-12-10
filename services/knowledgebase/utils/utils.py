import re

def replace_special_characters(input_string):
    """
    Replaces all special characters in the input string with underscores.
    
    Args:
        input_string (str): The string to process.
    
    Returns:
        str: The processed string with special characters replaced by '_'.
    """
    return re.sub(r'[^a-zA-Z0-9]', '_', input_string)