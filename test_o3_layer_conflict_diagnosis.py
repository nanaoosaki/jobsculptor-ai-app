#!/usr/bin/env python3
"""
o3's Layer Conflict Diagnostic Test (T-Indent-001)
This test identifies conflicts between different indentation layers in Word styling hierarchy
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from docx import Document
from docx.oxml.ns import qn
from word_styles.numbering_engine import NumberingEngine
from style_manager import StyleManager
from utils.docx_builder import _apply_paragraph_style, create_bullet_point, _create_document_styles

def test_layer_conflict_diagnosis():
    """
    o3's comprehensive diagnostic test for bullet indentation layer conflicts.
    
    Tests the hierarchy:
    L-0: Direct paragraph formatting
    L-1: List-level formatting (NumberingEngine XML)
    L-2: Paragraph style (MR_BulletPoint)
    L-3: Document defaults
    """
    print("🔍 o3's Layer Conflict Diagnostic Test")
    print("=" * 60)
    
    # Set the environment variable for native bullets
    os.environ['DOCX_USE_NATIVE_BULLETS'] = 'true'
    
    # Create a document
    doc = Document()
    
    # Load the DOCX styles
    print("\n📋 Loading DOCX styles...")
    docx_styles = StyleManager.load_docx_styles()
    
    # Create document styles
    print("🔧 Creating document styles...")
    custom_styles = _create_document_styles(doc, docx_styles)
    
    # Check Layer 2: Style Definition
    print(f"\n🔍 LAYER 2 ANALYSIS: Paragraph Style")
    bullet_style_config = docx_styles.get("styles", {}).get("MR_BulletPoint", {})
    print(f"   JSON Config - indentCm: {bullet_style_config.get('indentCm')}")
    print(f"   JSON Config - hangingIndentCm: {bullet_style_config.get('hangingIndentCm')}")
    
    # Check if style was created in document
    if 'MR_BulletPoint' in [s.name for s in doc.styles]:
        style = doc.styles['MR_BulletPoint']
        style_left = style.paragraph_format.left_indent.cm if style.paragraph_format.left_indent else None
        style_first = style.paragraph_format.first_line_indent.cm if style.paragraph_format.first_line_indent else None
        print(f"   Document Style - left_indent: {style_left} cm")
        print(f"   Document Style - first_line_indent: {style_first} cm")
        print(f"   Expected: 0.33 cm / -0.33 cm (hanging)")
        
        # Verify style correctness
        if style_left and abs(style_left - 0.33) < 0.01:
            print("   ✅ Style L-2 indentation CORRECT")
        else:
            print(f"   ❌ Style L-2 indentation WRONG: expected 0.33, got {style_left}")
    else:
        print("   ❌ MR_BulletPoint style NOT found in document")
    
    # Create bullet point
    print(f"\n🔧 Creating bullet point...")
    para = create_bullet_point(doc, "Test bullet for layer conflict diagnosis", docx_styles)
    
    if not para:
        print("❌ FATAL: create_bullet_point returned None")
        return
        
    # Check Layer 0: Direct Paragraph Formatting
    print(f"\n🔍 LAYER 0 ANALYSIS: Direct Paragraph Formatting")
    direct_left = para.paragraph_format.left_indent
    direct_first = para.paragraph_format.first_line_indent
    
    print(f"   Direct left_indent: {direct_left.cm if direct_left else None} cm")
    print(f"   Direct first_line_indent: {direct_first.cm if direct_first else None} cm")
    
    if direct_left and abs(direct_left.cm - 0.33) < 0.01:
        print("   ✅ Direct L-0 formatting CORRECT")
    else:
        print(f"   ⚠️ Direct L-0 formatting: {direct_left.cm if direct_left else 'None'}")
    
    # Check Layer 1: List-level XML formatting
    print(f"\n🔍 LAYER 1 ANALYSIS: List-level XML Formatting")
    
    # Get paragraph properties XML
    pPr = para._element.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr')
    
    # Check for numbering properties
    numPr = pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr') if pPr is not None else None
    if numPr is not None:
        print("   ✅ Native numbering XML found")
        
        # Check for indentation XML
        ind = pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ind') if pPr is not None else None
        if ind is not None:
            left_twips = ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left')
            hanging_twips = ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hanging')
            
            if left_twips:
                left_inches_xml = int(left_twips) / 1440
                left_cm_xml = int(left_twips) / 567
                print(f"   XML Left: {left_twips} twips ({left_inches_xml:.3f} inches, {left_cm_xml:.3f} cm)")
                
                # Check if XML matches expected
                expected_twips = int(0.33 * 567)  # 187 twips
                if abs(int(left_twips) - expected_twips) < 5:
                    print("   ✅ XML L-1 indentation CORRECT")
                else:
                    print(f"   ❌ XML L-1 indentation WRONG: expected {expected_twips}, got {left_twips}")
            
            if hanging_twips:
                hanging_inches_xml = int(hanging_twips) / 1440
                hanging_cm_xml = int(hanging_twips) / 567
                print(f"   XML Hanging: {hanging_twips} twips ({hanging_inches_xml:.3f} inches, {hanging_cm_xml:.3f} cm)")
        else:
            print("   ❌ No XML indentation found in L-1")
    else:
        print("   ❌ No native numbering XML found")
    
    # Layer Priority Analysis
    print(f"\n🚨 LAYER PRIORITY ANALYSIS")
    print("Word's resolution order (highest to lowest priority):")
    print("1. L-0: Direct paragraph formatting")
    print("2. L-1: List-level XML formatting (NumberingEngine)")
    print("3. L-2: Paragraph style (MR_BulletPoint)")
    print("4. L-3: Document defaults")
    
    # Determine what Word will actually display
    print(f"\n🎯 WHAT WORD DISPLAYS:")
    
    # If both L-0 and L-1 exist, L-0 wins, but if L-0 is just applying style, then L-1 wins
    if direct_left and direct_left.cm > 0:
        print(f"   Display: {direct_left.cm:.3f} cm (from L-0 Direct formatting)")
        if abs(direct_left.cm - 0.33) < 0.01:
            print("   ✅ Word will show CORRECT 0.33 cm indentation")
        else:
            print("   ❌ Word will show WRONG indentation")
    elif numPr is not None and ind is not None and left_twips:
        xml_cm = int(left_twips) / 567
        print(f"   Display: {xml_cm:.3f} cm (from L-1 XML formatting)")
        if abs(xml_cm - 0.33) < 0.01:
            print("   ✅ Word will show CORRECT 0.33 cm indentation")
        else:
            print("   ❌ Word will show WRONG indentation")
    else:
        print("   Display: Style-based indentation (L-2)")
        if style_left and abs(style_left - 0.33) < 0.01:
            print("   ✅ Word will show CORRECT 0.33 cm indentation")
        else:
            print("   ❌ Word will show WRONG indentation")
    
    # Final recommendation
    print(f"\n💡 o3's RECOMMENDATION:")
    print("   Let ONLY ONE LAYER set the indent (preferably L-1 XML)")
    print("   Remove any conflicting L-0 direct formatting")
    print("   Ensure L-1 XML exactly matches L-2 style values")
    
    # Save test document
    print(f"\n💾 Saving diagnostic document...")
    try:
        doc.save("test_o3_layer_diagnosis.docx")
        print(f"✅ Saved: test_o3_layer_diagnosis.docx")
        print(f"   Open in Word to verify actual indentation display")
    except Exception as e:
        print(f"❌ Failed to save: {e}")

if __name__ == "__main__":
    test_layer_conflict_diagnosis() 