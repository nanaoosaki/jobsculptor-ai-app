#!/usr/bin/env python3
"""
Debug script to find where L-0 direct formatting is still being applied
"""

import os
import sys
from pathlib import Path

# Set environment for native bullets
os.environ['DOCX_USE_NATIVE_BULLETS'] = 'true'

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from docx import Document
from style_manager import StyleManager
from utils.docx_builder import create_bullet_point, _create_document_styles

def debug_direct_formatting():
    print("🔍 Debug: Tracing L-0 Direct Formatting Source")
    print("=" * 50)
    
    # Create document and styles
    doc = Document()
    docx_styles = StyleManager.load_docx_styles()
    _create_document_styles(doc, docx_styles)
    
    # Check style before bullet creation
    style = doc.styles['MR_BulletPoint']
    print(f"\n📋 MR_BulletPoint Style Definition:")
    print(f"   Style left_indent: {style.paragraph_format.left_indent}")
    print(f"   Style first_line_indent: {style.paragraph_format.first_line_indent}")
    
    # Create bullet point
    print(f"\n🔧 Creating bullet point...")
    para = create_bullet_point(doc, "Debug bullet", docx_styles)
    
    # Check final state
    print(f"\n📊 Final Paragraph State:")
    print(f"   Para style name: {para.style.name}")
    print(f"   Para direct left_indent: {para.paragraph_format.left_indent}")
    print(f"   Para direct first_line_indent: {para.paragraph_format.first_line_indent}")
    
    # Check if style was reassigned after creation
    print(f"\n🔍 Style Comparison:")
    if para.style.paragraph_format.left_indent:
        print(f"   Style AFTER bullet creation: {para.style.paragraph_format.left_indent.cm:.3f} cm")
        print("   ❌ Style has indentation - this shouldn't happen!")
    else:
        print(f"   Style AFTER bullet creation: None")
        print("   ✅ Style has no indentation (correct)")
    
    # Check if direct formatting matches intended value
    if para.paragraph_format.left_indent:
        direct_cm = para.paragraph_format.left_indent.cm
        print(f"\n🎯 Direct Formatting Analysis:")
        print(f"   Direct value: {direct_cm:.3f} cm")
        if abs(direct_cm - 0.33) < 0.01:
            print("   ✅ Value is correct (0.33 cm)")
            print("   🔧 Source: Likely from style application during paragraph creation")
        else:
            print(f"   ❌ Value is wrong (expected 0.33 cm)")
    
    # Check XML numbering
    pPr = para._element.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr')
    numPr = pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr') if pPr else None
    ind = pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ind') if pPr else None
    
    print(f"\n📄 XML Analysis:")
    if numPr is not None:
        print("   ✅ Native numbering XML present")
    else:
        print("   ❌ No native numbering XML")
    
    if ind is not None:
        left_twips = ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left')
        if left_twips:
            left_cm = int(left_twips) / 567
            print(f"   XML indentation: {left_twips} twips ({left_cm:.3f} cm)")
        else:
            print("   ❌ No XML left indentation")
    else:
        print("   ❌ No XML indentation element")
    
    print(f"\n💡 CONCLUSION:")
    print("   The L-0 direct formatting is likely applied when the style is")
    print("   initially assigned to the paragraph, before we remove the style's")
    print("   indentation. This is a timing issue in the style application.")

if __name__ == "__main__":
    debug_direct_formatting() 