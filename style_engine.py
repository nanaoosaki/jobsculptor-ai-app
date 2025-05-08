"""
StyleEngine for Resume Tailor Application

A unified style engine to ensure consistent styling across HTML/CSS, PDF, and DOCX outputs.
"""

import json
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

logger = logging.getLogger(__name__)

class StyleEngine:
    """
    Unified style engine for consistent styling across all output formats.
    Handles token loading, transformation, and application for HTML/CSS, PDF, and DOCX.
    """
    
    @staticmethod
    def load_tokens() -> Dict[str, Any]:
        """Load design tokens from JSON file."""
        try:
            token_path = Path(__file__).parent / 'design_tokens.json'
            with open(token_path, 'r', encoding='utf-8') as f:
                tokens = json.load(f)
            logger.info(f"Successfully loaded design tokens from {token_path}")
            return tokens
        except Exception as e:
            logger.error(f"Error loading design tokens: {e}")
            return {}
    
    @staticmethod
    def get_structured_tokens() -> Dict[str, Any]:
        """
        Convert flat design tokens to a structured format with base and format-specific properties.
        This is a transitional method until the design_tokens.json is restructured.
        """
        tokens = StyleEngine.load_tokens()
        
        # Create structured tokens dictionary
        structured = {
            "sectionHeader": {
                "base": {
                    "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif"),
                    "fontSize": tokens.get("sectionHeaderFontSize", "12pt"),
                    "color": tokens.get("pdfHeaderColor", "rgb(0, 0, 102)"),
                    "marginBottom": tokens.get("sectionMarginBottom", "0.5cm")
                },
                "html": {
                    "backgroundColor": tokens.get("color.sectionBox.bg", "#FFFFFF"),
                    "border": tokens.get("sectionHeaderBorder", "1px solid #0D2B7E"),
                    "paddingVertical": tokens.get("sectionHeaderPaddingVert", "1px"),
                    "paddingHorizontal": tokens.get("sectionHeaderPaddingHoriz", "12px")
                },
                "docx": {
                    "backgroundColor": tokens.get("color.sectionBox.bg", "#FFFFFF"),
                    "borderColor": tokens.get("sectionHeaderBorder", "1px solid #0D2B7E").replace("px solid ", ""),
                    "borderSize": "1pt",
                    "paddingVertical": tokens.get("sectionHeaderPaddingVert", "1px").replace("px", "pt"),
                    "paddingHorizontal": tokens.get("sectionHeaderPaddingHoriz", "12px").replace("px", "pt")
                }
            },
            "bulletPoint": {
                "base": {
                    "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif"),
                    "fontSize": tokens.get("baseFontSize", "11pt"),
                    "symbol": tokens.get("bullet-glyph", "\"\\2022\"").replace("\"", "").replace("\\\\", "\\")
                },
                "html": {
                    "indentation": tokens.get("bullet-list-padding-left", "1.5em"),
                    "itemPadding": tokens.get("bullet-item-padding-left", "1em"),
                    "textIndent": tokens.get("bullet-item-text-indent", "-1em")
                },
                "docx": {
                    "indentationCm": "0.75",
                    "hangingIndentCm": "-0.25"
                }
            }
        }
        
        return structured
    
    @staticmethod
    def generate_scss_variables(tokens: Optional[Dict[str, Any]] = None):
        """Transform tokens to SCSS variables."""
        if tokens is None:
            tokens = StyleEngine.load_tokens()
            
        # Use existing generate_scss_variables function
        try:
            from tools.generate_tokens import generate_scss_variables
            generate_scss_variables()
            logger.info("Successfully generated SCSS variables")
        except Exception as e:
            logger.error(f"Error generating SCSS variables: {e}")
    
    @staticmethod
    def generate_docx_styles(tokens: Optional[Dict[str, Any]] = None):
        """Transform tokens to DOCX styles."""
        if tokens is None:
            tokens = StyleEngine.load_tokens()
            
        # Use existing generate_docx_style_mappings function
        try:
            from tools.generate_tokens import generate_docx_style_mappings
            generate_docx_style_mappings()
            logger.info("Successfully generated DOCX styles")
        except Exception as e:
            logger.error(f"Error generating DOCX styles: {e}")
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        if not hex_color or not isinstance(hex_color, str):
            return (0, 0, 0)
            
        # Handle rgb() format
        if hex_color.startswith("rgb("):
            return tuple(int(x.strip()) for x in hex_color[4:-1].split(","))
        
        # Handle hex format
        hex_color = hex_color.lstrip('#')
        
        # Handle shorthand hex (e.g., #fff)
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
            
        # Ensure we have a valid hex color
        if len(hex_color) != 6:
            return (0, 0, 0)
            
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def create_docx_section_header_style(doc, tokens: Optional[Dict[str, Any]] = None):
        """Create a section header style for DOCX documents."""
        from docx.enum.style import WD_STYLE_TYPE
        from docx.shared import Pt, Cm, RGBColor
        
        try:
            structured_tokens = StyleEngine.get_structured_tokens()
            section_header = structured_tokens.get("sectionHeader", {})
            
            base = section_header.get("base", {})
            docx_specific = section_header.get("docx", {})
            
            # Create the style
            style = doc.styles.add_style('SectionHeader', WD_STYLE_TYPE.PARAGRAPH)
            font = style.font
            
            # Apply base properties
            font_family = base.get("fontFamily", "'Calibri', Arial, sans-serif")
            if "," in font_family:
                font_family = font_family.split(",")[0].strip("'")
            font.name = font_family
            
            font_size = base.get("fontSize", "12pt")
            if "pt" in font_size:
                font_size = float(font_size.replace("pt", ""))
            font.size = Pt(font_size)
            
            color = base.get("color", "rgb(0, 0, 102)")
            rgb_color = StyleEngine.hex_to_rgb(color)
            font.color.rgb = RGBColor(*rgb_color)
            
            # Make section headers bold
            font.bold = True
            
            # Apply DOCX-specific properties for spacing
            margin_bottom = base.get("marginBottom", "0.5cm")
            if "cm" in margin_bottom:
                margin_bottom = float(margin_bottom.replace("cm", ""))
            style.paragraph_format.space_after = Cm(margin_bottom)
            
            # Add specific settings to match HTML/PDF styles
            style.paragraph_format.alignment = 0  # 0 = left alignment
            style.paragraph_format.line_spacing = 1.0
            style.paragraph_format.keep_with_next = True
            
            logger.info("Successfully created DOCX section header style")
            return style
            
        except Exception as e:
            logger.error(f"Error creating DOCX section header style: {e}")
            return None
    
    @staticmethod
    def apply_docx_section_header_box_style(paragraph, tokens: Optional[Dict[str, Any]] = None):
        """Apply box styling to section headers in DOCX."""
        try:
            from docx.oxml.ns import nsdecls
            from docx.oxml import parse_xml
            
            structured_tokens = StyleEngine.get_structured_tokens()
            docx_specific = structured_tokens.get("sectionHeader", {}).get("docx", {})
            
            # Get background color
            bg_color = docx_specific.get("backgroundColor", "#FFFFFF")
            bg_rgb = StyleEngine.hex_to_rgb(bg_color)
            
            # Get border properties
            border_color = docx_specific.get("borderColor", "#0D2B7E")
            border_rgb = StyleEngine.hex_to_rgb(border_color)
            
            border_size = docx_specific.get("borderSize", "1pt")
            if "pt" in border_size:
                border_size_pt = float(border_size.replace("pt", ""))
            else:
                border_size_pt = float(border_size)
            
            # Apply background shading
            hex_bg = f"{bg_rgb[0]:02x}{bg_rgb[1]:02x}{bg_rgb[2]:02x}"
            shading_xml = f'<w:shd {nsdecls("w")} w:fill="{hex_bg}" w:val="clear"/>'
            paragraph._element.get_or_add_pPr().append(parse_xml(shading_xml))
            
            # Apply border
            hex_border = f"{border_rgb[0]:02x}{border_rgb[1]:02x}{border_rgb[2]:02x}"
            border_xml = f'''
                <w:pBdr {nsdecls("w")}>
                    <w:bottom w:val="single" w:sz="{int(border_size_pt*4)}" w:space="0" w:color="{hex_border}"/>
                    <w:top w:val="single" w:sz="{int(border_size_pt*4)}" w:space="0" w:color="{hex_border}"/>
                    <w:left w:val="single" w:sz="{int(border_size_pt*4)}" w:space="0" w:color="{hex_border}"/>
                    <w:right w:val="single" w:sz="{int(border_size_pt*4)}" w:space="0" w:color="{hex_border}"/>
                </w:pBdr>
            '''
            paragraph._element.get_or_add_pPr().append(parse_xml(border_xml))
            
            # Apply padding
            padding_h = docx_specific.get("paddingHorizontal", "12pt")
            padding_v = docx_specific.get("paddingVertical", "1pt")
            
            if "pt" in padding_h:
                padding_h_pt = float(padding_h.replace("pt", ""))
            else:
                padding_h_pt = float(padding_h)
                
            if "pt" in padding_v:
                padding_v_pt = float(padding_v.replace("pt", ""))
            else:
                padding_v_pt = float(padding_v)
            
            # Convert to twips (twentieth of a point)
            padding_left_twips = int(padding_h_pt * 20)
            padding_right_twips = int(padding_h_pt * 20)
            padding_top_twips = int(padding_v_pt * 20)
            padding_bottom_twips = int(padding_v_pt * 20)
            
            # Apply spacing - keep paragraph tight
            spacing_xml = f'''
                <w:spacing {nsdecls("w")} w:before="{padding_top_twips}" 
                w:after="{padding_bottom_twips}" w:line="240" w:lineRule="exact"/>
            '''
            paragraph._element.get_or_add_pPr().append(parse_xml(spacing_xml))
            
            # Apply indentation
            indent_xml = f'''
                <w:ind {nsdecls("w")} w:left="{padding_left_twips}" 
                w:right="{padding_right_twips}"/>
            '''
            paragraph._element.get_or_add_pPr().append(parse_xml(indent_xml))
            
            # Set alignment to left (to match HTML/PDF)
            align_xml = f'''
                <w:jc {nsdecls("w")} w:val="left"/>
            '''
            paragraph._element.get_or_add_pPr().append(parse_xml(align_xml))
            
            # Adjust paragraph properties directly
            paragraph.paragraph_format.space_before = 0
            paragraph.paragraph_format.space_after = 0
            
            logger.info("Successfully applied DOCX section header box styling")
            
        except Exception as e:
            logger.error(f"Error applying DOCX section header box styling: {e}")
    
    @staticmethod
    def create_docx_bullet_style(doc, tokens: Optional[Dict[str, Any]] = None):
        """Create a bullet point style for DOCX documents."""
        from docx.enum.style import WD_STYLE_TYPE
        from docx.shared import Pt, Cm
        
        try:
            structured_tokens = StyleEngine.get_structured_tokens()
            bullet_point = structured_tokens.get("bulletPoint", {})
            
            base = bullet_point.get("base", {})
            docx_specific = bullet_point.get("docx", {})
            
            # Create custom bullet style
            bullet_style = doc.styles.add_style('CustomBullet', WD_STYLE_TYPE.PARAGRAPH)
            font = bullet_style.font
            
            # Apply base properties
            font_family = base.get("fontFamily", "'Calibri', Arial, sans-serif")
            if "," in font_family:
                font_family = font_family.split(",")[0].strip("'")
            font.name = font_family
            
            font_size = base.get("fontSize", "11pt")
            if "pt" in font_size:
                font_size = float(font_size.replace("pt", ""))
            font.size = Pt(font_size)
            
            # Apply DOCX-specific properties
            indent_cm = float(docx_specific.get("indentationCm", "0.75"))
            hanging_cm = float(docx_specific.get("hangingIndentCm", "-0.25"))
            
            # Apply paragraph formatting
            bullet_style.paragraph_format.left_indent = Cm(indent_cm)
            bullet_style.paragraph_format.first_line_indent = Cm(hanging_cm)
            
            logger.info("Successfully created DOCX bullet point style")
            return bullet_style
            
        except Exception as e:
            logger.error(f"Error creating DOCX bullet point style: {e}")
            return None 