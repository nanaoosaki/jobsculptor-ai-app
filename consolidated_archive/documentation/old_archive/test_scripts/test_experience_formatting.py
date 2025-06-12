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
        logging.FileHandler('experience_formatting_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_experience_formatting():
    """Test experience section formatting in DOCX."""
    try:
        # Add root directory to path
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        
        # Import necessary modules
        from utils.docx_builder import build_docx
        
        logger.info("Starting experience formatting test")
        
        # Define the temp directory
        temp_dir = os.path.join("static", "uploads", "temp_session_data")
        if not os.path.exists(temp_dir):
            logger.error(f"Temp directory not found: {temp_dir}")
            return False
        
        # Find all unique request IDs in the temp directory with experience data
        file_list = os.listdir(temp_dir)
        request_ids = set()
        
        for file in file_list:
            if "_experience.json" in file:
                req_id = file.split("_")[0]
                request_ids.add(req_id)
        
        if not request_ids:
            logger.error("No experience data found in temp directory")
            return False
            
        # Use the first request ID found
        request_id = list(request_ids)[0]
        logger.info(f"Testing experience formatting with request ID: {request_id}")
        
        # Check for experience data to validate formatting
        experience_file = f"{request_id}_experience.json"
        experience_path = os.path.join(temp_dir, experience_file)
        
        if os.path.exists(experience_path):
            logger.info(f"Found experience data file: {experience_path}")
            try:
                with open(experience_path, 'r', encoding='utf-8') as f:
                    experience_data = json.load(f)
                
                # Log the experience data structure to help debug formatting
                if isinstance(experience_data, dict) and "experiences" in experience_data:
                    experiences = experience_data.get("experiences", [])
                    if experiences and len(experiences) > 0:
                        sample_job = experiences[0]
                        logger.info(f"Sample job title: {sample_job.get('title', 'N/A')}")
                        logger.info(f"Sample job dates: {sample_job.get('dates', 'N/A')}")
                        achievements = sample_job.get('achievements', [])
                        if achievements:
                            logger.info(f"Sample achievement: {achievements[0]}")
                            logger.info(f"Achievement count: {len(achievements)}")
                elif isinstance(experience_data, list) and len(experience_data) > 0:
                    sample_job = experience_data[0]
                    logger.info(f"Sample job title: {sample_job.get('title', 'N/A')}")
                    logger.info(f"Sample job dates: {sample_job.get('dates', 'N/A')}")
                    achievements = sample_job.get('achievements', [])
                    if achievements:
                        logger.info(f"Sample achievement: {achievements[0]}")
                        logger.info(f"Achievement count: {len(achievements)}")
            except Exception as e:
                logger.error(f"Error reading experience data: {e}")
        else:
            logger.warning(f"No experience data file found for request ID: {request_id}")
        
        # Generate the styled DOCX with the new formatting
        logger.info(f"Building DOCX with improved experience formatting for request ID: {request_id}")
        docx_bytes = build_docx(request_id, temp_dir)
        
        # Save for visual inspection
        output_path = f"experience_test_{request_id}.docx"
        with open(output_path, "wb") as f:
            f.write(docx_bytes.getvalue())
        
        logger.info(f"Test DOCX saved to: {output_path}")
        logger.info("Please visually inspect the experience section formatting")
        
        # Validation points
        logger.info("Validation check points:")
        logger.info("1. Job title and dates should be on the same line with a '|' separator")
        logger.info("2. Bullet points should have proper indentation and alignment")
        logger.info("3. Bullet points should have consistent styling with the document")
        
        logger.info("Test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error in test: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_experience_formatting()
    sys.exit(0 if success else 1) 