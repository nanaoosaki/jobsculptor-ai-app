#!/usr/bin/env python3
"""
CORRECTED: Comprehensive test for bullet integration with proper style creation
This test includes the missing _create_document_styles() call that the actual app uses
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from docx import Document
from word_styles.numbering_engine import NumberingEngine
from style_manager import StyleManager
from utils.docx_builder import _apply_paragraph_style, create_bullet_point, _create_document_styles

def test_proper_integration():
    """Test with the complete integration including style creation."""
    print("🚀 CORRECTED Full Bullet Integration Test")
    print("=" * 60)
    
    # Set the environment variable for native bullets
    os.environ['DOCX_USE_NATIVE_BULLETS'] = 'true'
    
    # Create a document
    doc = Document()
    
    # Load the DOCX styles (what the app actually uses)
    print("\n📋 Loading DOCX styles from StyleManager...")
    docx_styles = StyleManager.load_docx_styles()
    
    # ✅ CRITICAL MISSING STEP: Create the document styles!
    print("\n🔧 Creating document styles (the missing step)...")
    try:
        custom_styles = _create_document_styles(doc, docx_styles)
        print(f"✅ Custom styles created: {list(custom_styles.keys()) if custom_styles else 'None'}")
        
        # Check if MR_BulletPoint style now exists in the document
        available_styles = [s.name for s in doc.styles]
        print(f"📋 Available styles in document: {len(available_styles)} total")
        
        if 'MR_BulletPoint' in available_styles:
            print("✅ MR_BulletPoint style successfully created in document!")
        else:
            print("❌ MR_BulletPoint style still not found in document")
            print(f"Available styles: {available_styles[:10]}...")
            
    except Exception as e:
        print(f"❌ Error creating document styles: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check what the MR_BulletPoint style contains in the JSON
    bullet_style = docx_styles.get("styles", {}).get("MR_BulletPoint", {})
    print(f"\n📋 MR_BulletPoint style configuration:")
    print(f"   indentCm: {bullet_style.get('indentCm', 'NOT_FOUND')}")
    print(f"   hangingIndentCm: {bullet_style.get('hangingIndentCm', 'NOT_FOUND')}")
    
    # Test the actual create_bullet_point function (what the app uses)
    print("\n📋 Testing create_bullet_point function...")
    try:
        para = create_bullet_point(doc, "Test bullet point with proper style creation", docx_styles)
        
        if para:
            print("✅ Bullet point created successfully")
            
            # Check the final style assignment
            final_style = para.style.name if para.style else "None"
            print(f"📝 Final paragraph style: '{final_style}'")
            
            # Check the paragraph formatting that was applied
            left_indent = para.paragraph_format.left_indent
            first_line_indent = para.paragraph_format.first_line_indent
            
            print(f"\n📏 Paragraph formatting:")
            if left_indent:
                left_cm = left_indent.cm
                left_inches = left_cm / 2.54
                print(f"   Left indent: {left_cm:.3f} cm ({left_inches:.3f} inches)")
            else:
                print(f"   Left indent: None")
                
            if first_line_indent:
                first_cm = first_line_indent.cm
                first_inches = first_cm / 2.54
                print(f"   First line indent: {first_cm:.3f} cm ({first_inches:.3f} inches)")
            else:
                print(f"   First line indent: None")
            
            # Check the XML indentation as well
            print(f"\n📄 XML indentation:")
            pPr = para._element.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr')
            ind = pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ind') if pPr is not None else None
            
            if ind is not None:
                left_twips = ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left')
                hanging_twips = ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hanging')
                
                if left_twips:
                    left_inches_xml = int(left_twips) / 1440
                    left_cm_xml = int(left_twips) / 567
                    print(f"   XML Left: {left_twips} twips ({left_inches_xml:.3f} inches, {left_cm_xml:.3f} cm)")
                
                if hanging_twips:
                    hanging_inches_xml = int(hanging_twips) / 1440
                    hanging_cm_xml = int(hanging_twips) / 567
                    print(f"   XML Hanging: {hanging_twips} twips ({hanging_inches_xml:.3f} inches, {hanging_cm_xml:.3f} cm)")
            else:
                print("   No XML indentation found")
            
            # Check for native numbering
            numPr = pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr') if pPr is not None else None
            if numPr is not None:
                print("✅ Native numbering applied")
            else:
                print("⚠️ No native numbering found")
            
            # Final assessment
            print(f"\n🎯 FINAL ASSESSMENT:")
            expected_cm = 0.33
            expected_inches = expected_cm / 2.54
            
            success_criteria = []
            
            # Check style assignment
            if final_style == "MR_BulletPoint":
                print(f"✅ Style correctly assigned: {final_style}")
                success_criteria.append(True)
            else:
                print(f"❌ Style assignment failed: Expected 'MR_BulletPoint', got '{final_style}'")
                success_criteria.append(False)
            
            # Check indentation
            if left_indent and abs(left_indent.cm - expected_cm) < 0.01:
                print(f"✅ Left indent correct: {left_indent.cm:.3f} cm ≈ {expected_cm} cm")
                success_criteria.append(True)
            else:
                actual_cm = left_indent.cm if left_indent else 0
                print(f"❌ Left indent incorrect: Expected {expected_cm} cm, got {actual_cm:.3f} cm")
                success_criteria.append(False)
                
            # Overall success
            if all(success_criteria):
                print(f"\n🎉 OVERALL SUCCESS: All criteria met!")
            else:
                print(f"\n❌ OVERALL FAILURE: {sum(success_criteria)}/{len(success_criteria)} criteria met")
                
        else:
            print("❌ FAILURE: create_bullet_point returned None")
            
    except Exception as e:
        print(f"❌ FAILURE: Exception during bullet creation: {e}")
        import traceback
        traceback.print_exc()
    
    # Save a test document to verify manually
    print(f"\n💾 Saving test document...")
    try:
        doc.save("test_proper_integration.docx")
        print(f"✅ Test document saved: test_proper_integration.docx")
        print(f"   Open this file in Word to verify 0.13\" indentation")
    except Exception as e:
        print(f"❌ Failed to save test document: {e}")

if __name__ == "__main__":
    test_proper_integration() 