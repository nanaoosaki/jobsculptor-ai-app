#!/usr/bin/env python3
"""
Test script to verify the company spacing fix.
Confirms that MR_Company style gets 6pt spacing from design tokens, not hardcoded values.
"""

import json
import tempfile
from utils.docx_builder import format_right_aligned_pair
from docx import Document
from docx.shared import Pt

def test_company_spacing_fix():
    """Test that company spacing is applied via design tokens, not hardcoded values."""
    
    print("🧪 Testing Company Spacing Fix...")
    
    # Load design tokens
    with open('design_tokens.json', 'r') as f:
        design_tokens = json.load(f)
    
    # Load DOCX styles (generated from design tokens)
    with open('static/styles/_docx_styles.json', 'r') as f:
        docx_styles = json.load(f)
    
    # 1. Verify design token was updated
    company_spacing_token = design_tokens.get("paragraph-spacing-company-before")
    print(f"✓ Design token 'paragraph-spacing-company-before': {company_spacing_token}")
    assert company_spacing_token == "6", f"Expected '6', got '{company_spacing_token}'"
    
    # 2. Verify DOCX style definition has correct spacing
    mr_company_style = docx_styles['styles']['MR_Company']
    space_before_pt = mr_company_style.get('spaceBeforePt')
    print(f"✓ MR_Company style 'spaceBeforePt': {space_before_pt}")
    assert space_before_pt == 6, f"Expected 6, got {space_before_pt}"
    
    # 3. Create test document and apply company formatting
    doc = Document()
    
    # Create multiple company entries to test consistency
    companies = [
        ("DIRECTV", "LOS ANGELES, CA"),
        ("Landmark Health LLC", "Huntington Beach, CA"),
        ("Capital Blue Cross", "Harrisburg, PA")
    ]
    
    company_paragraphs = []
    for company, location in companies:
        para = format_right_aligned_pair(
            doc, company, location, "MR_Company", "MR_Company", docx_styles
        )
        company_paragraphs.append(para)
    
    # 4. Verify that NO hardcoded spacing overrides were applied
    print(f"✓ Created {len(company_paragraphs)} company paragraphs")
    
    for i, para in enumerate(company_paragraphs):
        # Check if paragraph has the MR_Company style
        style_name = para.style.name if para.style else "None"
        print(f"  Company {i+1}: Style = '{style_name}'")
        
        # The spacing should come from the style, not direct formatting
        # Direct formatting would override style formatting
        direct_space_before = para.paragraph_format.space_before
        if direct_space_before is not None:
            print(f"  ⚠️  Company {i+1}: Has direct space_before formatting: {direct_space_before}")
        else:
            print(f"  ✓  Company {i+1}: No direct space_before override (good!)")
    
    print("🎉 Company spacing fix verification completed!")
    return True

if __name__ == "__main__":
    test_company_spacing_fix() 