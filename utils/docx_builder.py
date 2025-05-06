"""
DOCX Builder for Resume Tailor Application

Generates Microsoft Word (.docx) files with consistent styling based on design tokens.
"""

import os
import logging
import json
import traceback
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
        logger.info(f"Looking for section file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return {}
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Successfully loaded '{section_name}' section: {type(data)}")
            if isinstance(data, dict):
                logger.info(f"Dict keys for {section_name}: {list(data.keys())}")
            elif isinstance(data, list):
                logger.info(f"List length for {section_name}: {len(data)}")
            return data
    except FileNotFoundError:
        logger.warning(f"Section file not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {e}")
        # Try to get raw content for debugging
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.error(f"Raw content from {file_path} (first 100 chars): {content[:100]}...")
        except Exception:
            pass
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
        logger.info(f"Temp directory path: {temp_dir}")
        
        # Check for files related to this request_id
        try:
            file_list = os.listdir(temp_dir)
            matching_files = [f for f in file_list if request_id in f]
            logger.info(f"Files containing request ID: {matching_files}")
        except Exception as e:
            logger.error(f"Error listing directory: {e}")
        
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
        logger.info("Processing Contact section...")
        contact = load_section_json(request_id, "contact", temp_dir)
        logger.info(f"Contact data loaded: {bool(contact)}")
        
        if contact:
            # Verify contact is a dictionary
            if not isinstance(contact, dict):
                logger.warning(f"Contact section is not a dictionary: {type(contact)}")
                contact = {}
            
            # Check if contact has a 'content' key (alternate structure)
            if 'content' in contact:
                logger.info("Found 'content' key in contact section")
                # Extract actual contact data from content
                try:
                    # Try to access the contact data
                    contact_data = contact['content']
                    if isinstance(contact_data, dict):
                        contact = contact_data
                    logger.info(f"Using contact content: {contact.keys() if isinstance(contact, dict) else type(contact)}")
                except Exception as e:
                    logger.warning(f"Error accessing contact content: {e}")
                
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
        logger.info("Processing Summary section...")
        summary = load_section_json(request_id, "summary", temp_dir)
        logger.info(f"Summary data loaded: {bool(summary)}")
        
        # Handle both direct summary and summary with 'content' key
        summary_text = ""
        if summary:
            if isinstance(summary, dict):
                if "summary" in summary:
                    summary_text = summary.get("summary", "")
                elif "content" in summary:
                    # Alternative structure with content key
                    content = summary.get("content", "")
                    if isinstance(content, dict) and "summary" in content:
                        summary_text = content.get("summary", "")
                    else:
                        summary_text = str(content)
            else:
                summary_text = str(summary)
                
            if summary_text:
                # Add section header
                summary_header = doc.add_paragraph("PROFESSIONAL SUMMARY")
                _apply_paragraph_style(summary_header, "heading2", docx_styles)
                
                # Add summary content
                summary_para = doc.add_paragraph(summary_text)
                _apply_paragraph_style(summary_para, "body", docx_styles)
                
                # Space after section
                doc.add_paragraph("").paragraph_format.space_after = Pt(6)
        
        # ------ EXPERIENCE SECTION ------
        logger.info("Processing Experience section...")
        experience = load_section_json(request_id, "experience", temp_dir)
        logger.info(f"Experience data loaded: {bool(experience)}")
        logger.info(f"Experience contains 'experiences' key: {isinstance(experience, dict) and 'experiences' in experience}")
        
        # Handle both dictionary with 'experiences' key and direct list of experiences
        experiences_list = []
        if experience:
            if isinstance(experience, dict) and "experiences" in experience:
                experiences_list = experience.get("experiences", [])
            elif isinstance(experience, list):
                # Direct list of experiences
                experiences_list = experience
            else:
                logger.warning(f"Unexpected experience format: {type(experience)}")
                
            if experiences_list:
                # Add section header
                exp_header = doc.add_paragraph("EXPERIENCE")
                _apply_paragraph_style(exp_header, "heading2", docx_styles)
                
                # Verify experiences is a list
                if not isinstance(experiences_list, list):
                    logger.warning(f"Experiences is not a list: {type(experiences_list)}")
                    experiences_list = []
                    
                # Add each job
                for job in experiences_list:
                    # Verify job is a dictionary
                    if not isinstance(job, dict):
                        logger.warning(f"Job is not a dictionary: {type(job)}")
                        continue
                        
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
                    achievements = job.get('achievements', [])
                    if not isinstance(achievements, list):
                        logger.warning(f"Achievements is not a list: {type(achievements)}")
                        achievements = []
                        
                    for achievement in achievements:
                        # Create a bullet point
                        bullet_para = doc.add_paragraph()
                        bullet_para.style = 'List Bullet'
                        bullet_para.add_run(str(achievement))
                        _apply_paragraph_style(bullet_para, "body", docx_styles)
                    
                    # Space between jobs
                    doc.add_paragraph("").paragraph_format.space_after = Pt(6)
        
        # ------ EDUCATION SECTION ------
        logger.info("Processing Education section...")
        education = load_section_json(request_id, "education", temp_dir)
        logger.info(f"Education data loaded: {bool(education)}")
        logger.info(f"Education contains 'institutions' key: {isinstance(education, dict) and 'institutions' in education}")
        
        # Handle both dictionary with 'institutions' key and direct list of institutions
        institutions_list = []
        if education:
            if isinstance(education, dict) and "institutions" in education:
                institutions_list = education.get("institutions", [])
            elif isinstance(education, list):
                # Direct list of institutions
                institutions_list = education
            else:
                logger.warning(f"Unexpected education format: {type(education)}")
                
            if institutions_list:
                # Add section header
                edu_header = doc.add_paragraph("EDUCATION")
                _apply_paragraph_style(edu_header, "heading2", docx_styles)
                
                # Verify institutions is a list
                if not isinstance(institutions_list, list):
                    logger.warning(f"Institutions is not a list: {type(institutions_list)}")
                    institutions_list = []
                    
                # Add each institution
                for school in institutions_list:
                    # Verify school is a dictionary
                    if not isinstance(school, dict):
                        logger.warning(f"School is not a dictionary: {type(school)}")
                        continue
                        
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
                    highlights = school.get('highlights', [])
                    if not isinstance(highlights, list):
                        logger.warning(f"Highlights is not a list: {type(highlights)}")
                        highlights = []
                        
                    for highlight in highlights:
                        # Create a bullet point
                        bullet_para = doc.add_paragraph()
                        bullet_para.style = 'List Bullet'
                        bullet_para.add_run(str(highlight))
                        _apply_paragraph_style(bullet_para, "body", docx_styles)
                    
                    # Space between institutions
                    doc.add_paragraph("").paragraph_format.space_after = Pt(6)
        
        # ------ SKILLS SECTION ------
        logger.info("Processing Skills section...")
        skills = load_section_json(request_id, "skills", temp_dir)
        logger.info(f"Skills data loaded: {bool(skills)}")
        logger.info(f"Skills data type: {type(skills)}")
        logger.info(f"Skills content sample: {str(skills)[:100]}")
        
        if skills:
            # Add section header
            skills_header = doc.add_paragraph("SKILLS")
            _apply_paragraph_style(skills_header, "heading2", docx_styles)
            
            # Add skills content - handle different possible formats
            if isinstance(skills, dict) and "skills" in skills:
                skills_content = skills.get("skills", "")
                logger.info(f"Skills content type: {type(skills_content)}")
                
                # Check if skills content is a list
                if isinstance(skills_content, list):
                    logger.info("Processing skills as list")
                    # Handle skills as list
                    for skill in skills_content:
                        skill_para = doc.add_paragraph()
                        skill_para.style = 'List Bullet'
                        skill_para.add_run(str(skill))
                        _apply_paragraph_style(skill_para, "body", docx_styles)
                elif isinstance(skills_content, dict):
                    logger.info("Processing skills as dict")
                    # Handle skills as dictionary with categories
                    for category, skill_list in skills_content.items():
                        # Add category as subheading
                        category_para = doc.add_paragraph(category.upper())
                        _apply_paragraph_style(category_para, "heading3", docx_styles)
                        
                        # Add skills in this category
                        if isinstance(skill_list, list):
                            for skill in skill_list:
                                skill_para = doc.add_paragraph()
                                skill_para.style = 'List Bullet'
                                skill_para.add_run(str(skill))
                                _apply_paragraph_style(skill_para, "body", docx_styles)
                        else:
                            # Not a list, just add as text
                            skill_para = doc.add_paragraph(str(skill_list))
                            _apply_paragraph_style(skill_para, "body", docx_styles)
                else:
                    logger.info("Processing skills as string")
                    # Handle skills as string or any other type
                    skills_para = doc.add_paragraph(str(skills_content))
                    _apply_paragraph_style(skills_para, "body", docx_styles)
            elif isinstance(skills, dict):
                logger.info("Processing skills dict directly")
                # Direct display of skills object if it doesn't have "skills" key
                for category, skill_list in skills.items():
                    # Add category as subheading
                    category_para = doc.add_paragraph(category.upper())
                    _apply_paragraph_style(category_para, "heading3", docx_styles)
                    
                    # Add skills in this category
                    if isinstance(skill_list, list):
                        for skill in skill_list:
                            skill_para = doc.add_paragraph()
                            skill_para.style = 'List Bullet'
                            skill_para.add_run(str(skill))
                            _apply_paragraph_style(skill_para, "body", docx_styles)
                    else:
                        # Not a list, just add as text
                        skill_para = doc.add_paragraph(str(skill_list))
                        _apply_paragraph_style(skill_para, "body", docx_styles)
            elif isinstance(skills, list):
                logger.info("Processing skills as top-level list")
                # Handle the case where skills is a list directly
                for skill in skills:
                    skill_para = doc.add_paragraph()
                    skill_para.style = 'List Bullet'
                    skill_para.add_run(str(skill))
                    _apply_paragraph_style(skill_para, "body", docx_styles)
            else:
                logger.info(f"Processing skills as fallback type: {type(skills)}")
                # Fallback for any other format
                skills_para = doc.add_paragraph(str(skills))
                _apply_paragraph_style(skills_para, "body", docx_styles)
        
        # ------ PROJECTS SECTION ------
        logger.info("Processing Projects section...")
        projects = load_section_json(request_id, "projects", temp_dir)
        logger.info(f"Projects data loaded: {bool(projects)}")
        logger.info(f"Projects contains 'projects' key: {isinstance(projects, dict) and 'projects' in projects}")
        
        # Handle both dictionary with 'projects' key, direct list of projects, and content key
        projects_list = []
        if projects:
            if isinstance(projects, dict) and "projects" in projects:
                projects_list = projects.get("projects", [])
            elif isinstance(projects, dict) and "content" in projects:
                # Handle content key similar to other sections
                logger.info("Found 'content' key in projects section")
                content = projects.get("content", [])
                if isinstance(content, list):
                    projects_list = content
                elif isinstance(content, dict) and "projects" in content:
                    projects_list = content.get("projects", [])
                elif isinstance(content, str):
                    # In some cases, content might be a string
                    logger.info("Projects content is a string, adding as single project")
                    # Add projects section header
                    projects_header = doc.add_paragraph("PROJECTS")
                    _apply_paragraph_style(projects_header, "heading2", docx_styles)
                    
                    # Add the string content directly as paragraph
                    projects_para = doc.add_paragraph(content)
                    _apply_paragraph_style(projects_para, "body", docx_styles)
                    
                    # Skip the rest of the projects processing
                    projects_list = []
                else:
                    logger.warning(f"Unexpected projects content format: {type(content)}")
            elif isinstance(projects, list):
                # Direct list of projects
                projects_list = projects
            else:
                logger.warning(f"Unexpected projects format: {type(projects)}")
                
            if projects_list:
                # Add section header
                projects_header = doc.add_paragraph("PROJECTS")
                _apply_paragraph_style(projects_header, "heading2", docx_styles)
                
                # Verify projects is a list
                if not isinstance(projects_list, list):
                    logger.warning(f"Projects is not a list: {type(projects_list)}")
                    projects_list = []
                    
                # Add each project
                for project in projects_list:
                    # Verify project is a dictionary
                    if not isinstance(project, dict):
                        logger.warning(f"Project is not a dictionary: {type(project)}")
                        continue
                        
                    # Project title and dates
                    title_line = f"{project.get('title', '')}"
                    if project.get('dates'):
                        title_line += f" | {project.get('dates', '')}"
                    title_para = doc.add_paragraph(title_line)
                    _apply_paragraph_style(title_para, "heading3", docx_styles)
                    
                    # Project details
                    details = project.get('details', [])
                    if not isinstance(details, list):
                        logger.warning(f"Details is not a list: {type(details)}")
                        details = []
                        
                    for detail in details:
                        # Create a bullet point
                        bullet_para = doc.add_paragraph()
                        bullet_para.style = 'List Bullet'
                        bullet_para.add_run(str(detail))
                        _apply_paragraph_style(bullet_para, "body", docx_styles)
                
                # Space between projects
                doc.add_paragraph("").paragraph_format.space_after = Pt(6)
        
        # Save the document to BytesIO
        logger.info("Saving DOCX to BytesIO...")
        docx_bytes = BytesIO()
        doc.save(docx_bytes)
        docx_bytes.seek(0)
        
        logger.info(f"Successfully built DOCX for request ID: {request_id}")
        return docx_bytes
    
    except Exception as e:
        # Enhanced error reporting
        logger.error(f"Error building DOCX for request ID {request_id}: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise 