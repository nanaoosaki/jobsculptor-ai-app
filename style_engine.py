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
                    "paddingHorizontal": tokens.get("sectionHeaderPaddingHoriz", "12px").replace("px", "pt"),
                    "indentCm": tokens.get("docx-section-header-indent-cm", "0"),
                    "fontSizePt": tokens.get("docx-section-header-font-size-pt", "14")
                }
            },
            "content": {
                "base": {
                    "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif"),
                    "fontSize": tokens.get("baseFontSize", "11pt")
                },
                "docx": {
                    "indentCm": tokens.get("docx-company-name-indent-cm", "0.5"),
                    "fontSizePt": tokens.get("docx-company-font-size-pt", "11"),
                    "spacingPt": tokens.get("docx-paragraph-spacing-pt", "6")
                }
            },
            "roleDescription": {
                "base": {
                    "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif"),
                    "fontSize": tokens.get("baseFontSize", "11pt"),
                    "fontStyle": "italic"
                },
                "docx": {
                    "indentCm": tokens.get("docx-role-description-indent-cm", "0.5"),
                    "fontSizePt": tokens.get("docx-role-font-size-pt", "11"),
                    "spacingPt": tokens.get("docx-paragraph-spacing-pt", "6")
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
                    "indentCm": tokens.get("docx-bullet-left-indent-cm", "0.5"),
                    "hangingIndentCm": tokens.get("docx-bullet-hanging-indent-cm", "0.5"),
                    "fontSizePt": tokens.get("docx-bullet-font-size-pt", "11"),
                    "spacingPt": tokens.get("docx-bullet-spacing-pt", "6")
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
    def create_docx_custom_styles(doc, design_tokens=None):
        """
        Create all custom styles needed for consistent DOCX formatting.
        
        Args:
            doc: The DOCX document
            design_tokens: Optional design tokens dictionary
        
        Returns:
            Dictionary of created styles
        """
        from docx.enum.style import WD_STYLE_TYPE
        from docx.shared import Pt, Cm, RGBColor
        from docx.oxml.ns import nsdecls
        from docx.oxml import parse_xml
        
        if not design_tokens:
            design_tokens = StyleEngine.load_tokens()
        
        structured_tokens = StyleEngine.get_structured_tokens()
        created_styles = {}
        
        try:
            # 1. Create MR_SectionHeader style
            section_tokens = structured_tokens.get("sectionHeader", {})
            section_docx = section_tokens.get("docx", {})
            
            # Check if the style already exists, if so, remove it
            if 'MR_SectionHeader' in [s.name for s in doc.styles]:
                doc.styles['MR_SectionHeader']._element.getparent().remove(doc.styles['MR_SectionHeader']._element)
            
            section_style = doc.styles.add_style('MR_SectionHeader', WD_STYLE_TYPE.PARAGRAPH)
            section_style.font.bold = True
            section_style.font.size = Pt(float(section_docx.get("fontSizePt", 14)))
            
            # Set font name
            font_family = section_tokens.get("base", {}).get("fontFamily", "'Calibri', Arial, sans-serif")
            if "," in font_family:
                font_family = font_family.split(",")[0].strip("'")
            section_style.font.name = font_family
            
            # Set color
            color = section_tokens.get("base", {}).get("color", "rgb(0, 0, 102)")
            rgb_color = StyleEngine.hex_to_rgb(color)
            section_style.font.color.rgb = RGBColor(*rgb_color)
            
            # Make sure there's no indent for section headers
            section_indent_cm = float(section_docx.get("indentCm", 0))
            section_style.paragraph_format.left_indent = Cm(section_indent_cm)
            section_style.paragraph_format.first_line_indent = Cm(0)
            logger.info(f"TESTING: Applied left_indent Cm({section_indent_cm}) to MR_SectionHeader style")
            
            # Set spacing
            section_spacing_pt = float(design_tokens.get("docx-section-spacing-pt", "12"))
            section_style.paragraph_format.space_after = Pt(section_spacing_pt)
            
            # Border and background will be applied directly to the paragraph in docx_builder.py
            # No XML for border or shading in the style definition itself.
            
            created_styles["MR_SectionHeader"] = section_style
            
            # 2. Create MR_Content style
            content_tokens = structured_tokens.get("content", {})
            content_docx = content_tokens.get("docx", {})
            
            # Check if the style already exists, if so, remove it
            if 'MR_Content' in [s.name for s in doc.styles]:
                doc.styles['MR_Content']._element.getparent().remove(doc.styles['MR_Content']._element)
                
            content_style = doc.styles.add_style('MR_Content', WD_STYLE_TYPE.PARAGRAPH)
            content_style.font.size = Pt(float(content_docx.get("fontSizePt", 11)))
            
            # Set font name
            font_family = content_tokens.get("base", {}).get("fontFamily", "'Calibri', Arial, sans-serif")
            if "," in font_family:
                font_family = font_family.split(",")[0].strip("'")
            content_style.font.name = font_family
            
            # Set indentation and spacing
            indent_cm = float(content_docx.get("indentCm", 0.5))
            spacing_pt = float(content_docx.get("spacingPt", 6))
            
            content_style.paragraph_format.left_indent = Cm(indent_cm)
            content_style.paragraph_format.first_line_indent = Cm(0)  # Ensure no first line indent
            content_style.paragraph_format.space_after = Pt(spacing_pt)
            logger.info(f"TESTING: Applied left_indent Cm({indent_cm}) to MR_Content style")
            
            # Removed direct XML styling for indentation and spacing
            
            created_styles["MR_Content"] = content_style
            
            # 3. Create MR_RoleDescription style
            role_tokens = structured_tokens.get("roleDescription", {})
            role_docx = role_tokens.get("docx", {})
            
            # Check if the style already exists, if so, remove it
            if 'MR_RoleDescription' in [s.name for s in doc.styles]:
                doc.styles['MR_RoleDescription']._element.getparent().remove(doc.styles['MR_RoleDescription']._element)
                
            role_style = doc.styles.add_style('MR_RoleDescription', WD_STYLE_TYPE.PARAGRAPH)
            role_style.font.size = Pt(float(role_docx.get("fontSizePt", 11)))
            role_style.font.italic = True
            
            # Set font name
            font_family = role_tokens.get("base", {}).get("fontFamily", "'Calibri', Arial, sans-serif")
            if "," in font_family:
                font_family = font_family.split(",")[0].strip("'")
            role_style.font.name = font_family
            
            # Set indentation and spacing
            indent_cm = float(role_docx.get("indentCm", 0.5))
            spacing_pt = float(role_docx.get("spacingPt", 6))
            
            role_style.paragraph_format.left_indent = Cm(indent_cm)
            role_style.paragraph_format.first_line_indent = Cm(0)  # Ensure no first line indent
            role_style.paragraph_format.space_after = Pt(spacing_pt)
            logger.info(f"TESTING: Applied left_indent Cm({indent_cm}) to MR_RoleDescription style")
            
            # Removed direct XML styling for indentation and spacing
            
            created_styles["MR_RoleDescription"] = role_style
            
            # 4. Create MR_BulletPoint style
            bullet_tokens = structured_tokens.get("bulletPoint", {})
            bullet_docx = bullet_tokens.get("docx", {})
            
            # Check if the style already exists, if so, remove it
            if 'MR_BulletPoint' in [s.name for s in doc.styles]:
                doc.styles['MR_BulletPoint']._element.getparent().remove(doc.styles['MR_BulletPoint']._element)
                
            bullet_style = doc.styles.add_style('MR_BulletPoint', WD_STYLE_TYPE.PARAGRAPH)
            bullet_style.font.size = Pt(float(bullet_docx.get("fontSizePt", 11)))
            
            # Set font name
            font_family = bullet_tokens.get("base", {}).get("fontFamily", "'Calibri', Arial, sans-serif")
            if "," in font_family:
                font_family = font_family.split(",")[0].strip("'")
            bullet_style.font.name = font_family
            
            # Set indentation and spacing
            indent_cm = float(bullet_docx.get("indentCm", 0.5))
            hanging_cm = float(bullet_docx.get("hangingIndentCm", 0.5)) # This should be positive for hanging
            spacing_pt = float(bullet_docx.get("spacingPt", 6))
            
            bullet_style.paragraph_format.left_indent = Cm(indent_cm)
            bullet_style.paragraph_format.first_line_indent = Cm(-hanging_cm) # Negative for hanging
            bullet_style.paragraph_format.space_after = Pt(spacing_pt)
            logger.info(f"TESTING: Applied left_indent Cm({indent_cm}) with first_line_indent Cm({-hanging_cm}) to MR_BulletPoint style")
            
            # Removed direct XML styling for indentation and spacing
            
            created_styles["MR_BulletPoint"] = bullet_style
            
            # 5. Create MR_SummaryText style
            # Check if the style already exists, if so, remove it
            if 'MR_SummaryText' in [s.name for s in doc.styles]:
                doc.styles['MR_SummaryText']._element.getparent().remove(doc.styles['MR_SummaryText']._element)
                
            summary_style = doc.styles.add_style('MR_SummaryText', WD_STYLE_TYPE.PARAGRAPH)
            summary_style.font.size = Pt(float(content_docx.get("fontSizePt", 11)))
            
            # Set font name
            font_family = content_tokens.get("base", {}).get("fontFamily", "'Calibri', Arial, sans-serif")
            if "," in font_family:
                font_family = font_family.split(",")[0].strip("'")
            summary_style.font.name = font_family
            
            # Set indentation and spacing - use same indent as section header for alignment
            indent_cm = float(section_docx.get("indentCm", 0))
            spacing_pt = float(content_docx.get("spacingPt", 6))
            
            summary_style.paragraph_format.left_indent = Cm(indent_cm)
            summary_style.paragraph_format.first_line_indent = Cm(0)  # Ensure no first line indent
            summary_style.paragraph_format.space_after = Pt(spacing_pt)
            logger.info(f"TESTING: Applied left_indent Cm({indent_cm}) to MR_SummaryText style")
            
            created_styles["MR_SummaryText"] = summary_style
            
            # 6. Create MR_SkillCategory style
            # Check if the style already exists, if so, remove it
            if 'MR_SkillCategory' in [s.name for s in doc.styles]:
                doc.styles['MR_SkillCategory']._element.getparent().remove(doc.styles['MR_SkillCategory']._element)
                
            skill_cat_style = doc.styles.add_style('MR_SkillCategory', WD_STYLE_TYPE.PARAGRAPH)
            skill_cat_style.font.size = Pt(float(content_docx.get("fontSizePt", 11)))
            skill_cat_style.font.bold = True
            
            # Set font name
            font_family = content_tokens.get("base", {}).get("fontFamily", "'Calibri', Arial, sans-serif")
            if "," in font_family:
                font_family = font_family.split(",")[0].strip("'")
            skill_cat_style.font.name = font_family
            
            # Set indentation and spacing - use same indent as section header for alignment
            indent_cm = float(section_docx.get("indentCm", 0))
            spacing_pt = float(content_docx.get("spacingPt", 6))
            
            skill_cat_style.paragraph_format.left_indent = Cm(indent_cm)
            skill_cat_style.paragraph_format.first_line_indent = Cm(0)  # Ensure no first line indent
            skill_cat_style.paragraph_format.space_after = Pt(spacing_pt)
            logger.info(f"TESTING: Applied left_indent Cm({indent_cm}) to MR_SkillCategory style")
            
            created_styles["MR_SkillCategory"] = skill_cat_style
            
            # 7. Create MR_SkillList style
            # Check if the style already exists, if so, remove it
            if 'MR_SkillList' in [s.name for s in doc.styles]:
                doc.styles['MR_SkillList']._element.getparent().remove(doc.styles['MR_SkillList']._element)
                
            skill_list_style = doc.styles.add_style('MR_SkillList', WD_STYLE_TYPE.PARAGRAPH)
            skill_list_style.font.size = Pt(float(content_docx.get("fontSizePt", 11)))
            
            # Set font name
            font_family = content_tokens.get("base", {}).get("fontFamily", "'Calibri', Arial, sans-serif")
            if "," in font_family:
                font_family = font_family.split(",")[0].strip("'")
            skill_list_style.font.name = font_family
            
            # Set indentation and spacing - use same indent as section header for alignment
            indent_cm = float(section_docx.get("indentCm", 0))
            spacing_pt = float(content_docx.get("spacingPt", 6))
            
            skill_list_style.paragraph_format.left_indent = Cm(indent_cm)
            skill_list_style.paragraph_format.first_line_indent = Cm(0)  # Ensure no first line indent
            skill_list_style.paragraph_format.space_after = Pt(spacing_pt)
            logger.info(f"TESTING: Applied left_indent Cm({indent_cm}) to MR_SkillList style")
            
            created_styles["MR_SkillList"] = skill_list_style
            
            logger.info("Successfully created all custom DOCX styles")
            return created_styles
            
        except Exception as e:
            logger.error(f"Error creating custom DOCX styles: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return created_styles
    
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
            
            font_size = docx_specific.get("fontSizePt", base.get("fontSize", "12pt"))
            if "pt" in str(font_size):
                font_size = float(font_size.replace("pt", ""))
            font.size = Pt(font_size)
            
            color = base.get("color", "rgb(0, 0, 102)")
            rgb_color = StyleEngine.hex_to_rgb(color)
            font.color.rgb = RGBColor(*rgb_color)
            
            # Make section headers bold
            font.bold = True
            
            # Apply DOCX-specific properties for spacing
            margin_bottom = base.get("marginBottom", "0.5cm")
            if "cm" in str(margin_bottom):
                margin_bottom = float(margin_bottom.replace("cm", ""))
            style.paragraph_format.space_after = Cm(margin_bottom)
            
            # Apply indentation from tokens
            indent_cm = docx_specific.get("indentCm", "0")
            style.paragraph_format.left_indent = Cm(float(indent_cm))
            
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
            from docx.shared import Cm, Pt
            
            # Load tokens if not provided
            if not tokens:
                tokens = StyleEngine.load_tokens()
                
            # Check if paragraph has direct style setting or is using style reference
            if hasattr(paragraph, 'style') and paragraph.style and paragraph.style.name in ['SectionHeader', 'MR_SectionHeader']:
                # Already using a style - just add the border if needed
                structured = StyleEngine.get_structured_tokens()
                section_header = structured.get("sectionHeader", {})
                docx_specific = section_header.get("docx", {})
                
                # Add border
                border_color = docx_specific.get("borderColor", "#0D2B7E")
                rgb_color = StyleEngine.hex_to_rgb(border_color)
                border_hex = f"{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}"
                border_size = int(float(docx_specific.get("borderSize", "1").replace("pt", "")))
                
                # Apply the border using XML - enhance with more specific border attributes
                border_xml = f'''
                    <w:pBdr {nsdecls("w")}>
                        <w:bottom w:val="single" w:sz="{border_size * 8}" w:space="0" w:color="{border_hex}"/>
                        <w:top w:val="nil"/>
                        <w:left w:val="nil"/>
                        <w:right w:val="nil"/>
                    </w:pBdr>
                '''
                if hasattr(paragraph._p, 'get_or_add_pPr'):
                    # Remove any existing border to prevent conflicts
                    for pPr in paragraph._p.xpath('./w:pPr'):
                        for pBdr in pPr.xpath('./w:pBdr'):
                            pPr.remove(pBdr)
                    # Add the new border
                    paragraph._p.get_or_add_pPr().append(parse_xml(border_xml))
                
                # Set spacing and indentation 
                section_spacing_pt = float(tokens.get("docx-section-spacing-pt", "12"))
                if hasattr(paragraph, 'paragraph_format'):
                    paragraph.paragraph_format.space_after = Pt(section_spacing_pt)
                    
                    # Set indentation from tokens if paragraph has style attribute
                    indent_cm = float(docx_specific.get("indentCm", "0"))
                    paragraph.paragraph_format.left_indent = Cm(indent_cm)
                    
                    # Ensure no first line indent to maintain alignment
                    paragraph.paragraph_format.first_line_indent = Cm(0)
                
                # Add specific XML for indentation to ensure it's applied
                indent_twips = int(indent_cm * 567)  # 567 twips per cm
                ind_xml = f'<w:ind {nsdecls("w")} w:left="{indent_twips}" w:firstLine="0"/>'
                if hasattr(paragraph._p, 'get_or_add_pPr'):
                    # Remove any existing indentation to prevent conflicts
                    for pPr in paragraph._p.xpath('./w:pPr'):
                        for ind in pPr.xpath('./w:ind'):
                            pPr.remove(ind)
                    # Add the new indentation
                    paragraph._p.get_or_add_pPr().append(parse_xml(ind_xml))
                
                # Add background color if specified
                if "backgroundColor" in docx_specific:
                    bg_color = docx_specific.get("backgroundColor", "#FFFFFF")
                    bg_rgb = StyleEngine.hex_to_rgb(bg_color)
                    bg_hex = f"{bg_rgb[0]:02x}{bg_rgb[1]:02x}{bg_rgb[2]:02x}"
                    
                    # Apply shading using XML
                    shading_xml = f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{bg_hex}"/>'
                    if hasattr(paragraph._p, 'get_or_add_pPr'):
                        # Remove any existing shading to prevent conflicts
                        for pPr in paragraph._p.xpath('./w:pPr'):
                            for shd in pPr.xpath('./w:shd'):
                                pPr.remove(shd)
                        # Add the new shading
                        paragraph._p.get_or_add_pPr().append(parse_xml(shading_xml))
                
                # If using a new custom style, don't do anything else (style handles everything)
                if paragraph.style.name == 'MR_SectionHeader':
                    logger.info("Successfully applied DOCX section header box styling with MR_SectionHeader style")
                    return
                    
            # For paragraphs without a style, or with the default style
            # Get the values from design tokens
            section_font_size_pt = float(tokens.get("docx-section-header-font-size-pt", "14"))
            section_indent_cm = float(tokens.get("docx-section-header-indent-cm", "0"))
            section_spacing_pt = float(tokens.get("docx-section-spacing-pt", "12"))
            
            # Apply direct formatting
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(section_font_size_pt)
            
            # Set paragraph formatting
            paragraph.paragraph_format.left_indent = Cm(section_indent_cm)
            paragraph.paragraph_format.first_line_indent = Cm(0)  # Ensure no first line indent
            paragraph.paragraph_format.space_after = Pt(section_spacing_pt)
            
            # Add specific XML for indentation to ensure it's applied
            indent_twips = int(section_indent_cm * 567)  # 567 twips per cm
            ind_xml = f'<w:ind {nsdecls("w")} w:left="{indent_twips}" w:firstLine="0"/>'
            
            # Remove any existing indentation to prevent conflicts
            if hasattr(paragraph._p, 'get_or_add_pPr'):
                for pPr in paragraph._p.xpath('./w:pPr'):
                    for ind in pPr.xpath('./w:ind'):
                        pPr.remove(ind)
                # Add the new indentation
                paragraph._p.get_or_add_pPr().append(parse_xml(ind_xml))
            
            # Add the border with enhanced attributes
            border_color = tokens.get("sectionHeaderBorder", "1px solid #0D2B7E").replace("px solid ", "")
            rgb_color = StyleEngine.hex_to_rgb(border_color)
            border_hex = f"{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}"
            
            # Apply the border using XML with more specific attributes
            border_xml = f'''
                <w:pBdr {nsdecls("w")}>
                    <w:bottom w:val="single" w:sz="8" w:space="0" w:color="{border_hex}"/>
                    <w:top w:val="nil"/>
                    <w:left w:val="nil"/>
                    <w:right w:val="nil"/>
                </w:pBdr>
            '''
            # Remove any existing border to prevent conflicts
            if hasattr(paragraph._p, 'get_or_add_pPr'):
                for pPr in paragraph._p.xpath('./w:pPr'):
                    for pBdr in pPr.xpath('./w:pBdr'):
                        pPr.remove(pBdr)
                # Add the new border
                paragraph._p.get_or_add_pPr().append(parse_xml(border_xml))
            
            # Add background color if specified in design tokens
            struct_tokens = StyleEngine.get_structured_tokens()
            section_header = struct_tokens.get("sectionHeader", {})
            docx_specific = section_header.get("docx", {})
            
            if "backgroundColor" in docx_specific:
                bg_color = docx_specific.get("backgroundColor", "#FFFFFF")
                bg_rgb = StyleEngine.hex_to_rgb(bg_color)
                bg_hex = f"{bg_rgb[0]:02x}{bg_rgb[1]:02x}{bg_rgb[2]:02x}"
                
                # Apply shading using XML
                shading_xml = f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{bg_hex}"/>'
                if hasattr(paragraph._p, 'get_or_add_pPr'):
                    # Remove any existing shading to prevent conflicts
                    for pPr in paragraph._p.xpath('./w:pPr'):
                        for shd in pPr.xpath('./w:shd'):
                            pPr.remove(shd)
                    # Add the new shading
                    paragraph._p.get_or_add_pPr().append(parse_xml(shading_xml))
            
            logger.info("Successfully applied DOCX section header box styling")
        except Exception as e:
            logger.error(f"Error applying DOCX section header box styling: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    @staticmethod
    def create_docx_bullet_style(doc, tokens: Optional[Dict[str, Any]] = None):
        """Create a bullet point style for DOCX documents."""
        from docx.enum.style import WD_STYLE_TYPE
        from docx.shared import Pt, Cm
        
        try:
            structured = StyleEngine.get_structured_tokens()
            bullet_point = structured.get("bulletPoint", {})
            
            base = bullet_point.get("base", {})
            docx_specific = bullet_point.get("docx", {})
            
            # Create the style
            style = doc.styles.add_style('CustomBullet', WD_STYLE_TYPE.PARAGRAPH)
            font = style.font
            
            # Apply base properties
            font_family = base.get("fontFamily", "'Calibri', Arial, sans-serif")
            if "," in font_family:
                font_family = font_family.split(",")[0].strip("'")
            font.name = font_family
            
            # Get font size
            font_size = docx_specific.get("fontSizePt", base.get("fontSize", "11pt"))
            if "pt" in str(font_size):
                font_size = float(font_size.replace("pt", ""))
            font.size = Pt(font_size)
            
            # Apply paragraph formatting
            indentation = float(docx_specific.get("indentCm", "0.75"))
            hanging = float(docx_specific.get("hangingIndentCm", "0.25"))
            
            # Apply indentation
            style.paragraph_format.left_indent = Cm(indentation)
            style.paragraph_format.first_line_indent = Cm(-hanging)
            
            # Apply spacing
            if "spacingPt" in docx_specific:
                style.paragraph_format.space_after = Pt(float(docx_specific.get("spacingPt", "6")))
            
            logger.info("Successfully created DOCX bullet style")
            return style
            
        except Exception as e:
            logger.error(f"Error creating DOCX bullet style: {e}")
            return None 