#!/usr/bin/env python3
"""
CSS Safety Validator - Auto-Derived Selectors & Critical Functionality Protection

Part of Phase 1, Day 1 implementation of the hybrid CSS refactor.
This validator ensures spacing enhancement preserves all critical functionality.

Key Features:
- Auto-derives critical selectors from design_tokens.json (no manual drift)
- Validates file size (prevents empty CSS generation)
- Protects critical styling tokens (colors, fonts)
- Enforces cascade layer requirements
"""

import json
import os
import re
from pathlib import Path
from typing import Set, List, Dict, Any


class ValidationError(Exception):
    """Raised when CSS validation fails"""
    pass


def validate_css_safety(original_css_path: str, spacing_css_path: str) -> bool:
    """
    Ensure spacing enhancement preserves all critical functionality
    
    Args:
        original_css_path: Path to legacy CSS file (preview.css or print.css)
        spacing_css_path: Path to generated spacing CSS file
        
    Returns:
        True if validation passes
        
    Raises:
        ValidationError: If validation fails
    """
    print(f"🔍 Validating CSS safety: {original_css_path} + {spacing_css_path}")
    
    # Read files
    if not os.path.exists(original_css_path):
        raise ValidationError(f"Original CSS missing: {original_css_path}")
    
    if not os.path.exists(spacing_css_path):
        raise ValidationError(f"Spacing CSS missing: {spacing_css_path}")
    
    with open(original_css_path, 'r', encoding='utf-8') as f:
        original_css = f.read()
    
    with open(spacing_css_path, 'r', encoding='utf-8') as f:
        spacing_css = f.read()
    
    # Auto-derive critical selectors from design tokens (no manual drift)
    critical_selectors = extract_selectors_from_design_tokens("design_tokens.json")
    
    # Size check - spacing.css should be reasonable size (not empty)
    if len(spacing_css) < 100:
        raise ValidationError(f"spacing.css too small ({len(spacing_css)} chars) - likely generation failed")
    
    # Critical selector preservation in original CSS
    missing_selectors = []
    for selector in critical_selectors:
        if selector not in original_css:
            missing_selectors.append(selector)
    
    if missing_selectors:
        raise ValidationError(f"Critical selectors missing from legacy CSS: {missing_selectors}")
    
    # Color/font preservation in original CSS
    critical_tokens = ['#4a6fdc', '#343a40', 'Calibri', 'Inter']
    missing_tokens = []
    for token in critical_tokens:
        if token not in original_css:
            missing_tokens.append(token)
    
    if missing_tokens:
        raise ValidationError(f"Critical styling tokens missing: {missing_tokens}")
    
    # Ensure spacing rules are in cascade layer (modern browser protection)
    if '@layer spacing' not in spacing_css:
        raise ValidationError("Spacing rules must be in @layer spacing for cascade protection")
    
    # Validate spacing CSS contains expected properties
    spacing_properties = ['margin-top', 'margin-bottom', 'margin-block', 'padding']
    has_spacing_props = any(prop in spacing_css for prop in spacing_properties)
    if not has_spacing_props:
        raise ValidationError("Spacing CSS contains no spacing properties")
    
    print(f"✅ CSS safety validation passed:")
    print(f"   - Original CSS: {len(original_css):,} chars")
    print(f"   - Spacing CSS: {len(spacing_css):,} chars") 
    print(f"   - Critical selectors: {len(critical_selectors)} validated")
    print(f"   - Critical tokens: {len(critical_tokens)} preserved")
    
    return True


def extract_selectors_from_design_tokens(tokens_file: str) -> List[str]:
    """
    Auto-derive critical selectors from design tokens - no manual maintenance needed
    
    Maps spacing tokens to their corresponding CSS selectors:
    - "role-description-margin-top" → ".role-description-text"
    - "job-content-margin-bottom" → ".job-content" 
    - "position-bar-margin-top" → ".position-bar"
    
    Args:
        tokens_file: Path to design_tokens.json
        
    Returns:
        List of CSS selectors that must be preserved
    """
    if not os.path.exists(tokens_file):
        print(f"⚠️ Design tokens file not found: {tokens_file}")
        return []
    
    with open(tokens_file, 'r', encoding='utf-8') as f:
        tokens = json.load(f)
    
    selectors = set()
    
    # Extract selectors from spacing-related tokens
    for token_name in tokens:
        if any(prop in token_name for prop in ['margin', 'padding', 'gap']):
            selector = derive_selector_from_token(token_name)
            if selector:
                selectors.add(selector)
    
    # Add known critical selectors from existing CSS patterns
    critical_patterns = [
        '.tailored-resume-content',
        '.job-content', 
        '.education-content',
        '.project-content',
        '.role-description-text',
        '.position-bar',
        '.role-box',
        '.section-box',
        '.resume-section',
        '.contact-section'
    ]
    
    selectors.update(critical_patterns)
    
    return sorted(list(selectors))


def derive_selector_from_token(token_name: str) -> str:
    """
    Derive CSS selector from design token name
    
    Examples:
    - "role-description-margin-top" → ".role-description-text"
    - "job-content-margin-bottom" → ".job-content"
    - "position-bar-margin-top" → ".position-bar"
    - "section-box-margin-bottom" → ".section-box"
    
    Args:
        token_name: Design token name
        
    Returns:
        CSS selector or empty string if no mapping
    """
    # Remove spacing property suffixes
    base_name = token_name
    spacing_props = ['-margin-top', '-margin-bottom', '-margin-left', '-margin-right', 
                    '-margin-block', '-margin-inline', '-padding-top', '-padding-bottom',
                    '-padding-left', '-padding-right', '-padding-block', '-padding-inline',
                    '-gap', '-line-height']
    
    for prop in spacing_props:
        if base_name.endswith(prop):
            base_name = base_name[:-len(prop)]
            break
    
    # Skip non-spacing tokens
    if base_name == token_name:
        return ""
    
    # Map common patterns
    selector_mappings = {
        'role-description': '.role-description-text',
        'job-content': '.job-content',
        'education-content': '.education-content', 
        'project-content': '.project-content',
        'position-bar': '.position-bar',
        'role-box': '.role-box',
        'section-box': '.section-box',
        'resume-section': '.resume-section',
        'contact-section': '.contact-section',
        'paragraph': 'p',
        'ul': 'ul',
        'li': 'li'
    }
    
    if base_name in selector_mappings:
        return selector_mappings[base_name]
    
    # Default pattern: convert kebab-case to CSS class
    return f".{base_name}"


def generate_critical_selectors_report(tokens_file: str = "design_tokens.json") -> None:
    """
    Generate a report of all critical selectors for documentation
    """
    selectors = extract_selectors_from_design_tokens(tokens_file)
    
    print(f"\n📋 Critical Selectors Report ({len(selectors)} total):")
    print("=" * 50)
    
    for selector in selectors:
        print(f"  {selector}")
    
    print("=" * 50)
    print(f"ℹ️ These selectors are auto-derived from {tokens_file}")
    print("ℹ️ They must be preserved in legacy CSS for functionality")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 2 and sys.argv[1] == '--report':
        # Generate critical selectors report
        generate_critical_selectors_report()
    elif len(sys.argv) == 3:
        # Validate CSS safety
        original_css = sys.argv[1]
        spacing_css = sys.argv[2]
        
        try:
            validate_css_safety(original_css, spacing_css)
            print("🎉 CSS Safety Validation PASSED")
            sys.exit(0)
        except ValidationError as e:
            print(f"❌ CSS Safety Validation FAILED: {e}")
            sys.exit(1)
    else:
        print("Usage:")
        print("  python tools/css_safety_validator.py preview.css spacing.css")
        print("  python tools/css_safety_validator.py --report")
        sys.exit(1) 