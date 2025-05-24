import os
import sys
import logging
from io import BytesIO
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('docx_debug.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_docx_builder():
    """Test function to debug DOCX generation."""
    try:
        from utils.docx_builder import build_docx
        from style_manager import StyleManager
        
        logger.info("Starting DOCX builder test")
        
        # List available session directories
        temp_dir = os.path.join("static", "uploads", "temp_session_data")
        if not os.path.exists(temp_dir):
            logger.error(f"Temp directory not found: {temp_dir}")
            return
            
        logger.info(f"Scanning temp directory: {temp_dir}")
        file_list = os.listdir(temp_dir)
        
        # Find available request IDs
        request_ids = set()
        for file in file_list:
            parts = file.split('_')
            if len(parts) >= 2:
                # The first part should be the request ID
                request_ids.add(parts[0])
        
        logger.info(f"Found request IDs: {request_ids}")
        
        if not request_ids:
            logger.error("No request IDs found in temp directory")
            return
            
        # Use the first request ID found
        request_id = list(request_ids)[0]
        logger.info(f"Using request ID: {request_id}")
        
        # List all files for this request ID
        request_files = [f for f in file_list if f.startswith(request_id)]
        logger.info(f"Files for request ID {request_id}: {request_files}")
        
        # Build the DOCX
        logger.info(f"Building DOCX for request ID: {request_id}")
        docx_bytes = build_docx(request_id, temp_dir)
        
        # Save to a file for inspection
        output_path = f"test_output_{request_id}.docx"
        with open(output_path, "wb") as f:
            f.write(docx_bytes.getvalue())
        
        logger.info(f"Test DOCX saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Error in test: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    test_docx_builder() 