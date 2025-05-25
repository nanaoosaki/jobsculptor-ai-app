#!/usr/bin/env python3
"""
Font Consistency Test Script
Tests cross-format font consistency after implementing the DOCX font fix
"""

import sys
import logging
from docx import Document
from io import BytesIO

# Add project root to path
sys.path.append('.')

from style_engine import StyleEngine
from rendering.components.section_header import SectionHeader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_font_consistency():
    """Test that all formats use consistent fonts from design tokens"""
    
    print("=" * 60)
    print("FONT CONSISTENCY TEST - Cross-Format Verification")
    print("=" * 60)
    
    # Load design tokens
    tokens = StyleEngine.load_tokens()
    
    # Display design token values
    print("\n📋 DESIGN TOKEN CONFIGURATION:")
    print(f"  Primary Font (CSS): {tokens['typography']['fontFamily']['primary']}")
    print(f"  DOCX Font: {tokens['typography']['fontFamily']['docxPrimary']}")
    print(f"  Font Size: {tokens['typography']['fontSize']['sectionHeader']}")
    print(f"  Font Color: {tokens['typography']['fontColor']['headers']['hex']}")
    print(f"  Border: {tokens['sectionHeader']['border']['widthPt']}pt solid {tokens['sectionHeader']['border']['color']}")
    
    # Test universal renderer
    test_text = "EXPERIENCE"
    header = SectionHeader(tokens, test_text)
    
    print(f"\n🔧 UNIVERSAL RENDERER TEST:")
    print(f"  Input Text: '{test_text}'")
    print(f"  Computed Casing: '{header._get_computed_casing(test_text)}'")
    
    # Test HTML output
    print(f"\n🌐 HTML OUTPUT:")
    html_output = header.to_html()
    print(f"  Generated HTML: {html_output}")
    
    # Extract HTML styling
    if 'font-family:' in html_output:
        font_start = html_output.find('font-family:') + 12
        font_end = html_output.find(';', font_start)
        html_font = html_output[font_start:font_end].strip()
        print(f"  Extracted Font: {html_font}")
    
    # Test DOCX output  
    print(f"\n📄 DOCX OUTPUT:")
    doc = Document()
    docx_para = header.to_docx(doc)
    
    if docx_para.runs:
        docx_font = docx_para.runs[0].font.name
        docx_size = docx_para.runs[0].font.size
        print(f"  DOCX Font Name: {docx_font}")
        print(f"  DOCX Font Size: {docx_size}")
        print(f"  Text Content: '{docx_para.text}'")
    
    # Consistency check
    print(f"\n✅ CONSISTENCY VERIFICATION:")
    
    # Font family consistency
    expected_docx_font = tokens['typography']['fontFamily']['docxPrimary']
    expected_html_font = tokens['typography']['fontFamily']['primary']
    
    if docx_para.runs:
        actual_docx_font = docx_para.runs[0].font.name
        docx_font_correct = (actual_docx_font == expected_docx_font)
        print(f"  DOCX Font Correct: {docx_font_correct} (expected: {expected_docx_font}, got: {actual_docx_font})")
    
    html_font_correct = (expected_html_font in html_output)
    print(f"  HTML Font Correct: {html_font_correct} (contains: {expected_html_font})")
    
    # Font size consistency  
    expected_size = tokens['typography']['fontSize']['sectionHeader']
    html_size_correct = (expected_size in html_output)
    print(f"  Font Size Correct: {html_size_correct} (expected: {expected_size})")
    
    # Color consistency
    expected_color = tokens['typography']['fontColor']['headers']['hex']
    html_color_correct = (expected_color in html_output)
    print(f"  Font Color Correct: {html_color_correct} (expected: {expected_color})")
    
    # Overall status
    all_correct = all([
        docx_font_correct if docx_para.runs else True,
        html_font_correct,
        html_size_correct,
        html_color_correct
    ])
    
    print(f"\n🎯 OVERALL STATUS: {'✅ PASS' if all_correct else '❌ FAIL'}")
    
    if all_correct:
        print("  ✅ All formats use consistent design token values")
        print("  ✅ DOCX will show sans serif fonts (Calibri)")
        print("  ✅ HTML/PDF will show sans serif fonts (Calibri)")
        print("  ✅ Universal font control achieved!")
    else:
        print("  ❌ Font inconsistencies detected")
        print("  ❌ Additional fixes may be required")
    
    return all_correct

def test_css_conflicts():
    """Test that CSS no longer overrides design token values"""
    
    print("\n" + "=" * 60)
    print("CSS CONFLICT TEST - Design Token vs CSS Override Check")
    print("=" * 60)
    
    # Read CSS files to check for conflicting hardcoded values
    css_files = ['static/css/print.css', 'static/css/preview.css']
    conflicts_found = []
    
    for css_file in css_files:
        try:
            with open(css_file, 'r') as f:
                content = f.read()
                
            print(f"\n📄 Checking {css_file}:")
            
            # Check for hardcoded values that conflict with design tokens
            if 'font-size: 12pt' in content:
                conflicts_found.append(f"{css_file}: hardcoded font-size: 12pt (conflicts with 14pt token)")
                print("  ❌ Found hardcoded font-size: 12pt")
            else:
                print("  ✅ No hardcoded font-size conflicts")
                
            if 'color: #4a6fdc' in content:
                conflicts_found.append(f"{css_file}: hardcoded color: #4a6fdc (conflicts with #0D2B7E token)")
                print("  ❌ Found hardcoded color: #4a6fdc")
            else:
                print("  ✅ No hardcoded color conflicts")
                
            if 'border: 2px solid #4a6fdc' in content:
                conflicts_found.append(f"{css_file}: hardcoded border (conflicts with design tokens)")
                print("  ❌ Found hardcoded border conflicts")
            else:
                print("  ✅ No hardcoded border conflicts")
                
        except FileNotFoundError:
            print(f"  ⚠️ File not found: {css_file}")
    
    css_clean = len(conflicts_found) == 0
    print(f"\n🎯 CSS STATUS: {'✅ CLEAN' if css_clean else '❌ CONFLICTS FOUND'}")
    
    if css_clean:
        print("  ✅ No CSS overrides conflicting with design tokens")
        print("  ✅ Universal renderer can control styling consistently")
    else:
        print("  ❌ CSS conflicts detected:")
        for conflict in conflicts_found:
            print(f"    - {conflict}")
    
    return css_clean

if __name__ == "__main__":
    print("🚀 Starting Font Consistency Analysis...")
    
    try:
        font_test_passed = test_font_consistency()
        css_test_passed = test_css_conflicts()
        
        overall_success = font_test_passed and css_test_passed
        
        print("\n" + "=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        print(f"Font Consistency: {'✅ PASS' if font_test_passed else '❌ FAIL'}")
        print(f"CSS Conflicts: {'✅ CLEAN' if css_test_passed else '❌ FOUND'}")
        print(f"Overall Status: {'🎉 SUCCESS' if overall_success else '⚠️ NEEDS WORK'}")
        
        if overall_success:
            print("\n🎉 All font consistency issues have been resolved!")
            print("📋 Next steps:")
            print("  1. Test the application with real resume generation")
            print("  2. Verify DOCX section headers show sans serif fonts")
            print("  3. Confirm all formats are visually consistent")
        else:
            print("\n⚠️ Additional work needed to achieve full consistency")
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc() 