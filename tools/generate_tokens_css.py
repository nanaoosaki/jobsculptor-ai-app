import json
import pathlib
import sys

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
                # Keep the key as is for SCSS variable name, assuming keys are already kebab-case or valid
                # scss_key = ''.join(['-' + i.lower() if i.isupper() 
                #                  else i for i in key]).lstrip('-')
                scss_key = key # Use the JSON key directly
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

if __name__ == "__main__":
    generate_scss_variables() 