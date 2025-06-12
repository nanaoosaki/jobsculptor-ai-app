#!/usr/bin/env python3
"""
o3's Diagnostic #3: Nuclear Option - Kill Direct Indents
Walk all bullet paragraphs after document creation and remove direct formatting
If this fixes the issue, we know something upstream is writing L-0 formatting
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

def test_nuclear_cleanup():
    print("🔍 o3 Diagnostic #3: Nuclear Direct Indent Cleanup")
    print("=" * 50)
    
    # Create document exactly like production
    doc = Document()
    docx_styles = StyleManager.load_docx_styles()
    _create_document_styles(doc, docx_styles)
    
    # Create multiple bullet points
    bullet_texts = [
        "First bullet achievement",
        "Second bullet achievement", 
        "Third bullet achievement"
    ]
    
    bullet_paras = []
    for text in bullet_texts:
        para = create_bullet_point(doc, text, docx_styles)
        bullet_paras.append(para)
    
    print(f"📊 Created {len(bullet_paras)} bullet paragraphs")
    
    # Examine BEFORE cleanup
    print("\n🔍 BEFORE Nuclear Cleanup:")
    print("-" * 30)
    
    for i, para in enumerate(bullet_paras):
        print(f"\nBullet {i+1}: '{para.text[:30]}...'")
        print(f"   Style: {para.style.name if para.style else 'None'}")
        
        if para.paragraph_format.left_indent:
            left_cm = para.paragraph_format.left_indent.cm
            left_twips = int(para.paragraph_format.left_indent.twips)
            print(f"   📐 Direct left indent: {left_twips} twips ({left_cm:.3f} cm)")
            
            if left_twips > 10000:
                print(f"   🚨 ROGUE FORMATTING: {left_twips} twips!")
        else:
            print(f"   📐 Direct left indent: None")
            
        if para.paragraph_format.first_line_indent:
            hanging_cm = para.paragraph_format.first_line_indent.cm
            hanging_twips = int(para.paragraph_format.first_line_indent.twips)
            print(f"   📐 First line indent: {hanging_twips} twips ({hanging_cm:.3f} cm)")
        else:
            print(f"   📐 First line indent: None")
    
    # NUCLEAR OPTION: Kill all direct indents
    print("\n💥 NUCLEAR CLEANUP: Removing ALL direct indents from bullets")
    print("-" * 50)
    
    cleaned_count = 0
    for para in doc.paragraphs:
        if para.style and para.style.name == "MR_BulletPoint":
            # o3's nuclear cleanup
            before_left = para.paragraph_format.left_indent
            before_first = para.paragraph_format.first_line_indent
            
            para.paragraph_format.left_indent = None
            para.paragraph_format.first_line_indent = None
            
            if before_left or before_first:
                cleaned_count += 1
                print(f"🧹 Cleaned paragraph: '{para.text[:30]}...'")
                if before_left:
                    left_cm = before_left.cm
                    left_twips = int(before_left.twips)
                    print(f"   Removed left: {left_twips} twips ({left_cm:.3f} cm)")
                if before_first:
                    first_cm = before_first.cm
                    first_twips = int(before_first.twips)
                    print(f"   Removed first: {first_twips} twips ({first_cm:.3f} cm)")
    
    print(f"\n✅ Cleaned {cleaned_count} paragraphs")
    
    # Examine AFTER cleanup
    print("\n🔍 AFTER Nuclear Cleanup:")
    print("-" * 30)
    
    for i, para in enumerate(bullet_paras):
        print(f"\nBullet {i+1}: '{para.text[:30]}...'")
        
        if para.paragraph_format.left_indent:
            left_cm = para.paragraph_format.left_indent.cm
            left_twips = int(para.paragraph_format.left_indent.twips)
            print(f"   📐 Direct left indent: {left_twips} twips ({left_cm:.3f} cm)")
            print(f"   ❌ STILL HAS DIRECT FORMATTING!")
        else:
            print(f"   📐 Direct left indent: None ✅")
            
        if para.paragraph_format.first_line_indent:
            hanging_cm = para.paragraph_format.first_line_indent.cm
            hanging_twips = int(para.paragraph_format.first_line_indent.twips)
            print(f"   📐 First line indent: {hanging_twips} twips ({hanging_cm:.3f} cm)")
            print(f"   ❌ STILL HAS DIRECT FORMATTING!")
        else:
            print(f"   📐 First line indent: None ✅")
    
    # Check XML after cleanup
    print("\n🔍 XML Analysis After Cleanup:")
    print("-" * 30)
    
    for i, para in enumerate(bullet_paras):
        print(f"\nBullet {i+1} XML:")
        
        # Check XML indentation
        pPr = para._element.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr')
        if pPr is not None:
            ind = pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ind')
            if ind is not None:
                left = ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left')
                hanging = ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hanging')
                
                if left:
                    left_twips = int(left)
                    left_cm = left_twips / 567
                    print(f"   📄 XML left: {left_twips} twips ({left_cm:.3f} cm)")
                    
                    if left_twips == 187:
                        print(f"   ✅ Correct numbering indent")
                    else:
                        print(f"   ⚠️  Unexpected XML value")
                        
                if hanging:
                    hanging_twips = int(hanging)
                    hanging_cm = hanging_twips / 567
                    print(f"   📄 XML hanging: {hanging_twips} twips ({hanging_cm:.3f} cm)")
            else:
                print("   📄 No XML indentation")
        
        # Check numbering
        numPr = pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr') if pPr else None
        if numPr is not None:
            print("   🎯 XML numbering present")
        else:
            print("   ❌ No XML numbering")
    
    # Save test document
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
        doc.save(tmp.name)
        print(f"\n💾 Saved test document: {tmp.name}")
        print("   Open this in Word to check if indentation is fixed!")
    
    print(f"\n💡 ANALYSIS:")
    print("   If the saved document shows correct indentation in Word,")
    print("   then the issue is definitely rogue direct formatting")
    print("   being applied somewhere in the production pipeline.")

if __name__ == "__main__":
    test_nuclear_cleanup() 