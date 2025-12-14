"""
Robust JSON Parser for LLM Outputs

Handles various formats and cleans the string before parsing.
"""
import json
import logging
import re

logger = logging.getLogger(__name__)

def parse_json_output(text: str) -> dict:
    """
    Cleans and parses a JSON string from LLM output.
    Handles markdown code blocks and other common formatting issues.
    """
    if not isinstance(text, str):
        logger.error(f"Invalid input to JSON parser: expected string, got {type(text)}")
        return {"error": "Invalid input type"}

    # 1. Find the start of the JSON content
    # Look for the first '{' or '[' that signals the start of JSON
    json_start = -1
    for i, char in enumerate(text):
        if char in ('{', '['):
            json_start = i
            break
    
    if json_start == -1:
        logger.warning("Could not find a starting JSON brace/bracket in the output.")
        return {"error": "No JSON content found in output"}

    text = text[json_start:]

    # 2. Find the end of the JSON content
    # Match the last '}' or ']' to the first '{' or '['
    if text.startswith('{'):
        last_char = '}'
    else:
        last_char = ']'
    
    json_end = text.rfind(last_char)
    if json_end == -1:
        logger.warning(f"Could not find a closing JSON character '{last_char}'.")
        return {"error": f"Mismatched JSON braces/brackets"}

    text = text[:json_end + 1]

    # 3. Attempt to parse the cleaned string
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning(f"Initial JSON parse failed: {e}. Attempting regex repair...")
        
        # Repair attempt 1: Fix missing commas between objects
        # Replace } \n { or } { with }, {
        text_repaired = re.sub(r'}\s*{', '}, {', text)
        
        # Repair attempt 2: Fix trailing commas
        text_repaired = re.sub(r',\s*]', ']', text_repaired)
        text_repaired = re.sub(r',\s*}', '}', text_repaired)
        
        try:
            return json.loads(text_repaired)
        except json.JSONDecodeError as e2:
            logger.error(f"Failed to parse JSON after repair: {e2}")
            logger.error(f"Content that failed parsing: {text[:500]}...")
        return {"error": "Final JSON parsing failed", "details": str(e)}
