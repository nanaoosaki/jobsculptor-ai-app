"""
Section Builder for DOCX Documents

This module provides functions to build sections (headers and content)
with proper spacing in DOCX documents.
"""

import logging
from typing import Optional

from docx import Document
from docx.shared import Pt

from .registry import get_or_create_style, apply_direct_paragraph_formatting

logger = logging.getLogger(__name__)

def add_section_header(doc: Document, text: str, style_name: str = "BoxedHeading2") -> None:
    """
    Add a section header with proper styling and spacing.
    
    This function adds a section header with the specified style and ensures
    that there's no unwanted spacing before it. If the previous paragraph is not
    empty, it adds an empty paragraph with zero spacing after.
    
    Args:
        doc: The document to add the section header to
        text: The section header text
        style_name: The name of the style to apply (must be in registry)
    
    Returns:
        The added paragraph
    """
    # Ensure the style exists
    style_name = get_or_create_style(style_name, doc)
    
    # Check if we need to add an empty paragraph first to control spacing
    if len(doc.paragraphs) > 0:
        last_para = doc.paragraphs[-1]
        
        # Only add a spacing control paragraph if the last paragraph is not empty
        if last_para.text.strip():
            # Create an empty paragraph with zero spacing after
            empty_para = doc.add_paragraph()
            empty_para.text = ""
            
            # Apply EmptyParagraph style - very small, no spacing
            empty_style = get_or_create_style("EmptyParagraph", doc)
            empty_para.style = empty_style
            
            # Double-ensure zero spacing after via direct XML
            apply_direct_paragraph_formatting(empty_para, "EmptyParagraph")
            logger.info("Added empty control paragraph before section header")
    
    # Now add the section header
    header_para = doc.add_paragraph()
    header_para.text = text
    
    # Apply the style
    header_para.style = style_name
    
    # Also apply direct formatting to ensure all properties are set
    # This helps with cross-platform compatibility
    apply_direct_paragraph_formatting(header_para, style_name)
    
    logger.info(f"Added section header: {text} with style {style_name}")
    return header_para

def add_content_paragraph(doc: Document, text: str, style_name: str = "ContentParagraph") -> None:
    """
    Add a content paragraph with proper styling and spacing.
    
    Args:
        doc: The document to add the paragraph to
        text: The paragraph text
        style_name: The name of the style to apply (must be in registry)
    
    Returns:
        The added paragraph
    """
    # Ensure the style exists
    style_name = get_or_create_style(style_name, doc)
    
    # Add the paragraph
    para = doc.add_paragraph()
    para.text = text
    
    # Apply the style
    para.style = style_name
    
    # Apply direct formatting to ensure all properties are set
    apply_direct_paragraph_formatting(para, style_name)
    
    logger.info(f"Added content paragraph with style {style_name}")
    return para

def add_bullet_point(doc: Document, text: str, level: int = 0, style_name: str = "ContentParagraph") -> None:
    """
    Add a bullet point with proper styling and spacing.
    
    Args:
        doc: The document to add the bullet point to
        text: The bullet point text
        level: The indentation level (0 = first level)
        style_name: The base style name to apply (will be formatted as bullet)
    
    Returns:
        The added paragraph
    """
    # Ensure the style exists
    style_name = get_or_create_style(style_name, doc)
    
    # Add the paragraph
    para = doc.add_paragraph(style=style_name)
    
    # Apply bullet styling
    para.style = style_name
    para.paragraph_format.left_indent = Pt(18 * (level + 1))  # 18pt per level
    para.paragraph_format.first_line_indent = Pt(-18)  # Hanging indent for bullet
    
    # Add text as a run
    run = para.add_run(text)
    
    # Apply bullet character
    para._p.get_or_add_pPr().get_or_add_numPr()
    
    # Apply direct formatting to ensure all properties are set
    apply_direct_paragraph_formatting(para, style_name)
    
    logger.info(f"Added bullet point with style {style_name}")
    return para

def remove_empty_paragraphs(doc: Document) -> int:
    """
    Remove all empty paragraphs from the document.
    
    Args:
        doc: The document to clean
        
    Returns:
        Number of paragraphs removed
    """
    removed_count = 0
    
    # We need to work backwards since removing elements changes indices
    for i in range(len(doc.paragraphs) - 1, -1, -1):
        para = doc.paragraphs[i]
        
        # Check if paragraph is empty (no text or only whitespace)
        if not para.text.strip():
            # Don't remove if it's the last paragraph (Word needs at least one)
            if i < len(doc.paragraphs) - 1:
                p_element = para._element
                parent = p_element.getparent()
                if parent is not None:
                    parent.remove(p_element)
                    removed_count += 1
    
    logger.info(f"Removed {removed_count} empty paragraphs")
    return removed_count 