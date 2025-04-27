import logging
import re
from typing import Dict, List, Union, Optional
import traceback

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


def generate_preview_from_llm_responses(llm_client, for_screen: bool = True) -> str:
    """
    Generate an HTML preview from LLM API responses.
    Reads structured JSON data saved by the LLM client.
    """
    import os
    import json
    from datetime import datetime
    from flask import current_app
    import hashlib

    # Find the response files directory
    api_responses_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'api_responses')
    logger.info(f"Looking for API responses in: {api_responses_dir}")

    if not os.path.exists(api_responses_dir):
        logger.warning(f"API responses directory not found: {api_responses_dir}")
        # Return an error message appropriate for the context (fragment or full page)
        return "<p>Error: API response data not found.</p>" if for_screen else \
               "<!DOCTYPE html><html><head><title>Error</title></head><body><p>Error: API response data not found.</p></body></html>"

    # Initialize HTML parts for the core content
    content_parts = []

    # --- Start of Core Resume Content ---
    content_parts.append('<div class="tailored-resume-content">')

    # --- Contact Section ---
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
        content_parts.append(contact_html)
    
    try:
        # Add summary section
        try:
            with open(os.path.join(api_responses_dir, 'summary.json'), 'r') as f:
                summary_data = json.load(f)
                
            summary_text = summary_data.get('content', '')
            if summary_text.strip():
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box"><h2>Professional Summary</h2></div>')
                content_parts.append('<div class="summary-content">')
                content_parts.append(format_section_content(summary_text))
                content_parts.append('</div>')
                content_parts.append('</div>')
                
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
                                    content_parts.append('<div class="resume-section">')
                                    content_parts.append('<div class="section-box"><h2>Professional Summary</h2></div>')
                                    content_parts.append('<div class="summary-content">')
                                    content_parts.append(format_section_content(summary_text))
                                    content_parts.append('</div>')
                                    content_parts.append('</div>')
                                    logger.info("Successfully recovered summary information from cached parsing")
            except Exception as fallback_error:
                logger.warning(f"Fallback summary recovery failed: {fallback_error}")
        
        # Add experience section
        try:
            with open(os.path.join(api_responses_dir, 'experience.json'), 'r') as f:
                experience_data = json.load(f)
                
            if experience_data:
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box"><h2>Experience</h2></div>')
                content_parts.append('<div class="experience-content">')
                
                for job in experience_data:
                    company = job.get('company', '')
                    location = job.get('location', '')
                    position = job.get('position', '')
                    dates = job.get('dates', '')
                    # Use the correct key 'achievements' instead of 'content'
                    achievements = job.get('achievements', []) 
                    
                    if not any([company, position]):  # Skip empty entries
                        continue
                        
                    # Pass the achievements list to the updated function
                    content_parts.append(
                        format_job_entry(company, location, position, dates, achievements)
                    )
                
                content_parts.append('</div>')
                content_parts.append('</div>')
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error processing experience section: {e}")
        
        # Add education section
        try:
            education_filepath = os.path.join(api_responses_dir, 'education.json')
            with open(education_filepath, 'r') as f:
                education_data = json.load(f)
                
            if education_data:
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box"><h2>Education</h2></div>')
                content_parts.append('<div class="education-content">')
                # Pass the loaded list directly to the formatter
                content_parts.append(format_education_content(education_data))
                content_parts.append('</div>')
                content_parts.append('</div>')
            else:
                 logger.info("Education data file was empty or contained no data.")
                
        except FileNotFoundError:
            logger.warning(f"Education section file not found: {education_filepath}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding education JSON from {education_filepath}: {e}")
        except Exception as e:
             logger.error(f"Error processing education section: {e}")
        
        # Add skills section
        try:
            skills_filepath = os.path.join(api_responses_dir, 'skills.json')
            with open(skills_filepath, 'r') as f:
                skills_data = json.load(f)
                
            if skills_data:
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box"><h2>Skills</h2></div>')
                content_parts.append('<div class="skills-content">')
                 # Pass the loaded dictionary directly to the new formatter
                content_parts.append(format_skills_content(skills_data))
                content_parts.append('</div>')
                content_parts.append('</div>')
            else:
                logger.info("Skills data file was empty or contained no data.")
                
        except FileNotFoundError:
             logger.warning(f"Skills section file not found: {skills_filepath}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding skills JSON from {skills_filepath}: {e}")
        except Exception as e:
            logger.error(f"Error processing skills section: {e}")
        
        # Add projects section
        try:
            projects_filepath = os.path.join(api_responses_dir, 'projects.json')
            with open(projects_filepath, 'r') as f:
                projects_data = json.load(f)
                
            if projects_data:
                content_parts.append('<div class="resume-section">')
                content_parts.append('<div class="section-box"><h2>Projects</h2></div>')
                content_parts.append('<div class="projects-content">')
                # Pass the loaded list directly to the formatter
                content_parts.append(format_projects_content(projects_data))
                content_parts.append('</div>')
                content_parts.append('</div>')
            else:
                logger.info("Projects data file was empty or contained no data.")
                
        except FileNotFoundError:
            logger.warning(f"Projects section file not found: {projects_filepath}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding projects JSON from {projects_filepath}: {e}")
        except Exception as e:
            logger.error(f"Error processing projects section: {e}")
        
    except Exception as e:
        logger.error(f"Error generating preview content: {e}")
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