import json
import pathlib
import sys
import os

# Add parent directory to path to import StyleManager
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from style_manager import StyleManager

def generate_scss_variables():
    """Reads design tokens and generates an SCSS variables file."""
    try:
        # Assuming script is in tools/ and tokens are at root
        repo_root = pathlib.Path(__file__).parent.parent 
        tokens_path = repo_root / 'design_tokens.json'
        output_dir = repo_root / 'static' / 'scss'
        output_path = output_dir / '_tokens.scss'

        print(f"Reading tokens from: {tokens_path}")
        print(f"Writing SCSS variables to: {output_path}")

        with open(tokens_path, 'r') as f:
            tokens = json.load(f)

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write("// Auto-generated from design_tokens.json. Do not edit directly.\n\n")
            for key, value in tokens.items():
                # Convert dots to hyphens in variable names
                scss_key = key.replace('.', '-')
                f.write(f"${scss_key}: {value};\n")
        
        print(f"Successfully generated {output_path}")

    except FileNotFoundError:
        print(f"Error: design_tokens.json not found at {tokens_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {tokens_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

def generate_docx_style_mappings():
    """Generate enhanced DOCX style mappings from design tokens."""
    try:
        repo_root = pathlib.Path(__file__).parent.parent 
        tokens_path = repo_root / 'design_tokens.json'
        output_dir = repo_root / 'static' / 'styles'
        output_path = output_dir / '_docx_styles.json'
        
        print(f"Reading tokens from: {tokens_path}")
        print(f"Writing DOCX style mappings to: {output_path}")
        
        with open(tokens_path, 'r') as f:
            tokens = json.load(f)
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get the indent values directly from our new DOCX-specific tokens
        docx_section_header_indent = float(tokens.get("docx-section-header-indent-cm", "0"))
        docx_company_indent = float(tokens.get("docx-company-name-indent-cm", "0.5"))
        docx_role_indent = float(tokens.get("docx-role-description-indent-cm", "0.5"))
        docx_bullet_indent = float(tokens.get("docx-bullet-left-indent-cm", "0.5"))
        docx_bullet_hanging = float(tokens.get("docx-bullet-hanging-indent-cm", "0.5"))
        docx_section_spacing = int(tokens.get("docx-section-spacing-pt", "12"))
        docx_bullet_spacing = int(tokens.get("docx-bullet-spacing-pt", "6"))
        docx_paragraph_spacing = int(tokens.get("docx-paragraph-spacing-pt", "6"))
        
        # Font sizes
        docx_section_header_font_size = int(tokens.get("docx-section-header-font-size-pt", "14"))
        docx_company_font_size = int(tokens.get("docx-company-font-size-pt", "11"))
        docx_role_font_size = int(tokens.get("docx-role-font-size-pt", "11"))
        docx_bullet_font_size = int(tokens.get("docx-bullet-font-size-pt", "11"))
        
        # Get global margin values
        global_left_margin_cm = float(tokens.get("docx-global-left-margin-cm", "2.0"))
        global_right_margin_cm = float(tokens.get("docx-global-right-margin-cm", "2.0"))
        
        # Enhanced mapping with more styling options
        docx_styles = {
            "page": {
                "marginTopCm": float(tokens.get("pageMarginVertical", "0.8cm").replace("cm", "")),
                "marginBottomCm": float(tokens.get("pageMarginVertical", "0.8cm").replace("cm", "")),
                "marginLeftCm": global_left_margin_cm,  # Use global left margin
                "marginRightCm": global_right_margin_cm  # Use global right margin
            },
            "global": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": int(tokens.get("baseFontSize", "11pt").replace("pt", "")),
                "lineHeight": float(tokens.get("baseLineHeight", "1.4")),
                "color": hex_to_rgb(tokens.get("textColor", "#333")),
                "backgroundColor": hex_to_rgb(tokens.get("backgroundColor", "#ffffff")),
                "tabStopPosition": 19.0,
                "contentIndentCm": docx_company_indent  # Use the company indent as the global base
            },
            "heading1": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": int(tokens.get("nameFontSize", "16pt").replace("pt", "")),
                "color": hex_to_rgb(tokens.get("textColor", "#333")),
                "bold": True,
                "spaceAfterPt": docx_section_spacing
            },
            "heading2": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": docx_section_header_font_size,
                "color": hex_to_rgb(tokens.get("pdfHeaderColor", "rgb(0, 0, 102)")),
                "spaceAfterPt": docx_section_spacing,
                "bold": True,
                "backgroundColor": hex_to_rgb(tokens.get("color.sectionBox.bg", "#FFFFFF")),
                "borderColor": hex_to_rgb(tokens.get("sectionHeaderBorder", "#0D2B7E").replace("px solid ", "")),
                "borderSize": 1,
                "paddingVertical": float(tokens.get("sectionHeaderPaddingVert", "1px").replace("px", "")),
                "paddingHorizontal": float(tokens.get("sectionHeaderPaddingHoriz", "12px").replace("px", "")),
                "marginBottom": float(tokens.get("section-box-margin-bottom", "0.5rem").replace("rem", "")) * 16,
                "indentCm": docx_section_header_indent  # Use dedicated section header indent
            },
            "heading3": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": docx_company_font_size,
                "bold": True,
                "spaceAfterPt": docx_paragraph_spacing
            },
            "body": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": docx_company_font_size,
                "lineHeight": float(tokens.get("baseLineHeight", "1.4")),
                "color": hex_to_rgb(tokens.get("textColor", "#333")),
                "spaceAfterPt": docx_paragraph_spacing,
                "indentCm": docx_company_indent  # Use company indent for body text
            },
            "bulletList": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": docx_bullet_font_size,
                "indentCm": docx_bullet_indent,
                "hangingIndentCm": docx_bullet_hanging, 
                "bulletCharacter": tokens.get("bullet-glyph", "\"\\2022\"").replace("\"\\\\", "").replace("\"", ""),
                "spaceAfterPt": docx_bullet_spacing,
                "color": hex_to_rgb(tokens.get("color.bullet", "#3A3A3A"))
            },
            "roleDescription": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": docx_role_font_size,
                "indentCm": docx_role_indent,
                "spaceAfterPt": docx_paragraph_spacing,
                "color": hex_to_rgb(tokens.get("textColor", "#333")),
                "fontStyle": "italic"
            },
            "positionBar": {
                "spaceAfterPt": docx_paragraph_spacing,
                "indentCm": docx_company_indent
            },
            "sectionSpacing": {
                "spacingPt": docx_section_spacing
            },
            "styles": {
                "MR_SectionHeader": {
                    "fontSizePt": docx_section_header_font_size,
                    "indentCm": docx_section_header_indent,
                    "spaceAfterPt": docx_section_spacing,
                    "bold": True
                },
                "MR_Content": {
                    "fontSizePt": docx_company_font_size,
                    "indentCm": docx_company_indent,
                    "spaceAfterPt": docx_paragraph_spacing
                },
                "MR_RoleDescription": {
                    "fontSizePt": docx_role_font_size,
                    "indentCm": docx_role_indent,
                    "spaceAfterPt": docx_paragraph_spacing,
                    "italic": True
                },
                "MR_BulletPoint": {
                    "fontSizePt": docx_bullet_font_size,
                    "indentCm": docx_bullet_indent,
                    "hangingIndentCm": docx_bullet_hanging,
                    "spaceAfterPt": docx_bullet_spacing
                }
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(docx_styles, f, indent=2)
        
        print(f"Successfully generated {output_path}")
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple for DOCX."""
    try:
        # Handle empty or None values
        if not hex_color:
            return [0, 0, 0]  # Default to black
            
        # Handle rgb() format
        if hex_color.startswith("rgb("):
            return [int(x.strip()) for x in hex_color[4:-1].split(",")]
        
        # Handle hex format
        hex_color = hex_color.lstrip('#')
        
        # Handle shorthand hex (e.g., #fff)
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
            
        # Ensure we have a valid hex color
        if len(hex_color) != 6:
            return [0, 0, 0]  # Default to black
            
        return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    except Exception as e:
        print(f"Error converting color '{hex_color}' to RGB: {e}")
        return [0, 0, 0]  # Default to black

if __name__ == "__main__":
    generate_scss_variables()
    generate_docx_style_mappings()
    
    # Test style load after generation
    print(f"DOCX styles path: {StyleManager.docx_styles_path()}")
    docx_styles = StyleManager.load_docx_styles()
    print(f"Loaded DOCX styles: {docx_styles}") 