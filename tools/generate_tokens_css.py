import json
import pathlib
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_scss_variables():
    """Reads design tokens and generates an SCSS variables file."""
    try:
        # Assuming script is in tools/ and tokens are at root
        repo_root = pathlib.Path(__file__).parent.parent 
        tokens_path = repo_root / 'design_tokens.json'
        scss_output_dir = repo_root / 'static' / 'scss'
        scss_output_path = scss_output_dir / '_tokens.scss'
        css_output_dir = repo_root / 'static' / 'css'
        css_output_path = css_output_dir / '_variables.css'

        print(f"Reading tokens from: {tokens_path}")
        print(f"Writing SCSS variables to: {scss_output_path}")
        print(f"Writing CSS custom properties to: {css_output_path}")

        with open(tokens_path, 'r') as f:
            tokens = json.load(f)

        # Ensure output directories exist
        scss_output_dir.mkdir(parents=True, exist_ok=True)
        css_output_dir.mkdir(parents=True, exist_ok=True)

        # Generate SCSS variables
        with open(scss_output_path, 'w') as f:
            f.write("// Auto-generated from design_tokens.json. Do not edit directly.\n\n")
            
            # Generate enhanced typography variables first
            typography_vars = _generate_typography_variables(tokens)
            if typography_vars:
                f.write("// === UNIFIED TYPOGRAPHY SYSTEM ===\n")
                f.write("// Enhanced typography tokens for consistent fonts across all formats\n")
                for var_name, var_value in typography_vars.items():
                    f.write(f"${var_name}: {var_value};\n")
                f.write("\n")
            
            f.write("// === LEGACY AND OTHER TOKENS ===\n")
            f.write("// Includes backward compatibility tokens and non-typography tokens\n")
            _write_variables(f, tokens, "", exclude_sections=["typography"])

        # Generate CSS custom properties
        with open(css_output_path, 'w') as f:
            f.write("/* Auto-generated CSS custom properties from design_tokens.json. Do not edit directly. */\n\n")
            f.write(":root {\n")
            
            # Typography system
            typography_vars = _generate_typography_variables(tokens)
            if typography_vars:
                f.write("  /* Typography System */\n")
                for var_name, var_value in typography_vars.items():
                    f.write(f"  --{var_name}: {var_value};\n")
                f.write("\n")
            
            f.write("  /* Other Design Tokens */\n")
            _write_css_custom_properties(f, tokens, "", exclude_sections=["typography"])
            f.write("}\n")
        
        print(f"Successfully generated {scss_output_path}")
        print(f"Successfully generated {css_output_path}")

    except FileNotFoundError:
        print(f"Error: design_tokens.json not found at {tokens_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {tokens_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

def _generate_typography_variables(tokens):
    """Generate enhanced typography variables with cache busting and multi-format support."""
    typography = tokens.get("typography", {})
    if not typography:
        return {}
    
    vars_dict = {}
    
    # Font families with versioning and multi-script support
    font_families = typography.get("fontFamily", {})
    font_version = font_families.get("fontVersion", "2025-01")
    
    vars_dict.update({
        "font-family-primary": _scss_string_value(font_families.get("primary", "Calibri, sans-serif")),
        "font-family-fallback": _scss_string_value(font_families.get("fallback", "Arial, sans-serif")),
        "font-family-docx": _scss_string_value(font_families.get("docxPrimary", "Calibri")),
        "font-family-web": _scss_string_value(font_families.get("webPrimary", "'Calibri', Arial, sans-serif")),
        "font-version": _scss_string_value(font_version),
    })
    
    # Multi-script font families
    secondary_fonts = font_families.get("secondary", {})
    for script, font_list in secondary_fonts.items():
        vars_dict[f"font-family-{script}"] = _scss_string_value(font_list)
    
    # Accessibility fonts
    accessibility = font_families.get("accessibility", {})
    for mode, font in accessibility.items():
        vars_dict[f"font-family-{mode.replace('Mode', '')}"] = _scss_string_value(font)
    
    # Font sizes with screen/print conversion
    font_sizes = typography.get("fontSize", {})
    for size_type, size_value in font_sizes.items():
        scss_type = size_type.replace("_", "-")
        vars_dict[f"font-size-{scss_type}"] = _css_value(size_value, for_screen=False)
        vars_dict[f"font-size-{scss_type}-screen"] = _css_value(size_value, for_screen=True)
    
    # Font weights
    font_weights = typography.get("fontWeight", {})
    for weight_type, weight_value in font_weights.items():
        vars_dict[f"font-weight-{weight_type}"] = weight_value
    
    # Line heights (unit-less for screen, pt for print)
    line_heights = typography.get("lineHeight", {})
    for lh_type, lh_value in line_heights.items():
        vars_dict[f"line-height-{lh_type}"] = lh_value
    
    # Point-based line heights for exact control
    line_heights_pt = typography.get("lineHeightPt", {})
    for lh_type, lh_value in line_heights_pt.items():
        vars_dict[f"line-height-{lh_type}-pt"] = f"{lh_value}pt"
    
    # Font colors with theme support
    font_colors = typography.get("fontColor", {})
    for color_type, color_value in font_colors.items():
        if isinstance(color_value, dict):
            # New structured color format
            hex_color = color_value.get("hex", "#000000")
            theme_color = color_value.get("themeColor")
            vars_dict[f"font-color-{color_type}"] = hex_color
            if theme_color:
                vars_dict[f"font-color-{color_type}-theme"] = _scss_string_value(theme_color)
        else:
            # Legacy string format
            vars_dict[f"font-color-{color_type}"] = color_value
    
    # Font styles
    font_styles = typography.get("fontStyle", {})
    for style_type, style_value in font_styles.items():
        vars_dict[f"font-style-{style_type}"] = _scss_string_value(style_value)
    
    # Font feature settings
    font_features = typography.get("fontFeatureSettings", {})
    for feature_type, feature_value in font_features.items():
        vars_dict[f"font-feature-{feature_type}"] = _scss_string_value(feature_value)
    
    return vars_dict

def _write_variables(file, obj, prefix, exclude_sections=None):
    """Recursively write SCSS variables from nested objects."""
    if exclude_sections is None:
        exclude_sections = []
    
    for key, value in obj.items():
        # Skip excluded sections
        if not prefix and key in exclude_sections:
            continue
            
        # Convert dots to hyphens in variable names
        scss_key = key.replace('.', '-')
        full_key = f"{prefix}-{scss_key}" if prefix else scss_key
        
        if isinstance(value, dict):
            # Recursively handle nested objects
            _write_variables(file, value, full_key, exclude_sections)
        else:
            # Write the variable
            file.write(f"${full_key}: {value};\n")

def _write_css_custom_properties(file, obj, prefix, exclude_sections=None):
    """Write CSS custom properties from nested objects."""
    if exclude_sections is None:
        exclude_sections = []
    
    for key, value in obj.items():
        # Skip excluded sections
        if not prefix and key in exclude_sections:
            continue
            
        # Convert dots to hyphens in variable names
        css_key = key.replace('.', '-')
        full_key = f"{prefix}-{css_key}" if prefix else css_key
        
        if isinstance(value, dict):
            # Recursively handle nested objects
            _write_css_custom_properties(file, value, full_key, exclude_sections)
        else:
            # Write the custom property
            file.write(f"  --{full_key}: {value};\n")

def _scss_string_value(value):
    """Ensure string values are properly quoted for SCSS."""
    if isinstance(value, str):
        # Don't double-quote already quoted strings
        if value.startswith('"') and value.endswith('"'):
            return value
        if value.startswith("'") and value.endswith("'"):
            return value
        # Quote unquoted strings
        return f'"{value}"'
    return value

def _css_value(val, *, for_screen=True):
    """Convert pt to rem for screen; leave pt for print."""
    if isinstance(val, str) and val.endswith("pt") and for_screen:
        pt = float(val[:-2])
        return f"{pt/12:.3f}rem"  # assuming 16px root, 12pt = 1rem
    return val

def check_token_groups_in_palettes(tokens, palettes):
    """Add warning for missing token groups in non-default palettes"""
    for palette_name, palette in palettes.items():
        if palette_name == "default":
            continue
        for group_name in ["roleBox"]:  # List of required groups
            if group_name not in palette:
                logger.warning(f"{group_name} missing in palette {palette_name} – falling back to default")

if __name__ == "__main__":
    generate_scss_variables() 