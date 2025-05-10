"""
DOCX Debug Utilities

This module provides tools for inspecting and debugging DOCX formatting.
"""

import logging
import json
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Pt, Cm

logger = logging.getLogger(__name__)

def inspect_docx_paragraphs(document):
    """
    Inspect all paragraphs in a document and log their formatting properties.
    
    Args:
        document: A python-docx Document object
        
    Returns:
        A list of dictionaries containing paragraph formatting information
    """
    results = []
    
    logger.info("Inspecting document paragraphs...")
    
    for i, paragraph in enumerate(document.paragraphs):
        # Skip empty paragraphs
        if not paragraph.text.strip():
            continue
            
        text = paragraph.text[:50] + "..." if len(paragraph.text) > 50 else paragraph.text
        style_name = paragraph.style.name if paragraph.style else "No Style"
        
        # Extract paragraph formatting
        fmt = paragraph.paragraph_format
        
        # Try to extract values directly from paragraph format - handle Twips objects
        try:
            left_indent = fmt.left_indent.cm if fmt.left_indent else "None"
        except (AttributeError, TypeError):
            left_indent = str(fmt.left_indent) if fmt.left_indent else "None"
            
        try:
            first_line_indent = fmt.first_line_indent.cm if fmt.first_line_indent else "None"
        except (AttributeError, TypeError):
            first_line_indent = str(fmt.first_line_indent) if fmt.first_line_indent else "None"
        
        # Extract values from the XML directly for more accurate information
        xml_values = {}
        
        if hasattr(paragraph, '_p') and hasattr(paragraph._p, 'pPr'):
            pPr = paragraph._p.pPr
            
            # Check for indentation in XML
            if hasattr(pPr, 'ind'):
                ind = pPr.ind
                
                # Extract left indent value
                if hasattr(ind, 'left') and ind.left:
                    try:
                        xml_values['left_twips'] = ind.left.val
                        xml_values['left_cm'] = f"{float(ind.left.val) / 567:.2f}"  # Convert twips to cm
                    except (AttributeError, TypeError):
                        xml_values['left_twips'] = str(ind.left)
                
                # Extract first line indent value
                if hasattr(ind, 'firstLine') and ind.firstLine:
                    try:
                        xml_values['first_line_twips'] = ind.firstLine.val
                        xml_values['first_line_cm'] = f"{float(ind.firstLine.val) / 567:.2f}"  # Convert twips to cm
                    except (AttributeError, TypeError):
                        xml_values['first_line_twips'] = str(ind.firstLine)
                
                # Extract hanging indent value
                if hasattr(ind, 'hanging') and ind.hanging:
                    try:
                        xml_values['hanging_twips'] = ind.hanging.val
                        xml_values['hanging_cm'] = f"{float(ind.hanging.val) / 567:.2f}"  # Convert twips to cm
                    except (AttributeError, TypeError):
                        xml_values['hanging_twips'] = str(ind.hanging)
                    
            # Check for spacing in XML
            if hasattr(pPr, 'spacing'):
                spacing = pPr.spacing
                
                # Extract before spacing
                if hasattr(spacing, 'before') and spacing.before:
                    # Handle Twips objects
                    try:
                        # Get the twips value - different versions of python-docx store it differently
                        before_twips = spacing.before.val if hasattr(spacing.before, 'val') else int(spacing.before)
                        xml_values['before_twips'] = before_twips
                        xml_values['before_pt'] = f"{float(before_twips) / 20:.2f}"  # Convert twips to points
                    except (AttributeError, TypeError):
                        # Fall back to string representation
                        xml_values['before_twips'] = str(spacing.before)
                
                # Extract after spacing
                if hasattr(spacing, 'after') and spacing.after:
                    # Handle Twips objects
                    try:
                        # Get the twips value - different versions of python-docx store it differently
                        after_twips = spacing.after.val if hasattr(spacing.after, 'val') else int(spacing.after)
                        xml_values['after_twips'] = after_twips
                        xml_values['after_pt'] = f"{float(after_twips) / 20:.2f}"  # Convert twips to points
                    except (AttributeError, TypeError):
                        # Fall back to string representation
                        xml_values['after_twips'] = str(spacing.after)
        
        # Check for style-defined indentation if direct formatting is "None"
        if left_indent == "None" and paragraph.style:
            style_fmt = paragraph.style.paragraph_format
            try:
                style_left_indent = style_fmt.left_indent.cm if style_fmt.left_indent else "None"
            except (AttributeError, TypeError):
                style_left_indent = str(style_fmt.left_indent) if style_fmt.left_indent else "None"
                
            try:
                style_first_line_indent = style_fmt.first_line_indent.cm if style_fmt.first_line_indent else "None"
            except (AttributeError, TypeError):
                style_first_line_indent = str(style_fmt.first_line_indent) if style_fmt.first_line_indent else "None"
                
            xml_values['style_left_indent_cm'] = style_left_indent
            xml_values['style_first_line_indent_cm'] = style_first_line_indent
        
        # Check for numbering (bullets)
        has_numbering = False
        numbering_id = None
        
        if hasattr(paragraph._p, 'pPr') and paragraph._p.pPr is not None:
            if hasattr(paragraph._p.pPr, 'numPr') and paragraph._p.pPr.numPr is not None:
                has_numbering = True
                if hasattr(paragraph._p.pPr.numPr, 'numId') and paragraph._p.pPr.numPr.numId is not None:
                    numbering_id = paragraph._p.pPr.numPr.numId.val
        
        # Determine if the paragraph is bold
        is_bold = False
        for run in paragraph.runs:
            if run.bold:
                is_bold = True
                break
        
        # Determine if the paragraph is italic
        is_italic = False
        for run in paragraph.runs:
            if run.italic:
                is_italic = True
                break
                
        result = {
            "index": i,
            "text": text,
            "style": style_name,
            "bold": is_bold,
            "italic": is_italic,
            "left_indent": left_indent,
            "first_line_indent": first_line_indent,
            "has_numbering": has_numbering,
            "numbering_id": numbering_id,
            "xml_values": xml_values
        }
        
        # Log key information with enhanced details
        log_message = f"Paragraph {i}: '{text}' | Style: {style_name}"
        
        # Add formatting info to log message
        if left_indent != "None" or 'left_cm' in xml_values:
            log_message += f" | Left indent: {left_indent if left_indent != 'None' else xml_values.get('left_cm', 'None')}"
        elif 'style_left_indent_cm' in xml_values and xml_values['style_left_indent_cm'] != "None":
            log_message += f" | Style Left indent: {xml_values['style_left_indent_cm']}"
            
        if first_line_indent != "None" or 'first_line_cm' in xml_values or 'hanging_cm' in xml_values:
            indent_value = first_line_indent
            if indent_value == "None":
                if 'first_line_cm' in xml_values:
                    indent_value = xml_values['first_line_cm']
                elif 'hanging_cm' in xml_values:
                    indent_value = f"-{xml_values['hanging_cm']}"
            log_message += f" | First line indent: {indent_value}"
        elif 'style_first_line_indent_cm' in xml_values and xml_values['style_first_line_indent_cm'] != "None":
            log_message += f" | Style First line indent: {xml_values['style_first_line_indent_cm']}"
            
        log_message += f" | Has numbering: {has_numbering}"
        
        logger.info(log_message)
        
        results.append(result)
    
    logger.info(f"Inspected {len(results)} paragraphs")
    return results

def inspect_docx_styles(document):
    """
    Inspect all paragraph styles in a document and log their properties.
    
    Args:
        document: A python-docx Document object
        
    Returns:
        A list of dictionaries containing style information
    """
    results = []
    
    logger.info("Inspecting document styles...")
    
    for style in document.styles:
        # Skip styles that aren't paragraph styles
        if not hasattr(style, 'paragraph_format'):
            continue
            
        style_name = style.name
        base_style = style.base_style.name if style.base_style else "None"
        
        # Get paragraph format properties
        fmt = style.paragraph_format
        
        # Extract indentation values, handling possible Twips objects
        try:
            left_indent = fmt.left_indent.cm if fmt.left_indent else None
        except (AttributeError, TypeError):
            left_indent = str(fmt.left_indent) if fmt.left_indent else None
            
        try:
            first_line_indent = fmt.first_line_indent.cm if fmt.first_line_indent else None
        except (AttributeError, TypeError):
            first_line_indent = str(fmt.first_line_indent) if fmt.first_line_indent else None
        
        # Log style information
        logger.info(f"Style: {style_name} | Base: {base_style} | Left indent: {left_indent} | First line indent: {first_line_indent}")
        
        result = {
            "name": style_name,
            "base_style": base_style,
            "left_indent": left_indent,
            "first_line_indent": first_line_indent,
        }
        
        # Add additional properties if they exist
        if hasattr(fmt, 'space_before') and fmt.space_before:
            try:
                result["space_before_pt"] = fmt.space_before.pt
            except (AttributeError, TypeError):
                result["space_before_pt"] = str(fmt.space_before)
            
        if hasattr(fmt, 'space_after') and fmt.space_after:
            try:
                result["space_after_pt"] = fmt.space_after.pt
            except (AttributeError, TypeError):
                result["space_after_pt"] = str(fmt.space_after)
            
        if hasattr(style, 'font'):
            if hasattr(style.font, 'name') and style.font.name:
                result["font_name"] = style.font.name
                
            if hasattr(style.font, 'size') and style.font.size:
                try:
                    result["font_size_pt"] = style.font.size.pt
                except (AttributeError, TypeError):
                    result["font_size_pt"] = str(style.font.size)
                
            if hasattr(style.font, 'bold'):
                result["bold"] = style.font.bold
                
            if hasattr(style.font, 'italic'):
                result["italic"] = style.font.italic
            
        results.append(result)
    
    logger.info(f"Inspected {len(results)} paragraph styles")
    return results

def generate_debug_report(document):
    """
    Generate a comprehensive debug report for a DOCX document.
    
    Args:
        document: A python-docx Document object
        
    Returns:
        A dictionary containing paragraph and style information
    """
    return {
        "paragraphs": inspect_docx_paragraphs(document),
        "styles": inspect_docx_styles(document)
    }

def create_debug_script():
    """
    Returns a Python script that can be used to debug a DOCX file.
    Useful for copying into a temporary script file.
    """
    return """
import os
import json
from docx import Document
from utils.docx_debug import inspect_docx_paragraphs, inspect_docx_styles

# Path to DOCX file to inspect
docx_path = 'debug_output.docx'  # Change this to your file path

# Load and inspect
doc = Document(docx_path)
para_info = inspect_docx_paragraphs(doc)
style_info = inspect_docx_styles(doc)

# Save debug info
with open('docx_debug_paragraphs.json', 'w') as f:
    json.dump(para_info, f, indent=2)
    
with open('docx_debug_styles.json', 'w') as f:
    json.dump(style_info, f, indent=2)

print('Debug files created: docx_debug_paragraphs.json, docx_debug_styles.json')
""" 