"""
Style Registry for Word Documents

This module provides a centralized registry for Word paragraph styles,
with a focus on properly handling boxed headers and spacing.

The style registry ensures consistent application of styles and prevents
duplicate style definitions in the document.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Tuple, Any

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn

from .xml_utils import (
    make_spacing_node, 
    make_border_node, 
    make_outline_level_node,
    make_compatibility_node,
    twips_from_pt
)

logger = logging.getLogger(__name__)

@dataclass
class ParagraphBoxStyle:
    """
    Dataclass representing a paragraph style with box styling capabilities.
    
    This provides a centralized definition of all styling attributes for a 
    paragraph, including borders, spacing, and outline level.
    """
    name: str
    base_style_name: str = "Normal"
    outline_level: Optional[int] = None
    
    # Font properties
    font_name: str = "Calibri"
    font_size_pt: float = 11.0
    font_bold: bool = False
    font_italic: bool = False
    font_color: str = "000000"  # Black
    
    # Border properties
    border_width_pt: float = 1.0
    border_color: str = "000000"  # Black
    border_style: str = "single"
    border_padding_pt: float = 1.0
    
    # Spacing properties
    space_before_pt: float = 0.0
    space_after_pt: float = 6.0
    line_rule: str = "auto"
    line_height_pt: Optional[float] = 13.8  # 276 twips
    
    # Paragraph properties
    keep_with_next: bool = False
    keep_lines: bool = False
    page_break_before: bool = False
    widow_control: bool = False
    
    # Flag to indicate if borders should be applied
    has_border: bool = False


class StyleRegistry:
    """
    Registry of paragraph styles for Word documents.
    
    This class manages a collection of paragraph styles and provides methods
    to create, retrieve, and apply them to a document.
    """
    
    def __init__(self):
        """Initialize the style registry with pre-defined styles."""
        self._styles: Dict[str, ParagraphBoxStyle] = {}
        
        # Register default styles
        self._register_default_styles()
    
    def _register_default_styles(self):
        """Register default paragraph styles."""
        # BoxedHeading2 - Section header with border
        self.register(ParagraphBoxStyle(
            name="BoxedHeading2",
            base_style_name="Heading 2",
            outline_level=1,  # Level 2 heading (0=Heading 1, 1=Heading 2)
            font_name="Calibri",
            font_size_pt=14.0,
            font_bold=True,
            font_color="0D2B7E",  # Navy blue
            border_width_pt=1.0,
            border_color="0D2B7E",  # Match font color
            border_style="single",
            border_padding_pt=1.0,  # 20 twips
            space_before_pt=0.0,
            space_after_pt=4.0,
            line_rule="exact",
            line_height_pt=15.0,  # 14pt font + 1pt extra = 15pt (300 twips)
            keep_with_next=True,
            has_border=True
        ))
        
        # ContentParagraph - Regular content paragraph
        self.register(ParagraphBoxStyle(
            name="ContentParagraph",
            base_style_name="Normal",
            font_name="Calibri",
            font_size_pt=11.0,
            space_before_pt=0.0,
            space_after_pt=6.0,
            line_rule="auto",
            has_border=False
        ))
        
        # EmptyParagraph - Used as a spacer with minimal height
        self.register(ParagraphBoxStyle(
            name="EmptyParagraph",
            base_style_name="Normal",
            font_size_pt=1.0,
            space_before_pt=0.0, 
            space_after_pt=0.0,
            line_rule="exact",
            line_height_pt=1.0,  # Minimal height
            has_border=False
        ))
    
    def register(self, style: ParagraphBoxStyle):
        """
        Register a paragraph style in the registry.
        
        Args:
            style: The ParagraphBoxStyle to register
        """
        self._styles[style.name] = style
        logger.info(f"Registered style '{style.name}' in registry")
    
    def get(self, style_name: str) -> Optional[ParagraphBoxStyle]:
        """
        Retrieve a style from the registry by name.
        
        Args:
            style_name: Name of the style to retrieve
            
        Returns:
            The style if found, None otherwise
        """
        return self._styles.get(style_name)
    
    def apply_compatibility_settings(self, doc: Document):
        """
        Apply Word compatibility settings to the document.
        
        Args:
            doc: The document to update
        """
        # Add compatibility settings to settings.xml
        try:
            settings = doc._part.get_or_add_settings()
            compat = settings.xpath('./w:compat')
            
            # Remove existing compatibility settings to avoid duplicates
            for existing in compat:
                settings.remove(existing)
            
            # Add new compatibility settings
            settings.append(make_compatibility_node())
            logger.info("Applied Word compatibility settings")
        except Exception as e:
            logger.error(f"Failed to apply compatibility settings: {e}")


# Singleton instance of the style registry
_registry = StyleRegistry()

def get_or_create_style(style_name: str, doc: Document) -> str:
    """
    Get or create a paragraph style in the document.
    
    This function retrieves a style from the registry and creates it in the
    document if it doesn't already exist. If the style exists in the document,
    it returns its name without modification.
    
    Args:
        style_name: Name of the style to retrieve or create
        doc: Document to create the style in
        
    Returns:
        Name of the style (existing or newly created)
    """
    # Check if style exists in registry
    style_def = _registry.get(style_name)
    if not style_def:
        logger.warning(f"Style '{style_name}' not found in registry, using 'Normal'")
        return "Normal"
    
    # Check if style already exists in document
    if style_name in doc.styles:
        logger.info(f"Style '{style_name}' already exists in document")
        return style_name
    
    # Create style
    try:
        # Check if base style exists
        if style_def.base_style_name not in doc.styles:
            logger.warning(f"Base style '{style_def.base_style_name}' not found, using 'Normal'")
            base_style_name = "Normal"
        else:
            base_style_name = style_def.base_style_name
        
        # Add style to document
        style = doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = doc.styles[base_style_name]
        
        # Set font properties
        font = style.font
        font.name = style_def.font_name
        font.size = Pt(style_def.font_size_pt)
        font.bold = style_def.font_bold
        font.italic = style_def.font_italic
        
        # Set color
        r, g, b = int(style_def.font_color[0:2], 16), int(style_def.font_color[2:4], 16), int(style_def.font_color[4:6], 16)
        font.color.rgb = RGBColor(r, g, b)
        
        # Set paragraph properties
        para_format = style.paragraph_format
        para_format.space_before = Pt(style_def.space_before_pt)
        para_format.space_after = Pt(style_def.space_after_pt)
        para_format.keep_with_next = style_def.keep_with_next
        para_format.keep_together = style_def.keep_lines
        para_format.page_break_before = style_def.page_break_before
        para_format.widow_control = style_def.widow_control
        
        # Get element for XML manipulation
        style_element = style._element
        
        # Set outline level if specified
        if style_def.outline_level is not None:
            p_pr = style_element.get_or_add_pPr()
            
            # Remove any existing outline level
            for existing in p_pr.xpath('./w:outlineLvl'):
                p_pr.remove(existing)
            
            # Add outline level
            p_pr.append(make_outline_level_node(style_def.outline_level))
        
        # Set spacing via XML for more precise control
        p_pr = style_element.get_or_add_pPr()
        
        # Remove any existing spacing to avoid conflicts
        for existing in p_pr.xpath('./w:spacing'):
            p_pr.remove(existing)
        
        # Prepare line spacing values
        line_twips = None
        if style_def.line_height_pt is not None:
            line_twips = twips_from_pt(style_def.line_height_pt)
        
        # Add spacing node
        spacing_node = make_spacing_node(
            before=twips_from_pt(style_def.space_before_pt),
            after=twips_from_pt(style_def.space_after_pt),
            line=line_twips,
            line_rule=style_def.line_rule
        )
        p_pr.append(spacing_node)
        
        # Apply borders if specified
        if style_def.has_border:
            # Remove any existing borders
            for existing in p_pr.xpath('./w:pBdr'):
                p_pr.remove(existing)
            
            # Add border node
            border_node = make_border_node(
                width_pt=style_def.border_width_pt,
                color=style_def.border_color,
                style=style_def.border_style,
                padding_pt=style_def.border_padding_pt
            )
            p_pr.append(border_node)
        
        logger.info(f"Created style '{style_name}' in document")
        return style_name
    
    except Exception as e:
        logger.error(f"Failed to create style '{style_name}': {e}")
        import traceback
        logger.error(traceback.format_exc())
        return "Normal"  # Fallback

def apply_direct_paragraph_formatting(paragraph, style_name: str):
    """
    Apply direct formatting to a paragraph based on a registered style.
    
    This is useful when you want to apply the formatting properties of a style
    directly to a paragraph, without changing its actual style.
    
    Args:
        paragraph: The paragraph to format
        style_name: Name of the registered style to apply
        
    Returns:
        The formatted paragraph
    """
    # Check if style exists in registry
    style_def = _registry.get(style_name)
    if not style_def:
        logger.warning(f"Style '{style_name}' not found in registry")
        return paragraph
    
    try:
        # Apply direct formatting to runs
        for run in paragraph.runs:
            run.font.name = style_def.font_name
            run.font.size = Pt(style_def.font_size_pt)
            run.font.bold = style_def.font_bold
            run.font.italic = style_def.font_italic
            
            # Set color
            r, g, b = int(style_def.font_color[0:2], 16), int(style_def.font_color[2:4], 16), int(style_def.font_color[4:6], 16)
            run.font.color.rgb = RGBColor(r, g, b)
        
        # Set paragraph properties
        para_format = paragraph.paragraph_format
        para_format.space_before = Pt(style_def.space_before_pt)
        para_format.space_after = Pt(style_def.space_after_pt)
        para_format.keep_with_next = style_def.keep_with_next
        para_format.keep_together = style_def.keep_lines
        para_format.page_break_before = style_def.page_break_before
        para_format.widow_control = style_def.widow_control
        
        # Get paragraph element for XML manipulation
        p_element = paragraph._element
        p_pr = p_element.get_or_add_pPr()
        
        # Set spacing via XML for more precise control
        # Remove any existing spacing to avoid conflicts
        for existing in p_pr.xpath('./w:spacing'):
            p_pr.remove(existing)
        
        # Prepare line spacing values
        line_twips = None
        if style_def.line_height_pt is not None:
            line_twips = twips_from_pt(style_def.line_height_pt)
        
        # Add spacing node
        spacing_node = make_spacing_node(
            before=twips_from_pt(style_def.space_before_pt),
            after=twips_from_pt(style_def.space_after_pt),
            line=line_twips,
            line_rule=style_def.line_rule
        )
        p_pr.append(spacing_node)
        
        # Apply borders if specified
        if style_def.has_border:
            # Remove any existing borders
            for existing in p_pr.xpath('./w:pBdr'):
                p_pr.remove(existing)
            
            # Add border node
            border_node = make_border_node(
                width_pt=style_def.border_width_pt,
                color=style_def.border_color,
                style=style_def.border_style,
                padding_pt=style_def.border_padding_pt
            )
            p_pr.append(border_node)
        
        logger.info(f"Applied direct formatting from style '{style_name}' to paragraph")
        return paragraph
    
    except Exception as e:
        logger.error(f"Failed to apply direct formatting from style '{style_name}': {e}")
        return paragraph 