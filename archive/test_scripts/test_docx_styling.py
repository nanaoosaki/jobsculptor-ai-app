import os
import sys
import json
import logging
from io import BytesIO
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('docx_styling_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_docx_styling():
    """Test function to verify DOCX styling enhancements."""
    try:
        # First, generate the updated DOCX styles
        from tools.generate_tokens import generate_docx_style_mappings
        logger.info("Generating updated DOCX style mappings")
        generate_docx_style_mappings()
        
        # Now import the DOCX builder
        from utils.docx_builder import build_docx, load_section_json
        from style_manager import StyleManager
        
        logger.info("Starting DOCX Styling Test")
        
        # Define the temp directory
        temp_dir = os.path.join("static", "uploads", "temp_session_data")
        if not os.path.exists(temp_dir):
            logger.error(f"Temp directory not found: {temp_dir}")
            return
        
        # Find all unique request IDs in the temp directory
        file_list = os.listdir(temp_dir)
        request_ids = set()
        
        for file in file_list:
            if "_" in file:
                req_id = file.split("_")[0]
                request_ids.add(req_id)
        
        if not request_ids:
            logger.error("No request IDs found in temp directory")
            return
            
        # Use the first request ID found
        request_id = list(request_ids)[0]
        logger.info(f"Using request ID: {request_id}")
        
        # Build the DOCX with enhanced styling
        logger.info(f"Building DOCX with enhanced styling for request ID: {request_id}")
        docx_bytes = build_docx(request_id, temp_dir)
        
        # Save to a file for inspection
        output_path = f"enhanced_styling_{request_id}.docx"
        with open(output_path, "wb") as f:
            f.write(docx_bytes.getvalue())
        
        logger.info(f"Enhanced styling DOCX saved to: {output_path}")
        logger.info("Test completed successfully")
        
    except Exception as e:
        logger.error(f"Error in test: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    test_docx_styling() 