import json
import pathlib
import sys
import os

# Add parent directory to path to import StyleManager
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from style_manager import StyleManager

def generate_typography_variables(tokens):
    """Generate SCSS variables for the new unified typography system."""
    typography = tokens.get("typography", {})
    
    # Generate both new structured variables and maintain backward compatibility
    scss_vars = {}
    
    # Font families
    font_families = typography.get("fontFamily", {})
    scss_vars.update({
        "font-family-primary": font_families.get("primary", "'Calibri', Arial, sans-serif"),
        "font-family-fallback": font_families.get("fallback", "Arial, sans-serif"),
        "font-family-docx": font_families.get("docxPrimary", "Calibri"),
        "font-family-web": font_families.get("webPrimary", "'Calibri', Arial, sans-serif"),
    })
    
    # Font sizes  
    font_sizes = typography.get("fontSize", {})
    for size_type, size_value in font_sizes.items():
        scss_vars[f"font-size-{size_type.replace('_', '-')}"] = size_value
    
    # Font weights
    font_weights = typography.get("fontWeight", {})
    for weight_type, weight_value in font_weights.items():
        scss_vars[f"font-weight-{weight_type}"] = weight_value
    
    # Line heights
    line_heights = typography.get("lineHeight", {})
    for lh_type, lh_value in line_heights.items():
        scss_vars[f"line-height-{lh_type}"] = lh_value
    
    # Font colors
    font_colors = typography.get("fontColor", {})
    for color_type, color_value in font_colors.items():
        scss_vars[f"font-color-{color_type}"] = color_value
    
    # Font styles
    font_styles = typography.get("fontStyle", {})
    for style_type, style_value in font_styles.items():
        scss_vars[f"font-style-{style_type}"] = style_value
    
    return scss_vars

def flatten_nested_tokens(tokens, parent_key="", separator="-"):
    """Recursively flatten nested token structures for SCSS generation."""
    flattened = {}
    
    for key, value in tokens.items():
        # Skip internal comments
        if key.startswith("_"):
            continue
            
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        
        # Convert dots to hyphens in variable names for SCSS compatibility
        scss_key = new_key.replace('.', '-')
        
        if isinstance(value, dict):
            # Recursively flatten nested dictionaries
            flattened.update(flatten_nested_tokens(value, scss_key, separator))
        else:
            flattened[scss_key] = value
    
    return flattened

def generate_scss_variables():
    """Reads design tokens and generates an SCSS variables file with enhanced typography support."""
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
            f.write("// Token naming convention: width/radius/padding values are unit-less strings. CSS applies units (px) via calc() multiplication. This prevents WeasyPrint calc() bugs and maintains clean token schema.\n")
            
            # Generate typography variables first (new unified system)
            if "typography" in tokens:
                f.write("\n// === UNIFIED TYPOGRAPHY SYSTEM ===\n")
                f.write("// New structured typography tokens for consistent fonts across all formats\n")
                typography_vars = generate_typography_variables(tokens)
                for key, value in typography_vars.items():
                    f.write(f"${key}: {value};\n")
            
            # Generate all other tokens (including backward compatibility)
            f.write("\n// === LEGACY AND OTHER TOKENS ===\n")
            f.write("// Includes backward compatibility tokens and non-typography tokens\n")
            
            # Flatten all tokens (including nested ones like roleBox, sectionHeader)
            flattened_tokens = flatten_nested_tokens(tokens)
            
            for key, value in flattened_tokens.items():
                # Skip typography tokens as they're handled above
                if not key.startswith("typography"):
                    f.write(f"${key}: {value};\n")
        
        print(f"Successfully generated {output_path}")
        
        # Generate CSS custom properties as well
        generate_css_custom_properties(tokens, output_dir)

    except FileNotFoundError:
        print(f"Error: design_tokens.json not found at {tokens_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {tokens_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

def generate_css_custom_properties(tokens, output_dir):
    """Generate CSS custom properties for browser consumption."""
    try:
        output_path = output_dir / '../css/_variables.css'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write("/* Auto-generated CSS custom properties from design_tokens.json. Do not edit directly. */\n\n")
            f.write(":root {\n")
            
            # Generate typography custom properties
            if "typography" in tokens:
                f.write("  /* Typography System */\n")
                typography_vars = generate_typography_variables(tokens)
                for key, value in typography_vars.items():
                    css_key = key.replace('_', '-')
                    f.write(f"  --{css_key}: {value};\n")
                f.write("\n")
            
            # Generate other custom properties
            f.write("  /* Other Design Tokens */\n")
            flattened_tokens = flatten_nested_tokens(tokens)
            for key, value in flattened_tokens.items():
                if not key.startswith("typography"):
                    css_key = key.replace('_', '-')
                    f.write(f"  --{css_key}: {value};\n")
            
            f.write("}\n")
            
        print(f"Successfully generated CSS custom properties at {output_path}")
        
    except Exception as e:
        print(f"Error generating CSS custom properties: {e}", file=sys.stderr)

def get_typography_value(tokens, category, item_type, fallback=""):
    """Helper to get typography values with fallbacks."""
    return tokens.get("typography", {}).get(category, {}).get(item_type, fallback)

def generate_docx_style_mappings():
    """Generate enhanced DOCX style mappings from design tokens with typography integration."""
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

        # Use new typography system if available, fallback to legacy tokens
        typography = tokens.get("typography", {})
        
        # Font family - prioritize new typography system
        font_family_docx = get_typography_value(tokens, "fontFamily", "docxPrimary", 
                                               tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip())
        
        # Font sizes - use new typography system or fallback to legacy
        font_size_body = get_typography_value(tokens, "fontSize", "body", tokens.get("baseFontSize", "11pt"))
        font_size_section = get_typography_value(tokens, "fontSize", "sectionHeader", "14pt") 
        font_size_name = get_typography_value(tokens, "fontSize", "nameHeader", tokens.get("nameFontSize", "16pt"))
        
        # Convert font sizes to points
        def parse_font_size(size_str):
            if isinstance(size_str, (int, float)):
                return int(size_str)
            return int(str(size_str).replace("pt", ""))
        
        # Colors - use new typography system or fallback
        color_primary = get_typography_value(tokens, "fontColor", "primary", tokens.get("textColor", "#333"))
        color_headers = get_typography_value(tokens, "fontColor", "headers", tokens.get("pdfHeaderColor", "rgb(0, 0, 102)"))
        
        # Legacy DOCX-specific values (maintain for now)
        docx_section_header_indent = float(tokens.get("docx-section-header-indent-cm", "0"))
        docx_company_indent = float(tokens.get("docx-company-name-indent-cm", "0"))
        docx_role_indent = float(tokens.get("docx-role-description-indent-cm", "0"))
        docx_bullet_indent = float(tokens.get("docx-bullet-left-indent-cm", "0"))
        docx_bullet_hanging = float(tokens.get("docx-bullet-hanging-indent-cm", "0"))
        
        # Spacing values - use new typography system spacing if available
        docx_spacing = typography.get("docx", {}).get("spacing", {})
        docx_section_spacing = int(docx_spacing.get("sectionAfterPt", tokens.get("docx-section-spacing-pt", "4")))
        docx_bullet_spacing = int(docx_spacing.get("bulletAfterPt", tokens.get("docx-bullet-spacing-pt", "6")))
        docx_paragraph_spacing = int(docx_spacing.get("paragraphAfterPt", tokens.get("docx-paragraph-spacing-pt", "6")))
        
        # Get global margin values
        global_left_margin_cm = float(tokens.get("docx-global-left-margin-cm", "2.0"))
        global_right_margin_cm = float(tokens.get("docx-global-right-margin-cm", "2.0"))
        
        # Enhanced mapping with typography integration
        docx_styles = {
            "typography": {
                "_comment": "Typography settings derived from unified typography system",
                "fontFamily": font_family_docx,
                "fontSize": {
                    "body": parse_font_size(font_size_body),
                    "sectionHeader": parse_font_size(font_size_section), 
                    "nameHeader": parse_font_size(font_size_name),
                    "roleTitle": parse_font_size(get_typography_value(tokens, "fontSize", "roleTitle", "11pt")),
                    "companyName": parse_font_size(get_typography_value(tokens, "fontSize", "companyName", "11pt")),
                    "bulletPoint": parse_font_size(get_typography_value(tokens, "fontSize", "bulletPoint", "11pt")),
                },
                "fontWeight": typography.get("fontWeight", {
                    "normal": 400,
                    "bold": 700
                }),
                "fontColor": {
                    "primary": color_primary,
                    "headers": color_headers,
                    "secondary": get_typography_value(tokens, "fontColor", "secondary", "#6c757d")
                },
                "lineHeight": typography.get("lineHeight", {
                    "normal": 1.4,
                    "tight": 1.2
                }),
                "spacing": {
                    "sectionAfterPt": docx_section_spacing,
                    "paragraphAfterPt": docx_paragraph_spacing,
                    "bulletAfterPt": docx_bullet_spacing
                }
            },
            "page": {
                "marginTopCm": float(tokens.get("pageMarginVertical", "0.8cm").replace("cm", "")),
                "marginBottomCm": float(tokens.get("pageMarginVertical", "0.8cm").replace("cm", "")),
                "marginLeftCm": global_left_margin_cm,
                "marginRightCm": global_right_margin_cm
            },
            "global": {
                "fontFamily": font_family_docx,
                "fontSizePt": parse_font_size(font_size_body),
                "lineHeight": float(tokens.get("baseLineHeight", "1.4")),
                "color": hex_to_rgb(color_primary),
                "backgroundColor": hex_to_rgb(tokens.get("backgroundColor", "#ffffff")),
                "tabStopPosition": 19.0,
                "contentIndentCm": docx_company_indent
            },
            "heading1": {
                "fontFamily": font_family_docx,
                "fontSizePt": parse_font_size(font_size_name),
                "color": hex_to_rgb(color_primary),
                "bold": True,
                "spaceAfterPt": docx_section_spacing
            },
            "heading2": {
                "fontFamily": font_family_docx,
                "fontSizePt": parse_font_size(font_size_section),
                "color": hex_to_rgb(color_headers),
                "spaceAfterPt": docx_section_spacing,
                "bold": True,
                "backgroundColor": hex_to_rgb(tokens.get("color.sectionBox.bg", "#FFFFFF")),
                "borderColor": hex_to_rgb(tokens.get("sectionHeaderBorder", "#0D2B7E").replace("px solid ", "")),
                "borderSize": 1,
                "paddingVertical": float(tokens.get("sectionHeaderPaddingVert", "1px").replace("px", "")),
                "paddingHorizontal": float(tokens.get("sectionHeaderPaddingHoriz", "12px").replace("px", "")),
                "marginBottom": float(tokens.get("section-box-margin-bottom", "0.5rem").replace("rem", "")) * 16,
                "indentCm": docx_section_header_indent
            },
            "heading3": {
                "fontFamily": font_family_docx,
                "fontSizePt": parse_font_size(get_typography_value(tokens, "fontSize", "companyName", "11pt")),
                "bold": True,
                "spaceAfterPt": docx_paragraph_spacing
            },
            "body": {
                "fontFamily": font_family_docx,
                "fontSizePt": parse_font_size(font_size_body),
                "lineHeight": float(tokens.get("baseLineHeight", "1.4")),
                "color": hex_to_rgb(color_primary),
                "spaceAfterPt": docx_paragraph_spacing,
                "indentCm": docx_company_indent
            },
            "bulletList": {
                "fontFamily": font_family_docx,
                "fontSizePt": parse_font_size(get_typography_value(tokens, "fontSize", "bulletPoint", "11pt")),
                "indentCm": docx_bullet_indent,
                "hangingIndentCm": docx_bullet_hanging, 
                "bulletCharacter": tokens.get("bullet-glyph", "\"\\2022\"").replace("\"\\\\", "").replace("\"", ""),
                "spaceAfterPt": docx_bullet_spacing,
                "color": hex_to_rgb(tokens.get("color.bullet", "#3A3A3A"))
            },
            "roleDescription": {
                "fontFamily": font_family_docx,
                "fontSizePt": parse_font_size(get_typography_value(tokens, "fontSize", "roleDescription", "11pt")),
                "indentCm": docx_role_indent,
                "spaceAfterPt": docx_paragraph_spacing,
                "color": hex_to_rgb(color_primary),
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
                    "fontFamily": font_family_docx,
                    "fontSizePt": parse_font_size(font_size_section),
                    "indentCm": docx_section_header_indent,
                    "spaceAfterPt": docx_section_spacing,
                    "bold": True,
                    "color": hex_to_rgb(color_headers)
                },
                "MR_Content": {
                    "fontFamily": font_family_docx,
                    "fontSizePt": parse_font_size(font_size_body),
                    "indentCm": docx_company_indent,
                    "spaceAfterPt": docx_paragraph_spacing,
                    "color": hex_to_rgb(color_primary)
                },
                "MR_RoleDescription": {
                    "fontFamily": font_family_docx,
                    "fontSizePt": parse_font_size(get_typography_value(tokens, "fontSize", "roleDescription", "11pt")),
                    "indentCm": docx_role_indent,
                    "spaceAfterPt": docx_paragraph_spacing,
                    "italic": True,
                    "color": hex_to_rgb(color_primary)
                },
                "MR_BulletPoint": {
                    "fontFamily": font_family_docx,
                    "fontSizePt": parse_font_size(get_typography_value(tokens, "fontSize", "bulletPoint", "11pt")),
                    "indentCm": docx_bullet_indent,
                    "hangingIndentCm": docx_bullet_hanging,
                    "spaceAfterPt": docx_bullet_spacing,
                    "color": hex_to_rgb(color_primary)
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