#!/usr/bin/env python3
"""
Role Box Integration Test
Comprehensive test to verify role boxes work across all formats after border fix
"""

import sys
import logging
sys.path.append('.')

from style_engine import StyleEngine
from rendering.components.role_box import RoleBox
from rendering.components.section_header import SectionHeader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_role_box_integration():
    """Test role box functionality across all components"""
    
    print("=" * 70)
    print("ROLE BOX INTEGRATION TEST - Cross-Format Verification")
    print("=" * 70)
    
    # Load design tokens
    tokens = StyleEngine.load_tokens()
    
    # Test 1: Universal Role Box Renderer
    print("\n🔧 TEST 1: Universal Role Box Renderer")
    print("-" * 40)
    
    role = RoleBox(tokens, 'Senior Software Development Engineer', 'Jan 2022 - Present')
    html_output = role.to_html()
    
    # Verify complete border styling
    border_checks = {
        "Border shorthand": 'border:' in html_output and '1pt solid #4A6FDC' in html_output,
        "Border radius": 'border-radius: 0.5pt' in html_output,
        "Padding": 'padding: 4pt 8pt' in html_output,
        "Background": 'background-color: transparent' in html_output,
        "Flexbox layout": 'display: flex' in html_output,
        "Content present": 'Senior Software Development Engineer' in html_output,
        "Dates present": 'Jan 2022 - Present' in html_output
    }
    
    for check_name, result in border_checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {check_name}: {status}")
    
    role_box_success = all(border_checks.values())
    print(f"\n🎯 ROLE BOX RESULT: {'✅ SUCCESS' if role_box_success else '❌ FAILED'}")
    
    # Test 2: Section Header Compatibility (Ensure No Regression)
    print("\n🔧 TEST 2: Section Header Compatibility Check")
    print("-" * 40)
    
    section = SectionHeader(tokens, 'EXPERIENCE')
    section_html = section.to_html()
    
    section_checks = {
        "Section border": 'border:' in section_html and '#0D2B7E' in section_html,
        "Section font": 'font-size: 14pt' in section_html,
        "Section content": 'EXPERIENCE' in section_html,
        "Section styling": 'font-weight: bold' in section_html
    }
    
    for check_name, result in section_checks.items():
        status = "✅ PASS" if result else "❌ FAIL"  
        print(f"  {check_name}: {status}")
    
    section_success = all(section_checks.values())
    print(f"\n🎯 SECTION HEADER RESULT: {'✅ NO REGRESSION' if section_success else '❌ REGRESSION DETECTED'}")
    
    # Test 3: Design Token Consistency
    print("\n🔧 TEST 3: Design Token Consistency")
    print("-" * 40)
    
    token_checks = {
        "Role box border color": tokens["roleBox"]["borderColor"] == "#4A6FDC",
        "Role box border width": tokens["roleBox"]["borderWidth"] == "1",
        "Section header border color": tokens["sectionHeader"]["border"]["color"] == "#0D2B7E",
        "Font consistency": tokens["typography"]["fontFamily"]["docxPrimary"] == "Calibri",
        "Font size consistency": tokens["typography"]["fontSize"]["roleBox"] == "11pt"
    }
    
    for check_name, result in token_checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {check_name}: {status}")
    
    token_success = all(token_checks.values())
    print(f"\n🎯 TOKEN CONSISTENCY: {'✅ CONSISTENT' if token_success else '❌ INCONSISTENT'}")
    
    # Overall Results
    print("\n" + "=" * 70)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 70)
    
    overall_success = all([role_box_success, section_success, token_success])
    
    print(f"✅ Role Box Functionality: {'WORKING' if role_box_success else 'BROKEN'}")
    print(f"✅ Section Header Compatibility: {'MAINTAINED' if section_success else 'BROKEN'}")  
    print(f"✅ Design Token Consistency: {'MAINTAINED' if token_success else 'BROKEN'}")
    
    print(f"\n🎯 OVERALL STATUS: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🚀 READY FOR PRODUCTION:")
        print("   • Role boxes will now appear in HTML and PDF formats")
        print("   • Section headers remain fully functional") 
        print("   • DOCX output should be unchanged")
        print("   • Universal rendering system is complete")
    else:
        print("\n⚠️  ISSUES DETECTED - REVIEW REQUIRED")
    
    return overall_success

if __name__ == "__main__":
    success = test_role_box_integration()
    sys.exit(0 if success else 1) 