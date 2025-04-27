import logging
import re
from typing import Dict, List, Union, Optional
import traceback
import os
import json

from utils.bullet_utils import strip_bullet_prefix, BULLET_ESCAPE_RE
from style_manager import StyleManager

logger = logging.getLogger(__name__)

def validate_html_content(html_content: str) -> str:
    """
    Remove empty bullet points from HTML content.
    This function looks for empty list items and unordered lists and removes them.
    """
    if not html_content:
        return ""
        
    # Replace empty list items (simple)
    html_content = re.sub(r'<li>\s*</li>', '', html_content)
    
    # Replace empty list items with just whitespace, non-breaking space, or punctuation
    html_content = re.sub(r'<li>\s*(?:&nbsp;|\.|\s)*\s*</li>', '', html_content)
    
    # Replace list items with only non-breaking spaces or punctuation
    html_content = re.sub(r'<li>[.,;:!?&nbsp;\s]{1,5}</li>', '', html_content)
    
    # Replace extremely short list items (likely just a character or two)
    html_content = re.sub(r'<li>[^>]{1,3}</li>', '', html_content)
    
    # Replace empty unordered lists (lists with no items)
    html_content = re.sub(r'<ul>\s*</ul>', '', html_content)
    
    # Clean up any double-spacing that might have been created
    html_content = re.sub(r'\n\s*\n\s*\n', '\n\n', html_content)
    
    return html_content


def format_section_content(content: str) -> str:
    """
    Format section content for HTML display.
    - Handles bullet points and markdown
    - Filters out job requirement phrases
    """
    if not content or content.strip() == "":
        return "<p>No content available for this section.</p>"
    
    # Filter out lines that look like job requirements
    job_requirement_phrases = [
        "requirements:", "qualifications:", "we're looking for", 
        "we are looking for", "what we're looking for", "what we are looking for",
        "required:", "required skills:", "preferred skills:", "preferred:",
        "responsibilities:", "about the role:", "about this role:", 
        "what you'll do:", "what you will do:"
    ]
    
    # Split content into lines, filter out job requirement sections
    lines = content.strip().split('\n')
    filtered_lines = []
    skip_section = False
    
    for line in lines:
        lower_line = line.lower()
        
        # Check if this line starts a job requirements section
        if any(phrase in lower_line for phrase in job_requirement_phrases):
            skip_section = True
            continue
            
        # If we find a line that looks like a new section header, stop skipping
        if skip_section and line.strip() and line.strip()[0].isupper() and ':' in line:
            skip_section = False
            
        if not skip_section:
            filtered_lines.append(line)
    
    # Join the filtered lines back together
    content = '\n'.join(filtered_lines)
    
    # Check if content contains any bulleted items
    # Accept real bullet glyphs, ASCII dashes/star, numbers, and textual escapes (u2022 etc.)
    bullet_pattern = r'^(?:[-•*]|\d+[.)\]]|(?:u2022|\\u2022|U\+2022|&#8226;|&bull;))\s'
    has_bullets = any(re.match(bullet_pattern, line.strip()) for line in content.split('\n'))
    
    if has_bullets:
        # Process as bullet points
        html = '<ul>'
        current_para = ''
        in_bullet_list = False
        
        for line in content.split('\n'):
            stripped_line = line.strip()
            
            # Skip empty lines
            if not stripped_line:
                continue
                
            # Check if it's a bullet point
            if re.match(bullet_pattern, stripped_line):
                # Extract content after bullet
                bullet_content = re.sub(r'^(?:[-•*]|\d+[.)\]]|(?:u2022|\\u2022|U\+2022|&#8226;|&bull;))\s*', '', stripped_line)
                if not in_bullet_list:
                    in_bullet_list = True
                    
                html += f'<li>{bullet_content}</li>'
            else:
                # Regular text, add as paragraph
                if in_bullet_list:
                    # Close bullet list if we were in one
                    html += '</ul>'
                    in_bullet_list = False
                    html += f'<p>{stripped_line}</p>'
                else:
                    html += f'<p>{stripped_line}</p>'
        
        # Close bullet list if we ended with one
        if in_bullet_list:
            html += '</ul>'
    else:
        # Process as regular paragraphs
        html = ''
        for line in content.split('\n'):
            stripped_line = line.strip()
            if stripped_line:
                html += f'<p>{stripped_line}</p>'
    
    return html


def format_job_entry(company: str, location: str, position: str, dates: str, achievements: List[str]) -> str:
    """
    Format a job entry into HTML.
    
    Args:
        company: Company name
        location: Job location
        position: Job position
        dates: Employment dates
        achievements: Job details/bullets (previously content)
    
    Returns:
        Formatted HTML for job entry
    """
    html_parts = []
    
    # Company name and location on the first line
    html_parts.append(f'<div class="job">')
    html_parts.append(f'<div class="job-title-line">')
    html_parts.append(f'<span class="company">{company}</span>')
    html_parts.append(f'<span class="location">{location}</span>')
    html_parts.append(f'</div>')
    
    # Position and dates on the second line
    html_parts.append(f'<div class="position-bar position-line">')
    html_parts.append(f'<span class="position">{position}</span>')
    html_parts.append(f'<span class="dates">{dates}</span>')
    html_parts.append(f'</div>')
    
    # Content as paragraphs
    if achievements:
        html_parts.append('<div class="job-content">')
        # Determine if the content list should be bullets
        if len(achievements) > 1:
            html_parts.append('<ul class="bullets">')
            for item in achievements:
                # Cleaning is now done before saving to JSON, removed here
                # cleaned_item = strip_bullet_prefix(item)
                # Use item directly as it should be clean
                html_parts.append(f'<li>{item}</li>')
            html_parts.append('</ul>')
        elif len(achievements) == 1:
            # Cleaning is now done before saving to JSON, removed here
            # cleaned_item = strip_bullet_prefix(content[0])
             # Use item directly as it should be clean
            html_parts.append(f'<p>{achievements[0]}</p>')
        html_parts.append('</div>')
    
    html_parts.append('</div>')
    
    return ''.join(html_parts)


def format_education_entry(institution: str, location: str, degree: str, dates: str, highlights: List[str]) -> str:
    """
    Format an education entry into HTML.
    
    Args:
        institution: School/university name
        location: School location
        degree: Degree earned
        dates: Education dates
        highlights: Education highlights/achievements
    
    Returns:
        Formatted HTML for education entry
    """
    html_parts = []
    
    # Institution and location on the first line
    html_parts.append(f'<div class="education">')
    html_parts.append(f'<div class="education-title-line">')
    html_parts.append(f'<span class="institution">{institution}</span>')
    html_parts.append(f'<span class="location">{location}</span>')
    html_parts.append(f'</div>')
    
    # Degree and dates on the second line
    html_parts.append(f'<div class="degree-line">')
    html_parts.append(f'<span class="degree">{degree}</span>')
    html_parts.append(f'<span class="dates">{dates}</span>')
    html_parts.append(f'</div>')
    
    # Content as paragraphs
    if highlights:
        html_parts.append('<div class="education-content">')
        for item in highlights:
            html_parts.append(f'<p>{item}</p>')
        html_parts.append('</div>')
    
    html_parts.append('</div>')
    
    return ''.join(html_parts)


def format_project_entry(title: str, dates: str, details: List[str]) -> str:
    """
    Format a project entry into HTML.
    
    Args:
        title: Project title
        dates: Project dates
        details: Project details/achievements
    
    Returns:
        Formatted HTML for project entry
    """
    html_parts = []
    
    # Project title and dates
    html_parts.append(f'<div class="project">')
    html_parts.append(f'<div class="project-title-line">')
    html_parts.append(f'<span class="project-title">{title}</span>')
    html_parts.append(f'<span class="dates">{dates}</span>')
    html_parts.append(f'</div>')
    
    # Content as paragraphs
    if details:
        html_parts.append('<div class="project-content">')
        for item in details:
            html_parts.append(f'<p>{item}</p>')
        html_parts.append('</div>')
    
    html_parts.append('</div>')
    
    return ''.join(html_parts)


def format_education_content(education_data: List[Dict]) -> str:
    """
    Format education content (structured list) for HTML display.
    """
    if not education_data:
        return "<p>No education information available.</p>"
    
    html = ""
    try:
                if isinstance(education_data, list):
                    for entry in education_data:
                        institution = entry.get('institution', '')
                        location = entry.get('location', '')
                        degree = entry.get('degree', '')
                        dates = entry.get('dates', '')
                        highlights = entry.get('highlights', [])
                
                # Ensure highlights is a list of strings
                if not isinstance(highlights, list):
                    highlights = [str(highlights)] if highlights else []
                        
                        html += format_education_entry(institution, location, degree, dates, highlights)
                    return html
        else:
            # Handle case where unexpected data type is passed
            logger.warning(f"Unexpected data type for education content: {type(education_data)}")
            return "<p>Error formatting education section: Invalid data format.</p>"
            
    except Exception as e:
        logger.error(f"Error formatting education content: {str(e)}")
        logger.error(traceback.format_exc())
        return f"<p>Error formatting education section: {str(e)}</p>"


def format_projects_content(projects_data: List[Dict]) -> str:
    """
    Format projects content (structured list) for HTML display.
    """
    if not projects_data:
        return "<p>No projects information available.</p>"
    
    html = ""
    try:
                if isinstance(projects_data, list):
                    for entry in projects_data:
                        title = entry.get('title', '')
                        dates = entry.get('dates', '')
                        details = entry.get('details', [])
                        
                 # Ensure details is a list of strings
                if not isinstance(details, list):
                    details = [str(details)] if details else []
                
                        html += format_project_entry(title, dates, details)
                    return html
        else:
            # Handle case where unexpected data type is passed
            logger.warning(f"Unexpected data type for projects content: {type(projects_data)}")
            return "<p>Error formatting projects section: Invalid data format.</p>"
    except Exception as e:
        logger.error(f"Error formatting projects content: {str(e)}")
        logger.error(traceback.format_exc())
        return f"<p>Error formatting projects section: {str(e)}</p>"


def format_skills_content(skills_data: Dict) -> str:
    """
    Format skills content (structured dict) for HTML display.
    """
    if not skills_data or not isinstance(skills_data, dict):
        return "<p>No skills information available.</p>"

    html_parts = []
    # Define the order and titles for skill categories
    skill_categories = {
        "technical": "Technical Skills",
        "soft": "Soft Skills",
        "other": "Other Skills"
    }

    for key, title in skill_categories.items():
        skills_list = skills_data.get(key, [])
        if skills_list and isinstance(skills_list, list):
            # Join skills with a comma and space
            skills_text = ", ".join(filter(None, skills_list)) # Filter out potential None values
            if skills_text: # Add paragraph only if there are skills to show
                html_parts.append(f'<p><strong>{title}:</strong> {skills_text}</p>')

    if not html_parts:
        return "<p>No skills information available.</p>"
        
    return "\n".join(html_parts)


# Define a helper function to load data from temp files
def _load_cleaned_data_from_temp(request_id: str, section_name: str, temp_dir: str) -> Optional[Union[Dict, List, str]]:
    """Loads cleaned data for a specific section from its temporary file."""
    temp_filename = f"{request_id}_{section_name}.json"
    temp_filepath = os.path.join(temp_dir, temp_filename)
    
    if not os.path.exists(temp_filepath):
        logger.warning(f"Temporary data file not found for section '{section_name}' (Req ID: {request_id}): {temp_filepath}")
        return None
        
    try:
        with open(temp_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # If it was a simple string saved as {"content": ...}, extract the string
        if isinstance(data, dict) and len(data) == 1 and "content" in data:
            return data["content"]
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from temp file {temp_filepath}: {e}")
        return None # Return None if file is corrupt
    except Exception as e:
        logger.error(f"Error loading data from temp file {temp_filepath}: {e}")
        return None


def generate_preview_from_llm_responses(request_id: str, for_screen: bool = True) -> str:
    """
    Generate an HTML preview from cleaned data stored in temporary session files.
    
    Args:
        request_id (str): The unique ID for the tailoring request.
        for_screen (bool): If True, returns only the HTML fragment for the resume content.
                          If False, generates a full HTML document suitable for PDF conversion.
    """
    # import os # Removed redundant import
    import json
    from flask import current_app
    
    # Define the directory where temporary session files are stored
    temp_data_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp_session_data')
    logger.info(f"Looking for cleaned data for request ID {request_id} in: {temp_data_dir}")

    if not os.path.exists(temp_data_dir):
        logger.error(f"Temporary session data directory not found: {temp_data_dir}")
        error_msg = "<p>Error: Temporary data directory not found.</p>"
        return error_msg if for_screen else f"<!DOCTYPE html><html><head><title>Error</title></head><body>{error_msg}</body></html>"

    # Initialize HTML parts for the core content
    content_parts = []
    
    # Define the sections to load and format
    sections_to_process = ["contact", "summary", "experience", "education", "skills", "projects"]

    # --- Start of Core Resume Content ---
    content_parts.append('<div class="tailored-resume-content">')

    # --- Load and Format Each Section ---
    for section_name in sections_to_process:
        logger.debug(f"Processing section: {section_name} for request ID: {request_id}")
        cleaned_data = _load_cleaned_data_from_temp(request_id, section_name, temp_data_dir)

        if cleaned_data is None:
            logger.warning(f"No cleaned data found for section '{section_name}' (Req ID: {request_id}). Skipping section.")
            continue # Skip this section if data is missing or invalid

        # Add section header (adjust title casing as needed)
        section_title = section_name.replace("_", " ").title()
        content_parts.append('<div class="resume-section">')
        # Only add section box/title for major sections, not contact
        if section_name != "contact":
             content_parts.append(f'<div class="section-box"><h2>{section_title}</h2></div>')
        
        # Add section content div
        content_parts.append(f'<div class="{section_name}-content">')

        # Format content based on section type
        try:
            if section_name == "contact":
                if isinstance(cleaned_data, str):
                    contact_lines = cleaned_data.strip().split('\n')
                                if contact_lines:
                        content_parts.append(f'<p class="name">{contact_lines[0]}</p>')
                                    for line in contact_lines[1:]:
                                        if line.strip():
                                content_parts.append(f'<p>{line.strip()}</p>')
                    content_parts.append('<hr class="contact-divider"/>') # Add divider after contact
                else:
                     logger.warning(f"Unexpected data type for contact section: {type(cleaned_data)}")
            elif section_name == "summary":
                if isinstance(cleaned_data, str):
                    # Summary is expected as a simple string, format using format_section_content
                    content_parts.append(format_section_content(cleaned_data))
                else:
                    logger.warning(f"Unexpected data type for summary section: {type(cleaned_data)}")
            elif section_name == "experience":
                if isinstance(cleaned_data, list):
                    for job in cleaned_data:
                        if isinstance(job, dict):
                    company = job.get('company', '')
                    location = job.get('location', '')
                    position = job.get('position', '')
                    dates = job.get('dates', '')
                            achievements = job.get('achievements', [])
                            if not any([company, position]): continue # Skip potentially empty entries
                            # Pass cleaned data directly to entry formatter
                            content_parts.append(format_job_entry(company, location, position, dates, achievements))
                        else:
                            logger.warning(f"Skipping non-dictionary item in experience data: {job}")
                else:
                    logger.warning(f"Unexpected data type for experience section: {type(cleaned_data)}")
            elif section_name == "education":
                 if isinstance(cleaned_data, list):
                    # Pass the list directly to the content formatter
                    content_parts.append(format_education_content(cleaned_data))
                 else:
                     logger.warning(f"Unexpected data type for education section: {type(cleaned_data)}")
            elif section_name == "skills":
                 if isinstance(cleaned_data, dict):
                     # Pass the dict directly to the content formatter
                     content_parts.append(format_skills_content(cleaned_data))
                 else:
                     logger.warning(f"Unexpected data type for skills section: {type(cleaned_data)}")
            elif section_name == "projects":
                 if isinstance(cleaned_data, list):
                     # Pass the list directly to the content formatter
                     content_parts.append(format_projects_content(cleaned_data))
                 else:
                      logger.warning(f"Unexpected data type for projects section: {type(cleaned_data)}")
            # Add other sections if necessary

        except Exception as e:
            logger.error(f"Error formatting HTML for section '{section_name}' (Req ID: {request_id}): {e}")
            content_parts.append(f"<p>Error formatting {section_name} section.</p>")
        
        # Close section content and resume section divs
        content_parts.append('</div>') # Close {section-name}-content
        content_parts.append('</div>') # Close resume-section

    # --- End of Core Resume Content ---
    content_parts.append('</div>') # Close tailored-resume-content

    # --- Decide Final Output ---
    if for_screen:
        # Return only the content fragment
        html_content = ''.join(content_parts)
    else:
        # Construct the full HTML document for PDF generation
        full_html_parts = [
            "<!DOCTYPE html>",
            "<html lang=\"en\">",
            "<head>",
            "    <meta charset=\"UTF-8\">",
            "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
            "    <title>Tailored Resume</title>",
            "    <!-- No CSS link here; PDF exporter adds it -->",
            "</head>",
            "<body>"
        ]
        full_html_parts.extend(content_parts) # Add the core content
        full_html_parts.extend([
            "</body>",
            "</html>"
        ])
        html_content = '\n'.join(full_html_parts) # Use newline for readability


    # Validate HTML content (if needed, apply to fragment or full doc)
    # Consider if validation needs adjustment based on context
    validated_html = validate_html_content(html_content)

    # Log length based on context
    if for_screen:
        logger.info(f"Generated HTML fragment for preview: {len(validated_html)} chars")
    else:
        logger.info(f"Generated full HTML document for PDF: {len(validated_html)} chars")

    return validated_html


def generate_resume_preview(resume_path: str, for_screen: bool = True) -> str:
    """
    Generate HTML preview of the resume document (stub).
    
    Args:
        resume_path (str): Path to the resume file.
        for_screen (bool): If True, includes screen-specific elements.
    """
    html_parts = []
    
    # Add HTML header with conditional link to preview CSS
    html_parts.append(f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resume Preview</title>""")
        
    if for_screen:
         html_parts.append(f'    <link rel="stylesheet" href="/static/css/preview.css"> ')
         
    html_parts.append("""</head>
    <body>""")
    
    if for_screen:
        html_parts.append('<div class="resume-preview-container">')
        
    html_parts.append("""<div class="tailored-resume-content">
        <div class="resume-section">
            <h2>Resume Preview</h2>
            <p>This is a placeholder preview. The actual resume preview functionality is temporarily unavailable.</p>
            <p>Please use the "Tailor Resume" feature to see the tailored resume preview.</p>
        </div>
    </div>""") # Close tailored-resume-content
    
    if for_screen:
        html_parts.append('</div>') # Close resume-preview-container
        
    html_parts.append("""</body>
    </html>""")
    
    # Join HTML parts
    html_content = ''.join(html_parts)
    
    return html_content


def extract_resume_sections(doc_path: str) -> Dict[str, str]:
    """
    Extract sections from a resume document.
    This is a temporary stub to replace the function in claude_integration.py
    """
    logger.info(f"Extracting resume sections from {doc_path}")
    
    # Return a stub with placeholder sections
    return {
        "contact": "John Doe\njohndoe@example.com\n(123) 456-7890",
        "summary": "Experienced professional with skills in software development, project management, and team leadership.",
        "experience": "Company ABC | New York, NY | 2018-Present\nSenior Developer\n- Led development of key features\n- Managed team of 5 developers",
        "education": "University XYZ | Computer Science | 2014-2018",
        "skills": "Python, JavaScript, Project Management, Team Leadership",
        "projects": "Project XYZ | 2020\n- Developed innovative solution\n- Improved performance by 50%"
    } 