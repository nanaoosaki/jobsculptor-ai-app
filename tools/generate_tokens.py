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

        with open(tokens_path, 'r', encoding='utf-8') as f:
            tokens = json.load(f)

        # Apply auto-conversion for perfect HTML ↔ DOCX alignment (o3 suggestion B)
        tokens = auto_convert_em_to_docx_cm(tokens)

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
        
        with open(tokens_path, 'r', encoding='utf-8') as f:
            tokens = json.load(f)
        
        # Apply auto-conversion for perfect HTML ↔ DOCX alignment (o3 suggestion B)
        tokens = auto_convert_em_to_docx_cm(tokens)
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Extract new specification values with fallbacks
        font_family_base = tokens.get("font-family-base", "Palatino Linotype")
        
        # Font sizes from specification
        font_size_base = int(tokens.get("font-size-base-pt", "10"))
        font_size_name = int(tokens.get("font-size-name-pt", "20"))
        font_size_section = int(tokens.get("font-size-sectionheader-pt", "12"))
        font_size_company = int(tokens.get("font-size-company-pt", "11"))
        font_size_role = int(tokens.get("font-size-role-pt", "10"))
        font_size_contact = int(tokens.get("font-size-contact-pt", "10"))
        font_size_roledesc = int(tokens.get("font-size-roledescription-pt", "10"))
        font_size_bullet = int(tokens.get("font-size-bullet-pt", "10"))
        
        # Colors from specification
        color_primary_blue = tokens.get("color-primary-blue", "#1F497D")
        color_rolebox_fill = tokens.get("color-rolebox-fill", "#D6E0F5")
        color_black = tokens.get("color-black", "#000000")
        color_grey_text = tokens.get("color-grey-text", "#505050")
        
        # Line spacing and paragraph spacing
        line_spacing_base = float(tokens.get("line-spacing-base", "1.15"))
        line_spacing_bullet = float(tokens.get("line-spacing-bullet", "1.0"))
        
        # Paragraph spacing (before/after in pt)
        para_default_before = int(tokens.get("paragraph-spacing-before-default", "0"))
        para_default_after = int(tokens.get("paragraph-spacing-after-default", "0"))
        para_name_before = int(tokens.get("paragraph-spacing-name-before", "0"))
        para_name_after = int(tokens.get("paragraph-spacing-name-after", "0"))
        para_contact_before = int(tokens.get("paragraph-spacing-contact-before", "0"))
        para_contact_after = int(tokens.get("paragraph-spacing-contact-after", "0"))
        para_section_before = int(tokens.get("paragraph-spacing-section-before", "0"))
        para_section_after = int(tokens.get("paragraph-spacing-section-after", "0"))
        para_company_before = int(tokens.get("paragraph-spacing-company-before", "0"))
        para_company_after = int(tokens.get("paragraph-spacing-company-after", "0"))
        para_role_before = int(tokens.get("paragraph-spacing-role-before", "0"))
        para_role_after = int(tokens.get("paragraph-spacing-role-after", "0"))
        para_roledesc_before = int(tokens.get("paragraph-spacing-roledesc-before", "0"))
        para_roledesc_after = int(tokens.get("paragraph-spacing-roledesc-after", "0"))
        para_bullet_before = int(tokens.get("paragraph-spacing-bullet-before", "0"))
        para_bullet_after = int(tokens.get("paragraph-spacing-bullet-after", "0"))
        
        # Page margins
        page_margin_top = float(tokens.get("docx-page-margin-top-cm", "1.5"))
        page_margin_bottom = float(tokens.get("docx-page-margin-bottom-cm", "1.5"))
        page_margin_left = float(tokens.get("docx-page-margin-left-cm", "1.5"))
        page_margin_right = float(tokens.get("docx-page-margin-right-cm", "1.5"))
        
        # Border widths
        border_section = float(tokens.get("border-width-section", "0.5"))
        border_role = float(tokens.get("border-width-role", "0.5"))
        
        # Bullet indentation
        bullet_indent = float(tokens.get("docx-bullet-left-indent-cm", "0.39"))
        bullet_hanging = float(tokens.get("docx-bullet-hanging-indent-cm", "0.39"))
        
        # Enhanced mapping with new specification
        docx_styles = {
            "typography": {
                "_comment": "Typography settings derived from comprehensive DOCX specification",
                "fontFamily": font_family_base,
                "fontSize": {
                    "base": font_size_base,
                    "name": font_size_name,
                    "sectionHeader": font_size_section,
                    "company": font_size_company,
                    "role": font_size_role,
                    "contact": font_size_contact,
                    "roleDescription": font_size_roledesc,
                    "bullet": font_size_bullet
                },
                "fontWeight": {
                    "normal": 400,
                    "bold": 700
                },
                "fontColor": {
                    "primaryBlue": color_primary_blue,
                    "roleboxFill": color_rolebox_fill,
                    "black": color_black,
                    "greyText": color_grey_text
                },
                "lineHeight": {
                    "base": line_spacing_base,
                    "bullet": line_spacing_bullet
                },
                "spacing": {
                    "defaultAfterPt": para_default_after,
                    "nameAfterPt": para_name_after,
                    "contactAfterPt": para_contact_after,
                    "sectionAfterPt": para_section_after,
                    "companyAfterPt": para_company_after,
                    "roleAfterPt": para_role_after,
                    "roleDescAfterPt": para_roledesc_after,
                    "bulletAfterPt": para_bullet_after
                }
            },
            "page": {
                "marginTopCm": page_margin_top,
                "marginBottomCm": page_margin_bottom,
                "marginLeftCm": page_margin_left,
                "marginRightCm": page_margin_right,
                "size": "A4"
            },
            "global": {
                "fontFamily": font_family_base,
                "fontSizePt": font_size_base,
                "lineHeight": line_spacing_base,
                "color": hex_to_rgb(color_black),
                "backgroundColor": hex_to_rgb("#FFFFFF"),
                "defaultSpacingAfterPt": para_default_after
            },
            "styles": {
                "MR_Name": {
                    "fontFamily": font_family_base,
                    "fontSizePt": font_size_name,
                    "bold": True,
                    "color": hex_to_rgb(color_black),
                    "alignment": "center",
                    "spaceBeforePt": para_name_before,
                    "spaceAfterPt": para_name_after
                },
                "MR_Contact": {
                    "fontFamily": font_family_base,
                    "fontSizePt": font_size_contact,
                    "color": hex_to_rgb(color_black),
                    "alignment": "center",
                    "spaceBeforePt": para_contact_before,
                    "spaceAfterPt": para_contact_after
                },
                "MR_SectionHeader": {
                    "fontFamily": font_family_base,
                    "fontSizePt": font_size_section,
                    "bold": True,
                    "allCaps": True,
                    "color": hex_to_rgb(color_black),
                    "borderColor": hex_to_rgb(color_primary_blue),
                    "borderWidthPt": border_section,
                    "spaceBeforePt": para_section_before,
                    "spaceAfterPt": para_section_after,
                    "indentCm": 0.0
                },
                "MR_Company": {
                    "fontFamily": font_family_base,
                    "fontSizePt": font_size_company,
                    "bold": True,
                    "color": hex_to_rgb(color_primary_blue),
                    "alignment": "left",
                    "spaceBeforePt": para_company_before,
                    "spaceAfterPt": para_company_after,
                    "indentCm": 0.0,
                    "rightTabCm": 17.59  # Page width minus margins
                },
                "MR_RoleBox": {
                    "fontFamily": font_family_base,
                    "fontSizePt": font_size_role,
                    "bold": True,
                    "color": hex_to_rgb(color_black),
                    "backgroundColor": hex_to_rgb(color_rolebox_fill),
                    "borderColor": hex_to_rgb(color_primary_blue),
                    "borderWidthPt": border_role,
                    "spaceBeforePt": para_role_before,
                    "spaceAfterPt": para_role_after,
                    "indentCm": 0.0
                },
                "MR_RoleDescription": {
                    "fontFamily": font_family_base,
                    "fontSizePt": font_size_roledesc,
                    "italic": True,
                    "color": hex_to_rgb(color_black),
                    "spaceBeforePt": para_roledesc_before,
                    "spaceAfterPt": para_roledesc_after,
                    "indentCm": 0.0
                },
                "MR_BulletPoint": {
                    "fontFamily": font_family_base,
                    "fontSizePt": font_size_bullet,
                    "color": hex_to_rgb(color_black),
                    "indentCm": bullet_indent,
                    "hangingIndentCm": bullet_hanging,
                    "spaceBeforePt": para_bullet_before,
                    "spaceAfterPt": para_bullet_after,
                    "lineHeight": line_spacing_bullet,
                    "bulletCharacter": "–"  # En-dash as specified
                },
                "MR_SummaryText": {
                    "fontFamily": font_family_base,
                    "fontSizePt": font_size_base,
                    "color": hex_to_rgb(color_black),
                    "spaceBeforePt": para_default_before,
                    "spaceAfterPt": para_default_after,
                    "indentCm": 0.0
                },
                "MR_SkillCategory": {
                    "fontFamily": font_family_base,
                    "fontSizePt": font_size_base,
                    "bold": True,
                    "color": hex_to_rgb(color_black),
                    "spaceBeforePt": para_default_before,
                    "spaceAfterPt": para_default_after,
                    "indentCm": 0.0
                },
                "MR_SkillList": {
                    "fontFamily": font_family_base,
                    "fontSizePt": font_size_base,
                    "color": hex_to_rgb(color_black),
                    "spaceBeforePt": para_default_before,
                    "spaceAfterPt": para_default_after,
                    "indentCm": 0.0
                }
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(docx_styles, f, indent=2)
        
        print(f"Successfully generated {output_path}")
        print(f"DOCX styles path: {output_path}")
        print(f"Loaded DOCX styles: {docx_styles}")
        
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

# Auto-conversion helper functions (o3 suggestion B)
def em_to_cm(em_value, base_font_pt):
    """Convert em units to cm based on font size"""
    points = em_value * base_font_pt
    return round(points * 0.0352778, 2)  # 1 pt = 0.0352778 cm

def auto_convert_em_to_docx_cm(tokens):
    """Auto-generate DOCX cm values from HTML em values for perfect alignment"""
    
    # Extract base font size using the correct token name
    base_font_str = tokens.get('font-size-base-pt', '10')  # Updated token name
    if isinstance(base_font_str, str) and base_font_str.endswith('pt'):
        base_font_pt = float(base_font_str.rstrip('pt'))
    else:
        base_font_pt = float(str(base_font_str))  # Handle numeric values
    
    # Auto-convert bullet indentation
    bullet_padding_str = tokens.get('bullet-item-padding-left', '1em')
    if bullet_padding_str.endswith('em'):
        bullet_padding_em = float(bullet_padding_str.rstrip('em'))
        docx_indent_cm = em_to_cm(bullet_padding_em, base_font_pt)
        
        # Update tokens with auto-converted values
        tokens['docx-bullet-left-indent-cm'] = str(docx_indent_cm)
        tokens['docx-bullet-hanging-indent-cm'] = str(docx_indent_cm)
        
        print(f"Auto-converted: {bullet_padding_em}em → {docx_indent_cm}cm (at {base_font_pt}pt)")
    
    return tokens

if __name__ == "__main__":
    generate_scss_variables()
    generate_docx_style_mappings()
    
    # Test style load after generation
    print(f"DOCX styles path: {StyleManager.docx_styles_path()}")
    docx_styles = StyleManager.load_docx_styles()
    print(f"Loaded DOCX styles: {docx_styles}") 