# Utility functions for CSS AST manipulation
# Common helpers for transforms and serialization

import re
from typing import Dict, List, Union

def parse_spacing_value(value: str) -> List[str]:
    """
    Parse CSS spacing values (margin, padding) into components.
    
    Args:
        value: CSS spacing value like "0rem", "0.5rem 1rem", etc.
        
    Returns:
        List of individual values
    """
    return value.strip().split()

def normalize_selector(selector: str) -> str:
    """
    Normalize CSS selector for consistent processing.
    
    Args:
        selector: CSS selector string
        
    Returns:
        Normalized selector
    """
    # Remove extra whitespace
    selector = re.sub(r'\s+', ' ', selector.strip())
    
    # Normalize pseudo-selectors
    selector = re.sub(r'\s*::\s*', '::', selector)
    selector = re.sub(r'\s*:\s*', ':', selector)
    
    return selector

def merge_declarations(base_decls: Dict[str, str], override_decls: Dict[str, str]) -> Dict[str, str]:
    """
    Merge CSS declarations with override precedence.
    
    Args:
        base_decls: Base declarations
        override_decls: Override declarations (take precedence)
        
    Returns:
        Merged declarations
    """
    merged = base_decls.copy()
    merged.update(override_decls)
    return merged

def extract_important_properties(decls: Dict[str, str]) -> Dict[str, bool]:
    """
    Extract !important flags from CSS declarations.
    
    Args:
        decls: CSS declarations
        
    Returns:
        Dict mapping property names to important flags
    """
    important_flags = {}
    
    for prop, value in decls.items():
        if '!important' in value:
            important_flags[prop] = True
        else:
            important_flags[prop] = False
    
    return important_flags

def clean_css_value(value: str) -> str:
    """
    Clean CSS value by removing !important and normalizing whitespace.
    
    Args:
        value: CSS property value
        
    Returns:
        Cleaned value
    """
    value = value.replace('!important', '').strip()
    return re.sub(r'\s+', ' ', value)

def is_zero_value(value: str) -> bool:
    """
    Check if a CSS value represents zero.
    
    Args:
        value: CSS property value
        
    Returns:
        True if value represents zero
    """
    clean_value = clean_css_value(value).lower()
    zero_patterns = ['0', '0px', '0rem', '0em', '0%', '0pt']
    return clean_value in zero_patterns

def convert_to_physical_properties(logical_prop: str, value: str, direction: str = 'ltr') -> Dict[str, str]:
    """
    Convert logical CSS properties to physical equivalents.
    
    Args:
        logical_prop: Logical property name
        value: Property value
        direction: Text direction ('ltr' or 'rtl')
        
    Returns:
        Dict of physical properties
    """
    values = parse_spacing_value(value)
    physical_props = {}
    
    if logical_prop == 'margin-block':
        if len(values) == 1:
            physical_props['margin-top'] = values[0]
            physical_props['margin-bottom'] = values[0]
        elif len(values) == 2:
            physical_props['margin-top'] = values[0]
            physical_props['margin-bottom'] = values[1]
    elif logical_prop == 'margin-inline':
        if len(values) == 1:
            physical_props['margin-left'] = values[0]
            physical_props['margin-right'] = values[0]
        elif len(values) == 2:
            if direction == 'ltr':
                physical_props['margin-left'] = values[0]
                physical_props['margin-right'] = values[1]
            else:  # rtl
                physical_props['margin-right'] = values[0]
                physical_props['margin-left'] = values[1]
    
    # Similar logic for padding-block, padding-inline
    elif logical_prop == 'padding-block':
        if len(values) == 1:
            physical_props['padding-top'] = values[0]
            physical_props['padding-bottom'] = values[0]
        elif len(values) == 2:
            physical_props['padding-top'] = values[0]
            physical_props['padding-bottom'] = values[1]
    elif logical_prop == 'padding-inline':
        if len(values) == 1:
            physical_props['padding-left'] = values[0]
            physical_props['padding-right'] = values[0]
        elif len(values) == 2:
            if direction == 'ltr':
                physical_props['padding-left'] = values[0]
                physical_props['padding-right'] = values[1]
            else:  # rtl
                physical_props['padding-right'] = values[0]
                physical_props['padding-left'] = values[1]
    
    return physical_props 