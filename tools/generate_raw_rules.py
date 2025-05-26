# Generate raw CSS rules from design tokens
# This replaces hardcoded SCSS with token-driven CSS generation

import json
import pathlib
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def load_design_tokens():
    """Load design tokens from JSON file."""
    repo_root = pathlib.Path(__file__).parent.parent
    tokens_path = repo_root / 'design_tokens.json'
    
    with open(tokens_path, 'r') as f:
        return json.load(f)

def build_raw_rules(tokens):
    """
    Build raw CSS rules from design tokens.
    These rules will be processed by the translator layer for each target engine.
    """
    
    # Use logical properties where possible - translator will convert as needed
    raw_rules = {
        # === RESET RULES FOR WEASYPRINT COMPATIBILITY ===
        ".tailored-resume-content": {
            "font-family": tokens["baseFontFamily"],
            "font-size": tokens["baseFontSize"],
            "line-height": str(tokens["font.lineHeight.tight"]),
            "color": tokens["textColor"],
        },
        
        ".tailored-resume-content p": {
            "margin-block": tokens["paragraph-margin-block"],
        },
        
        ".tailored-resume-content ul": {
            "margin-block": tokens["ul-margin-block"],
            "list-style-type": "none",
            "padding-left": "0",
        },
        
        ".tailored-resume-content ol": {
            "margin-block": tokens["ul-margin-block"],
            "padding-left": "0",
        },
        
        ".tailored-resume-content li": {
            "margin-block": tokens["li-margin-block"],
        },
        
        # === SPECIFIC CONTENT RESETS ===
        ".job-content p, .education-content p, .project-content p": {
            "margin-block": "0rem",
        },
        
        ".job-content ul, .education-content ul, .project-content ul": {
            "margin-block": "0rem",
        },
        
        ".job-content ol, .education-content ol, .project-content ol": {
            "margin-block": "0rem",
        },
        
        ".job-content li, .education-content li, .project-content li": {
            "margin-block": "0rem",
        },
        
        # === ROLE DESCRIPTION SPACING ===
        ".role-description-text": {
            "margin-top": tokens["role-description-margin-top"],
            "margin-bottom": tokens["role-description-margin-bottom"],
            "font-style": "italic",
            "color": "#555",
            "display": "block",
            "width": "100%",
        },
        
        # === ROLE BOX TO LIST SPACING ===
        ".role-box + ul": {
            "margin-top": tokens["role-list-margin-top"],
        },
        
        # === SECTION SPACING ===
        ".resume-section": {
            "margin-bottom": tokens["section-spacing-vertical"],
        },
        
        ".section-box": {
            "margin-bottom": tokens["section-box-margin-bottom"],
            "border": f"2px solid {tokens['primaryColor']}",
            "background": "transparent",
            "color": tokens["primaryColor"],
            "font-weight": str(tokens["font.weight.bold"]),
            "padding": f"{tokens['sectionHeaderPaddingVert']} {tokens['sectionHeaderPaddingHoriz']}",
            "font-size": tokens["sectionHeaderFontSize"],
            "line-height": tokens["sectionHeaderLineHeight"],
        },
        
        # === POSITION BAR SPACING ===
        ".position-bar": {
            "margin-top": tokens["position-bar-margin-top"],
            "margin-bottom": tokens["position-line-margin-bottom"],
            "background": tokens["color.positionBar.bg"],
            "padding": "0.25rem 0.45rem",
        },
        
        ".position-line": {
            "margin-bottom": tokens["position-line-margin-bottom"],
        },
        
        # === JOB CONTENT SPACING ===
        ".job-content": {
            "margin-top": tokens["job-content-margin-top"],
        },
        
        ".education-content": {
            "margin-top": tokens["job-content-margin-top"], 
        },
        
        ".project-content": {
            "margin-top": tokens["job-content-margin-top"],
        },
        
        # === BULLET SPACING ===
        ".bullets li": {
            "margin-bottom": tokens["bullet-spacing-after"],
            "line-height": str(tokens["font.lineHeight.tight"]),
            "position": "relative",
        },
        
        ".bullets li::before": {
            "content": '"\\2022 "',  # Unicode bullet character
            "color": tokens["color.bullet"],
            "font-weight": "normal",
        },
        
        # === SKILLS CONTENT ===
        ".skills-content": {
            "margin-left": tokens["content-left-margin"],
        },
        
        ".skills-content p": {
            "margin-bottom": tokens["space.bullet.y"],
        },
        
        ".skills-content ul": {
            "list-style-type": "none",
            "padding-left": "0",
        },
        
        ".skills-content li": {
            "margin-bottom": tokens["bullet-spacing-after"],
            "line-height": str(tokens["font.lineHeight.tight"]),
        },
        
        ".skills-content li::before": {
            "content": '"\\2022 "',  # Unicode bullet character
            "color": tokens["color.bullet"],
            "font-weight": "normal",
        },
        
        # === ROLE BOX STYLING ===
        ".role-box": {
            "border-color": tokens["roleBox"]["borderColor"],
            "border-width": f"{tokens['roleBox']['borderWidth']}px",
            "padding": f"{tokens['roleBox']['padding']}px",
            "background-color": tokens["roleBox"]["backgroundColor"],
            "color": tokens["roleBox"]["textColor"],
            "border-radius": f"{tokens['roleBox']['borderRadius']}px",
            "display": "flex",
            "justify-content": "space-between",
            "align-items": "center",
        },
        
        ".role-box .role": {
            "font-weight": "bold",
            "flex-grow": "1",
        },
        
        ".role-box .dates": {
            "font-style": "italic",
            "margin-left": "1rem",
            "white-space": "nowrap",
        },
        
        # === CONTACT SECTION ===
        ".contact-section": {
            "text-align": "center",
            "margin-bottom": "1rem",
        },
        
        ".contact-section .name": {
            "font-size": tokens["nameFontSize"],
            "font-weight": str(tokens["font.weight.bold"]),
            "color": tokens["darkColor"],
            "margin-bottom": "0.5rem",
        },
        
        ".contact-divider": {
            "border": "none",
            "height": "1px",
            "background-color": tokens["darkColor"],
            "width": tokens["contact-divider-width"],
            "margin": "1rem auto",
        },
        
        # === CONTENT ALIGNMENT ===
        ".summary-content, .experience-content, .education-content, .skills-content, .projects-content": {
            "margin-left": tokens["content-left-margin"],
        },
        
        # === PREVENT ORPHANED LIST ITEMS ===
        ".bullets li": {
            "break-inside": "avoid",
        },
        
        # === ACCESSIBILITY ===
        ".visually-hidden": {
            "position": "absolute !important",
            "width": "1px !important", 
            "height": "1px !important",
            "padding": "0 !important",
            "margin": "-1px !important",
            "overflow": "hidden !important",
            "clip": "rect(0, 0, 0, 0) !important",
            "white-space": "nowrap !important",
            "border": "0 !important",
        },
    }
    
    return raw_rules

def generate_raw_rules_file():
    """Generate Python file with raw CSS rules."""
    tokens = load_design_tokens()
    raw_rules = build_raw_rules(tokens)
    
    repo_root = pathlib.Path(__file__).parent.parent
    output_path = repo_root / 'static' / 'css' / 'raw_rules.py'
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Auto-generated raw CSS rules from design tokens\n")
        f.write("# Do not edit directly - regenerate with tools/generate_raw_rules.py\n\n")
        f.write("RAW_RULES = ")
        
        # Pretty-print the rules dictionary
        import pprint
        f.write(pprint.pformat(raw_rules, width=120, sort_dicts=False))
        f.write("\n")
    
    print(f"Generated raw CSS rules at {output_path}")
    return raw_rules

if __name__ == "__main__":
    generate_raw_rules_file() 