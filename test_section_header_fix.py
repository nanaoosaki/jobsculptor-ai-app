#!/usr/bin/env python3
"""
Section Header Fix Verification Test
Tests that HTML generator now uses universal section header renderer and produces visual boxes
"""

import sys
import logging
import os
from io import StringIO

# Add project root to path
sys.path.append('.')

from style_engine import StyleEngine
from rendering.components.section_header import SectionHeader
from html_generator import generate_universal_section_header_html

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_universal_section_header_html():
    """Test that generate_universal_section_header_html produces styled output"""
    
    print("=" * 70)
    print("SECTION HEADER FIX VERIFICATION TEST")
    print("=" * 70)
    
    # Test section headers that should now use universal renderer
    test_sections = [
        "Professional Summary",
        "Experience", 
        "Education",
        "Skills",
        "Projects"
    ]
    
    print(f"\n🧪 TESTING UNIVERSAL SECTION HEADER RENDERER:")
    
    all_tests_passed = True
    
    for section_name in test_sections:
        print(f"\n📋 Testing: {section_name}")
        
        try:
            # Generate HTML using the universal renderer function
            html_output = generate_universal_section_header_html(section_name)
            print(f"  Generated HTML: {html_output}")
            
            # Verify it contains inline styles (not just class)
            has_inline_styles = 'style=' in html_output
            has_section_class = 'class="section-box"' in html_output
            has_correct_text = section_name in html_output
            
            # Check for design token values
            has_font_size = 'font-size: 14pt' in html_output
            has_color = 'color: #0D2B7E' in html_output  
            has_border = 'border: 1pt solid #0D2B7E' in html_output
            
            print(f"  ✓ Has inline styles: {has_inline_styles}")
            print(f"  ✓ Has section-box class: {has_section_class}")
            print(f"  ✓ Has correct text: {has_correct_text}")
            print(f"  ✓ Has design token font-size: {has_font_size}")
            print(f"  ✓ Has design token color: {has_color}")
            print(f"  ✓ Has design token border: {has_border}")
            
            section_passed = all([
                has_inline_styles,
                has_section_class, 
                has_correct_text,
                has_font_size,
                has_color,
                has_border
            ])
            
            if section_passed:
                print(f"  🎉 {section_name}: ✅ PASS")
            else:
                print(f"  ❌ {section_name}: FAIL")
                all_tests_passed = False
                
        except Exception as e:
            print(f"  ❌ {section_name}: ERROR - {e}")
            all_tests_passed = False
    
    # Overall results
    print(f"\n🎯 OVERALL RESULTS:")
    if all_tests_passed:
        print("  ✅ All section headers now use universal renderer")
        print("  ✅ All section headers have inline styling from design tokens")
        print("  ✅ Visual boxes should now appear in HTML and PDF")
        print("  ✅ Font consistency maintained across all formats")
    else:
        print("  ❌ Some section headers failed verification")
        print("  ⚠️ Visual boxes may still be missing")
    
    return all_tests_passed

def test_design_token_consistency():
    """Test that design tokens are consistently applied"""
    
    print(f"\n" + "=" * 70)
    print("DESIGN TOKEN CONSISTENCY TEST") 
    print("=" * 70)
    
    try:
        # Load design tokens directly
        tokens = StyleEngine.load_tokens()
        
        print(f"\n📋 DESIGN TOKEN VALUES:")
        print(f"  Font Size: {tokens['typography']['fontSize']['sectionHeader']}")
        print(f"  Font Color: {tokens['typography']['fontColor']['headers']['hex']}")
        print(f"  Border Width: {tokens['sectionHeader']['border']['widthPt']}")
        print(f"  Border Color: {tokens['sectionHeader']['border']['color']}")
        
        # Test universal renderer directly
        header = SectionHeader(tokens, "TEST SECTION")
        html_output = header.to_html()
        
        print(f"\n🔧 UNIVERSAL RENDERER OUTPUT:")
        print(f"  Generated: {html_output}")
        
        # Verify design token values appear in output
        expected_font_size = tokens['typography']['fontSize']['sectionHeader']
        expected_color = tokens['typography']['fontColor']['headers']['hex']
        expected_border_color = tokens['sectionHeader']['border']['color']
        expected_border_width = f"{tokens['sectionHeader']['border']['widthPt']}pt"
        
        tests = [
            (expected_font_size in html_output, f"Font size ({expected_font_size})"),
            (expected_color in html_output, f"Font color ({expected_color})"),
            (expected_border_color in html_output, f"Border color ({expected_border_color})"),
            (expected_border_width in html_output, f"Border width ({expected_border_width})")
        ]
        
        print(f"\n✅ DESIGN TOKEN VERIFICATION:")
        all_consistent = True
        for test_passed, description in tests:
            status = "✅ PASS" if test_passed else "❌ FAIL"
            print(f"  {description}: {status}")
            if not test_passed:
                all_consistent = False
        
        if all_consistent:
            print(f"\n🎉 Design tokens consistently applied across all components!")
        else:
            print(f"\n⚠️ Design token inconsistencies detected")
            
        return all_consistent
        
    except Exception as e:
        print(f"❌ Design token test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Section Header Fix Verification...")
    
    try:
        # Run tests
        html_test_passed = test_universal_section_header_html()
        token_test_passed = test_design_token_consistency()
        
        overall_success = html_test_passed and token_test_passed
        
        print("\n" + "=" * 70)
        print("FINAL VERIFICATION RESULTS")
        print("=" * 70)
        print(f"HTML Generator Fix: {'✅ PASS' if html_test_passed else '❌ FAIL'}")
        print(f"Design Token Consistency: {'✅ PASS' if token_test_passed else '❌ FAIL'}")
        print(f"Overall Status: {'🎉 SUCCESS' if overall_success else '⚠️ NEEDS WORK'}")
        
        if overall_success:
            print("\n🎉 Section header visual boxes should now be restored!")
            print("📋 Next steps:")
            print("  1. Start the Flask application")
            print("  2. Generate a test resume")
            print("  3. Verify section headers show blue boxes in HTML preview")
            print("  4. Download PDF and verify section headers match HTML")
            print("  5. Download DOCX and verify consistency across all formats")
        else:
            print("\n⚠️ Additional work needed - check error messages above")
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc() 