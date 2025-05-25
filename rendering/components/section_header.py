"""
Universal Section Header Renderer

Single source of truth for section header styling across HTML, PDF, and DOCX formats.
Implements strict token enforcement with JSON schema validation.
"""

from typing import Any, Dict, Optional
import logging
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn

logger = logging.getLogger(__name__)


class SectionHeader:
    """Universal section header - data carrier with format-specific renderers"""
    
    REQUIRED_TOKEN_SCHEMA = {
        "typography": {
            "fontSize": {"sectionHeader": "required"},
            "fontColor": {"headers": {"hex": "required"}},
            "fontFamily": {"primary": "required"},
            "casing": {"sectionHeaders": "required"}
        },
        "sectionHeader": {
            "border": {
                "widthPt": "required", 
                "color": "required"
            },
            "padding": {
                "verticalPt": "required",
                "horizontalPt": "required"
            },
            "background": {"color": "required"}
        }
    }
    
    def __init__(self, tokens: Dict, text: str):
        """
        Initialize section header with design tokens and text
        
        Args:
            tokens: Design tokens dictionary
            text: Header text content
        """
        self.tokens = tokens
        self.text = text
        self._validate_required_tokens()
        logger.debug(f"Created SectionHeader for '{text}' with validated tokens")
    
    def _validate_required_tokens(self):
        """Validate that all required design tokens are present"""
        missing_tokens = []
        
        def check_nested_path(tokens_dict, path_dict, current_path=""):
            for key, value in path_dict.items():
                full_path = f"{current_path}.{key}" if current_path else key
                
                if key not in tokens_dict:
                    missing_tokens.append(full_path)
                    continue
                
                if isinstance(value, dict):
                    if isinstance(tokens_dict[key], dict):
                        check_nested_path(tokens_dict[key], value, full_path)
                    else:
                        missing_tokens.append(full_path)
                elif value == "required" and tokens_dict[key] is None:
                    missing_tokens.append(full_path)
        
        check_nested_path(self.tokens, self.REQUIRED_TOKEN_SCHEMA)
        
        if missing_tokens:
            raise ValueError(f"Required design tokens missing: {', '.join(missing_tokens)}")
    
    def _get_computed_casing(self, text: str) -> str:
        """Apply casing transformation based on design tokens"""
        casing_rule = self.tokens["typography"]["casing"]["sectionHeaders"]
        
        if casing_rule == "uppercase":
            return text.upper()
        elif casing_rule == "lowercase":
            return text.lower()
        else:  # "normal" or any other value
            return text
    
    def to_docx(self, doc) -> Any:
        """Render section header as DOCX paragraph with borders (matches legacy behavior)"""
        # Create paragraph instead of table - this matches what legacy system actually does
        para = doc.add_paragraph()
        para.text = self._get_computed_casing(self.text)
        
        # Apply token-driven paragraph styling
        self._apply_docx_paragraph_styling(para)
        
        logger.info(f"Generated DOCX section header (paragraph-based): '{self.text}' -> '{para.text}'")
        return para
    
    def _apply_docx_paragraph_styling(self, paragraph):
        """Apply paragraph-level styling from design tokens"""
        font_size = self.tokens["typography"]["fontSize"]["sectionHeader"]
        font_color = self.tokens["typography"]["fontColor"]["headers"]["hex"]
        # Use DOCX-specific font name instead of CSS font stack
        # This fixes the serif vs sans serif inconsistency across formats
        font_family = self.tokens["typography"]["fontFamily"]["docxPrimary"]
        border_width = self.tokens["sectionHeader"]["border"]["widthPt"]
        border_color = self.tokens["sectionHeader"]["border"]["color"]
        v_padding = self.tokens["sectionHeader"]["padding"]["verticalPt"]
        h_padding = self.tokens["sectionHeader"]["padding"]["horizontalPt"]
        
        # Extract numeric font size (handle "14pt" format)
        if isinstance(font_size, str) and font_size.endswith('pt'):
            size_value = float(font_size[:-2])
        else:
            size_value = float(font_size)
        
        # Apply text formatting
        run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
        run.font.size = Pt(size_value)
        run.font.name = font_family
        run.font.bold = True  # Section headers are typically bold
        
        # Apply color (remove # prefix for DOCX)
        if font_color.startswith('#'):
            from docx.shared import RGBColor
            hex_color = font_color[1:]
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            run.font.color.rgb = RGBColor(*rgb)
        
        # Apply paragraph formatting
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Apply paragraph borders using XML (like legacy system)
        pPr = paragraph._element.get_or_add_pPr()
        
        # Remove any existing borders
        for pBdr in pPr.xpath('./w:pBdr'):
            pPr.remove(pBdr)
        
        # Create paragraph borders
        pBdr = OxmlElement('w:pBdr')
        
        # Convert border width to eighth-points for Word
        width_8th_pt = int(border_width * 8)
        border_color_hex = border_color.lstrip('#')
        
        # Add borders to all sides
        for side in ['top', 'left', 'bottom', 'right']:
            border = OxmlElement(f'w:{side}')
            border.set(qn('w:val'), 'single')
            border.set(qn('w:sz'), str(width_8th_pt))
            border.set(qn('w:color'), border_color_hex)
            border.set(qn('w:space'), str(int(h_padding)))  # Use design token value consistently across formats
            pBdr.append(border)
        
        pPr.append(pBdr)
        
        # Apply spacing
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(4)  # Small spacing after header
    
    def to_html(self) -> str:
        """Render section header as HTML div with inline styles"""
        styles = self._build_css_styles()
        computed_text = self._get_computed_casing(self.text)
        
        logger.info(f"Generated HTML section header: '{self.text}' -> '{computed_text}'")
        return f'<div class="section-box" style="{styles}">{computed_text}</div>'
    
    def _build_css_styles(self) -> str:
        """Build inline CSS styles from design tokens"""
        font_size = self.tokens["typography"]["fontSize"]["sectionHeader"]
        font_color = self.tokens["typography"]["fontColor"]["headers"]["hex"]
        font_family = self.tokens["typography"]["fontFamily"]["primary"]
        border_width = self.tokens["sectionHeader"]["border"]["widthPt"]
        border_color = self.tokens["sectionHeader"]["border"]["color"]
        bg_color = self.tokens["sectionHeader"]["background"]["color"]
        v_padding = self.tokens["sectionHeader"]["padding"]["verticalPt"]
        h_padding = self.tokens["sectionHeader"]["padding"]["horizontalPt"]
        
        # Build CSS string
        styles = [
            f"font-size: {font_size}",
            f"color: {font_color}",
            f"font-family: {font_family}",
            f"font-weight: bold",
            f"border: {border_width}pt solid {border_color}",
            f"padding: {v_padding}pt {h_padding}pt",
            f"margin: 10pt 0",  # Standard section spacing
        ]
        
        if bg_color and bg_color != "transparent":
            styles.append(f"background-color: {bg_color}")
        
        # Note: text-transform is NOT included here - casing is handled by _get_computed_casing
        # This ensures consistent casing across all formats
        
        return "; ".join(styles)
    
    def get_debug_info(self) -> Dict:
        """Get debug information about this section header"""
        return {
            "text": self.text,
            "computed_text": self._get_computed_casing(self.text),
            "casing_rule": self.tokens["typography"]["casing"]["sectionHeaders"],
            "font_size": self.tokens["typography"]["fontSize"]["sectionHeader"],
            "font_color": self.tokens["typography"]["fontColor"]["headers"]["hex"],
            "border_style": f"{self.tokens['sectionHeader']['border']['widthPt']}pt solid {self.tokens['sectionHeader']['border']['color']}"
        } 