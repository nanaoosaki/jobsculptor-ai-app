# Test script for the new translator layer
# Verifies that the translator correctly transforms CSS based on engine capabilities

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from rendering.compat import translate, to_css, CAPABILITY
from static.css.raw_rules import RAW_RULES

def test_translator():
    """Test the translator with different engines."""
    
    print("=== TESTING TRANSLATOR LAYER ===\n")
    
    # Test with browser engine (should preserve logical properties)
    print("1. BROWSER ENGINE:")
    browser_ast = translate(RAW_RULES, "browser")
    browser_css = to_css(browser_ast)
    print("Sample browser CSS:")
    print(browser_css[:500] + "...\n")
    
    # Test with WeasyPrint (should convert logical to physical)
    print("2. WEASYPRINT ENGINE:")
    weasy_ast = translate(RAW_RULES, "weasyprint")
    weasy_css = to_css(weasy_ast)
    print("Sample WeasyPrint CSS:")
    print(weasy_css[:500] + "...\n")
    
    # Test with Word engine
    print("3. WORD ENGINE:")
    word_ast = translate(RAW_RULES, "word")
    word_css = to_css(word_ast)
    print("Sample Word CSS:")
    print(word_css[:500] + "...\n")
    
    # Verify logical property transformation
    print("4. LOGICAL PROPERTY TRANSFORMATION TEST:")
    
    # Check if margin-block was transformed in WeasyPrint
    test_selector = ".tailored-resume-content p"
    if test_selector in browser_ast:
        browser_margin = browser_ast[test_selector].get("margin-block", "NOT_FOUND")
        print(f"Browser margin-block: {browser_margin}")
    
    if test_selector in weasy_ast:
        weasy_margin_top = weasy_ast[test_selector].get("margin-top", "NOT_FOUND")
        weasy_margin_bottom = weasy_ast[test_selector].get("margin-bottom", "NOT_FOUND") 
        weasy_margin_block = weasy_ast[test_selector].get("margin-block", "NOT_FOUND")
        print(f"WeasyPrint margin-top: {weasy_margin_top}")
        print(f"WeasyPrint margin-bottom: {weasy_margin_bottom}")
        print(f"WeasyPrint margin-block: {weasy_margin_block}")
    
    print("\n=== TRANSLATOR TEST COMPLETE ===")

if __name__ == "__main__":
    test_translator() 