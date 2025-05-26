# Comprehensive test for spacing implementation
# Validates that zero spacing is correctly implemented across all engines

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from rendering.compat import translate, to_css, CAPABILITY
from static.css.raw_rules import RAW_RULES

def test_spacing_implementation():
    """Test that spacing implementation works correctly across engines."""
    
    print("=== TESTING SPACING IMPLEMENTATION ===\n")
    
    # Key selectors to test for zero spacing
    test_selectors = [
        ".tailored-resume-content p",
        ".job-content p, .education-content p, .project-content p",
        ".role-description-text",
        ".role-box + ul",
        ".job-content",
        ".bullets li"
    ]
    
    engines = ['browser', 'weasyprint', 'word']
    
    for engine in engines:
        print(f"=== {engine.upper()} ENGINE ===")
        
        # Translate rules for this engine
        translated_ast = translate(RAW_RULES, engine)
        
        # Check each test selector
        for selector in test_selectors:
            if selector in translated_ast:
                decls = translated_ast[selector]
                
                # Check for zero spacing values
                spacing_props = [
                    'margin-top', 'margin-bottom', 'margin-block',
                    'padding-top', 'padding-bottom', 'padding-block'
                ]
                
                zero_spacing = []
                for prop in spacing_props:
                    if prop in decls and decls[prop] == '0rem':
                        zero_spacing.append(prop)
                
                if zero_spacing:
                    print(f"  ✓ {selector}: {', '.join(zero_spacing)} = 0rem")
                else:
                    print(f"  - {selector}: No zero spacing found")
            else:
                print(f"  ! {selector}: Selector not found")
        
        print()
    
    # Test logical property transformation specifically
    print("=== LOGICAL PROPERTY TRANSFORMATION TEST ===")
    
    test_selector = ".tailored-resume-content p"
    
    # Browser should preserve logical properties
    browser_ast = translate(RAW_RULES, "browser")
    if test_selector in browser_ast:
        browser_decls = browser_ast[test_selector]
        if "margin-block" in browser_decls:
            print(f"✓ Browser preserves logical: margin-block = {browser_decls['margin-block']}")
        else:
            print("! Browser missing margin-block")
    
    # WeasyPrint should convert to physical properties
    weasy_ast = translate(RAW_RULES, "weasyprint")
    if test_selector in weasy_ast:
        weasy_decls = weasy_ast[test_selector]
        if "margin-top" in weasy_decls and "margin-bottom" in weasy_decls:
            print(f"✓ WeasyPrint converts to physical: margin-top = {weasy_decls['margin-top']}, margin-bottom = {weasy_decls['margin-bottom']}")
        else:
            print("! WeasyPrint missing physical properties")
        
        if "margin-block" in weasy_decls:
            print("! WeasyPrint still has logical properties (should be converted)")
    
    print("\n=== SPACING TEST COMPLETE ===")

def test_css_generation():
    """Test that CSS generation produces valid output."""
    
    print("=== TESTING CSS GENERATION ===\n")
    
    engines = ['browser', 'weasyprint', 'word']
    
    for engine in engines:
        print(f"Testing {engine} CSS generation...")
        
        # Translate and generate CSS
        translated_ast = translate(RAW_RULES, engine)
        css_output = to_css(translated_ast)
        
        # Basic validation
        if css_output:
            print(f"  ✓ Generated {len(css_output)} characters of CSS")
            
            # Check for key patterns
            if "margin-top: 0rem" in css_output or "margin-block: 0rem" in css_output:
                print("  ✓ Contains zero margin rules")
            else:
                print("  ! Missing zero margin rules")
                
            # Check for proper CSS syntax
            if css_output.count('{') == css_output.count('}'):
                print("  ✓ Balanced CSS braces")
            else:
                print("  ! Unbalanced CSS braces")
        else:
            print(f"  ! No CSS generated for {engine}")
        
        print()
    
    print("=== CSS GENERATION TEST COMPLETE ===")

if __name__ == "__main__":
    test_spacing_implementation()
    test_css_generation() 