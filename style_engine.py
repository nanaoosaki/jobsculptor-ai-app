"""
StyleEngine for Resume Tailor Application

A unified style engine to ensure consistent styling across HTML/CSS, PDF, and DOCX outputs.
"""

import json
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union

from docx.shared import Pt, RGBColor
from docx.oxml.shared import qn
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx import Document
from docx.shared import Cm
import traceback

logger = logging.getLogger(__name__)

class TokenAccessor:
    """
    Utility class for safely accessing nested tokens with fallbacks and warning logging.
    
    This class provides a safe way to access tokens in a nested dictionary structure
    using dot notation, with fallback values if the token doesn't exist. It also logs
    warnings when tokens are missing, but only once per token key to avoid log spam.
    
    Example usage:
        tokens_data = {"sectionHeader": {"border": {"widthPt": 1}}}
        accessor = TokenAccessor(tokens_data)
        
        # Access existing token
        width = accessor.get("sectionHeader.border.widthPt", 0.5)  # Returns 1
        
        # Access missing token with fallback
        color = accessor.get("sectionHeader.border.color", "#000000")  # Returns "#000000" with warning
    """
    
    def __init__(self, tokens_data):
        """
        Initialize with a tokens dictionary.
        
        Args:
            tokens_data: Dictionary containing design tokens
        """
        self.tokens = tokens_data
        self.warnings = set()  # Track warned keys to avoid repetition
    
    def get(self, key_path, default=None):
        """
        Access a token by dot-notation path with fallback.
        
        Args:
            key_path: Dot-separated path to the token (e.g., "sectionHeader.border.widthPt")
            default: Default value to return if token doesn't exist
            
        Returns:
            The token value if found, otherwise the default value
        """
        parts = key_path.split('.')
        current = self.tokens
        
        try:
            for part in parts:
                current = current[part]
            return current
        except (KeyError, TypeError):
            if key_path not in self.warnings:
                logger.warning(f"Missing token: {key_path}, using default: {default}")
                self.warnings.add(key_path)
            return default

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
        Get structured design tokens optimized for component access.
        
        Returns a structured view of design tokens organized by component type
        with format-specific sections (base, html, docx).
        """
        tokens = StyleEngine.load_tokens()
        
        # Check if we have the new typography system
        typography = tokens.get("typography", {})
        
        if typography:
            # Use new unified typography system
            structured = {
                "global": {
                    "margins": {
                        "leftCm": tokens.get("docx-global-left-margin-cm", "2.0"),
                        "rightCm": tokens.get("docx-global-right-margin-cm", "2.0")
                    }
                },
                "sectionHeader": {
                    "base": {
                        "fontFamily": typography.get("fontFamily", {}).get("primary", "'Calibri', Arial, sans-serif"),
                        "fontSize": typography.get("fontSize", {}).get("sectionHeader", "14pt"),
                        "color": StyleEngine.get_typography_font_color(tokens, "headers", "hex"),
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
                        "fontSizePt": typography.get("docx", {}).get("fontSize", {}).get("sectionHeaderPt", 14),
                        "fontFamily": typography.get("fontFamily", {}).get("docxPrimary", "Calibri"),
                        "fontColor": typography.get("docx", {}).get("color", {}).get("headers", "0D2B7E"),
                        "spacingAfterPt": typography.get("docx", {}).get("spacing", {}).get("sectionAfterPt", 4)
                    }
                },
                "content": {
                    "base": {
                        "fontFamily": typography.get("fontFamily", {}).get("primary", "'Calibri', Arial, sans-serif"),
                        "fontSize": typography.get("fontSize", {}).get("body", "11pt"),
                        "color": StyleEngine.get_typography_font_color(tokens, "primary", "hex")
                    },
                    "docx": {
                        "indentCm": tokens.get("docx-company-name-indent-cm", "0"),
                        "fontSizePt": typography.get("docx", {}).get("fontSize", {}).get("bodyPt", 11),
                        "fontFamily": typography.get("fontFamily", {}).get("docxPrimary", "Calibri"),
                        "fontColor": typography.get("docx", {}).get("color", {}).get("primary", "333333"),
                        "spacingPt": typography.get("docx", {}).get("spacing", {}).get("paragraphAfterPt", 0)
                    }
                },
                "roleDescription": {
                    "base": {
                        "fontFamily": typography.get("fontFamily", {}).get("primary", "'Calibri', Arial, sans-serif"),
                        "fontSize": typography.get("fontSize", {}).get("roleDescription", "11pt"),
                        "fontStyle": "italic",
                        "color": StyleEngine.get_typography_font_color(tokens, "primary", "hex")
                    },
                    "docx": {
                        "indentCm": tokens.get("docx-role-description-indent-cm", "0"),
                        "fontSizePt": typography.get("docx", {}).get("fontSize", {}).get("rolePt", 11),
                        "fontFamily": typography.get("fontFamily", {}).get("docxPrimary", "Calibri"),
                        "fontColor": typography.get("docx", {}).get("color", {}).get("primary", "333333"),
                        "spacingPt": typography.get("docx", {}).get("spacing", {}).get("paragraphAfterPt", 0)
                    }
                },
                "bulletPoint": {
                    "base": {
                        "fontFamily": typography.get("fontFamily", {}).get("primary", "'Calibri', Arial, sans-serif"),
                        "fontSize": typography.get("fontSize", {}).get("bulletPoint", "11pt"),
                        "symbol": tokens.get("bullet-glyph", "\"\\2022\"").replace("\"", "").replace("\\\\", "\\"),
                        "color": StyleEngine.get_typography_font_color(tokens, "primary", "hex")
                    },
                    "html": {
                        "indentation": tokens.get("bullet-list-padding-left", "0"),
                        "itemPadding": tokens.get("bullet-item-padding-left", "1em"),
                        "textIndent": tokens.get("bullet-item-text-indent", "-1em")
                    },
                    "docx": {
                        "indentCm": tokens.get("docx-bullet-left-indent-cm", "0"),
                        "hangingIndentCm": tokens.get("docx-bullet-hanging-indent-cm", "0"),
                        "fontSizePt": typography.get("docx", {}).get("fontSize", {}).get("bulletPt", 11),
                        "fontFamily": typography.get("fontFamily", {}).get("docxPrimary", "Calibri"),
                        "fontColor": typography.get("docx", {}).get("color", {}).get("primary", "333333"),
                        "spacingPt": typography.get("docx", {}).get("spacing", {}).get("bulletAfterPt", 0)
                    }
                }
            }
        else:
            # Fallback to legacy system
            structured = {
                "global": {
                    "margins": {
                        "leftCm": tokens.get("docx-global-left-margin-cm", "2.0"),
                        "rightCm": tokens.get("docx-global-right-margin-cm", "2.0")
                    }
                },
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
                        "spacingPt": tokens.get("docx-paragraph-spacing-pt", "0")
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
                        "spacingPt": tokens.get("docx-paragraph-spacing-pt", "0")
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
                        "spacingPt": tokens.get("docx-bullet-spacing-pt", "0")
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
    def get_typography_font_family(tokens: Optional[Dict[str, Any]] = None, format_type: str = "primary") -> str:
        """Get font family for a specific format from typography tokens."""
        if tokens is None:
            tokens = StyleEngine.load_tokens()
        
        typography = tokens.get("typography", {})
        font_families = typography.get("fontFamily", {})
        
        # Map format types to token keys
        format_map = {
            "primary": "primary",
            "docx": "docxPrimary", 
            "web": "webPrimary",
            "fallback": "fallback"
        }
        
        font_key = format_map.get(format_type, "primary")
        font_family = font_families.get(font_key, "'Calibri', Arial, sans-serif")
        
        # For DOCX, return just the primary font name without quotes or fallbacks
        if format_type == "docx" and "," in font_family:
            font_family = font_family.split(",")[0].strip("'\"")
        
        return font_family

    @staticmethod
    def get_typography_font_size(tokens: Optional[Dict[str, Any]] = None, element_type: str = "body", format_type: str = "pt") -> Union[str, int, float]:
        """Get font size for a specific element type from typography tokens."""
        if tokens is None:
            tokens = StyleEngine.load_tokens()
        
        typography = tokens.get("typography", {})
        font_sizes = typography.get("fontSize", {})
        
        # Get base size
        font_size = font_sizes.get(element_type, "11pt")
        
        # For DOCX, check if there are format-specific overrides
        if format_type == "pt":
            docx_sizes = typography.get("docx", {}).get("fontSize", {})
            pt_key = f"{element_type}Pt"
            if pt_key in docx_sizes:
                return docx_sizes[pt_key]
            
            # Convert string size to numeric
            if isinstance(font_size, str) and font_size.endswith("pt"):
                return int(font_size.replace("pt", ""))
        
        return font_size

    @staticmethod
    def get_typography_font_color(tokens: Optional[Dict[str, Any]] = None, color_type: str = "primary", format_type: str = "hex") -> str:
        """Get font color for a specific color type from typography tokens."""
        if tokens is None:
            tokens = StyleEngine.load_tokens()
        
        typography = tokens.get("typography", {})
        font_colors = typography.get("fontColor", {})
        
        # Get base color
        color = font_colors.get(color_type, "#333333")
        
        # Handle new structured color format
        if isinstance(color, dict):
            # New structured format: {"hex": "#333333", "themeColor": "text1"}
            if format_type == "hex":
                color = color.get("hex", "#333333")
            elif format_type == "theme":
                return color.get("themeColor", "")
            elif format_type == "docx":
                # For DOCX, prefer the hex value but check for overrides
                color = color.get("hex", "#333333")
        
        # For DOCX, check if there are format-specific overrides
        if format_type == "docx":
            docx_colors = typography.get("docx", {}).get("color", {})
            if color_type in docx_colors:
                color = "#" + docx_colors[color_type].lstrip("#")
        
        # Ensure we return a string, not a dict
        if isinstance(color, dict):
            color = color.get("hex", "#333333")
        
        return color

    @staticmethod
    def get_typography_font_weight(tokens: Optional[Dict[str, Any]] = None, weight_type: str = "normal") -> int:
        """Get font weight from typography tokens."""
        if tokens is None:
            tokens = StyleEngine.load_tokens()
        
        typography = tokens.get("typography", {})
        font_weights = typography.get("fontWeight", {})
        
        return font_weights.get(weight_type, 400)

    @staticmethod
    def get_typography_line_height(tokens: Optional[Dict[str, Any]] = None, height_type: str = "normal") -> float:
        """Get line height from typography tokens."""
        if tokens is None:
            tokens = StyleEngine.load_tokens()
        
        typography = tokens.get("typography", {})
        line_heights = typography.get("lineHeight", {})
        
        return line_heights.get(height_type, 1.4)

    @staticmethod
    def get_typography_spacing(tokens: Optional[Dict[str, Any]] = None, spacing_type: str = "paragraphAfterPt", format_type: str = "docx") -> int:
        """Get spacing values from typography tokens."""
        if tokens is None:
            tokens = StyleEngine.load_tokens()
        
        typography = tokens.get("typography", {})
        
        if format_type == "docx":
            spacing = typography.get("docx", {}).get("spacing", {})
            return spacing.get(spacing_type, 6)
        elif format_type == "html":
            spacing = typography.get("html", {}).get("spacing", {})
            return spacing.get(spacing_type, "0.15rem")
        
        return 6

    @staticmethod
    def create_docx_custom_styles(doc: Document, design_tokens=None):
        """
        Creates and configures all custom DOCX styles based on design tokens
        and a predefined specification. This version includes robust XML handling
        for specific styles like MR_Company.
        """
        if design_tokens is None:
            design_tokens = StyleEngine.load_tokens()

        try:
            # Corrected path finding for _docx_styles.json
            base_path = Path(__file__).parent
            spec_path = base_path / 'static' / 'styles' / '_docx_styles.json'
            if not spec_path.exists():
                # Fallback for common project structures if static is at root sibling to module
                spec_path = base_path.parent / 'static' / 'styles' / '_docx_styles.json'
                if not spec_path.exists():
                    # Another fallback if script is run from project root and module is in subdir
                    spec_path = Path('.') / 'static' / 'styles' / '_docx_styles.json'

            with open(spec_path, 'r', encoding='utf-8') as f:
                docx_style_spec = json.load(f)
            logger.info(f"Successfully loaded DOCX style specification from {spec_path}")
        except FileNotFoundError:
            logger.error(f"DOCX style specification file could not be found. Looked at: {Path(__file__).parent / 'static' / 'styles' / '_docx_styles.json'} and other fallbacks. Cannot create custom styles.")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from DOCX style specification: {e}")
            return {}

        styles_created = {}
        style_configs_from_spec = docx_style_spec.get("styles", {})

        predefined_style_names = [
            'MR_Name', 'MR_Contact', 'MR_SectionHeader', 'MR_Company', 
            'MR_RoleBox', 'MR_RoleDescription', 'MR_BulletPoint', 
            'MR_SummaryText', 'MR_SkillCategory', 'MR_SkillList',
            'MR_Content' 
        ]

        # Helper function to create and configure a single style
        def _create_and_configure_style(style_name: str, cfg: Dict[str, Any]):
            """Helper to create and configure a single style with robust XML handling for specific styles."""
            try:
                # Create the style
                style = doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
                logger.info(f"✅ Created custom style: {style_name}")
                
                # **ENHANCED HANDLING FOR MR_Company (per O3's advice + design token support)**
                if style_name == "MR_Company":
                    # Step 1: Set base style to 'No Spacing' to inherit 0/0 spacing baseline
                    try:
                        style.base_style = doc.styles['No Spacing']
                        logger.info("✅ MR_Company: Set base_style to 'No Spacing'")
                    except Exception as e:
                        logger.warning(f"⚠️ MR_Company: Could not set base_style to 'No Spacing': {e}")
                    
                    # Step 3: XML-level controls to kill implicit spacing (O3's approach)
                    try:
                        spacing = style._element.get_or_add_pPr().get_or_add_spacing()
                        spacing.set(qn('w:afterLines'), '0')
                        spacing.set(qn('w:contextualSpacing'), '1')
                        logger.info("✅ MR_Company: Set XML w:afterLines=0 and w:contextualSpacing=1")
                    except Exception as e:
                        logger.warning(f"⚠️ MR_Company: XML spacing controls failed: {e}")
                        logger.warning(f"⚠️ Traceback: {traceback.format_exc()}")
                
                # Configure basic properties for all styles
                paragraph_format = style.paragraph_format
                
                # Font properties
                font = style.font
                if "fontFamily" in cfg:
                    font.name = cfg["fontFamily"]
                if "fontSizePt" in cfg:
                    font.size = Pt(cfg["fontSizePt"])
                if "color" in cfg:
                    r, g, b = cfg["color"]
                    font.color.rgb = RGBColor(r, g, b)
                if cfg.get("bold", False):
                    font.bold = True
                if cfg.get("italic", False):
                    font.italic = True
                if cfg.get("allCaps", False):
                    font.all_caps = True
                
                # Paragraph spacing (NOW APPLIES TO ALL STYLES INCLUDING MR_Company)
                # FIX: Remove the hardcoded exclusion of MR_Company to respect design tokens
                if "spaceAfterPt" in cfg:
                    paragraph_format.space_after = Pt(cfg["spaceAfterPt"])
                    logger.info(f"✅ {style_name}: Applied space_after = {cfg['spaceAfterPt']}pt from design tokens")
                if "spaceBeforePt" in cfg:
                    paragraph_format.space_before = Pt(cfg["spaceBeforePt"])
                    logger.info(f"✅ {style_name}: Applied space_before = {cfg['spaceBeforePt']}pt from design tokens")
                
                # Alignment
                alignment = cfg.get("alignment", "left")
                if alignment == "center":
                    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif alignment == "right":
                    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                else:
                    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                # Indentation (✅ o3's FIX: Skip indentation for bullet points to prevent layer conflicts)
                if "indentCm" in cfg and style_name != "MR_BulletPoint":
                    paragraph_format.left_indent = Cm(cfg["indentCm"])
                elif style_name == "MR_BulletPoint":
                    logger.info(f"🚫 Skipped style indentation for {style_name} - letting XML numbering (L-1) control it")
                    
                if "hangingIndentCm" in cfg and style_name != "MR_BulletPoint":
                    paragraph_format.first_line_indent = Cm(-cfg["hangingIndentCm"])
                elif style_name == "MR_BulletPoint":
                    logger.info(f"🚫 Skipped style hanging indent for {style_name} - letting XML numbering (L-1) control it")
                
                # Line spacing
                if "lineHeight" in cfg:
                    paragraph_format.line_spacing = cfg["lineHeight"]
                
                return style
                
            except Exception as e:
                logger.error(f"❌ Failed to create style {style_name}: {e}")
                logger.error(f"❌ Traceback: {traceback.format_exc()}")
                return None

        for style_name in predefined_style_names:
            if style_name in style_configs_from_spec:
                config = style_configs_from_spec[style_name]
                _create_and_configure_style(style_name, config)
            else:
                logger.warning(f"Style '{style_name}' is in predefined_style_names but not found in DOCX style specification. It will not be created.")
        
        final_doc_styles = [s.name for s in doc.styles]
        logger.info(f"Final list of styles in document post-creation: {final_doc_styles}")

        return styles_created
    
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
                
            # Create token accessor for safe nested access
            tokens_access = TokenAccessor(tokens)
                
            # Get border properties from the new token structure
            border_width_pt = tokens_access.get("sectionHeader.border.widthPt", 1)
            border_color = tokens_access.get("sectionHeader.border.color", "#000000")
            border_style = tokens_access.get("sectionHeader.border.style", "single")
            padding_pt = tokens_access.get("sectionHeader.paddingPt", 3)
            spacing_after_pt = tokens_access.get("sectionHeader.spacingAfterPt", 4)
            
            # Strip # prefix from hex color
            border_color = border_color.lstrip('#')
            
            # Apply direct formatting to runs
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(14)  # Default size for section headers
            
            # Set paragraph formatting for consistent spacing
            paragraph.paragraph_format.space_before = Pt(0)
            paragraph.paragraph_format.space_after = Pt(spacing_after_pt)
            paragraph.paragraph_format.line_spacing = 1.0
            paragraph.paragraph_format.left_indent = Cm(0)  # No indent
            paragraph.paragraph_format.first_line_indent = Cm(0)  # No first line indent
            
            # Apply direct XML for spacing to ensure it's applied consistently
            spacing_xml = f'''
            <w:spacing {nsdecls("w")} 
                w:before="0" 
                w:after="{int(spacing_after_pt * 20)}" 
                w:line="276"
                w:lineRule="auto" 
                w:beforeAutospacing="0" 
                w:afterAutospacing="0"/>
            '''
            
            # Apply borders directly using XML
            border_xml = f'''
            <w:pBdr {nsdecls("w")}>
                <w:top w:val="{border_style}" w:sz="{int(border_width_pt * 8)}" w:space="{int(padding_pt * 20)}" w:color="{border_color}"/>
                <w:left w:val="{border_style}" w:sz="{int(border_width_pt * 8)}" w:space="{int(padding_pt * 20)}" w:color="{border_color}"/>
                <w:bottom w:val="{border_style}" w:sz="{int(border_width_pt * 8)}" w:space="{int(padding_pt * 20)}" w:color="{border_color}"/>
                <w:right w:val="{border_style}" w:sz="{int(border_width_pt * 8)}" w:space="{int(padding_pt * 20)}" w:color="{border_color}"/>
            </w:pBdr>
            '''
            
            # Get paragraph properties
            if hasattr(paragraph._p, 'get_or_add_pPr'):
                pPr = paragraph._p.get_or_add_pPr()
                
                # Remove any existing spacing to prevent conflicts
                for existing in pPr.xpath('./w:spacing'):
                    pPr.remove(existing)
                
                # Add new spacing
                pPr.append(parse_xml(spacing_xml))
                
                # Remove any existing borders to prevent conflicts
                for existing in pPr.xpath('./w:pBdr'):
                    pPr.remove(existing)
                
                # Add new borders
                pPr.append(parse_xml(border_xml))
                
                logger.info("Successfully applied DOCX section header box styling")
            else:
                logger.warning("Could not access paragraph properties to apply borders")
                
        except Exception as e:
            logger.error(f"Error applying DOCX section header box style: {e}")
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
    
    @staticmethod
    def create_boxed_heading_style(doc, tokens=None):
        """
        Create a BoxedHeading2 style for section headers with borders on all four sides.
        
        This implementation follows the recommendations from the styling improvements plan:
        1. Uses paragraph borders rather than tables for better:
           - Accessibility (preserve document outline)
           - Copy-paste behavior
           - Style consistency
        
        2. Creates a named style that inherits from Heading 2, maintaining the document hierarchy
           while adding box borders on all sides.
           
        3. Sets the outline level explicitly to ensure proper TOC generation.
        
        4. Uses direct XML manipulation for aspects that aren't exposed through the python-docx API.
        
        The style is created once per document and then applied to all section headers.
        
        Args:
            doc: The DOCX document object
            tokens: Optional design tokens dictionary (loads from file if not provided)
            
        Returns:
            str: The name of the created style ('BoxedHeading2' or fallback 'Heading 2')
        """
        # Import DOCX-specific modules
        from docx.enum.style import WD_STYLE_TYPE
        from docx.shared import Pt, Cm
        from docx.oxml.ns import nsdecls
        from docx.oxml import parse_xml
        
        # Load tokens if not provided
        if not tokens:
            tokens = StyleEngine.load_tokens()
            
        # Create a token accessor for safe nested access
        tokens_access = TokenAccessor(tokens)
        
        # Check if style already exists to avoid ValueError on repeated runs
        if 'BoxedHeading2' in doc.styles:
            logger.info("BoxedHeading2 style already exists, skipping creation")
            return 'BoxedHeading2'
            
        # Create a new style based on Heading 2
        try:
            boxed_heading = doc.styles.add_style('BoxedHeading2', WD_STYLE_TYPE.PARAGRAPH)
            
            # Check if Heading 2 exists, if not, base on Normal
            if 'Heading 2' in doc.styles:
                boxed_heading.base_style = doc.styles['Heading 2']
            else:
                logger.warning("'Heading 2' style not found, basing BoxedHeading2 on 'Normal'")
                boxed_heading.base_style = doc.styles['Normal']
                # Add heading-like properties
                boxed_heading.font.bold = True
                boxed_heading.font.size = Pt(14)
                
            # Set outline level for accessibility and TOC inclusion
            try:
                # Use proper namespace declaration with nsdecls
                outline_xml = f'<w:outlineLvl {nsdecls("w")} w:val="1"/>'
                pPr = boxed_heading._element.get_or_add_pPr()
                
                # Remove any existing outlineLvl to prevent conflicts
                for existing in pPr.xpath('./w:outlineLvl'):
                    pPr.remove(existing)
                    
                pPr.append(parse_xml(outline_xml))
                logger.info("Successfully set outline level for section header")
            except Exception as e:
                logger.warning(f"Could not set outline level: {e}. Document TOC may not work properly.")
            
            # Get token values or use defaults
            border_width_pt = tokens_access.get("sectionHeader.border.widthPt", 1)
            border_color = tokens_access.get("sectionHeader.border.color", "#000000")
            # Strip # prefix from hex color for python-docx
            border_color = border_color.lstrip('#')
            border_style = tokens_access.get("sectionHeader.border.style", "single")
            padding_pt = tokens_access.get("sectionHeader.paddingPt", 1)
            spacing_after_pt = tokens_access.get("sectionHeader.spacingAfterPt", 4)
            
            # Set spacing properties for the paragraph format
            # Set space before to 0 to eliminate unwanted spacing
            boxed_heading.paragraph_format.space_before = Pt(0)
            boxed_heading.paragraph_format.space_after = Pt(spacing_after_pt)
            
            # Set single line spacing (1.0) - using direct assignment instead of WD_LINE_SPACING enum
            # boxed_heading.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE # This import doesn't exist
            boxed_heading.paragraph_format.line_spacing = 1.0 # Value for SINGLE line spacing

            # Apply explicit XML for spacing control with auto spacing disabled
            # Using lineRule="auto" for optimal box height, removing w:line attribute
            spacing_xml = f'''
            <w:spacing {nsdecls("w")} 
                w:before="0" 
                w:after="{int(spacing_after_pt * 20)}" 
                w:line="276"
                w:lineRule="auto" 
                w:beforeAutospacing="0" 
                w:afterAutospacing="0"/>
            '''
            
            # Get or create paragraph properties
            pPr = boxed_heading._element.get_or_add_pPr()
            
            # Remove any existing spacing to prevent conflicts
            for existing in pPr.xpath('./w:spacing'):
                pPr.remove(existing)
                
            # Add new spacing
            pPr.append(parse_xml(spacing_xml))
            
            # Apply border to the style using XML with proper namespace declaration
            border_xml = f'''
            <w:pBdr {nsdecls("w")}>
                <w:top w:val="{border_style}" w:sz="{int(border_width_pt * 8)}" w:space="20" w:color="{border_color}"/>
                <w:left w:val="{border_style}" w:sz="{int(border_width_pt * 8)}" w:space="20" w:color="{border_color}"/>
                <w:bottom w:val="{border_style}" w:sz="{int(border_width_pt * 8)}" w:space="20" w:color="{border_color}"/>
                <w:right w:val="{border_style}" w:sz="{int(border_width_pt * 8)}" w:space="20" w:color="{border_color}"/>
            </w:pBdr>
            '''
            
            # Remove any existing borders to prevent conflicts
            for existing in pPr.xpath('./w:pBdr'):
                pPr.remove(existing)
                
            # Add new border
            pPr.append(parse_xml(border_xml))
            
            logger.info("Successfully created BoxedHeading2 style with borders")
            return 'BoxedHeading2'
            
        except Exception as e:
            logger.error(f"Failed to apply BoxedHeading2 style: {e}")
            # Default to regular heading if style creation fails
            logger.warning("Using regular 'Heading 2' style as fallback")
            return 'Heading 2'
            
    @staticmethod
    def apply_boxed_section_header_style(doc, paragraph, tokens=None):
        """
        Apply the BoxedHeading2 style to a section header paragraph.
        
        This method ensures that the BoxedHeading2 style exists in the document
        and then applies it to the provided paragraph. It also sets additional
        paragraph formatting properties for consistent spacing.
        
        This is the preferred method for applying box styling to section headers
        as it leverages a named style which preserves document structure and
        accessibility features like outline levels.
        
        If the BoxedHeading2 style application fails, it will fall back to direct
        paragraph formatting using apply_docx_section_header_box_style.
        
        Args:
            doc: The DOCX document object
            paragraph: The paragraph to style as a section header with box
            tokens: Optional design tokens dictionary (loads from file if not provided)
            
        Returns:
            The styled paragraph
        """
        # Import required modules
        from docx.shared import Pt
        from docx.oxml.ns import nsdecls
        from docx.oxml import parse_xml
        
        # Load tokens if not provided
        if not tokens:
            tokens = StyleEngine.load_tokens()
            
        # Create token accessor
        tokens_access = TokenAccessor(tokens)
        
        try:
            # Ensure the style exists in the document
            style_name = StyleEngine.create_boxed_heading_style(doc, tokens)
            
            # Apply the style to the paragraph
            paragraph.style = style_name
            
            # Get spacing values from tokens
            spacing_after_pt = tokens_access.get("sectionHeader.spacingAfterPt", 4)
            
            # Set paragraph formatting explicitly to override any base style issues
            paragraph.paragraph_format.space_before = Pt(0)
            paragraph.paragraph_format.space_after = Pt(spacing_after_pt)

            # Apply direct XML for spacing to ensure it's applied consistently
            # Using lineRule="auto", removing w:line attribute
            spacing_xml = f'''
            <w:spacing {nsdecls("w")} 
                w:before="0" 
                w:after="{int(spacing_after_pt * 20)}" 
                w:line="276"
                w:lineRule="auto" 
                w:beforeAutospacing="0" 
                w:afterAutospacing="0"/>
            '''
            
            # Get paragraph properties
            p_pr = paragraph._element.get_or_add_pPr()
            
            # Remove any existing spacing to prevent conflicts
            for existing in p_pr.xpath('./w:spacing'):
                p_pr.remove(existing)
                
            # Add new spacing
            p_pr.append(parse_xml(spacing_xml))
            
            # Get border values from tokens
            border_width_pt = tokens_access.get("sectionHeader.border.widthPt", 1)
            border_color = tokens_access.get("sectionHeader.border.color", "#000000")
            # Strip # prefix from hex color for python-docx
            border_color = border_color.lstrip('#')
            border_style = tokens_access.get("sectionHeader.border.style", "single")
            
            # Apply borders to the paragraph element directly
            border_xml = f'''
            <w:pBdr {nsdecls("w")}>
                <w:top w:val="{border_style}" w:sz="{int(border_width_pt * 8)}" w:space="20" w:color="{border_color}"/>
                <w:left w:val="{border_style}" w:sz="{int(border_width_pt * 8)}" w:space="20" w:color="{border_color}"/>
                <w:bottom w:val="{border_style}" w:sz="{int(border_width_pt * 8)}" w:space="20" w:color="{border_color}"/>
                <w:right w:val="{border_style}" w:sz="{int(border_width_pt * 8)}" w:space="20" w:color="{border_color}"/>
            </w:pBdr>
            '''
            
            # Remove any existing borders to prevent conflicts
            for existing in p_pr.xpath('./w:pBdr'):
                p_pr.remove(existing)
                
            # Add borders directly to the paragraph
            p_pr.append(parse_xml(border_xml))
            
            logger.info(f"Applied BoxedHeading2 style and direct border to paragraph: '{paragraph.text[:30]}'")
            
            return paragraph
            
        except Exception as e:
            logger.error(f"Failed to apply boxed section header style: {e}")
            # Apply fallback styling if the style application failed
            StyleEngine.apply_docx_section_header_box_style(paragraph, tokens)
            return paragraph 