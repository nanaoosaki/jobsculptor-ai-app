"""
Unit conversion utilities for handling different measurement systems.

This module provides functions to convert between CSS units (px, rem, em, etc.)
and DOCX units (twips, points) for consistent styling across formats.
"""

import re
import logging

logger = logging.getLogger(__name__)

def twip(width_str, base_px=16):
    """
    Convert CSS length values to DOCX twips (1/20 of a point, 1/1440 of an inch).
    
    Args:
        width_str: String with CSS units (e.g., '1px', '0.5rem', '2em')
        base_px: Base pixel size for relative units (default 16px = 1rem)
    
    Returns:
        Integer number of twips
        
    Raises:
        ValueError: If the input string has an invalid or unsupported format
    """
    if not width_str or not isinstance(width_str, str):
        raise ValueError(f"Invalid width value: {width_str}")
    
    # Clean and normalize the input
    width_str = width_str.strip().lower()
    
    # Extract the numeric part and unit
    match = re.match(r'^([-+]?[0-9]*\.?[0-9]+)([a-z%]*)$', width_str)
    
    if not match:
        raise ValueError(f"Invalid width format: {width_str}")
    
    value, unit = match.groups()
    value = float(value)
    
    # Convert to points first (1pt = 20twip)
    points = 0
    
    if unit == 'pt' or unit == 'point' or unit == 'points':
        points = value
    elif unit == 'px':
        points = value * 0.75  # 1px ≈ 0.75pt
    elif unit == 'in':
        points = value * 72  # 1in = 72pt
    elif unit == 'cm':
        points = value * 28.35  # 1cm ≈ 28.35pt
    elif unit == 'mm':
        points = value * 2.835  # 1mm ≈ 2.835pt
    elif unit == 'rem':
        points = value * base_px * 0.75  # Convert rem to px to pt
    elif unit == 'em':
        points = value * base_px * 0.75  # Similar to rem for our purposes
    elif unit == '%':
        # Percentage is context-dependent, warn and use a fallback
        logger.warning(f"Percentage units ({width_str}) cannot be reliably converted to twips. Using 0.")
        return 0
    elif unit == '':
        # Unitless values are interpreted as points in CSS
        points = value
    else:
        raise ValueError(f"Unsupported unit: {unit}")
    
    # Convert points to twips (1pt = 20twip)
    twips = int(points * 20)
    
    return twips 