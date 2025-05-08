import unittest
import os
import json
import zipfile
import tempfile
from io import BytesIO
from pathlib import Path
import sys

# Add the parent directory to sys.path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import our modules
from utils.docx_builder import build_docx, load_section_json
from style_manager import StyleManager

class TestDOCXBuilder(unittest.TestCase):
    """Tests for the DOCX builder functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.temp_dir = tempfile.mkdtemp()
        self.request_id = "test_request_123"
        
        # Create sample section JSON files
        self._create_sample_section_files()
    
    def _create_sample_section_files(self):
        """Create sample section JSON files for testing."""
        # Contact section
        contact = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "123-456-7890",
            "location": "New York, NY",
            "linkedin": "linkedin.com/in/johndoe"
        }
        self._save_section("contact", contact)
        
        # Summary section
        summary = {
            "summary": "Experienced software engineer with 5+ years of experience in web development."
        }
        self._save_section("summary", summary)
        
        # Experience section
        experience = {
            "experiences": [
                {
                    "company": "Example Corp",
                    "location": "New York, NY",
                    "title": "Senior Software Engineer",
                    "dates": "2020-Present",
                    "role_description": "Leading a team of 5 engineers developing web applications.",
                    "achievements": [
                        "Reduced API response time by 40% through optimization.",
                        "Implemented CI/CD pipeline reducing deployment time by 60%."
                    ]
                }
            ]
        }
        self._save_section("experience", experience)
        
        # Education section
        education = {
            "institutions": [
                {
                    "institution": "University of Example",
                    "location": "Boston, MA",
                    "degree": "Bachelor of Science in Computer Science",
                    "dates": "2015-2019",
                    "highlights": [
                        "GPA: 3.8/4.0",
                        "Relevant coursework: Data Structures, Algorithms, Database Systems"
                    ]
                }
            ]
        }
        self._save_section("education", education)
        
        # Skills section
        skills = {
            "skills": [
                "Python",
                "JavaScript",
                "React",
                "Node.js",
                "SQL"
            ]
        }
        self._save_section("skills", skills)
    
    def _save_section(self, section_name, data):
        """Save a section's JSON data to a file."""
        file_path = os.path.join(self.temp_dir, f"{self.request_id}_{section_name}.json")
        with open(file_path, 'w') as f:
            json.dump(data, f)
    
    def test_load_section_json(self):
        """Test loading a section's JSON data."""
        contact = load_section_json(self.request_id, "contact", self.temp_dir)
        self.assertEqual(contact["name"], "John Doe")
        self.assertEqual(contact["email"], "john.doe@example.com")
    
    def test_build_docx(self):
        """Test building a DOCX file."""
        try:
            # Build the DOCX file
            docx_bytes = build_docx(self.request_id, self.temp_dir)
            
            # Verify the DOCX file was created
            self.assertIsInstance(docx_bytes, BytesIO)
            
            # Verify it's a valid DOCX file by checking for expected files in the ZIP
            docx_zip = zipfile.ZipFile(docx_bytes)
            self.assertIn("word/document.xml", docx_zip.namelist())
            
            # Write to temp file for manual inspection if needed
            temp_docx_path = os.path.join(self.temp_dir, "test_output.docx")
            with open(temp_docx_path, 'wb') as f:
                f.write(docx_bytes.getvalue())
            
            print(f"Test DOCX saved to: {temp_docx_path}")
            
        except Exception as e:
            self.fail(f"build_docx raised an exception: {e}")
    
    def tearDown(self):
        """Clean up after tests."""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

if __name__ == '__main__':
    unittest.main() 