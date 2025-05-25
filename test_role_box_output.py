#!/usr/bin/env python3
"""Test what the universal role box renderer outputs"""

import sys
sys.path.append('.')

from style_engine import StyleEngine
from rendering.components.role_box import RoleBox

def test_role_box_output():
    print("Testing Role Box Universal Renderer Output")
    print("=" * 50)
    
    tokens = StyleEngine.load_tokens()
    role = RoleBox(tokens, 'Test Position', '2020-Present')
    html_output = role.to_html()
    
    print(f"Generated HTML: {html_output}")
    
    # Check for specific styling
    print(f"\nAnalysis:")
    print(f"- Has border-style: {'border-style' in html_output}")
    print(f"- Has border-color: {'border-color' in html_output}")
    print(f"- Has border-width: {'border-width' in html_output}")
    print(f"- Has border shorthand: {'border:' in html_output}")
    
    # NEW: Check for role box border styling
    has_border_shorthand = 'border:' in html_output
    has_border_radius = 'border-radius' in html_output  
    has_padding = 'padding:' in html_output
    border_color_present = '#4A6FDC' in html_output
    
    print(f"- Has border shorthand: {has_border_shorthand}")
    print(f"- Has border radius: {has_border_radius}")
    print(f"- Has padding: {has_padding}")
    print(f"- Has role box color (#4A6FDC): {border_color_present}")
    
    # Overall status
    border_styling_complete = all([
        has_border_shorthand,
        has_border_radius,
        has_padding,
        border_color_present
    ])
    
    print(f"\n🎯 BORDER STYLING STATUS: {'✅ COMPLETE' if border_styling_complete else '❌ INCOMPLETE'}")
    
    if border_styling_complete:
        print("✅ Role box now includes complete border styling from design tokens!")
        print("✅ HTML and PDF formats should now show visual role boxes")
    else:
        print("❌ Role box still missing some border styling")
    
    return border_styling_complete

if __name__ == "__main__":
    test_role_box_output() 