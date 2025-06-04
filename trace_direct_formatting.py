#!/usr/bin/env python3
"""
Trace all calls to paragraph_format.left_indent to find the rogue formatting source
This will help identify exactly where the 118,745 twips is being applied
"""

import os
import sys
from pathlib import Path
import logging

# Set environment for native bullets
os.environ['DOCX_USE_NATIVE_BULLETS'] = 'true'

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging to capture all formatting calls
logging.basicConfig(level=logging.DEBUG, format='%(name)s:%(lineno)d - %(message)s')

def trace_formatting_calls():
    print("🔍 Tracing All paragraph_format.left_indent Calls")
    print("=" * 50)
    
    # Monkey patch the paragraph format setter to trace calls
    from docx.text.paragraph import ParagraphFormat
    from docx.shared import Length
    
    original_left_indent_setter = ParagraphFormat.left_indent.fset
    
    def traced_left_indent_setter(self, value):
        # Get call stack info
        import traceback
        stack = traceback.extract_stack()
        
        # Find the calling location (skip this wrapper)
        caller = stack[-2]
        
        if value is not None:
            if hasattr(value, 'twips'):
                twips_value = value.twips
                cm_value = value.cm
                
                print(f"\n🔧 LEFT INDENT SET:")
                print(f"   📍 Called from: {caller.filename}:{caller.lineno}")
                print(f"   📏 Value: {twips_value} twips ({cm_value:.3f} cm)")
                
                if twips_value > 10000:
                    print(f"   🚨 ROGUE FORMATTING DETECTED!")
                    print(f"   📋 Function: {caller.name}")
                    print(f"   📝 Code: {caller.line}")
                    
                    # Print more stack context
                    print(f"   📚 Call Stack:")
                    for i, frame in enumerate(stack[-5:-1]):
                        print(f"      {i+1}. {frame.filename}:{frame.lineno} in {frame.name}")
                        if frame.line:
                            print(f"         {frame.line.strip()}")
        
        # Call the original setter
        return original_left_indent_setter(self, value)
    
    # Apply the monkey patch
    ParagraphFormat.left_indent = ParagraphFormat.left_indent.setter(traced_left_indent_setter)
    
    # Now run our document creation
    try:
        from docx import Document
        from style_manager import StyleManager
        from utils.docx_builder import create_bullet_point, _create_document_styles
        
        print("\n📄 Creating Document...")
        doc = Document()
        
        print("\n📊 Loading Styles...")
        docx_styles = StyleManager.load_docx_styles()
        
        print("\n🎨 Creating Document Styles...")
        _create_document_styles(doc, docx_styles)
        
        print("\n🔸 Creating First Bullet...")
        para1 = create_bullet_point(doc, "First bullet point", docx_styles)
        
        print("\n🔸 Creating Second Bullet...")
        para2 = create_bullet_point(doc, "Second bullet point", docx_styles)
        
        print("\n✅ Document creation complete")
        
        # Final analysis
        print("\n📊 Final Paragraph Analysis:")
        print("-" * 30)
        
        for i, para in enumerate([para1, para2], 1):
            print(f"\nBullet {i}:")
            if para.paragraph_format.left_indent:
                twips = para.paragraph_format.left_indent.twips
                cm = para.paragraph_format.left_indent.cm
                print(f"   📏 Final left indent: {twips} twips ({cm:.3f} cm)")
            else:
                print(f"   📏 Final left indent: None")
    
    except Exception as e:
        print(f"❌ Error during tracing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    trace_formatting_calls() 