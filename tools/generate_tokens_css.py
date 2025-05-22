import json
import pathlib
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenValidationError(Exception):
    """Custom exception for token validation errors."""
    pass

def validate_tokens_version(tokens):
    """Validate the token version to prevent using outdated tokens."""
    version = tokens.get('tokensVersion')
    if not version:
        raise TokenValidationError("Missing tokensVersion in design tokens")
    
    logger.info(f"Using token version: {version}")

def validate_token_object(token_name, token_obj):
    """Validate a token object including the deprecation field."""
    # Check for deprecated flag
    if isinstance(token_obj, dict) and token_obj.get('deprecated', False):
        logger.warning(f"Token '{token_name}' is marked as deprecated and will be removed in a future version")
    
    return token_obj

def generate_css_variables(tokens, output_path, is_print=False):
    """Generates CSS variables from tokens with validation."""
    try:
        # Validate token version
        validate_tokens_version(tokens)
        
        with open(output_path, 'w') as f:
            f.write("/* Auto-generated from design_tokens.json. Do not edit directly. */\n\n")
            f.write(":root {\n")
            
            # Process all tokens except nested objects
            for key, value in tokens.items():
                if isinstance(value, dict):
                    # Skip nested objects - they'll be handled specifically
                    continue
                
                # Convert dots to hyphens in variable names
                css_key = key.replace('.', '-')
                f.write(f"  --{css_key}: {value};\n")
            
            # Add job title box variables if present
            if 'jobTitleBox' in tokens:
                job_title_box = validate_token_object('jobTitleBox', tokens['jobTitleBox'])
                
                # Required keys for jobTitleBox
                required_keys = ['backgroundColor', 'borderColor', 'borderWidth', 'borderStyle']
                missing_keys = [key for key in required_keys if key not in job_title_box]
                
                if missing_keys:
                    raise TokenValidationError(f"Missing required jobTitleBox properties: {', '.join(missing_keys)}")
                
                # Add each jobTitleBox property as a CSS variable
                for prop, value in job_title_box.items():
                    if prop not in ['docx', 'deprecated']:  # Skip docx specific properties and metadata
                        f.write(f"  --job-title-box-{prop}: {value};\n")
                
                # Add line-height variable for print CSS to match DOCX
                if is_print and 'lineHeight' in job_title_box:
                    f.write(f"  --job-title-box-line-height: {job_title_box['lineHeight']};\n")
            
            f.write("}\n")
        
        logger.info(f"Successfully generated {output_path}")

    except TokenValidationError as e:
        logger.error(f"Token validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

def generate_scss_variables():
    """Reads design tokens and generates CSS variable files for both preview and print."""
    try:
        # Assuming script is in tools/ and tokens are at root
        repo_root = pathlib.Path(__file__).parent.parent 
        tokens_path = repo_root / 'design_tokens.json'
        static_dir = repo_root / 'static'
        css_dir = static_dir / 'css'
        
        # Ensure output directories exist
        css_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Reading tokens from: {tokens_path}")
        
        with open(tokens_path, 'r') as f:
            tokens = json.load(f)
        
        # Generate preview CSS variables
        preview_css_path = css_dir / 'preview.css'
        print(f"Writing preview CSS variables to: {preview_css_path}")
        generate_css_variables(tokens, preview_css_path, is_print=False)
        
        # Generate print CSS variables
        print_css_path = css_dir / 'print.css'
        print(f"Writing print CSS variables to: {print_css_path}")
        generate_css_variables(tokens, print_css_path, is_print=True)

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