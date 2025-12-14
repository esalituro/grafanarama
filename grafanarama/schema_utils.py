"""Utilities for working with JSON schemas to determine defaults"""
from typing import Any, Dict, List


def is_array_type(schema: Dict[str, Any]) -> bool:
    """Check if a schema property represents an array type"""
    if 'anyOf' in schema:
        # Check if any of the union types is an array
        return any(item.get('type') == 'array' for item in schema['anyOf'])
    if 'oneOf' in schema:
        return any(item.get('type') == 'array' for item in schema['oneOf'])
    return schema.get('type') == 'array'


def is_object_type(schema: Dict[str, Any]) -> bool:
    """Check if a schema property represents an object type"""
    if 'anyOf' in schema:
        return any(item.get('type') == 'object' or '$ref' in item for item in schema['anyOf'])
    if 'oneOf' in schema:
        return any(item.get('type') == 'object' or '$ref' in item for item in schema['oneOf'])
    return schema.get('type') == 'object' or '$ref' in schema


def get_array_fields(model_class) -> List[str]:
    """Get all field names from a Pydantic model that are array types"""
    schema = model_class.model_json_schema()
    array_fields = []
    
    for field_name, field_schema in schema.get('properties', {}).items():
        if is_array_type(field_schema):
            array_fields.append(field_name)
    
    return array_fields


def get_nested_array_fields(model_class) -> Dict[str, List[str]]:
    """Get nested array fields (e.g., templating.list, annotations.list)"""
    schema = model_class.model_json_schema()
    nested = {}
    
    # Get $defs for referenced types
    defs = schema.get('$defs', {})
    
    for field_name, field_schema in schema.get('properties', {}).items():
        if is_object_type(field_schema):
            # Check if it references a type in $defs
            ref = None
            if '$ref' in field_schema:
                ref = field_schema['$ref'].split('/')[-1]
            elif 'anyOf' in field_schema:
                for item in field_schema['anyOf']:
                    if '$ref' in item:
                        ref = item['$ref'].split('/')[-1]
                        break
            
            if ref and ref in defs:
                nested_fields = []
                nested_schema = defs[ref]
                for nested_field_name, nested_field_schema in nested_schema.get('properties', {}).items():
                    if is_array_type(nested_field_schema):
                        nested_fields.append(nested_field_name)
                
                if nested_fields:
                    nested[field_name] = nested_fields
    
    return nested


def apply_schema_defaults(data: Dict[str, Any], model_class) -> Dict[str, Any]:
    """Apply defaults based on schema - convert null arrays to empty arrays"""
    result = data.copy()
    schema = model_class.model_json_schema()
    
    # Handle top-level array fields
    array_fields = get_array_fields(model_class)
    for field in array_fields:
        if field in result and result[field] is None:
            result[field] = []
    
    # Handle nested array fields
    nested = get_nested_array_fields(model_class)
    for parent_field, nested_array_fields in nested.items():
        if parent_field in result:
            if result[parent_field] is None:
                # Create the parent object with empty arrays for nested fields
                result[parent_field] = {field: [] for field in nested_array_fields}
            elif isinstance(result[parent_field], dict):
                # Ensure nested array fields are arrays, not null
                for nested_field in nested_array_fields:
                    if nested_field in result[parent_field] and result[parent_field][nested_field] is None:
                        result[parent_field][nested_field] = []
                    elif nested_field not in result[parent_field]:
                        result[parent_field][nested_field] = []
    
    return result

