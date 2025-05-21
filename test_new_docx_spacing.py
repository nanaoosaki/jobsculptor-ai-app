"""
Test New DOCX Spacing Implementation

This script tests the updated docx_builder.py with the new style registry approach.
"""

import os
import sys
import json
import logging
import uuid
from pathlib import Path
import tempfile
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('new_docx_spacing.log')
    ]
)
logger = logging.getLogger(__name__)

def create_test_data(temp_dir):
    """Create test resume data files in the temp directory."""
    # Generate a request ID
    request_id = str(uuid.uuid4())
    logger.info(f"Creating test data with request ID: {request_id}")
    
    # Contact data
    contact_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1 (555) 123-4567",
        "location": "New York, NY",
        "linkedin": "linkedin.com/in/johndoe",
        "github": "github.com/johndoe"
    }
    
    with open(os.path.join(temp_dir, f"{request_id}_contact.json"), 'w') as f:
        json.dump(contact_data, f)
    
    # Summary data
    summary_data = {
        "summary": "Experienced software engineer with a strong background in Python, JavaScript, and cloud technologies. Proven track record of delivering high-quality software solutions and leading development teams."
    }
    
    with open(os.path.join(temp_dir, f"{request_id}_summary.json"), 'w') as f:
        json.dump(summary_data, f)
    
    # Experience data
    experience_data = {
        "experiences": [
            {
                "company": "Tech Company A",
                "location": "New York, NY",
                "position": "Senior Software Engineer",
                "dates": "Jan 2020 - Present",
                "role_description": "Lead developer for cloud-based applications and services.",
                "achievements": [
                    "Implemented CI/CD pipeline reducing deployment time by 50%",
                    "Developed microservice architecture for scalable backend systems",
                    "Led team of 5 engineers in successful product launches"
                ]
            },
            {
                "company": "Tech Company B",
                "location": "Boston, MA",
                "position": "Software Engineer",
                "dates": "Jun 2016 - Dec 2019",
                "role_description": "Full-stack developer for web applications.",
                "achievements": [
                    "Redesigned user interface improving user satisfaction by 35%",
                    "Optimized database queries reducing load times by 40%",
                    "Implemented automated testing framework with 85% code coverage"
                ]
            }
        ]
    }
    
    with open(os.path.join(temp_dir, f"{request_id}_experience.json"), 'w') as f:
        json.dump(experience_data, f)
    
    # Education data
    education_data = {
        "institutions": [
            {
                "institution": "University of Technology",
                "location": "New York, NY",
                "degree": "Master of Science in Computer Science",
                "dates": "2014 - 2016",
                "highlights": [
                    "GPA: 3.8/4.0",
                    "Specialization in Artificial Intelligence"
                ]
            }
        ]
    }
    
    with open(os.path.join(temp_dir, f"{request_id}_education.json"), 'w') as f:
        json.dump(education_data, f)
    
    # Skills data
    skills_data = {
        "Technical Skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes"],
        "Soft Skills": ["Leadership", "Communication", "Problem Solving", "Team Collaboration"]
    }
    
    with open(os.path.join(temp_dir, f"{request_id}_skills.json"), 'w') as f:
        json.dump(skills_data, f)
    
    # Projects data
    projects_data = [
        {
            "name": "Serverless Document Processing System",
            "details": [
                "Designed and delivered a serverless solution for document processing",
                "Implemented DynamoDB-triggered Lambda functions for document analysis"
            ]
        },
        {
            "name": "E-commerce Website",
            "details": [
                "Developed a functional lightweight e-commerce platform"
            ]
        }
    ]
    
    with open(os.path.join(temp_dir, f"{request_id}_projects.json"), 'w') as f:
        json.dump(projects_data, f)
    
    return request_id

def main():
    """Main test function."""
    # Create temporary directory for test data
    temp_dir = tempfile.mkdtemp()
    try:
        # Create test data
        request_id = create_test_data(temp_dir)
        
        # Import our utils.docx_builder module
        try:
            from utils.docx_builder import build_docx
        except ImportError:
            logger.error("Failed to import utils.docx_builder module")
            return
        
        # Build DOCX
        logger.info("Building DOCX with updated docx_builder...")
        docx_bytes = build_docx(request_id, temp_dir)
        
        # Save output file
        output_path = f"test_new_spacing_{request_id}.docx"
        with open(output_path, 'wb') as f:
            f.write(docx_bytes.getvalue())
        
        logger.info(f"Successfully created test DOCX file: {output_path}")
        print(f"\nTest DOCX generated at: {output_path}")
        print("Please open in Word to verify that:")
        print("1. Section header boxes are compact (no excessive whitespace)")
        print("2. Spacing between sections is minimal (no large gaps)")
        print("3. All sections and content are properly formatted")
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main() 