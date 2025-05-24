import logging
import re
import os
import json
from typing import Dict, List, Union, Optional
from flask import current_app
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


def format_job_entry(company: str, location: str, position: str, dates: str, content: List[str], role_description: Optional[str] = None) -> str:
    """
    Format a job entry into HTML.
    
    Args:
        company: Company name
        location: Job location
        position: Job title/position
        dates: Employment dates
        content: Job content/achievements
        role_description: Optional role description
    
    Returns:
        Formatted HTML for job entry
    """
    html_parts = []
    
    # Job entry container
    html_parts.append(f'<div class="job">')
    
    # Company and location on the first line
    html_parts.append(f'<div class="job-title-line" id="company-location">')
    html_parts.append(f'<span class="company">{company}</span>')
    html_parts.append(f'<span class="location">{location}</span>')
    html_parts.append(f'</div>')
    
    # Position and dates on the second line with unified role box
    html_parts.append(f'<div class="position-bar position-line" aria-labelledby="company-location">')
    
    # Role box now contains both role and dates
    # O3: Fix double comma in ARIA label
    aria_label = f"Position: {position}"
    if dates:
        aria_label += f", {dates}"
    html_parts.append(f'<div class="role-box" role="presentation" aria-label="{aria_label}">')
    html_parts.append(f'<span class="role">{position}</span>')
    
    # Add non-breaking space for screen reader pause between role and dates
    if dates:
        html_parts.append(f'&nbsp;<span class="dates">{dates}</span>')
    
    html_parts.append('</div>')  # Close role-box
    
    # Add noscript fallback for aggressive email clients
    html_parts.append(f'<noscript><div class="visually-hidden" aria-hidden="true">{position} {dates if dates else ""}</div></noscript>')
    
    html_parts.append('</div>')  # Close position-bar
    
    # Content div opened here
    html_parts.append('<div class="job-content">')
    
    # Add role description if available (below position/dates, before bullets)
    if role_description and role_description.strip():
        html_parts.append(f'<p class="role-description-text">{role_description.strip()}</p>')
    
    # Content as paragraphs
    if content:
        # Determine if the content list should be bullets
        if len(content) > 1:
            html_parts.append('<ul class="bullets">')
            for item in content:
                html_parts.append(f'<li>{item}</li>')
            html_parts.append('</ul>')
        else:
            html_parts.append(f'<p>{content[0]}</p>')
    
    # Close the job-content div
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


def generate_preview_from_llm_responses(request_id: str, upload_folder: str, for_screen: bool = True) -> str:
    """
    Generate an HTML preview from LLM API responses stored in session-specific files.
    
    This function reads the tailored section files from the temporary session data directory
    based on the request_id and generates an HTML preview.
    
    Args:
        request_id (str): The unique identifier for the tailoring request.
        upload_folder (str): The absolute path to the base upload folder.
        for_screen (bool): If True, returns only the HTML fragment for the resume content.
                          If False, generates a full HTML document suitable for PDF conversion.
    """
    # Define the temporary session data directory
    temp_data_dir = os.path.join(upload_folder, 'temp_session_data')
    logger.info(f"Looking for tailored section files for request_id {request_id} in: {temp_data_dir}")

    if not os.path.exists(temp_data_dir):
        logger.error(f"Temporary session data directory not found: {temp_data_dir}")
        # Return an error message appropriate for the context (fragment or full page)
        return "<p>Error: Temporary session data directory not found.</p>" if for_screen else \
               "<!DOCTYPE html><html><head><title>Error</title></head><body><p>Error: Temporary session data directory not found.</p></body></html>"

    # Initialize HTML parts for the core content
    content_parts = []

    # --- Start of Core Resume Content ---
    content_parts.append('<div class="tailored-resume-content">')

    # --- Contact Section ---
    contact_html = ""
    try:
        contact_filepath = os.path.join(temp_data_dir, f'{request_id}_contact.json')
        with open(contact_filepath, 'r', encoding='utf-8') as f:
            contact_data = json.load(f)
            contact_text = contact_data.get('content', '')

            if contact_text:
                contact_lines = contact_text.strip().split('\n')
                contact_html = '<div class="contact-section">'

                # First line is usually the name
                if contact_lines:
                    contact_html += f'<p class="name">{contact_lines[0]}</p>'

                    # Add remaining contact lines
                    for line in contact_lines[1:]:
                        if line.strip():
                            contact_html += f'<p>{line.strip()}</p>'

                contact_html += '</div><hr class="contact-divider"/>'
                logger.info(f"Successfully loaded contact information from {os.path.basename(contact_filepath)}")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Contact file not found or invalid - try fallback methods
        logger.warning(f"Contact information not found in JSON file: {e}")
        
        # Fallback 1: Try to get contact info from the original resume parsing
        try:
            # Avoid flask imports here if possible, but keep g for now
            try:
                from flask import g
                has_g = True
            except ImportError:
                has_g = False

            if has_g and hasattr(g, 'resume_file_id') and g.resume_file_id:
                resume_id = g.resume_file_id
                logger.info(f"Attempting to recover contact from original resume parsing (ID: {resume_id})")
                
                # Try to locate the cached parsing result
                import glob
                llm_parsed_files = glob.glob(os.path.join(upload_folder, f"*{resume_id}*_llm_parsed.json"))
                
                if llm_parsed_files:
                    with open(llm_parsed_files[0], 'r') as f:
                        cached_data = json.load(f)
                        if cached_data.get('contact'):
                            contact_text = cached_data.get('contact', '')
                            if contact_text:
                                contact_lines = contact_text.strip().split('\n')
                                contact_html = '<div class="contact-section">'
                                
                                # First line is usually the name
                                if contact_lines:
                                    contact_html += f'<p class="name">{contact_lines[0]}</p>'
                                    
                                    # Add remaining contact lines
                                    for line in contact_lines[1:]:
                                        if line.strip():
                                            contact_html += f'<p>{line.strip()}</p>'
                                
                                contact_html += '</div><hr class="contact-divider"/>'
                                logger.info("Successfully recovered contact information from cached parsing")
        except Exception as fallback_error:
            logger.warning(f"Could not load or recover contact info for request {request_id}: {fallback_error}")
            # The resume will be generated without contact info
        
    # Add contact section if available
    if contact_html:
        content_parts.append(contact_html)
    
    try:
        # Add summary section
        try:
            summary_filepath = os.path.join(temp_data_dir, f'{request_id}_summary.json')
            with open(summary_filepath, 'r', encoding='utf-8') as f:
                summary_data = json.load(f)
                
            summary_text = summary_data.get('content', '')
            if summary_text.strip():
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box">Professional Summary</div>')
                content_parts.append('<div class="summary-content">')
                content_parts.append(format_section_content(summary_text))
                content_parts.append('</div>')
                content_parts.append('</div>')
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error processing summary section for request {request_id}: {e}")
            
            # Fallback: Try to get summary info from the original resume parsing
            try:
                # Avoid flask imports here if possible, but keep g for now
                try:
                    from flask import g
                    has_g = True
                except ImportError:
                    has_g = False

                if has_g and hasattr(g, 'resume_file_id') and g.resume_file_id:
                    resume_id = g.resume_file_id
                    logger.info(f"Attempting to recover summary from original resume parsing (ID: {resume_id})")
                    
                    # Try to locate the cached parsing result
                    import glob
                    llm_parsed_files = glob.glob(os.path.join(upload_folder, f"*{resume_id}*_llm_parsed.json"))
                    
                    if llm_parsed_files:
                        with open(llm_parsed_files[0], 'r') as f:
                            cached_data = json.load(f)
                            # Adjust based on actual cached structure if needed
                            summary_text = cached_data.get('summary') or (cached_data.get('sections') and cached_data['sections'].get('summary'))
                            if summary_text and summary_text.strip():
                                content_parts.append('<div class="resume-section">')
                                content_parts.append('<div class="section-box">Professional Summary</div>')
                                content_parts.append('<div class="summary-content">')
                                content_parts.append(format_section_content(summary_text))
                                content_parts.append('</div>')
                                content_parts.append('</div>')
                                logger.info("Successfully recovered summary information from cached parsing")
            except Exception as fallback_error:
                logger.warning(f"Could not load or recover summary info for request {request_id}: {fallback_error}")
        
        # Add experience section
        try:
            experience_filepath = os.path.join(temp_data_dir, f'{request_id}_experience.json')
            with open(experience_filepath, 'r', encoding='utf-8') as f:
                experience_data = json.load(f)
                
            if isinstance(experience_data, list):
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box">Experience</div>')
                content_parts.append('<div class="experience-content">')
                
                for job in experience_data:
                    company = job.get('company', '')
                    location = job.get('location', '')
                    position = job.get('position', '')
                    dates = job.get('dates', '')
                    role_description = job.get('role_description', '') # Extract role description
                    # The structured data has 'achievements' directly
                    achievements = job.get('achievements', [])
                    
                    if not any([company, position]):  # Skip empty entries
                        continue
                        
                    # Pass role_description to format_job_entry
                    content_parts.append(
                        format_job_entry(company, location, position, dates, achievements, role_description)
                    )
                
                content_parts.append('</div>')
                content_parts.append('</div>')
            elif isinstance(experience_data, dict) and experience_data.get('content'):
                logger.warning(f"Experience section for {request_id} loaded as simple content, formatting as text.")
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box">Experience</div>')
                content_parts.append('<div class="experience-content">')
                content_parts.append(format_section_content(experience_data['content']))
                content_parts.append('</div>')
                content_parts.append('</div>')
            elif isinstance(experience_data, str):
                logger.warning(f"Experience section for {request_id} loaded as raw string, formatting as text.")
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box">Experience</div>')
                content_parts.append('<div class="experience-content">')
                content_parts.append(format_section_content(experience_data))
                content_parts.append('</div>')
                content_parts.append('</div>')
        
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error processing experience section for request {request_id}: {e}")
        
        # Add education section
        try:
            education_filepath = os.path.join(temp_data_dir, f'{request_id}_education.json')
            # Education might be saved differently, let's load as JSON
            with open(education_filepath, 'r', encoding='utf-8') as f:
                # education_content = f.read() # Old way reading raw string
                education_data = json.load(f) # Should be a list of dicts
                
            if isinstance(education_data, list):
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box">Education</div>')
                content_parts.append('<div class="education-content">')
                # Iterate and format each entry
                for edu_entry in education_data:
                    institution = edu_entry.get('institution', '')
                    location = edu_entry.get('location', '')
                    degree = edu_entry.get('degree', '')
                    dates = edu_entry.get('dates', '')
                    highlights = edu_entry.get('highlights', [])
                    content_parts.append(format_education_entry(institution, location, degree, dates, highlights))
                content_parts.append('</div>')
                content_parts.append('</div>')
            elif isinstance(education_data, dict) and education_data.get('content'):
                logger.warning(f"Education section for {request_id} loaded as simple content, formatting as text.")
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box">Education</div>')
                content_parts.append('<div class="education-content">')
                content_parts.append(format_section_content(education_data['content']))
                content_parts.append('</div>')
                content_parts.append('</div>')
            elif isinstance(education_data, str):
                logger.warning(f"Education section for {request_id} loaded as raw string, formatting as text.")
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box">Education</div>')
                content_parts.append('<div class="education-content">')
                content_parts.append(format_section_content(education_data))
                content_parts.append('</div>')
                content_parts.append('</div>')
        
        except FileNotFoundError as e:
            logger.error(f"Error processing education section for request {request_id}: {e}")
        
        # Add skills section
        try:
            skills_filepath = os.path.join(temp_data_dir, f'{request_id}_skills.json')
            with open(skills_filepath, 'r', encoding='utf-8') as f:
                skills_data = json.load(f)
                
            # Handle both structured dict {"technical": [], ...} and simple {"content": "..."}
            skills_html = ""
            if isinstance(skills_data, dict):
                if 'technical' in skills_data or 'soft' in skills_data or 'other' in skills_data:
                     # Process structured skills
                    if skills_data.get('technical'):
                        skills_html += "<p><strong>Technical Skills:</strong> " + ", ".join(skills_data['technical']) + "</p>"
                    if skills_data.get('soft'):
                        skills_html += "<p><strong>Soft Skills:</strong> " + ", ".join(skills_data['soft']) + "</p>"
                    if skills_data.get('other'):
                        skills_html += "<p><strong>Other Skills:</strong> " + ", ".join(skills_data['other']) + "</p>"
                elif skills_data.get('content'):
                     # Process simple content string
                     skills_html = format_section_content(skills_data['content'])
            elif isinstance(skills_data, str):
                 # Handle raw string if saved incorrectly
                 logger.warning(f"Skills section for {request_id} loaded as raw string.")
                 skills_html = format_section_content(skills_data)

            if skills_html.strip():
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box">Skills</div>')
                content_parts.append('<div class="skills-content">')
                content_parts.append(skills_html)
                content_parts.append('</div>')
                content_parts.append('</div>')
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error processing skills section for request {request_id}: {e}")
        
        # Add projects section
        try:
            projects_filepath = os.path.join(temp_data_dir, f'{request_id}_projects.json')
            # Projects might be saved differently, let's load as JSON
            with open(projects_filepath, 'r', encoding='utf-8') as f:
                # projects_content = f.read() # Old way reading raw string
                projects_data = json.load(f) # Should be list of dicts
                
            if isinstance(projects_data, list):
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box">Projects</div>')
                content_parts.append('<div class="projects-content">')
                # Iterate and format each entry
                for proj_entry in projects_data:
                    title = proj_entry.get('title', '')
                    dates = proj_entry.get('dates', '')
                    details = proj_entry.get('details', [])
                    content_parts.append(format_project_entry(title, dates, details))
                content_parts.append('</div>')
                content_parts.append('</div>')
            elif isinstance(projects_data, dict) and projects_data.get('content'):
                logger.warning(f"Projects section for {request_id} loaded as simple content, formatting as text.")
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box">Projects</div>')
                content_parts.append('<div class="projects-content">')
                content_parts.append(format_section_content(projects_data['content']))
                content_parts.append('</div>')
                content_parts.append('</div>')
            elif isinstance(projects_data, str):
                logger.warning(f"Projects section for {request_id} loaded as raw string, formatting as text.")
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box">Projects</div>')
                content_parts.append('<div class="projects-content">')
                content_parts.append(format_section_content(projects_data))
                content_parts.append('</div>')
                content_parts.append('</div>')
        
        except FileNotFoundError as e:
            logger.error(f"Error processing projects section for request {request_id}: {e}")
        
    except Exception as e:
        logger.error(f"Error generating preview content for request {request_id}: {e}")
        # Return error fragment or full page error based on for_screen
        error_msg = f"<p>Error generating preview: {str(e)}</p>"
        if for_screen:
            return error_msg
        else:
             return f"<!DOCTYPE html><html><head><title>Error</title></head><body>{error_msg}</body></html>"

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
    This might be obsolete or needs adjustment depending on where section extraction happens now.
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