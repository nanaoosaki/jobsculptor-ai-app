#!/usr/bin/env python3
"""
Test script for unified margin control in DOCX.
This script will generate a test DOCX file with our new global margin settings.
"""

import os
import sys
import json
import logging
import tempfile
import uuid
from io import BytesIO
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import necessary modules
from style_engine import StyleEngine
from utils.docx_builder import build_docx

def create_test_docx():
    """Create a test DOCX file with our global margin settings."""
    try:
        # Create a unique request ID for testing
        request_id = f"test_margin_{uuid.uuid4().hex[:8]}"
        
        # Create a temporary directory for files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create dummy contact data
            contact_data = {
                "name": "Test User",
                "location": "New York, NY",
                "phone": "555-123-4567",
                "email": "test@example.com",
                "linkedin": "linkedin.com/in/testuser"
            }
            
            # Save contact data
            with open(os.path.join(temp_dir, f"{request_id}_contact.json"), "w") as f:
                json.dump(contact_data, f)
            
            # Create dummy summary section
            summary_data = {
                "content": "This is a test professional summary to verify margin settings."
            }
            
            # Save summary data
            with open(os.path.join(temp_dir, f"{request_id}_summary.json"), "w") as f:
                json.dump(summary_data, f)
            
            # Create dummy experience section
            experience_data = {
                "content": [
                    {
                        "company": "Test Company",
                        "title": "Senior Developer",
                        "date": "2020 - Present",
                        "location": "New York, NY",
                        "achievements": [
                            "This is a bullet point with a lot of text to test the right margin alignment and ensure that text wraps properly when it reaches the right margin.",
                            "Another bullet point with significant text to verify margin settings and alignment for both left and right edges.",
                            "A third bullet that wraps to test indentation"
                        ]
                    }
                ]
            }
            
            # Save experience data
            with open(os.path.join(temp_dir, f"{request_id}_experience.json"), "w") as f:
                json.dump(experience_data, f)
            
            # Generate DOCX with debug logs enabled
            docx_bytes = build_docx(request_id, temp_dir, debug=True)
            
            # Save the generated DOCX
            output_path = "margin_test.docx"
            with open(output_path, "wb") as f:
                f.write(docx_bytes.getvalue())
            
            logger.info(f"Test DOCX saved to: {output_path}")
            return output_path
    
    except Exception as e:
        logger.error(f"Error creating test DOCX: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    # First, let's display the current margin settings
    tokens = StyleEngine.load_tokens()
    left_margin = tokens.get("docx-global-left-margin-cm", "Not set")
    right_margin = tokens.get("docx-global-right-margin-cm", "Not set")
    
    logger.info(f"Current global margin settings: Left={left_margin}cm, Right={right_margin}cm")
    
    # Now, create a test DOCX with these settings
    output_path = create_test_docx()
    
    if output_path:
        logger.info(f"Successfully created test DOCX with current margin settings: {output_path}")
        logger.info(f"Open the file in Word/LibreOffice to verify the margins.")
    else:
        logger.error("Failed to create test DOCX.") 