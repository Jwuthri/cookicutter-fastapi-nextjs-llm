"""
Structured streaming utilities for LangChain + OpenRouter.

Provides incremental parsing of partial JSON chunks into BaseModel instances,
similar to Agno's implementation. Handles streaming structured output by:
1. Accumulating content chunks
2. Trying multiple strategies to parse partial JSON (Agno's approach)
3. Merging fields intelligently based on BaseModel schema
4. Validating and returning incremental BaseModel updates
"""
import json
import re
from typing import List, Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

from app.utils.logging import get_logger

logger = get_logger("structured_streaming")

T = TypeVar("T", bound=BaseModel)


def try_parse_partial_json(text: str) -> Optional[dict]:
    """
    Try to parse partial JSON, returning what we can.
    
    Uses Agno's approach: tries multiple strategies to close incomplete JSON structures.
    This handles streaming scenarios where JSON arrives incrementally.
    
    Args:
        text: String that may contain partial JSON
        
    Returns:
        Parsed dict if successful, None otherwise
    """
    if not text or not text.strip():
        return None
    
    # Try parsing as-is first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try closing open structures (Agno's approach)
    # These are common patterns when JSON is incomplete
    attempts = [
        text + '}',
        text + ']}',
        text + '"}',
        text + '"]}',
        text + '"}]}',
        text + '": null}',
        text + '": []}',
        text + '": {}}',
        text + '": ""}',
    ]
    
    for attempt in attempts:
        try:
            return json.loads(attempt)
        except json.JSONDecodeError:
            continue
    
    # Try to extract JSON from markdown code blocks
    json_block_pattern = r"```(?:json)?\s*(\{.*?)\s*```"
    matches = re.findall(json_block_pattern, text, re.DOTALL)
    
    if matches:
        for match in matches:
            # Try closing the extracted JSON
            for attempt in [match + '}', match + ']}', match + '"}']:
                try:
                    return json.loads(attempt)
                except json.JSONDecodeError:
                    continue
    
    return None


def _parse_individual_json(
    content: str, output_schema: Type[T]
) -> Optional[T]:
    """
    Parse JSON from content and merge fields based on response model schema.
    
    Uses Agno's approach: tries to parse partial JSON, then merges fields intelligently.
    
    This function:
    1. Tries to parse JSON (complete or partial) using try_parse_partial_json
    2. Merges fields intelligently:
       - Lists: extend the list (accumulate items)
       - Other fields: use the latest value (overwrite)
    3. Validates merged data against BaseModel schema
    
    Args:
        content: String content containing JSON (may be partial)
        output_schema: Pydantic BaseModel class to parse into
        
    Returns:
        BaseModel instance if valid data found, None otherwise
    """
    # Try to parse the JSON (handles partial JSON)
    parsed_dict = try_parse_partial_json(content)
    
    if not parsed_dict or not isinstance(parsed_dict, dict):
        return None
    
    # Get the expected fields from the response model
    model_fields = (
        output_schema.model_fields
        if hasattr(output_schema, "model_fields")
        else {}
    )
    
    # Merge data based on model fields (Agno's merging strategy)
    merged_data: dict = {}
    
    for field_name, field_info in model_fields.items():
        if field_name in parsed_dict:
            field_value = parsed_dict[field_name]
            
            # If field is a list, extend it; otherwise, use the latest value
            if isinstance(field_value, list):
                if field_name not in merged_data:
                    merged_data[field_name] = []
                # Extend with new items (avoid duplicates if needed)
                for item in field_value:
                    if item not in merged_data[field_name]:
                        merged_data[field_name].append(item)
            else:
                merged_data[field_name] = field_value
    
    if not merged_data:
        return None
    
    try:
        return output_schema.model_validate(merged_data)
    except ValidationError as e:
        # Log debug but don't break streaming (partial JSON is expected)
        logger.debug(f"Validation failed on merged data: {e}")
        return None


def parse_response_model_str(
    content: str, output_schema: Type[T]
) -> Optional[T]:
    """
    Parse response model from string content (may be partial JSON).
    
    Main parsing function that handles edge cases. Uses Agno's approach:
    tries multiple strategies to parse partial JSON, then merges fields.
    
    Args:
        content: String content containing JSON (may be partial)
        output_schema: Pydantic BaseModel class to parse into
        
    Returns:
        BaseModel instance if valid data found, None otherwise
    """
    if not content or not content.strip():
        return None
    
    # Try to parse directly (handles partial JSON)
    result = _parse_individual_json(content, output_schema)
    
    if result is not None:
        return result
    
    # If no result, try to extract JSON from markdown code blocks
    # Some LLMs wrap JSON in ```json ... ``` blocks
    json_block_pattern = r"```(?:json)?\s*(\{.*?)\s*```"
    matches = re.findall(json_block_pattern, content, re.DOTALL)
    
    if matches:
        for match in matches:
            result = _parse_individual_json(match, output_schema)
            if result is not None:
                return result
    
    return None


class StructuredStreamingHandler:
    """
    Handler for streaming structured output that accumulates chunks and parses incrementally.
    
    Similar to Agno's approach: accumulates content, tries to parse partial JSON,
    and tracks changes to avoid duplicate updates.
    
    Supports both async generator and callback patterns for streaming BaseModel updates.
    """
    
    def __init__(self, output_schema: Type[T]):
        """
        Initialize streaming handler.
        
        Args:
            output_schema: Pydantic BaseModel class to parse into
        """
        self.output_schema = output_schema
        self.response_content = ""
        self.last_valid_model: Optional[T] = None
        self.last_parsed_dict: Optional[dict] = None
    
    def add_chunk(self, chunk: str) -> Optional[T]:
        """
        Add a chunk of content and return incremental BaseModel update if available.
        
        Only returns an update if the parsed data has changed (Agno's approach).
        
        Args:
            chunk: Content chunk to add
            
        Returns:
            Updated BaseModel instance if valid data found and changed, None otherwise
        """
        if chunk:
            self.response_content += chunk
            
            # Try to parse incremental update
            parsed = parse_response_model_str(
                self.response_content, self.output_schema
            )
            
            if parsed is not None:
                # Check if this is different from last parsed (Agno's approach)
                current_dict = parsed.model_dump()
                
                if current_dict != self.last_parsed_dict:
                    self.last_parsed_dict = current_dict
                    self.last_valid_model = parsed
                    return parsed
            
            return None
        
        return None
    
    def get_last_valid(self) -> Optional[T]:
        """
        Get the last valid BaseModel instance parsed.
        
        Returns:
            Last valid BaseModel instance or None
        """
        return self.last_valid_model
    
    def reset(self):
        """Reset the handler state."""
        self.response_content = ""
        self.last_valid_model = None
        self.last_parsed_dict = None
