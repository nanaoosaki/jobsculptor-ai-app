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
        
        # Enhanced mapping with more styling options
        docx_styles = {
            "page": {
                "marginTopCm": float(tokens.get("pageMarginVertical", "0.8cm").replace("cm", "")),
                "marginBottomCm": float(tokens.get("pageMarginVertical", "0.8cm").replace("cm", "")),
                "marginLeftCm": float(tokens.get("pageMarginHorizontal", "0.8cm").replace("cm", "")),
                "marginRightCm": float(tokens.get("pageMarginHorizontal", "0.8cm").replace("cm", ""))
            },
            "global": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": int(tokens.get("baseFontSize", "11pt").replace("pt", "")),
                "lineHeight": float(tokens.get("baseLineHeight", "1.4")),
                "color": hex_to_rgb(tokens.get("textColor", "#333")),
                "backgroundColor": hex_to_rgb(tokens.get("backgroundColor", "#ffffff")),
                "tabStopPosition": float(tokens.get("tab-stop-position-cm", "15"))
            },
            "heading1": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": int(tokens.get("nameFontSize", "16pt").replace("pt", "")),
                "color": hex_to_rgb(tokens.get("textColor", "#333")),
                "bold": True,
                "spaceAfterPt": 12
            },
            "heading2": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": int(tokens.get("sectionHeaderFontSize", "12pt").replace("pt", "")),
                "color": hex_to_rgb(tokens.get("pdfHeaderColor", "rgb(0, 0, 102)")),
                "spaceAfterPt": 6,
                "bold": True,
                "backgroundColor": hex_to_rgb(tokens.get("color.sectionBox.bg", "#FFFFFF")),
                "borderColor": hex_to_rgb(tokens.get("sectionHeaderBorder", "#0D2B7E").replace("px solid ", "")),
                "borderSize": 1,
                "paddingVertical": float(tokens.get("sectionHeaderPaddingVert", "1px").replace("px", "")),
                "paddingHorizontal": float(tokens.get("sectionHeaderPaddingHoriz", "12px").replace("px", "")),
                "marginBottom": float(tokens.get("section-box-margin-bottom", "0.5rem").replace("rem", "")) * 16
            },
            "heading3": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": int(tokens.get("baseFontSize", "11pt").replace("pt", "")),
                "bold": True,
                "spaceAfterPt": 4
            },
            "body": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": int(tokens.get("baseFontSize", "11pt").replace("pt", "")),
                "lineHeight": float(tokens.get("baseLineHeight", "1.4")),
                "color": hex_to_rgb(tokens.get("textColor", "#333")),
                "marginLeft": float(tokens.get("content-left-margin", "0").replace("rem", "").replace("em", "").replace("px", ""))
            },
            "bulletList": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": int(tokens.get("baseFontSize", "11pt").replace("pt", "")),
                "indentCm": float(tokens.get("bullet-list-indent-cm", "0.75")),
                "hangingIndentCm": float(tokens.get("bullet-list-hanging-indent-cm", "0.25")), 
                "bulletCharacter": tokens.get("bullet-glyph", "\"\\2022\"").replace("\"\\\\", "").replace("\"", ""),
                "spaceAfterPt": float(tokens.get("bullet-spacing-after", "0.15").replace("rem", "")) * 12,
                "color": hex_to_rgb(tokens.get("color.bullet", "#3A3A3A"))
            },
            "roleDescription": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": int(tokens.get("baseFontSize", "11pt").replace("pt", "")),
                "indentCm": float(tokens.get("role-description-indent-cm", "0")),
                "spaceAfterPt": 6,
                "color": hex_to_rgb(tokens.get("textColor", "#333")),
                "fontStyle": "italic"
            },
            "positionBar": {
                "spaceAfterPt": float(tokens.get("position-line-margin-bottom", "0.15").replace("rem", "")) * 12
            },
            "sectionSpacing": {
                "spacingCm": float(tokens.get("section-spacing-vertical", "0.8").replace("rem", "")) / 2.54
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