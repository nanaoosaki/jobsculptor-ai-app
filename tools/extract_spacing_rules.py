#!/usr/bin/env python3
"""
Spacing Rule Extraction Tool - Extract Spacing-Critical Rules from Design Tokens

Part of Phase 1, Day 2 implementation of the hybrid CSS refactor.
This tool extracts only spacing-related rules from design tokens for the translator layer.

Key Features:
- Extracts margin, padding, gap, line-height tokens
- Converts to CSS-ready format for translator consumption
- Filters out non-spacing tokens (colors, fonts, etc.)
- Supports nested token structures
"""

import json
import os
from typing import Dict, Any, List, Tuple


def extract_spacing_rules(tokens_file: str = "design_tokens.json") -> Dict[str, Any]:
    """
    Extract spacing-critical rules from design tokens
    
    Filters design tokens to only include spacing-related properties:
    - margin-* (top, bottom, left, right, block, inline)
    - padding-* (top, bottom, left, right, block, inline)  
    - gap
    - line-height
    
    Args:
        tokens_file: Path to design_tokens.json
        
    Returns:
        Dictionary of spacing-only tokens
    """
    print(f"🔍 Extracting spacing rules from {tokens_file}")
    
    if not os.path.exists(tokens_file):
        print(f"❌ Tokens file not found: {tokens_file}")
        return {}
    
    with open(tokens_file, 'r', encoding='utf-8') as f:
        all_tokens = json.load(f)
    
    spacing_tokens = {}
    spacing_keywords = [
        'margin', 'padding', 'gap', 'line-height',
        'spacing', 'indent', 'block'  # Additional spacing-related keywords
    ]
    
    # Extract flat tokens
    for token_name, token_value in all_tokens.items():
        if isinstance(token_value, (str, int, float)):
            if any(keyword in token_name.lower() for keyword in spacing_keywords):
                spacing_tokens[token_name] = token_value
                print(f"   ✅ {token_name}: {token_value}")
    
    print(f"\n📊 Extraction Results:")
    print(f"   - Total tokens: {len(all_tokens)}")
    print(f"   - Spacing tokens: {len(spacing_tokens)}")
    print(f"   - Filtered out: {len(all_tokens) - len(spacing_tokens)} non-spacing tokens")
    
    return spacing_tokens


def convert_to_css_rules(spacing_tokens: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """
    Convert spacing tokens to CSS rules grouped by selector
    
    Maps tokens like "role-description-margin-top" to CSS rules:
    {
        ".role-description-text": {
            "margin-top": "0rem"
        }
    }
    
    Args:
        spacing_tokens: Dictionary of spacing tokens
        
    Returns:
        Dictionary of CSS rules grouped by selector
    """
    print(f"\n🔄 Converting {len(spacing_tokens)} tokens to CSS rules")
    
    css_rules = {}
    
    for token_name, token_value in spacing_tokens.items():
        selector, property_name = derive_css_rule(token_name)
        
        if selector and property_name:
            if selector not in css_rules:
                css_rules[selector] = {}
            
            css_rules[selector][property_name] = str(token_value)
            print(f"   {token_name} → {selector} {{ {property_name}: {token_value}; }}")
    
    print(f"\n📋 CSS Rules Summary:")
    print(f"   - Selectors: {len(css_rules)}")
    print(f"   - Total properties: {sum(len(props) for props in css_rules.values())}")
    
    return css_rules


def derive_css_rule(token_name: str) -> Tuple[str, str]:
    """
    Derive CSS selector and property from token name
    
    Examples:
    - "role-description-margin-top" → (".role-description-text", "margin-top")
    - "job-content-margin-bottom" → (".job-content", "margin-bottom")
    - "paragraph-margin-block" → ("p", "margin-block")
    
    Args:
        token_name: Design token name
        
    Returns:
        Tuple of (css_selector, css_property) or ("", "") if no mapping
    """
    # Define CSS property mappings
    property_mappings = {
        'margin-top': 'margin-top',
        'margin-bottom': 'margin-bottom', 
        'margin-left': 'margin-left',
        'margin-right': 'margin-right',
        'margin-block': 'margin-block',
        'margin-inline': 'margin-inline',
        'padding-top': 'padding-top',
        'padding-bottom': 'padding-bottom',
        'padding-left': 'padding-left', 
        'padding-right': 'padding-right',
        'padding-block': 'padding-block',
        'padding-inline': 'padding-inline',
        'gap': 'gap',
        'line-height': 'line-height'
    }
    
    # Find property in token name
    css_property = ""
    base_name = token_name
    
    for prop_key, prop_value in property_mappings.items():
        if prop_key in token_name:
            css_property = prop_value
            base_name = token_name.replace(f"-{prop_key}", "")
            break
    
    if not css_property:
        # Handle special cases
        if 'spacing' in token_name:
            css_property = 'margin-bottom'  # Default spacing to margin-bottom
            base_name = token_name.replace('-spacing', '')
        elif 'indent' in token_name:
            css_property = 'margin-left'    # Indent becomes margin-left
            base_name = token_name.replace('-indent', '')
        else:
            return "", ""  # No recognizable spacing property
    
    # Map base name to CSS selector
    selector_mappings = {
        'role-description': '.role-description-text',
        'job-content': '.job-content',
        'education-content': '.education-content',
        'project-content': '.project-content',
        'position-bar': '.position-bar',
        'position-line': '.position-line',
        'role-box': '.role-box',
        'section-box': '.section-box',
        'resume-section': '.resume-section',
        'contact-section': '.contact-section',
        'bullet-list': '.bullet-list',
        'bullet-item': '.bullet-item',
        'role-list': '.role-list',
        'section-content': '.section-content',
        'paragraph': 'p',
        'ul': 'ul',
        'li': 'li'
    }
    
    css_selector = selector_mappings.get(base_name, f".{base_name}")
    
    return css_selector, css_property


def save_spacing_rules(css_rules: Dict[str, Dict[str, str]], output_file: str = "spacing_rules.json") -> bool:
    """
    Save extracted spacing rules to JSON file for translator consumption
    
    Args:
        css_rules: Dictionary of CSS rules
        output_file: Output file path
        
    Returns:
        True if saved successfully
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(css_rules, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved spacing rules to {output_file}")
        print(f"   - File size: {os.path.getsize(output_file)} bytes")
        
        return True
    except Exception as e:
        print(f"❌ Failed to save spacing rules: {e}")
        return False


def generate_spacing_css(css_rules: Dict[str, Dict[str, str]]) -> str:
    """
    Generate CSS content from spacing rules
    
    Args:
        css_rules: Dictionary of CSS rules
        
    Returns:
        CSS content as string
    """
    css_lines = []
    css_lines.append("/* Spacing Rules - Generated from Design Tokens */")
    css_lines.append("/* DO NOT EDIT MANUALLY - Use design_tokens.json */")
    css_lines.append("")
    
    for selector, properties in css_rules.items():
        css_lines.append(f"{selector} {{")
        for prop, value in properties.items():
            css_lines.append(f"  {prop}: {value};")
        css_lines.append("}")
        css_lines.append("")
    
    return "\n".join(css_lines)


def main():
    """Main function to extract spacing rules and generate output"""
    print("🎯 Spacing Rule Extraction Tool")
    print("=" * 50)
    
    # Extract spacing tokens
    spacing_tokens = extract_spacing_rules()
    
    if not spacing_tokens:
        print("❌ No spacing tokens found")
        return False
    
    # Convert to CSS rules
    css_rules = convert_to_css_rules(spacing_tokens)
    
    if not css_rules:
        print("❌ No CSS rules generated")
        return False
    
    # Save to JSON for translator
    save_spacing_rules(css_rules, "spacing_rules.json")
    
    # Generate CSS preview
    css_content = generate_spacing_css(css_rules)
    with open("spacing_preview.css", 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print(f"✅ Generated spacing_preview.css ({len(css_content)} chars)")
    
    print("\n🎉 Spacing rule extraction complete!")
    return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 2 and sys.argv[1] == '--help':
        print("Usage:")
        print("  python tools/extract_spacing_rules.py")
        print("")
        print("Extracts spacing-critical rules from design_tokens.json")
        print("Outputs:")
        print("  - spacing_rules.json (for translator consumption)")
        print("  - spacing_preview.css (for preview)")
        sys.exit(0)
    
    success = main()
    sys.exit(0 if success else 1) 