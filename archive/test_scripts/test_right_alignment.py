#!/usr/bin/env python3
"""
Test script for right-alignment in DOCX.
This script will generate a test DOCX file to verify right alignment fixes.
"""

import os
import sys
import logging
from io import BytesIO

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path for imports if necessary
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT

from style_engine import StyleEngine
from utils.docx_builder import format_right_aligned_pair, add_section_header

def create_test_docx():
    """Create a test DOCX file to verify right alignment."""
    logger.info("Creating test DOCX for right alignment verification...")
    
    # Create a new document
    doc = Document()
    
    # Set up the document with our custom styles
    custom_styles = StyleEngine.create_docx_custom_styles(doc)
    
    # Add a title
    doc.add_paragraph("RIGHT ALIGNMENT TEST", style='Title')
    
    # Add section header for Experience
    section_para = add_section_header(doc, "EXPERIENCE", {})
    
    # Add multiple right-aligned pairs with various lengths to test alignment
    format_right_aligned_pair(
        doc, 
        "Company ABC, Software Developer", 
        "Jan 2020 - Present",
        "company",
        "date",
        {}
    )
    
    format_right_aligned_pair(
        doc, 
        "Very Long Company Name with Many Words Inc., Senior Engineer", 
        "2018 - 2020",
        "company",
        "date",
        {}
    )
    
    format_right_aligned_pair(
        doc, 
        "Short Name Ltd.", 
        "March 2015 - December 2017",
        "company",
        "date",
        {}
    )
    
    # Add section header for Education
    section_para = add_section_header(doc, "EDUCATION", {})
    
    format_right_aligned_pair(
        doc, 
        "University of Example, Computer Science", 
        "2010 - 2014",
        "company",
        "date",
        {}
    )
    
    format_right_aligned_pair(
        doc, 
        "School of Design", 
        "LOCATION, PA",
        "company",
        "date",
        {}
    )
    
    # Save the document
    output_path = "right_alignment_test.docx"
    doc.save(output_path)
    logger.info(f"Test DOCX saved to {output_path}")
    
    return output_path

if __name__ == "__main__":
    try:
        output_file = create_test_docx()
        print(f"Success! Test DOCX created at: {output_file}")
        print("Open this file to verify that dates and locations are properly right-aligned.")
    except Exception as e:
        logger.error(f"Error creating test DOCX: {e}")
        import traceback
        traceback.print_exc() 