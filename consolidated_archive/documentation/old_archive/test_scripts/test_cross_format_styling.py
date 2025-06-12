import os
import sys
import json
import logging
from pathlib import Path
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cross_format_styling_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_cross_format_styling():
    """Test styling consistency across output formats."""
    try:
        # Add root directory to path
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        
        # Import necessary modules
        from style_engine import StyleEngine
        from utils.docx_builder import build_docx
        
        logger.info("Starting cross-format styling test")
        
        # Define the temp directory
        temp_dir = os.path.join("static", "uploads", "temp_session_data")
        if not os.path.exists(temp_dir):
            logger.error(f"Temp directory not found: {temp_dir}")
            return False
        
        # Find all unique request IDs in the temp directory
        file_list = os.listdir(temp_dir)
        request_ids = set()
        
        for file in file_list:
            if "_" in file:
                req_id = file.split("_")[0]
                request_ids.add(req_id)
        
        if not request_ids:
            logger.error("No request IDs found in temp directory")
            return False
            
        # Use the first request ID found
        request_id = list(request_ids)[0]
        logger.info(f"Testing with request ID: {request_id}")
        
        # Check for skills data to validate skills formatting
        skills_file = f"{request_id}_skills.json"
        skills_path = os.path.join(temp_dir, skills_file)
        
        if os.path.exists(skills_path):
            logger.info(f"Found skills data file: {skills_path}")
            try:
                with open(skills_path, 'r', encoding='utf-8') as f:
                    skills_data = json.load(f)
                logger.info(f"Skills data type: {type(skills_data)}")
                
                # Log the skills data structure to help debug formatting
                if isinstance(skills_data, dict) and "skills" in skills_data:
                    skills_content = skills_data.get("skills", "")
                    logger.info(f"Skills content type: {type(skills_content)}")
                    if isinstance(skills_content, list):
                        logger.info(f"Skills list has {len(skills_content)} items")
                        logger.info(f"Sample skills: {', '.join(str(s) for s in skills_content[:5])}")
                        logger.info("These skills should be rendered inline with commas in DOCX")
            except Exception as e:
                logger.error(f"Error reading skills data: {e}")
        else:
            logger.warning(f"No skills data file found for request ID: {request_id}")
        
        # Generate the styled DOCX with the new styling engine
        logger.info(f"Building DOCX with cross-format styling for request ID: {request_id}")
        docx_bytes = build_docx(request_id, temp_dir)
        
        # Save for visual inspection
        output_path = f"cross_format_test_{request_id}.docx"
        with open(output_path, "wb") as f:
            f.write(docx_bytes.getvalue())
        
        logger.info(f"Test DOCX saved to: {output_path}")
        logger.info("Please compare visually with the PDF version")
        
        # Log section header styling information
        structured_tokens = StyleEngine.get_structured_tokens()
        logger.info("Section Header Styling Information:")
        logger.info(f"- Base font size: {structured_tokens.get('sectionHeader', {}).get('base', {}).get('fontSize', 'N/A')}")
        logger.info(f"- Base color: {structured_tokens.get('sectionHeader', {}).get('base', {}).get('color', 'N/A')}")
        logger.info(f"- DOCX border: {structured_tokens.get('sectionHeader', {}).get('docx', {}).get('borderColor', 'N/A')}")
        logger.info(f"- DOCX padding: {structured_tokens.get('sectionHeader', {}).get('docx', {}).get('paddingHorizontal', 'N/A')} horizontal, {structured_tokens.get('sectionHeader', {}).get('docx', {}).get('paddingVertical', 'N/A')} vertical")
        
        # Validation notes for manual inspection
        logger.info("Validation check points:")
        logger.info("1. Section headers should have a border box with proper alignment")
        logger.info("2. Skills should be on a single line with comma separation")
        logger.info("3. Spacing and margins should be consistent with HTML/PDF output")
        
        logger.info("Test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error in test: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_cross_format_styling()
    sys.exit(0 if success else 1) 