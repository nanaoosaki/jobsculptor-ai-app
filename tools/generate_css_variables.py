import json
import pathlib
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_css_variables():
    """Reads design tokens and generates CSS custom properties file."""
    try:
        # Assuming script is in tools/ and tokens are at root
        repo_root = pathlib.Path(__file__).parent.parent 
        tokens_path = repo_root / 'design_tokens.json'
        output_dir = repo_root / 'static' / 'css'
        output_path = output_dir / '_variables.css'

        print(f"Reading tokens from: {tokens_path}")
        print(f"Writing CSS variables to: {output_path}")

        with open(tokens_path, 'r') as f:
            tokens = json.load(f)

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write("/* Auto-generated CSS custom properties from design_tokens.json. Do not edit directly. */\n\n")
            f.write(":root {\n")
            _write_css_variables(f, tokens, "")
            f.write("}\n")
        
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

def _write_css_variables(file, obj, prefix):
    """Recursively write CSS custom properties from nested objects."""
    for key, value in obj.items():
        # Convert camelCase to kebab-case and handle dots
        css_key = _camel_to_kebab(key.replace('.', '-'))
        full_key = f"{prefix}-{css_key}" if prefix else css_key
        
        if isinstance(value, dict):
            # Recursively handle nested objects
            _write_css_variables(file, value, full_key)
        else:
            # Write the CSS custom property
            file.write(f"  --{full_key}: {value};\n")

def _camel_to_kebab(name):
    """Convert camelCase to kebab-case."""
    import re
    # Insert a hyphen before any uppercase letter that follows a lowercase letter
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    # Insert a hyphen before any uppercase letter that follows a lowercase letter or digit
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()

if __name__ == "__main__":
    generate_css_variables() 