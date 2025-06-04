#!/usr/bin/env python3
"""
Test single bullet creation to debug the missing bullet character issue
"""

import os
from docx import Document

# Set environment for native bullets
os.environ['DOCX_USE_NATIVE_BULLETS'] = 'true'

from utils.docx_builder import create_bullet_point
from style_manager import StyleManager

def test_single_bullet():
    """Test the specific failing bullet text."""
    
    # Create a test document
    doc = Document()
    docx_styles = StyleManager.load_docx_styles()
    
    # Test the specific failing bullet text
    failing_text = 'Fifth achievement to test style repair loops and second-pass formatting'
    print(f'Testing bullet text: {failing_text}')
    
    # Create the bullet
    para = create_bullet_point(doc, failing_text, docx_styles)
    
    # Check the actual text content
    print(f'Paragraph text: "{para.text}"')
    print(f'Paragraph runs: {len(para.runs)}')
    for i, run in enumerate(para.runs):
        print(f'  Run {i}: "{run.text}"')
    
    # Check if it has numbering
    pPr = para._element.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr')
    numPr = pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr') if pPr is not None else None
    
    print(f'Has numbering: {numPr is not None}')
    
    # Check the style
    print(f'Paragraph style: {para.style.name if para.style else "None"}')
    
    # Save and check
    doc.save('test_single_bullet.docx')
    print('Saved test_single_bullet.docx')

if __name__ == "__main__":
    test_single_bullet() 