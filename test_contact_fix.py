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
        logging.FileHandler('contact_fix_debug.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_contact_section_fix():
    """Test function to debug DOCX contact section generation."""
    try:
        from utils.docx_builder import build_docx, load_section_json
        from style_manager import StyleManager
        
        logger.info("Starting Contact Section fix test")
        
        # List available session directories
        temp_dir = os.path.join("static", "uploads", "temp_session_data")
        if not os.path.exists(temp_dir):
            logger.error(f"Temp directory not found: {temp_dir}")
            return
            
        logger.info(f"Scanning temp directory: {temp_dir}")
        file_list = os.listdir(temp_dir)
        
        # Find available request IDs with contact data
        contact_files = [f for f in file_list if "_contact.json" in f]
        logger.info(f"Found contact files: {contact_files}")
        
        if not contact_files:
            logger.error("No contact files found in temp directory")
            return
            
        # Use the first contact file found to extract the request ID
        request_id = contact_files[0].split('_')[0]
        logger.info(f"Using request ID: {request_id}")
        
        # Inspect the contact JSON file
        contact_file = os.path.join(temp_dir, f"{request_id}_contact.json")
        logger.info(f"Inspecting contact file: {contact_file}")
        
        try:
            with open(contact_file, 'r', encoding='utf-8') as f:
                contact_data = json.load(f)
                logger.info(f"Contact data type: {type(contact_data)}")
                if isinstance(contact_data, dict):
                    logger.info(f"Contact data keys: {list(contact_data.keys())}")
                    
                    # Check for content key
                    if 'content' in contact_data:
                        content = contact_data['content']
                        logger.info(f"Content type: {type(content)}")
                        if isinstance(content, dict):
                            logger.info(f"Content keys: {list(content.keys())}")
                        elif isinstance(content, list) and len(content) > 0:
                            logger.info(f"Content is list with {len(content)} items")
                            logger.info(f"First item type: {type(content[0])}")
                            if isinstance(content[0], dict):
                                logger.info(f"First item keys: {list(content[0].keys())}")
                else:
                    logger.info(f"Contact data is not a dictionary: {type(contact_data)}")
        except Exception as e:
            logger.error(f"Error inspecting contact file: {e}")
        
        # Now test loading the contact section through our load_section_json function
        contact = load_section_json(request_id, "contact", temp_dir)
        logger.info(f"Loaded contact via function: {bool(contact)}")
        logger.info(f"Contact type: {type(contact)}")
        if isinstance(contact, dict):
            logger.info(f"Contact keys: {list(contact.keys())}")
        
        # Build the DOCX to test if contact is included
        logger.info(f"Building DOCX for request ID: {request_id}")
        docx_bytes = build_docx(request_id, temp_dir)
        
        # Save to a file for inspection
        output_path = f"contact_fix_{request_id}.docx"
        with open(output_path, "wb") as f:
            f.write(docx_bytes.getvalue())
        
        logger.info(f"Test DOCX saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Error in test: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    test_contact_section_fix() 