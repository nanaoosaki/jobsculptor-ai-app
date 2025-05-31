#!/usr/bin/env python3
"""
CSS Safety Validator - o3's Suggestion #5
Guards against regression by ensuring critical CSS rules remain in place.
"""

import re
import sys
from pathlib import Path

def validate_print_css():
    """Validate that print.css has the critical @page margin: 0 rule at the top."""
    
    print_css_path = Path("static/css/print.css")
    
    if not print_css_path.exists():
        print(f"❌ FAIL: {print_css_path} does not exist")
        return False
    
    try:
        with open(print_css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find @page blocks and check if they contain margin: 0
        page_blocks = re.findall(r'@page\s*\{[^}]*\}', content, re.MULTILINE | re.DOTALL)
        
        found_zero_margin = False
        found_line = None
        
        for block in page_blocks:
            # Check if this @page block has margin: 0 or margin: 0cm
            if re.search(r'margin\s*:\s*0(?:cm)?\s*(?:!important)?', block):
                found_zero_margin = True
                # Find line number
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if '@page' in line:
                        found_line = i
                        break
                break
        
        if found_zero_margin:
            print(f"✅ PASS: @page margin: 0 rule found on line {found_line}")
            print(f"   Block content: {page_blocks[0][:100]}...")
            
            # Check if it's reasonably early in the file (within first 400 lines)
            if found_line and found_line > 400:
                print(f"⚠️  WARNING: @page rule is quite late in file (line {found_line})")
                print("   For optimal WeasyPrint behavior, it should be earlier")
            
            return True
        else:
            print("❌ FAIL: @page { margin: 0 } or @page { margin: 0cm } NOT found")
            print("   This is critical - PDF alignment will be broken!")
            if page_blocks:
                print(f"   Found @page blocks but none with margin: 0: {page_blocks[0][:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ ERROR reading {print_css_path}: {e}")
        return False

def validate_container_padding_consistency():
    """Validate that container padding is consistent between preview and print CSS."""
    
    preview_css_path = Path("static/css/preview.css")
    print_css_path = Path("static/css/print.css")
    
    if not preview_css_path.exists() or not print_css_path.exists():
        print("❌ FAIL: CSS files missing for padding consistency check")
        return False
    
    try:
        # Extract padding values
        preview_padding = extract_container_padding(preview_css_path)
        print_padding = extract_container_padding(print_css_path)
        
        if preview_padding and print_padding:
            if preview_padding == print_padding:
                print(f"✅ PASS: Container padding consistent ({preview_padding})")
                return True
            else:
                print(f"❌ FAIL: Container padding mismatch")
                print(f"   Preview: {preview_padding}")
                print(f"   Print:   {print_padding}")
                return False
        else:
            print("❌ FAIL: Could not extract container padding values")
            return False
            
    except Exception as e:
        print(f"❌ ERROR validating container padding: {e}")
        return False

def extract_container_padding(css_path):
    """Extract .tailored-resume-content padding value from CSS file."""
    
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for .tailored-resume-content { ... padding: VALUE; ... }
    pattern = r'\.tailored-resume-content\s*\{[^}]*padding:\s*([^;]+);'
    match = re.search(pattern, content)
    
    if match:
        return match.group(1).strip()
    return None

def validate_bullet_hanging_indent():
    """Validate that bullet hanging indent tokens are properly set."""
    
    tokens_path = Path("design_tokens.json")
    
    if not tokens_path.exists():
        print("❌ FAIL: design_tokens.json not found")
        return False
    
    try:
        import json
        with open(tokens_path, 'r', encoding='utf-8') as f:
            tokens = json.load(f)
        
        # Check for bullet indent tokens
        bullet_padding = tokens.get("bullet-item-padding-left")
        docx_indent = tokens.get("docx-bullet-left-indent-cm") 
        docx_hanging = tokens.get("docx-bullet-hanging-indent-cm")
        
        if bullet_padding and docx_indent and docx_hanging:
            print(f"✅ PASS: Bullet hanging indent tokens present")
            print(f"   HTML: {bullet_padding}")
            print(f"   DOCX: {docx_indent}cm / {docx_hanging}cm hanging")
            return True
        else:
            print("❌ FAIL: Missing bullet hanging indent tokens")
            return False
            
    except Exception as e:
        print(f"❌ ERROR validating bullet tokens: {e}")
        return False

def main():
    """Run all CSS safety validations."""
    
    print("🔍 CSS SAFETY VALIDATOR - o3's Regression Guards")
    print("=" * 50)
    
    all_passed = True
    
    # Validation 1: Critical @page margin rule
    print("\n1. Validating critical @page margin: 0 rule...")
    if not validate_print_css():
        all_passed = False
    
    # Validation 2: Container padding consistency
    print("\n2. Validating container padding consistency...")
    if not validate_container_padding_consistency():
        all_passed = False
    
    # Validation 3: Bullet hanging indent
    print("\n3. Validating bullet hanging indent tokens...")
    if not validate_bullet_hanging_indent():
        all_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED - CSS is safe for deployment")
        return 0
    else:
        print("❌ VALIDATION FAILURES DETECTED - Fix before deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 