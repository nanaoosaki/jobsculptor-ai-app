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
        logging.FileHandler('specific_contact_debug.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_specific_contact():
    """Test function to debug DOCX contact section generation for a specific request ID."""
    try:
        from utils.docx_builder import build_docx, load_section_json
        from style_manager import StyleManager
        
        logger.info("Starting Specific Contact Test")
        
        # Use the specific request ID mentioned in the issue
        request_id = "ab723b19-2fe8-441e-b53d-468bc2f7abd7"
        
        # Define the temp directory
        temp_dir = os.path.join("static", "uploads", "temp_session_data")
        if not os.path.exists(temp_dir):
            logger.error(f"Temp directory not found: {temp_dir}")
            return
        
        # Verify the contact file exists
        contact_file = os.path.join(temp_dir, f"{request_id}_contact.json")
        if not os.path.exists(contact_file):
            logger.error(f"Contact file not found: {contact_file}")
            return
            
        logger.info(f"Contact file exists: {contact_file}")
        
        # Inspect the contact JSON file
        try:
            with open(contact_file, 'r', encoding='utf-8') as f:
                raw_content = f.read()
                logger.info(f"Raw contact file content (first 200 chars): {raw_content[:200]}")
                
                # Parse the JSON 
                contact_data = json.loads(raw_content)
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
                        elif isinstance(content, str):
                            logger.info(f"Content is string: {content[:100]}...")
                else:
                    logger.info(f"Contact data is not a dictionary: {type(contact_data)}")
        except Exception as e:
            logger.error(f"Error inspecting contact file: {e}")
        
        # Try loading with our load_section_json function
        logger.info("Testing contact section loading with load_section_json function")
        contact = load_section_json(request_id, "contact", temp_dir)
        logger.info(f"Loaded contact data: {contact}")
        
        # Now build the DOCX to see if it works
        logger.info(f"Building DOCX for request ID: {request_id}")
        docx_bytes = build_docx(request_id, temp_dir)
        
        # Save to a file for inspection
        output_path = f"specific_contact_{request_id}.docx"
        with open(output_path, "wb") as f:
            f.write(docx_bytes.getvalue())
        
        logger.info(f"Test DOCX saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Error in test: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    test_specific_contact() 