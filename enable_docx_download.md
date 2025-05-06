# DOCX Download Implementation Plan for Resume Tailor

## Overview
This implementation plan outlines the steps needed to add DOCX download functionality to the Resume Tailor application. The plan is designed to:

1. Integrate seamlessly with the existing single-source styling approach
2. Minimize disruption to the current codebase
3. Maintain visual consistency across HTML, PDF, and DOCX outputs
4. Provide users with editable resume documents that retain professional formatting

## Phase 1: Dependencies and Foundation Setup (1-2 days)

### 1.1. Update Dependencies
```bash
# Update requirements.txt with the required packages
pip install python-docx>=1.1.0 Pillow>=10.0.0
```

- Add to `requirements.txt`:
  ```
  python-docx>=1.1.0
  Pillow>=10.0.0
  ```

### 1.2. Extend Design Token System
Current state:
- `design_tokens.json` contains styling variables
- `tools/generate_tokens_css.py` transforms these to SCSS variables

Actions:
1. Rename `generate_tokens_css.py` to `generate_tokens.py`
2. Add a function to generate DOCX style mappings:

```python
def generate_docx_style_mappings():
    """Generate DOCX style mappings from design tokens."""
    try:
        repo_root = pathlib.Path(__file__).parent.parent 
        tokens_path = repo_root / 'design_tokens.json'
        output_dir = repo_root / 'static' / 'styles'
        output_path = output_dir / '_docx_styles.json'
        
        print(f"Reading tokens from: {tokens_path}")
        print(f"Writing DOCX style mappings to: {output_path}")
        
        with open(tokens_path, 'r') as f:
            tokens = json.load(f)
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Transform tokens to DOCX-specific format
        docx_styles = {
            "page": {
                "marginTopCm": float(tokens.get("pageMarginVertical", "0.8cm").replace("cm", "")),
                "marginBottomCm": float(tokens.get("pageMarginVertical", "0.8cm").replace("cm", "")),
                "marginLeftCm": float(tokens.get("pageMarginHorizontal", "0.8cm").replace("cm", "")),
                "marginRightCm": float(tokens.get("pageMarginHorizontal", "0.8cm").replace("cm", ""))
            },
            "heading1": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": int(tokens.get("nameFontSize", "16pt").replace("pt", "")),
                "color": hex_to_rgb(tokens.get("textColor", "#333"))
            },
            "heading2": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": int(tokens.get("sectionHeaderFontSize", "12pt").replace("pt", "")),
                "color": hex_to_rgb(tokens.get("pdfHeaderColor", "rgb(0, 0, 102)")),
                "spaceAfterPt": 6
            },
            "heading3": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": int(tokens.get("baseFontSize", "11pt").replace("pt", "")),
                "bold": True,
                "spaceAfterPt": 4
            },
            "body": {
                "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                "fontSizePt": int(tokens.get("baseFontSize", "11pt").replace("pt", "")),
                "lineHeight": float(tokens.get("baseLineHeight", "1.4")),
                "color": hex_to_rgb(tokens.get("textColor", "#333"))
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(docx_styles, f, indent=2)
        
        print(f"Successfully generated {output_path}")
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple for DOCX."""
    # Handle rgb() format
    if hex_color.startswith("rgb("):
        return [int(x.strip()) for x in hex_color[4:-1].split(",")]
    
    # Handle hex format
    hex_color = hex_color.lstrip('#')
    return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
```

3. Modify main function to generate both SCSS and DOCX styles:

```python
if __name__ == "__main__":
    generate_scss_variables()
    generate_docx_style_mappings()
```

### 1.3. Update StyleManager
Add methods to `style_manager.py` to load DOCX styles:

```python
def docx_styles_path() -> str:
    """Get the absolute path to the DOCX styles JSON file."""
    path = Path(__file__).parent / 'static' / 'styles' / '_docx_styles.json'
    if not path.exists():
        logger.warning(f"DOCX styles file not found at {path}. Run 'python tools/generate_tokens.py' to generate it.")
    return str(path.resolve())

def load_docx_styles() -> dict:
    """Load DOCX styles from the JSON file."""
    try:
        with open(docx_styles_path(), 'r') as f:
            styles = json.load(f)
        return styles
    except Exception as e:
        logger.error(f"Error loading DOCX styles: {e}")
        return {}  # Fallback to empty dict
```

## Phase 2: DOCX Builder Implementation (2-3 days)

### 2.1. Create DOCX Builder Module
Create a new file `utils/docx_builder.py`:

```python
"""
DOCX Builder for Resume Tailor Application

Generates Microsoft Word (.docx) files with consistent styling based on design tokens.
"""

import os
import logging
import json
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

from style_manager import StyleManager

logger = logging.getLogger(__name__)

def load_section_json(request_id: str, section_name: str, temp_dir: str) -> Dict[str, Any]:
    """Load a section's JSON data from the temporary session directory."""
    try:
        file_path = os.path.join(temp_dir, f"{request_id}_{section_name}.json")
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Section file not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {file_path}")
        return {}
    except Exception as e:
        logger.error(f"Error loading section JSON: {e}")
        return {}

def _apply_paragraph_style(p, style_name: str, docx_styles: Dict[str, Any]):
    """Apply style to a paragraph based on DOCX style definitions."""
    if not p.runs:
        return  # Skip empty paragraphs
    
    style_config = docx_styles.get(style_name, {})
    if not style_config:
        logger.warning(f"Style not found: {style_name}")
        return
    
    # Apply font properties
    font = p.runs[0].font
    if "fontSizePt" in style_config:
        font.size = Pt(style_config["fontSizePt"])
    if "fontFamily" in style_config:
        font.name = style_config["fontFamily"]
    if "color" in style_config:
        r, g, b = style_config["color"]
        font.color.rgb = RGBColor(r, g, b)
    if style_config.get("bold", False):
        font.bold = True
    
    # Apply paragraph formatting
    if "spaceAfterPt" in style_config:
        p.paragraph_format.space_after = Pt(style_config["spaceAfterPt"])
    
    # For heading1 (name), center align
    if style_name == "heading1":
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

def build_docx(request_id: str, temp_dir: str) -> BytesIO:
    """
    Build a DOCX file from the resume data for the given request ID.
    
    Args:
        request_id: The unique request ID for the resume
        temp_dir: Directory containing the temp session data files
        
    Returns:
        BytesIO object containing the DOCX file data
    """
    try:
        logger.info(f"Building DOCX for request ID: {request_id}")
        
        # Load DOCX styles from StyleManager
        docx_styles = StyleManager.load_docx_styles()
        if not docx_styles:
            logger.error("No DOCX styles found. Using defaults.")
            docx_styles = {
                "page": {"marginTopCm": 1.0, "marginBottomCm": 1.0, "marginLeftCm": 2.0, "marginRightCm": 2.0},
                "heading1": {"fontFamily": "Calibri", "fontSizePt": 16},
                "heading2": {"fontFamily": "Calibri", "fontSizePt": 14, "color": [0, 0, 102], "spaceAfterPt": 6},
                "heading3": {"fontFamily": "Calibri", "fontSizePt": 11, "bold": True, "spaceAfterPt": 4},
                "body": {"fontFamily": "Calibri", "fontSizePt": 11}
            }
        
        # Create a new Document
        doc = Document()
        
        # Configure page margins
        section = doc.sections[0]
        page_config = docx_styles.get("page", {})
        section.top_margin = Cm(page_config.get("marginTopCm", 1.0))
        section.bottom_margin = Cm(page_config.get("marginBottomCm", 1.0))
        section.left_margin = Cm(page_config.get("marginLeftCm", 2.0))
        section.right_margin = Cm(page_config.get("marginRightCm", 2.0))
        
        # ------ CONTACT SECTION ------
        contact = load_section_json(request_id, "contact", temp_dir)
        if contact:
            # Name
            name_para = doc.add_paragraph(contact.get("name", ""))
            _apply_paragraph_style(name_para, "heading1", docx_styles)
            
            # Contact details
            contact_parts = []
            if "location" in contact and contact["location"]:
                contact_parts.append(contact["location"])
            if "phone" in contact and contact["phone"]:
                contact_parts.append(contact["phone"])
            if "email" in contact and contact["email"]:
                contact_parts.append(contact["email"])
            if "linkedin" in contact and contact["linkedin"]:
                contact_parts.append(contact["linkedin"])
            
            contact_text = " | ".join(contact_parts)
            contact_para = doc.add_paragraph(contact_text)
            _apply_paragraph_style(contact_para, "body", docx_styles)
            contact_para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Add a horizontal line
            doc.add_paragraph("").paragraph_format.space_after = Pt(6)
        
        # ------ SUMMARY SECTION ------
        summary = load_section_json(request_id, "summary", temp_dir)
        if summary and summary.get("summary"):
            # Add section header
            summary_header = doc.add_paragraph("PROFESSIONAL SUMMARY")
            _apply_paragraph_style(summary_header, "heading2", docx_styles)
            
            # Add summary content
            summary_para = doc.add_paragraph(summary.get("summary", ""))
            _apply_paragraph_style(summary_para, "body", docx_styles)
            
            # Space after section
            doc.add_paragraph("").paragraph_format.space_after = Pt(6)
        
        # ------ EXPERIENCE SECTION ------
        experience = load_section_json(request_id, "experience", temp_dir)
        if experience and "experiences" in experience:
            # Add section header
            exp_header = doc.add_paragraph("EXPERIENCE")
            _apply_paragraph_style(exp_header, "heading2", docx_styles)
            
            # Add each job
            for job in experience.get("experiences", []):
                # Company and location
                company_line = f"{job.get('company', '')}"
                if job.get('location'):
                    company_line += f", {job.get('location', '')}"
                company_para = doc.add_paragraph(company_line)
                _apply_paragraph_style(company_para, "heading3", docx_styles)
                
                # Position and dates
                position_line = f"{job.get('title', '')}"
                if job.get('dates'):
                    position_line += f" | {job.get('dates', '')}"
                position_para = doc.add_paragraph(position_line)
                _apply_paragraph_style(position_para, "body", docx_styles)
                
                # Role description if available
                if job.get('role_description'):
                    role_para = doc.add_paragraph(job.get('role_description', ''))
                    _apply_paragraph_style(role_para, "body", docx_styles)
                
                # Achievements/bullets
                for achievement in job.get('achievements', []):
                    # Create a bullet point
                    bullet_para = doc.add_paragraph()
                    bullet_para.style = 'List Bullet'
                    bullet_para.add_run(achievement)
                    _apply_paragraph_style(bullet_para, "body", docx_styles)
                
                # Space between jobs
                doc.add_paragraph("").paragraph_format.space_after = Pt(6)
        
        # ------ EDUCATION SECTION ------
        education = load_section_json(request_id, "education", temp_dir)
        if education and education.get("institutions"):
            # Add section header
            edu_header = doc.add_paragraph("EDUCATION")
            _apply_paragraph_style(edu_header, "heading2", docx_styles)
            
            # Add each institution
            for school in education.get("institutions", []):
                # Institution and location
                school_line = f"{school.get('institution', '')}"
                if school.get('location'):
                    school_line += f", {school.get('location', '')}"
                school_para = doc.add_paragraph(school_line)
                _apply_paragraph_style(school_para, "heading3", docx_styles)
                
                # Degree and dates
                degree_line = f"{school.get('degree', '')}"
                if school.get('dates'):
                    degree_line += f" | {school.get('dates', '')}"
                degree_para = doc.add_paragraph(degree_line)
                _apply_paragraph_style(degree_para, "body", docx_styles)
                
                # Highlights/bullets
                for highlight in school.get('highlights', []):
                    # Create a bullet point
                    bullet_para = doc.add_paragraph()
                    bullet_para.style = 'List Bullet'
                    bullet_para.add_run(highlight)
                    _apply_paragraph_style(bullet_para, "body", docx_styles)
                
                # Space between institutions
                doc.add_paragraph("").paragraph_format.space_after = Pt(6)
        
        # ------ SKILLS SECTION ------
        skills = load_section_json(request_id, "skills", temp_dir)
        if skills and skills.get("skills"):
            # Add section header
            skills_header = doc.add_paragraph("SKILLS")
            _apply_paragraph_style(skills_header, "heading2", docx_styles)
            
            # Add skills content
            skills_content = skills.get("skills", "")
            if isinstance(skills_content, list):
                # Handle skills as list
                for skill in skills_content:
                    skill_para = doc.add_paragraph()
                    skill_para.style = 'List Bullet'
                    skill_para.add_run(skill)
                    _apply_paragraph_style(skill_para, "body", docx_styles)
            else:
                # Handle skills as string
                skills_para = doc.add_paragraph(skills_content)
                _apply_paragraph_style(skills_para, "body", docx_styles)
        
        # ------ PROJECTS SECTION ------
        projects = load_section_json(request_id, "projects", temp_dir)
        if projects and projects.get("projects"):
            # Add section header
            projects_header = doc.add_paragraph("PROJECTS")
            _apply_paragraph_style(projects_header, "heading2", docx_styles)
            
            # Add each project
            for project in projects.get("projects", []):
                # Project title and dates
                title_line = f"{project.get('title', '')}"
                if project.get('dates'):
                    title_line += f" | {project.get('dates', '')}"
                title_para = doc.add_paragraph(title_line)
                _apply_paragraph_style(title_para, "heading3", docx_styles)
                
                # Project details
                for detail in project.get('details', []):
                    # Create a bullet point
                    bullet_para = doc.add_paragraph()
                    bullet_para.style = 'List Bullet'
                    bullet_para.add_run(detail)
                    _apply_paragraph_style(bullet_para, "body", docx_styles)
                
                # Space between projects
                doc.add_paragraph("").paragraph_format.space_after = Pt(6)
        
        # Save the document to BytesIO
        docx_bytes = BytesIO()
        doc.save(docx_bytes)
        docx_bytes.seek(0)
        
        logger.info(f"Successfully built DOCX for request ID: {request_id}")
        return docx_bytes
    
    except Exception as e:
        logger.error(f"Error building DOCX: {e}")
        raise
```

## Phase 3: Route Integration (1 day)

### 3.1. Add DOCX Download Route
Add a new route in `app.py`:

```python
@app.route('/download/docx/<request_id>')
def download_docx_resume(request_id):
    """Generate and download DOCX for a specific tailoring request_id"""
    try:
        # Get temp directory path
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_session_data')
        
        # Import the docx builder
        from utils.docx_builder import build_docx
        
        # Build the DOCX file
        docx_bytes = build_docx(request_id, temp_dir)
        
        # Set the output filename
        filename = f"tailored_resume_{request_id}.docx"
        
        # Send the file for download
        return send_file(
            docx_bytes,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except FileNotFoundError:
        app.logger.error(f"Data not found for generating DOCX for request_id: {request_id}")
        return jsonify({
            'success': False, 
            'error': 'Could not find the data needed to generate the DOCX. Please try tailoring the resume again.'
        }), 404
    except Exception as e:
        app.logger.error(f"Error generating DOCX for request_id {request_id}: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Error generating DOCX: {str(e)}'
        }), 500
```

## Phase 4: Frontend Integration (1 day)

### 4.1. Add DOCX Download Button
Update the template file that displays the tailored resume preview (likely in `templates/index.html`) to add a DOCX download button alongside the PDF download button:

```html
<div class="download-buttons mt-3">
  <a href="/download/{{ request_id }}" class="btn btn-primary mx-1" target="_blank">
    <i class="fas fa-file-pdf"></i> Download PDF
  </a>
  <a href="/download/docx/{{ request_id }}" class="btn btn-outline-primary mx-1" target="_blank">
    <i class="fas fa-file-word"></i> Download DOCX
  </a>
</div>
```

### 4.2. Add Feature Flag (Optional)
For controlled rollout, add a feature flag in `config.py`:

```python
# Feature flags
ENABLE_DOCX_DOWNLOAD = os.environ.get('ENABLE_DOCX_DOWNLOAD', 'true').lower() == 'true'
```

And modify the template to conditionally display the DOCX button:

```html
{% if config.ENABLE_DOCX_DOWNLOAD %}
<a href="/download/docx/{{ request_id }}" class="btn btn-outline-primary mx-1" target="_blank">
  <i class="fas fa-file-word"></i> Download DOCX
</a>
{% endif %}
```

## Phase 5: Testing and Refinement (2-3 days)

### 5.1. Unit Tests
Create tests in a new file `tests/test_docx_builder.py`:

```python
import unittest
import os
import json
import zipfile
import tempfile
from io import BytesIO
from pathlib import Path

from utils.docx_builder import build_docx, load_section_json

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
    
    def tearDown(self):
        """Clean up after tests."""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

if __name__ == '__main__':
    unittest.main()
```

### 5.2. Integration Tests
Create a test that verifies the download route returns the correct MIME type and status code.

### 5.3. Visual Testing
- Generate sample resumes in PDF and DOCX formats
- Compare the visual appearance to ensure consistency
- Check formatting in different Word versions

## Phase 6: Documentation and Deployment (1 day)

### 6.1. Update Documentation
- Add information about the DOCX download feature to README.md
- Document the process for regenerating style tokens
- Add tooltip near the download button explaining format differences

### 6.2. Deployment Preparation
- Verify all requirements are in requirements.txt
- Test the feature in a staging environment
- Add any necessary environment variables

## Execution Timeline

| Phase | Description | Duration | Dependencies |
|-------|-------------|----------|--------------|
| 1 | Dependencies and Foundation Setup | 1-2 days | - |
| 2 | DOCX Builder Implementation | 2-3 days | Phase 1 |
| 3 | Route Integration | 1 day | Phase 2 |
| 4 | Frontend Integration | 1 day | Phase 3 |
| 5 | Testing and Refinement | 2-3 days | Phase 4 |
| 6 | Documentation and Deployment | 1 day | Phase 5 |

Total estimated time: 8-11 days

## Risk Assessment

### Medium Risks:
- **Visual consistency**: DOCX format may not perfectly match PDF/HTML due to Word's layout engine
  - **Mitigation**: Focus on essential styling elements, provide a tooltip explaining potential minor differences

### Low Risks:
- **Token parsing errors**: Converting design tokens to DOCX styles might fail for some values
  - **Mitigation**: Add robust fallback values and error handling
- **Performance impact**: Building DOCX files might be resource-intensive
  - **Mitigation**: Optimize the builder function and add caching if needed

## Future Enhancements

After initial implementation, consider these enhancements:

1. **Improved Bullet Points**: Refine bullet point formatting for better visual consistency
2. **Caching**: Add caching of generated DOCX files to improve performance
3. **Advanced Styling**: Add more sophisticated styling options like borders and background colors
4. **Template-Based Generation**: Switch to python-docx-template for more efficient code
5. **Custom Font Embedding**: Embed custom fonts in the DOCX for consistent appearance

## DOCX Download Implementation Issues and Enhancement Plan

### Issue #1: Missing Contact Section in DOCX Output
**Status**: Resolved

**Description**: 
The contact section was missing from the DOCX output, despite being visible in the PDF output and the corresponding JSON file (e.g., `ab723b19-2fe8-441e-b53d-468bc2f7abd7_contact.json`) existing in the temporary directory.

**Root Cause**:
The issue was caused by the contact data being stored as a string within a 'content' key rather than as a structured object. The code was only handling dictionary-based contact information and wasn't properly parsing string-based contact data.

**Resolution**:
1. Added enhanced debugging to track contact file loading and structure
2. Implemented string parsing logic to extract contact details from string format
3. Added support for various contact data structures:
   - Dictionary with direct fields
   - Dictionary with 'content' key containing a nested dictionary
   - Dictionary with 'content' key containing a string
   - List of contact details

**Implementation Details**:
```python
# Handling string-based contact data
if isinstance(contact_data, str):
    # Parse the contact information from the string
    lines = contact_data.strip().split('\n')
    
    # Extract name from the first line
    name = lines[0].strip() if lines else ""
    
    # Extract contact details from subsequent lines
    contact_details = {}
    if len(lines) > 1:
        details_line = lines[1].strip()
        # Split by common separators
        details_parts = [p.strip() for p in details_line.replace('|', '|').split('|')]
        
        for part in details_parts:
            # Identify the type of contact detail
            if '@' in part:
                contact_details['email'] = part
            elif 'P:' in part or 'Phone:' in part:
                contact_details['phone'] = part
            # Additional field identification logic...
    
    # Create a structured contact object
    contact = {'name': name, **contact_details}
```

**Verification**:
Tested with multiple request IDs including the specific problematic ID `ab723b19-2fe8-441e-b53d-468bc2f7abd7` and confirmed that contact information now appears correctly in the DOCX output.

### Issue #2: Lack of Styling in DOCX Output
**Status**: Unresolved

**Description**: 
The DOCX file lacks proper styling compared to the PDF and HTML outputs. The current implementation doesn't fully leverage the design tokens system for consistent styling across all output formats.

**Current State Analysis**:
- The design tokens are already being transformed into DOCX-compatible format via `_docx_styles.json`
- However, the mapping between design tokens and DOCX styles is minimal and doesn't cover all styling aspects
- DOCX styling requires specialized handling for many elements like fonts, colors, spacing, etc.

**Implementation Plan**:

1. **Enhanced Design Token Mapping**:
   - Expand the `generate_docx_style_mappings()` function to include more DOCX-specific styles
   - Create a more comprehensive mapping between design tokens and DOCX style properties

   ```python
   def generate_docx_style_mappings():
       """Generate enhanced DOCX style mappings from design tokens."""
       try:
           # ... existing code ...
           
           # Enhanced mapping with more styling options
           docx_styles = {
               "page": {
                   "marginTopCm": float(tokens.get("pageMarginVertical", "0.8cm").replace("cm", "")),
                   "marginBottomCm": float(tokens.get("pageMarginVertical", "0.8cm").replace("cm", "")),
                   "marginLeftCm": float(tokens.get("pageMarginHorizontal", "0.8cm").replace("cm", "")),
                   "marginRightCm": float(tokens.get("pageMarginHorizontal", "0.8cm").replace("cm", ""))
               },
               "global": {
                   "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                   "fontSizePt": int(tokens.get("baseFontSize", "11pt").replace("pt", "")),
                   "lineHeight": float(tokens.get("baseLineHeight", "1.4")),
                   "color": hex_to_rgb(tokens.get("textColor", "#333")),
                   "backgroundColor": hex_to_rgb(tokens.get("backgroundColor", "#ffffff"))
               },
               "heading1": {
                   "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                   "fontSizePt": int(tokens.get("nameFontSize", "16pt").replace("pt", "")),
                   "color": hex_to_rgb(tokens.get("textColor", "#333")),
                   "bold": True,
                   "spaceAfterPt": 12
               },
               "heading2": {
                   "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                   "fontSizePt": int(tokens.get("sectionHeaderFontSize", "12pt").replace("pt", "")),
                   "color": hex_to_rgb(tokens.get("pdfHeaderColor", "rgb(0, 0, 102)")),
                   "spaceAfterPt": 6,
                   "bold": True,
                   "backgroundColor": hex_to_rgb(tokens.get("sectionHeaderBackground", "#eee")), 
                   "borderColor": hex_to_rgb(tokens.get("sectionHeaderBorder", "#000"))
               },
               "heading3": {
                   "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                   "fontSizePt": int(tokens.get("baseFontSize", "11pt").replace("pt", "")),
                   "bold": True,
                   "spaceAfterPt": 4
               },
               "body": {
                   "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                   "fontSizePt": int(tokens.get("baseFontSize", "11pt").replace("pt", "")),
                   "lineHeight": float(tokens.get("baseLineHeight", "1.4")),
                   "color": hex_to_rgb(tokens.get("textColor", "#333"))
               },
               "bulletList": {
                   "fontFamily": tokens.get("baseFontFamily", "'Calibri', Arial, sans-serif").replace("'", "").split(",")[0].strip(),
                   "fontSizePt": int(tokens.get("baseFontSize", "11pt").replace("pt", "")),
                   "indentCm": float(tokens.get("bulletIndent", "0.5cm").replace("cm", "")),
                   "spaceAfterPt": 3
               }
           }
           # ... existing code ...
       except Exception as e:
           print(f"An unexpected error occurred: {e}", file=sys.stderr)
           sys.exit(1)
   ```

2. **DOCX Style Implementation**:
   - Enhance the `_apply_paragraph_style` function to handle more styling properties
   - Add support for section headers with background colors and borders
   - Implement consistent bullet list styling

   ```python
   def _apply_paragraph_style(p, style_name: str, docx_styles: Dict[str, Any]):
       """Enhanced style application for paragraphs in DOCX."""
       if not p.runs:
           return  # Skip empty paragraphs
       
       # Get style configuration
       style_config = docx_styles.get(style_name, {})
       if not style_config:
           logger.warning(f"Style not found: {style_name}")
           return
       
       # Apply font properties to all runs in the paragraph for consistency
       for run in p.runs:
           font = run.font
           if "fontSizePt" in style_config:
               font.size = Pt(style_config["fontSizePt"])
           if "fontFamily" in style_config:
               font.name = style_config["fontFamily"]
           if "color" in style_config:
               r, g, b = style_config["color"]
               font.color.rgb = RGBColor(r, g, b)
           if style_config.get("bold", False):
               font.bold = True
           if style_config.get("italic", False):
               font.italic = True
       
       # Apply paragraph formatting
       if "spaceAfterPt" in style_config:
           p.paragraph_format.space_after = Pt(style_config["spaceAfterPt"])
       if "spaceBeforePt" in style_config:
           p.paragraph_format.space_before = Pt(style_config["spaceBeforePt"])
       if "indentCm" in style_config:
           p.paragraph_format.left_indent = Cm(style_config["indentCm"])
       
       # Apply alignment
       if style_name == "heading1":
           p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
       elif style_config.get("alignment") == "center":
           p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
       else:
           p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
       
       # For section headers (heading2), apply shading if specified
       if style_name == "heading2" and "backgroundColor" in style_config:
           from docx.oxml.ns import nsdecls
           from docx.oxml import parse_xml
           
           r, g, b = style_config["backgroundColor"]
           hex_color = f"{r:02x}{g:02x}{b:02x}"
           
           # Apply background shading
           shading_xml = f'<w:shd {nsdecls("w")} w:fill="{hex_color}" w:val="clear"/>'
           p._element.get_or_add_pPr().append(parse_xml(shading_xml))
           
           # Add border if specified
           if "borderColor" in style_config:
               r, g, b = style_config["borderColor"]
               border_hex = f"{r:02x}{g:02x}{b:02x}"
               border_xml = f'''
                   <w:pBdr {nsdecls("w")}>
                       <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{border_hex}"/>
                   </w:pBdr>
               '''
               p._element.get_or_add_pPr().append(parse_xml(border_xml))
   ```

3. **Custom Styles Definition**:
   - Create predefined styles in the document instead of applying formatting directly
   - This approach allows for more consistent styling and easier maintenance

   ```python
   def _create_document_styles(doc, docx_styles):
       """Create custom styles in the document for consistent formatting."""
       # Create a style for section headers
       if 'heading2' in docx_styles:
           style = doc.styles.add_style('SectionHeader', WD_STYLE_TYPE.PARAGRAPH)
           font = style.font
           h2_style = docx_styles['heading2']
           
           if "fontFamily" in h2_style:
               font.name = h2_style["fontFamily"]
           if "fontSizePt" in h2_style:
               font.size = Pt(h2_style["fontSizePt"])
           if "color" in h2_style:
               r, g, b = h2_style["color"]
               font.color.rgb = RGBColor(r, g, b)
           if h2_style.get("bold", False):
               font.bold = True
           
           # Apply paragraph formatting
           style.paragraph_format.space_after = Pt(h2_style.get("spaceAfterPt", 6))
           style.paragraph_format.space_before = Pt(h2_style.get("spaceBeforePt", 12))
       
       # Create a style for bullet lists
       if 'bulletList' in docx_styles:
           style = doc.styles.add_style('CustomBullet', WD_STYLE_TYPE.PARAGRAPH)
           font = style.font
           bullet_style = docx_styles['bulletList']
           
           if "fontFamily" in bullet_style:
               font.name = bullet_style["fontFamily"]
           if "fontSizePt" in bullet_style:
               font.size = Pt(bullet_style["fontSizePt"])
           
           # Add custom bullet format
           style.paragraph_format.left_indent = Cm(bullet_style.get("indentCm", 0.5))
           style.paragraph_format.first_line_indent = Cm(-0.25)  # Hanging indent for bullet
   ```

4. **Testing Phase**:
   - Create test documents to verify styling
   - Compare styling between PDF and DOCX outputs
   - Refine style mappings based on visual inspection

### Implementation Timeline

| Task | Description | Estimated Time |
|------|-------------|----------------|
| Investigate Contact Section Issue | Debug and fix missing contact section | 1 day |
| Enhanced Design Token Mapping | Expand the DOCX style mapping to include more properties | 1-2 days |
| DOCX Style Implementation | Improve the styling application in the DOCX builder | 2-3 days |
| Custom Styles Definition | Create predefined styles in DOCX for consistent formatting | 1-2 days |
| Testing and Refinement | Test all changes and refine based on feedback | 2 days |

**Total Estimated Time**: 7-10 days

### Future Enhancements

1. **Advanced Style Templates**: Create predefined DOCX templates with styles already defined, then populate them with content.
2. **Font Embedding**: Support for embedding custom fonts in DOCX files to ensure consistent appearance.
3. **Theme Support**: Allow switching between multiple resume themes/styles via design tokens.
4. **Table Layouts**: Support for table-based layouts in certain resume sections.
5. **Image Support**: Add support for including profile images or logos in the DOCX output.
6. **Header/Footer Support**: Add customizable headers and footers to the DOCX output.

## Next Steps

Future enhancements:

1. Caching generated DOCX files
2. Adding support for embedded images in DOCX
3. Improving bullet point formatting
4. Adding more style customization options
