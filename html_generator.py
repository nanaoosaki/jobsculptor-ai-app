import logging
import re
from typing import Dict, List, Union, Optional

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
    bullet_pattern = r'^[-•*]\s|^\d+[.)\]]\s'
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
                bullet_content = re.sub(r'^[-•*\d.)\]]+\s*', '', stripped_line)
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


def format_job_entry(company: str, location: str, position: str, dates: str, content: List[str]) -> str:
    """
    Format a job entry into HTML.
    
    Args:
        company: Company name
        location: Job location
        position: Job position
        dates: Employment dates
        content: Job details/bullets
    
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
    html_parts.append(f'<div class="position-line">')
    html_parts.append(f'<span class="position">{position}</span>')
    html_parts.append(f'<span class="dates">{dates}</span>')
    html_parts.append(f'</div>')
    
    # Content as paragraphs
    if content:
        html_parts.append('<div class="job-content">')
        for item in content:
            html_parts.append(f'<p>{item}</p>')
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


def format_education_content(content: str) -> str:
    """
    Format education content for HTML display.
    
    This function parses education content that could be either raw string or JSON,
    and converts it to HTML.
    """
    import json
    import logging
    logger = logging.getLogger(__name__)
    
    if not content or content.strip() == "":
        return "<p>No education information available.</p>"
    
    try:
        # Try to parse as JSON first
        if content.strip().startswith('{') or content.strip().startswith('['):
            try:
                education_data = json.loads(content)
                # Process structured JSON data
                # This would need specific logic based on your data structure
                if isinstance(education_data, list):
                    html = ""
                    for entry in education_data:
                        institution = entry.get('institution', '')
                        location = entry.get('location', '')
                        degree = entry.get('degree', '')
                        dates = entry.get('dates', '')
                        highlights = entry.get('highlights', [])
                        
                        html += format_education_entry(institution, location, degree, dates, highlights)
                    return html
                elif isinstance(education_data, dict):
                    # Handle single education entry as dictionary
                    return format_section_content(education_data.get('content', ''))
                else:
                    # Use the raw content as fallback
                    return format_section_content(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, treat as raw content
                logger.debug("Education content not valid JSON, processing as raw text")
                return format_section_content(content)
        else:
            # Treat as raw content
            return format_section_content(content)
    except Exception as e:
        logger.error(f"Error formatting education content: {str(e)}")
        return f"<p>Error formatting education section: {str(e)}</p>"


def format_projects_content(content: str) -> str:
    """
    Format projects content for HTML display.
    
    This function parses projects content that could be either raw string or JSON,
    and converts it to HTML.
    """
    import json
    import logging
    logger = logging.getLogger(__name__)
    
    if not content or content.strip() == "":
        return "<p>No projects information available.</p>"
    
    try:
        # Try to parse as JSON first
        if content.strip().startswith('{') or content.strip().startswith('['):
            try:
                projects_data = json.loads(content)
                # Process structured JSON data
                if isinstance(projects_data, list):
                    html = ""
                    for entry in projects_data:
                        title = entry.get('title', '')
                        dates = entry.get('dates', '')
                        details = entry.get('details', [])
                        
                        html += format_project_entry(title, dates, details)
                    return html
                elif isinstance(projects_data, dict):
                    # Handle single project entry or content field
                    return format_section_content(projects_data.get('content', ''))
                else:
                    # Use the raw content as fallback
                    return format_section_content(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, treat as raw content
                logger.debug("Projects content not valid JSON, processing as raw text")
                return format_section_content(content)
        else:
            # Treat as raw content
            return format_section_content(content)
    except Exception as e:
        logger.error(f"Error formatting projects content: {str(e)}")
        return f"<p>Error formatting projects section: {str(e)}</p>"


def generate_preview_from_llm_responses(llm_client) -> str:
    """
    Generate an HTML preview from LLM API responses.
    
    This function reads the response files from the API responses directory
    and generates an HTML preview of the tailored resume.
    """
    import os
    import json
    from datetime import datetime
    from flask import current_app
    
    # Find the response files directory - use consistent path with claude_integration.py
    api_responses_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'api_responses')
    logger.info(f"Looking for API responses in: {api_responses_dir}")
    
    # Create directory if it doesn't exist
    if not os.path.exists(api_responses_dir):
        logger.warning(f"API responses directory not found, creating: {api_responses_dir}")
        os.makedirs(api_responses_dir)
    
    # Initialize HTML parts
    html_parts = []
    
    # Add HTML header
    html_parts.append("""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resume Preview</title>
        <style>
            body {
                font-family: 'Calibri', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
                background-color: #f5f7fa;
            }
            .resume-preview-container {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 0.5rem;
                margin: 1.5rem auto;
                background-color: #fff;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                width: 95%;
                max-width: 95%;
            }
            .tailored-resume-content {
                width: 8.27in; /* A4 width in inches */
                max-width: 100%; /* Ensure responsiveness */
                margin: 0 auto;
                padding: 0 0.5in; /* Reduced horizontal padding */
                box-sizing: border-box; /* Include padding in width calculation */
                min-height: 10in; /* Approximate A4 height with some space for scrolling */
                background-color: white;
                line-height: 1.5;
                font-family: 'Calibri', Arial, sans-serif;
                font-size: 11pt;
            }
            h1, h2 {
                color: #2c3e50;
            }
            .resume-section {
                margin-bottom: 20px;
            }
            .resume-section h2 {
                font-size: 14pt;
                font-weight: bold;
                color: rgb(0, 0, 102);
                text-align: center;
                text-transform: uppercase;
                margin-top: 0.5cm;
                margin-bottom: 0.3cm;
                padding: 0.1cm 0.5cm;
                border: 1px solid #000;
                width: 100%;
                margin-left: auto;
                margin-right: auto;
            }
            .job, .education, .project {
                margin-bottom: 15px;
            }
            .job-title-line, .education-title-line, .project-title-line {
                display: flex;
                justify-content: space-between;
                font-weight: bold;
            }
            .position-line, .degree-line {
                font-style: italic;
                margin-bottom: 5px;
            }
            .dates {
                color: #7f8c8d;
            }
            p {
                margin: 5px 0;
            }
            .job-content, .education-content, .project-content {
                margin-left: 0;
            }
            .contact-section {
                text-align: center;
                margin-bottom: 0.4cm;
            }
            .contact-section p {
                margin: 0.05cm 0;
                line-height: 1.3;
            }
            .contact-section .name {
                font-size: 16pt;
                font-weight: bold;
                margin-bottom: 0.1cm;
            }
            .contact-divider {
                margin-top: 0.2cm;
                margin-bottom: 0.4cm;
                border: none;
                height: 1px;
                background-color: #000;
                width: 90%;
            }
            .company, .institution, .project-title {
                font-weight: bold;
                text-transform: uppercase;
                text-align: left;
            }
            .location, .dates {
                text-align: right;
                margin-left: auto;
            }
            ul {
                padding-left: 1.5em;
                margin-top: 0.2cm;
            }
            li {
                page-break-inside: avoid;
                margin-bottom: 0.1cm;
            }
        </style>
    </head>
    <body>
    <div class="resume-preview-container">
    <div class="tailored-resume-content">
    """)
    
    # Try to get contact information from API responses
    contact_html = ""
    try:
        with open(os.path.join(api_responses_dir, 'contact.json'), 'r') as f:
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
                logger.info("Successfully loaded contact information from contact.json")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Contact file not found or invalid - try fallback methods
        logger.warning(f"Contact information not found in JSON file: {e}")
        
        # Fallback 1: Try to get contact info from the original resume parsing
        try:
            # Get the resume file ID from the current context
            from flask import current_app, g
            if hasattr(g, 'resume_file_id') and g.resume_file_id:
                resume_id = g.resume_file_id
                logger.info(f"Attempting to recover contact from original resume parsing (ID: {resume_id})")
                
                # Try to locate the cached parsing result
                import glob
                llm_parsed_files = glob.glob(os.path.join(current_app.config['UPLOAD_FOLDER'], f"*{resume_id}*_llm_parsed.json"))
                
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
            logger.warning(f"Fallback contact recovery failed: {fallback_error}")
            # The resume will be generated without contact info
        
    # Add contact section if available
    if contact_html:
        html_parts.append(contact_html)
    
    try:
        # Add summary section
        try:
            with open(os.path.join(api_responses_dir, 'summary.json'), 'r') as f:
                summary_data = json.load(f)
                
            summary_text = summary_data.get('content', '')
            if summary_text.strip():
                html_parts.append('<div class="resume-section">')
                html_parts.append('<h2>Professional Summary</h2>')
                html_parts.append('<div class="summary-content">')
                html_parts.append(format_section_content(summary_text))
                html_parts.append('</div>')
                html_parts.append('</div>')
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error processing summary section: {e}")
            
            # Fallback: Try to get summary info from the original resume parsing
            try:
                # Get the resume file ID from the current context
                from flask import current_app, g
                if hasattr(g, 'resume_file_id') and g.resume_file_id:
                    resume_id = g.resume_file_id
                    logger.info(f"Attempting to recover summary from original resume parsing (ID: {resume_id})")
                    
                    # Try to locate the cached parsing result
                    import glob
                    llm_parsed_files = glob.glob(os.path.join(current_app.config['UPLOAD_FOLDER'], f"*{resume_id}*_llm_parsed.json"))
                    
                    if llm_parsed_files:
                        with open(llm_parsed_files[0], 'r') as f:
                            cached_data = json.load(f)
                            if cached_data.get('sections') and cached_data['sections'].get('summary'):
                                summary_text = cached_data['sections'].get('summary', '')
                                if summary_text.strip():
                                    html_parts.append('<div class="resume-section">')
                                    html_parts.append('<h2>Professional Summary</h2>')
                                    html_parts.append('<div class="summary-content">')
                                    html_parts.append(format_section_content(summary_text))
                                    html_parts.append('</div>')
                                    html_parts.append('</div>')
                                    logger.info("Successfully recovered summary information from cached parsing")
            except Exception as fallback_error:
                logger.warning(f"Fallback summary recovery failed: {fallback_error}")
        
        # Add experience section
        try:
            with open(os.path.join(api_responses_dir, 'experience.json'), 'r') as f:
                experience_data = json.load(f)
                
            if experience_data:
                html_parts.append('<div class="resume-section">')
                html_parts.append('<h2>Experience</h2>')
                html_parts.append('<div class="experience-content">')
                
                for job in experience_data:
                    company = job.get('company', '')
                    location = job.get('location', '')
                    position = job.get('position', '')
                    dates = job.get('dates', '')
                    content = job.get('content', [])
                    
                    if not any([company, position]):  # Skip empty entries
                        continue
                        
                    html_parts.append(
                        format_job_entry(company, location, position, dates, content)
                    )
                
                html_parts.append('</div>')
                html_parts.append('</div>')
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error processing experience section: {e}")
        
        # Add education section
        try:
            with open(os.path.join(api_responses_dir, 'education.json'), 'r') as f:
                education_content = f.read()
                
            if education_content.strip():
                html_parts.append('<div class="resume-section">')
                html_parts.append('<h2>Education</h2>')
                html_parts.append('<div class="education-content">')
                html_parts.append(format_education_content(education_content))
                html_parts.append('</div>')
                html_parts.append('</div>')
                
        except FileNotFoundError as e:
            logger.error(f"Error processing education section: {e}")
        
        # Add skills section
        try:
            with open(os.path.join(api_responses_dir, 'skills.json'), 'r') as f:
                skills_data = json.load(f)
                
            skills_text = skills_data.get('content', '')
            if skills_text.strip():
                html_parts.append('<div class="resume-section">')
                html_parts.append('<h2>Skills</h2>')
                html_parts.append('<div class="skills-content">')
                html_parts.append(format_section_content(skills_text))
                html_parts.append('</div>')
                html_parts.append('</div>')
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error processing skills section: {e}")
        
        # Add projects section
        try:
            with open(os.path.join(api_responses_dir, 'projects.json'), 'r') as f:
                projects_content = f.read()
                
            if projects_content.strip():
                html_parts.append('<div class="resume-section">')
                html_parts.append('<h2>Projects</h2>')
                html_parts.append('<div class="projects-content">')
                html_parts.append(format_projects_content(projects_content))
                html_parts.append('</div>')
                html_parts.append('</div>')
                
        except FileNotFoundError as e:
            logger.error(f"Error processing projects section: {e}")
        
    except Exception as e:
        logger.error(f"Error generating preview: {e}")
        html_parts.append(f"<p>Error generating preview: {str(e)}</p>")
    
    # Add HTML footer
    html_parts.append("""
    <div style="margin-top: 30px; font-size: 12px; color: #95a5a6; text-align: center;">
        Generated on """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
    </div>
    </div>
    </div>
    </body>
    </html>
    """)
    
    # Join HTML parts
    html_content = ''.join(html_parts)
    
    # Validate HTML content to remove empty bullet points
    html_content = validate_html_content(html_content)
    
    return html_content


def generate_resume_preview(resume_path: str) -> str:
    """
    Generate HTML preview of the resume document
    
    This is a temporary stub to replace the function in claude_integration.py
    """
    html_parts = []
    
    # Add HTML header
    html_parts.append("""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resume Preview</title>
        <style>
            body {
                font-family: 'Calibri', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
                background-color: #f5f7fa;
            }
            .resume-preview-container {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 0.5rem;
                margin: 1.5rem auto;
                background-color: #fff;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                width: 95%;
                max-width: 95%;
            }
            .tailored-resume-content {
                width: 8.27in; /* A4 width in inches */
                max-width: 100%; /* Ensure responsiveness */
                margin: 0 auto;
                padding: 0 0.5in; /* Reduced horizontal padding */
                box-sizing: border-box; /* Include padding in width calculation */
                min-height: 10in; /* Approximate A4 height with some space for scrolling */
                background-color: white;
                line-height: 1.5;
                font-family: 'Calibri', Arial, sans-serif;
                font-size: 11pt;
            }
            h1, h2 {
                color: #2c3e50;
            }
            .resume-section {
                margin-bottom: 20px;
            }
            .resume-section h2 {
                font-size: 14pt;
                font-weight: bold;
                color: rgb(0, 0, 102);
                text-align: center;
                text-transform: uppercase;
                margin-top: 0.5cm;
                margin-bottom: 0.3cm;
                padding: 0.1cm 0.5cm;
                border: 1px solid #000;
                width: 100%;
                margin-left: auto;
                margin-right: auto;
            }
        </style>
    </head>
    <body>
    <div class="resume-preview-container">
    <div class="tailored-resume-content">
        <div class="resume-section">
            <h2>Resume Preview</h2>
            <p>This is a placeholder preview. The actual resume preview functionality is temporarily unavailable.</p>
            <p>Please use the "Tailor Resume" feature to see the tailored resume preview.</p>
        </div>
    </div>
    </div>
    </body>
    </html>
    """)
    
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