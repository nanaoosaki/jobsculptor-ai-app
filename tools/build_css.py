# Build CSS using the new translator layer
# Generates engine-specific CSS from design tokens

import json
import pathlib
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rendering.compat import translate, to_css
from tools.generate_raw_rules import load_design_tokens, build_raw_rules

def build_css_for_engines():
    """Build CSS files for different rendering engines."""
    
    print("=== BUILDING CSS WITH TRANSLATOR LAYER ===\n")
    
    # Load tokens and build raw rules
    tokens = load_design_tokens()
    raw_rules = build_raw_rules(tokens)
    
    repo_root = pathlib.Path(__file__).parent.parent
    css_dir = repo_root / 'static' / 'css'
    css_dir.mkdir(parents=True, exist_ok=True)
    
    # Build CSS for each engine
    engines = {
        'browser': 'preview.css',
        'weasyprint': 'print.css'
    }
    
    for engine, filename in engines.items():
        print(f"Building {filename} for {engine} engine...")
        
        # Translate rules for this engine
        translated_ast = translate(raw_rules, engine)
        
        # Generate CSS
        css_content = to_css(translated_ast)
        
        # Add header comment
        header = f"""/* Auto-generated CSS for {engine} engine */
/* Generated from design tokens via translator layer */
/* Do not edit directly - regenerate with tools/build_css.py */

"""
        
        # Write CSS file
        output_path = css_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(header + css_content)
        
        print(f"✓ Generated {output_path}")
        print(f"  Rules: {len(translated_ast)}")
        print(f"  Size: {len(css_content)} characters\n")
    
    print("=== CSS BUILD COMPLETE ===")

def build_css_variables():
    """Build CSS custom properties from design tokens."""
    
    print("Building CSS custom properties...")
    
    tokens = load_design_tokens()
    repo_root = pathlib.Path(__file__).parent.parent
    output_path = repo_root / 'static' / 'css' / '_variables.css'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("/* Auto-generated CSS custom properties from design tokens */\n")
        f.write("/* Do not edit directly - regenerate with tools/build_css.py */\n\n")
        f.write(":root {\n")
        
        # Flatten tokens for CSS custom properties
        def flatten_tokens(obj, prefix=""):
            for key, value in obj.items():
                if isinstance(value, dict):
                    yield from flatten_tokens(value, f"{prefix}{key}-")
                else:
                    css_key = f"{prefix}{key}".replace('.', '-').replace('_', '-')
                    yield f"  --{css_key}: {value};\n"
        
        for line in flatten_tokens(tokens):
            f.write(line)
        
        f.write("}\n")
    
    print(f"✓ Generated {output_path}")

if __name__ == "__main__":
    build_css_for_engines()
    build_css_variables() 