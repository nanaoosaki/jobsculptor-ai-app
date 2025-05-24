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
            _write_variables(f, tokens, "")
        
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

def _write_variables(file, obj, prefix):
    """Recursively write SCSS variables from nested objects."""
    for key, value in obj.items():
        # Convert dots to hyphens in variable names
        scss_key = key.replace('.', '-')
        full_key = f"{prefix}-{scss_key}" if prefix else scss_key
        
        if isinstance(value, dict):
            # Recursively handle nested objects
            _write_variables(file, value, full_key)
        else:
            # Write the variable
            file.write(f"${full_key}: {value};\n")

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