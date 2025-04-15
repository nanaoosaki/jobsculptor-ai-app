import os
import json
import logging
import time
import traceback
import re
import io
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import docx2txt
import tempfile
from typing import Dict, List, Tuple, Optional, Any, Union

# Third-party imports for Claude
from anthropic import Anthropic, RateLimitError

# Third-party imports for OpenAI
import openai
from openai import OpenAI
from claude_api_logger import api_logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to track the last LLM client used
last_llm_client = None

class LLMClient:
    """Base class for LLM API clients"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.tailored_content = {}  # Store tailored responses for direct HTML generation
        
    def tailor_resume_content(self, section_name: str, content: str, job_data: Dict) -> str:
        """Tailor resume content using LLM API - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement this method")

class ClaudeClient(LLMClient):
    """Client for interacting with Claude API"""
    
    def __init__(self, api_key: str, api_url: str = None):
        super().__init__(api_key)
        self.api_url = api_url
        self.client = None
        
        # Validate API key format
        if not api_key or not api_key.startswith('sk-ant'):
            print(f"WARNING: Invalid Claude API key format. Key starts with: {api_key[:6] if api_key else 'None'}")
            print(f"API key length: {len(api_key) if api_key else 0} characters")
            raise ValueError("Claude API key must start with 'sk-ant'")
            
        print(f"Initializing Claude client with API key starting with: {api_key[:8]}...")
        print(f"API key length: {len(api_key)} characters")
        
        # Initialize Anthropic client
        try:
            print("Testing Claude API connection...")
            self.client = Anthropic(api_key=api_key)
            print("Claude client initialized successfully")
        except Exception as e:
            print(f"Error initializing Claude client: {str(e)}")
            print(traceback.format_exc())
            raise ValueError(f"Failed to initialize Claude client: {str(e)}")
    
    def tailor_resume_content(self, section_name: str, content: str, job_data: Dict) -> str:
        """Tailor resume content using Claude API"""
        try:
            logger.info(f"Tailoring {section_name} with Claude API")
            
            # Create the system prompt
            system_prompt = (
                "You are an expert resume writer helping customize a resume for a specific job posting. "
                "Your task is to rewrite and enhance the provided resume section to better align with the "
                "job requirements while maintaining truthfulness. Make impactful improvements that highlight "
                "relevant experience and skills. Be concise and impactful."
            )
            
            # Format requirements and skills as bullet points for clearer prompting
            requirements_text = "\n".join([f"• {req}" for req in job_data.get('requirements', [])])
            skills_text = "\n".join([f"• {skill}" for skill in job_data.get('skills', [])])
            
            # Create the user prompt
            user_prompt = f"""
            # Job Requirements
            {requirements_text}

            # Desired Skills
            {skills_text}

            # Current Resume Section: {section_name}
            {content}

            Please rewrite and enhance the "{section_name}" section to better align with the job requirements. 
            Make specific, tailored improvements while maintaining factual accuracy.
            
            For experience and skills sections, emphasize relevant experience and use industry keywords from the job posting.
            
            Bold (using **text**) the most significant changes that directly address job requirements.
            
            Return ONLY the enhanced content, maintaining the original format with bullet points if present.
            """
            
            # Make the API request
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Log token usage
            logger.info(f"Claude API response for {section_name}: {len(response.content[0].text)} chars")
            logger.info(f"Input tokens: {response.usage.input_tokens}, Output tokens: {response.usage.output_tokens}")
            
            # Store the tailored content for direct HTML generation
            self.tailored_content[section_name] = response.content[0].text.strip()
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Error tailoring {section_name} with Claude API: {str(e)}")
            logger.error(traceback.format_exc())
            # Partial key for debugging
            api_key_prefix = self.api_key[:8] + "..." if self.api_key else "None"
            logger.error(f"Claude API key prefix: {api_key_prefix}, API URL: {self.api_url}")
            raise Exception(f"Claude API error: {str(e)}")

class OpenAIClient(LLMClient):
    """Client for interacting with OpenAI API"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = None
        
        # Validate API key format
        if not api_key or not api_key.startswith('sk-'):
            print(f"WARNING: Invalid OpenAI API key format. Key starts with: {api_key[:6] if api_key else 'None'}")
            print(f"API key length: {len(api_key) if api_key else 0} characters")
            raise ValueError("OpenAI API key must start with 'sk-'")
            
        print(f"Initializing OpenAI client with API key starting with: {api_key[:8]}...")
        print(f"API key length: {len(api_key)} characters")
        
        # Initialize OpenAI client
        try:
            print("Testing OpenAI API connection...")
            self.client = OpenAI(api_key=api_key)
            # No API call validation - just initialize the client
            print("OpenAI client initialized successfully")
        except Exception as e:
            print(f"Error initializing OpenAI client: {str(e)}")
            print(traceback.format_exc())
            raise ValueError(f"Failed to initialize OpenAI client: {str(e)}")
    
    def tailor_resume_content(self, section_name: str, content: str, job_data: Dict) -> str:
        """Tailor resume content using OpenAI API"""
        try:
            logger.info(f"Tailoring {section_name} with OpenAI API")
            
            # Create the system prompt
            system_prompt = (
                "You are an expert resume writer helping customize a resume for a specific job posting. "
                "Your task is to rewrite and enhance the provided resume section to better align with the "
                "job requirements while maintaining truthfulness. Make impactful improvements that highlight "
                "relevant experience and skills. Be concise and impactful."
            )
            
            # Format requirements and skills as bullet points for clearer prompting
            requirements_text = "\n".join([f"• {req}" for req in job_data.get('requirements', [])])
            skills_text = "\n".join([f"• {skill}" for skill in job_data.get('skills', [])])
            
            # Create the user prompt
            user_prompt = f"""
            # Job Requirements
            {requirements_text}

            # Desired Skills
            {skills_text}

            # Current Resume Section: {section_name}
            {content}

            Please rewrite and enhance the "{section_name}" section to better align with the job requirements. 
            Make specific, tailored improvements while maintaining factual accuracy.
            
            For experience and skills sections, emphasize relevant experience and use industry keywords from the job posting.
            
            Bold (using **text**) the most significant changes that directly address job requirements.
            
            Return ONLY the enhanced content, maintaining the original format with bullet points if present.
            """
            
            # Make the API request
            response = self.client.chat.completions.create(
                model="gpt-4o",
                temperature=0.7,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Log token usage
            output_text = response.choices[0].message.content
            logger.info(f"OpenAI API response for {section_name}: {len(output_text)} chars")
            logger.info(f"Completion tokens: {response.usage.completion_tokens}, Prompt tokens: {response.usage.prompt_tokens}")
            
            # Store the tailored content for direct HTML generation
            self.tailored_content[section_name] = output_text.strip()
            
            return output_text.strip()
            
        except Exception as e:
            logger.error(f"Error tailoring {section_name} with OpenAI API: {str(e)}")
            logger.error(traceback.format_exc())
            # Partial key for debugging
            api_key_prefix = self.api_key[:8] + "..." if self.api_key else "None"
            logger.error(f"OpenAI API key prefix: {api_key_prefix}")
            raise Exception(f"OpenAI API error: {str(e)}")

def format_section_content(content: str) -> str:
    """Format section content for HTML display, handling bullet points and markdown"""
    if not content:
        return ""
    
    # Convert markdown bold to HTML bold
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    
    # Check if the content has bullet points
    bullet_point_pattern = r'^[\s]*[•\-\*][\s]'
    lines = content.strip().split('\n')
    
    # If content contains bullet points, format as a list
    if any(re.match(bullet_point_pattern, line) for line in lines):
        formatted_lines = []
        is_in_list = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Handle bullet points (•, -, *)
            if re.match(bullet_point_pattern, line):
                if not is_in_list:
                    formatted_lines.append("<ul>")
                    is_in_list = True
                
                # Remove the bullet and any leading/trailing whitespace
                bullet_content = re.sub(r'^[\s]*[•\-\*][\s]*', '', line).strip()
                formatted_lines.append(f"<li>{bullet_content}</li>")
            else:
                if is_in_list:
                    formatted_lines.append("</ul>")
                    is_in_list = False
                formatted_lines.append(f"<p>{line}</p>")
        
        # Close any open list
        if is_in_list:
            formatted_lines.append("</ul>")
            
        return "\n".join(formatted_lines)
    else:
        # Regular paragraph text
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        return "\n".join([f"<p>{p}</p>" for p in paragraphs])

def extract_resume_sections(doc_path: str) -> Dict[str, str]:
    """Extract sections from a resume document"""
    try:
        logger.info(f"Extracting sections from resume: {doc_path}")
        
        # Import config to check if LLM parsing is enabled
        from config import Config
        use_llm_parsing = Config.USE_LLM_RESUME_PARSING
        llm_provider_config = Config.LLM_RESUME_PARSER_PROVIDER
        
        # First try to parse with LLM if enabled and the module is available
        if use_llm_parsing:
            try:
                # Import the LLM parser module
                from llm_resume_parser import parse_resume_with_llm
                
                # Determine which LLM provider to use based on config or available API keys
                llm_provider = llm_provider_config
                if llm_provider == "auto":
                    if os.environ.get("OPENAI_API_KEY"):
                        llm_provider = "openai"
                    elif os.environ.get("CLAUDE_API_KEY"):
                        llm_provider = "claude"
                    else:
                        logger.warning("No LLM API keys found for resume parsing. Will use traditional parsing.")
                        raise ImportError("No LLM API keys available")
                    
                # Try to parse with LLM
                logger.info(f"Attempting to parse resume with LLM ({llm_provider})...")
                llm_sections = parse_resume_with_llm(doc_path, llm_provider)
                
                # If LLM parsing succeeded, return the results
                if llm_sections and any(content for content in llm_sections.values()):
                    logger.info("LLM parsing successful. Using LLM-parsed sections.")
                    
                    # Log extraction results from LLM
                    for section, content in llm_sections.items():
                        if content:
                            logger.info(f"LLM extracted {section} section: {len(content)} chars")
                        else:
                            logger.info(f"LLM found no content for {section} section")
                    
                    return llm_sections
                else:
                    logger.warning("LLM parsing did not return usable results. Falling back to traditional parsing.")
            except (ImportError, Exception) as e:
                logger.warning(f"LLM parsing unavailable or failed: {str(e)}. Using traditional parsing.")
        else:
            logger.info("LLM parsing is disabled by configuration. Using traditional parsing.")
        
        # If LLM parsing failed, is unavailable, or is disabled, fall back to traditional parsing
        logger.info("Using traditional resume section extraction...")
        
        # Extract plain text content from the DOCX file
        text = docx2txt.process(doc_path)
        
        # Parse the document into sections
        doc = Document(doc_path)
        
        # Initialize standard resume sections
        sections = {
            "contact": "",
            "summary": "",
            "experience": "",
            "education": "",
            "skills": "",
            "projects": "",
            "additional": ""
        }
        
        # Debug: Count total paragraphs with content
        total_paragraphs = sum(1 for para in doc.paragraphs if para.text.strip())
        logger.info(f"Total paragraphs with content: {total_paragraphs}")
        
        # Extract sections based on heading style
        current_section = "contact"  # Default to contact for initial content
        section_content = []
        
        # Log all potential section headers for debugging
        logger.info("Scanning document for potential section headers...")
        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            
            # Skip empty paragraphs
            if not text:
                continue
            
            # Debug potential headers
            if para.style.name.startswith('Heading') or any(p.bold for p in para.runs):
                logger.info(f"Potential header found at para {i}: '{text}' (Style: {para.style.name}, Bold: {any(p.bold for p in para.runs)})")
            
        # First pass - try to extract based on formatting
        for para in doc.paragraphs:
            text = para.text.strip()
            
            # Skip empty paragraphs
            if not text:
                continue
            
            # Check if this is a heading (section title)
            if para.style.name.startswith('Heading') or any(p.bold for p in para.runs):
                # Store previous section content
                if section_content:
                    sections[current_section] = "\n".join(section_content)
                    section_content = []
                
                # Determine new section type based on heading text
                if re.search(r'contact|info|email|phone|address', text.lower()):
                    current_section = "contact"
                elif re.search(r'summary|objective|profile|about', text.lower()):
                    current_section = "summary"
                elif re.search(r'experience|work|employment|job|career|professional', text.lower()):
                    current_section = "experience"
                elif re.search(r'education|degree|university|college|school|academic', text.lower()):
                    current_section = "education"
                elif re.search(r'skills|expertise|technologies|competencies|qualification|proficiencies', text.lower()):
                    current_section = "skills"
                elif re.search(r'projects|portfolio|works', text.lower()):
                    current_section = "projects"
                elif re.search(r'additional|interests|activities|volunteer|certification|awards|achievements', text.lower()):
                    current_section = "additional"
                else:
                    # Default to additional for unknown headings
                    current_section = "additional"
                
                logger.info(f"Section header detected: '{text}' -> categorized as '{current_section}'")
            else:
                # Add content to current section
                section_content.append(text)
        
        # Add the last section content
        if section_content:
            sections[current_section] = "\n".join(section_content)
        
        # Check if we actually found any sections beyond contact
        sections_found = sum(1 for section, content in sections.items() if content and section != "contact")
        logger.info(f"Sections found with standard detection: {sections_found}")
        
        # If we didn't find any sections or only found contact, try a simpler approach
        if sections_found == 0:
            logger.info("No sections detected with standard method. Using fallback approach...")
            
            # Fallback: Treat the entire document as experience section
            if total_paragraphs > 0:
                all_content = "\n".join(para.text for para in doc.paragraphs if para.text.strip())
                if len(all_content) > 0:
                    sections["experience"] = all_content
                    logger.info(f"Fallback: Added {len(all_content)} chars to experience section")
        
        # Log extraction results
        for section, content in sections.items():
            if content:
                logger.info(f"Final extracted {section} section: {len(content)} chars")
            else:
                logger.info(f"No content found for {section} section")
        
        return sections
    
    except Exception as e:
        logger.error(f"Error extracting resume sections: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return at least an empty structure in case of error
        return {
            "contact": "",
            "summary": "",
            "experience": "Error extracting content. Please check your resume format.",
            "education": "",
            "skills": "",
            "projects": "",
            "additional": ""
        }

def generate_preview_from_llm_responses(llm_client: Union[ClaudeClient, OpenAIClient]) -> str:
    """Generate HTML preview directly from LLM API responses"""
    if not llm_client or not llm_client.tailored_content:
        logger.warning("No direct LLM responses available for preview generation")
        return None
        
    logger.info(f"Generating preview from direct LLM responses: {len(llm_client.tailored_content)} sections")
    
    html_parts = []
    
    # Contact information (usually not tailored)
    if "contact" in llm_client.tailored_content:
        contact_html = format_section_content(llm_client.tailored_content["contact"])
        html_parts.append(f'<div class="resume-section"><h2>Contact Information</h2>{contact_html}</div>')
    
    # Summary section
    if "summary" in llm_client.tailored_content:
        summary_html = format_section_content(llm_client.tailored_content["summary"])
        html_parts.append(f'<div class="resume-section"><h2>Professional Summary</h2>{summary_html}</div>')
    
    # Experience section
    if "experience" in llm_client.tailored_content:
        experience_html = format_section_content(llm_client.tailored_content["experience"])
        html_parts.append(f'<div class="resume-section"><h2>Work Experience</h2>{experience_html}</div>')
    
    # Education section
    if "education" in llm_client.tailored_content:
        education_html = format_section_content(llm_client.tailored_content["education"])
        html_parts.append(f'<div class="resume-section"><h2>Education</h2>{education_html}</div>')
    
    # Skills section
    if "skills" in llm_client.tailored_content:
        skills_html = format_section_content(llm_client.tailored_content["skills"])
        html_parts.append(f'<div class="resume-section"><h2>Skills</h2>{skills_html}</div>')
    
    # Projects section
    if "projects" in llm_client.tailored_content:
        projects_html = format_section_content(llm_client.tailored_content["projects"])
        html_parts.append(f'<div class="resume-section"><h2>Projects</h2>{projects_html}</div>')
    
    # Additional information section
    if "additional" in llm_client.tailored_content:
        additional_html = format_section_content(llm_client.tailored_content["additional"])
        html_parts.append(f'<div class="resume-section"><h2>Additional Information</h2>{additional_html}</div>')
    
    # Combine all HTML parts
    preview_html = "\n".join(html_parts)
    
    logger.info(f"Generated tailored resume preview HTML from direct LLM responses: {len(preview_html)} characters")
    
    return preview_html

def generate_resume_preview(doc_path: str) -> str:
    """Generate HTML preview of the resume document"""
    global last_llm_client
    
    # Try to generate preview from direct LLM responses if available
    if last_llm_client:
        preview_html = generate_preview_from_llm_responses(last_llm_client)
        if preview_html:
            logger.info("Using direct LLM responses for preview")
            return preview_html
    
    logger.info("No direct LLM responses available, generating preview from DOCX file")
    
    try:
        # Extract plain text from the document
        text = docx2txt.process(doc_path)
        
        # Parse the document object
        doc = Document(doc_path)
        
        html_parts = []
        current_section = None
        section_content = []
        
        for para in doc.paragraphs:
            text = para.text.strip()
            
            # Skip empty paragraphs
            if not text:
                continue
            
            # Check if this is a heading (section title)
            if para.style.name.startswith('Heading') or any(p.bold for p in para.runs):
                # Add previous section to HTML
                if current_section and section_content:
                    section_html = "\n".join(section_content)
                    html_parts.append(f'<div class="resume-section"><h2>{current_section}</h2>{section_html}</div>')
                    section_content = []
                
                # Set new section
                current_section = text
                
            else:
                # Process content based on if it's a bullet point
                if text.startswith('•') or text.startswith('-') or text.startswith('*'):
                    if not section_content or not section_content[-1].startswith('<ul>'):
                        section_content.append('<ul>')
                    
                    # Remove the bullet point character and format as list item
                    item_text = text[1:].strip()
                    section_content.append(f'<li>{item_text}</li>')
                    
                    # Check if we need to close the list
                    next_is_bullet = False
                    for next_para in doc.paragraphs:
                        if next_para.text.strip() and (next_para.text.strip().startswith('•') or 
                                                      next_para.text.strip().startswith('-') or 
                                                      next_para.text.strip().startswith('*')):
                            next_is_bullet = True
                            break
                    
                    if not next_is_bullet:
                        section_content.append('</ul>')
                else:
                    # Regular paragraph
                    section_content.append(f'<p>{text}</p>')
        
        # Add last section
        if current_section and section_content:
            section_html = "\n".join(section_content)
            html_parts.append(f'<div class="resume-section"><h2>{current_section}</h2>{section_html}</div>')
        
        # Combine all HTML parts
        preview_html = "\n".join(html_parts)
        
        logger.info(f"Generated tailored resume preview HTML from DOCX: {len(preview_html)} characters")
        
        return preview_html
    
    except Exception as e:
        logger.error(f"Error generating resume preview: {str(e)}")
        return f"<p>Error generating preview: {str(e)}</p>"

def tailor_resume_with_llm(resume_path: str, job_data: Dict, api_key: str, provider: str = 'openai', api_url: str = None) -> Tuple[str, str]:
    """Tailor a resume using an LLM API (Claude or OpenAI)"""
    global last_llm_client
    
    try:
        logger.info(f"Tailoring resume with {provider.upper()} API: {resume_path}")
        
        # Extract resume sections
        resume_sections = extract_resume_sections(resume_path)
        
        # Initialize the appropriate LLM client based on provider
        if provider.lower() == 'claude':
            llm_client = ClaudeClient(api_key, api_url)
        elif provider.lower() == 'openai':
            llm_client = OpenAIClient(api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}. Please use 'claude' or 'openai'.")
            
        # Store the client for preview generation
        last_llm_client = llm_client
        
        # Create a new document based on the template
        template_path = os.path.join(os.path.dirname(__file__), 'static', 'template_resume.docx')
        if not os.path.exists(template_path):
            template_path = os.path.join('static', 'template_resume.docx')
            
        if not os.path.exists(template_path):
            # Copy original as template
            template_path = resume_path
            
        logger.info(f"Using template: {template_path}")
        
        doc = Document(template_path)
        
        # Clear the document content
        for para in list(doc.paragraphs):
            p = para._element
            if p.getparent() is not None:
                p.getparent().remove(p)
        
        # Add contact information (not tailored)
        if resume_sections.get('contact'):
            contact_para = doc.add_paragraph()
            contact_para.add_run("Contact Information").bold = True
            contact_para.style = 'Heading 1'
            doc.add_paragraph(resume_sections.get('contact', ''))
        
        # Tailor the professional summary
        if resume_sections.get('summary'):
            summary_para = doc.add_paragraph()
            summary_para.add_run("Professional Summary").bold = True
            summary_para.style = 'Heading 1'
            
            tailored_summary = llm_client.tailor_resume_content(
                'summary', 
                resume_sections.get('summary', ''),
                job_data
            )
            doc.add_paragraph(tailored_summary)
        
        # Tailor the work experience
        if resume_sections.get('experience'):
            exp_para = doc.add_paragraph()
            exp_para.add_run("Work Experience").bold = True
            exp_para.style = 'Heading 1'
            
            tailored_experience = llm_client.tailor_resume_content(
                'experience', 
                resume_sections.get('experience', ''),
                job_data
            )
            
            # Process experience content with bullet points
            for line in tailored_experience.split('\n'):
                if line.strip():
                    if line.strip().startswith('•') or line.strip().startswith('-') or line.strip().startswith('*'):
                        # Add as bullet point
                        p = doc.add_paragraph(line.strip()[1:].strip(), style='List Bullet')
                    else:
                        # Add as regular paragraph
                        doc.add_paragraph(line.strip())
        
        # Add education section (typically not heavily tailored)
        if resume_sections.get('education'):
            edu_para = doc.add_paragraph()
            edu_para.add_run("Education").bold = True
            edu_para.style = 'Heading 1'
            
            tailored_education = llm_client.tailor_resume_content(
                'education',
                resume_sections.get('education', ''),
                job_data
            )
            
            for line in tailored_education.split('\n'):
                if line.strip():
                    doc.add_paragraph(line.strip())
        
        # Tailor the skills section
        if resume_sections.get('skills'):
            skills_para = doc.add_paragraph()
            skills_para.add_run("Skills").bold = True
            skills_para.style = 'Heading 1'
            
            tailored_skills = llm_client.tailor_resume_content(
                'skills', 
                resume_sections.get('skills', ''),
                job_data
            )
            
            # Process skills with bullet points
            for line in tailored_skills.split('\n'):
                if line.strip():
                    if line.strip().startswith('•') or line.strip().startswith('-') or line.strip().startswith('*'):
                        # Add as bullet point
                        p = doc.add_paragraph(line.strip()[1:].strip(), style='List Bullet')
                    else:
                        # Add as regular paragraph
                        doc.add_paragraph(line.strip())
        
        # Add projects section
        if resume_sections.get('projects'):
            proj_para = doc.add_paragraph()
            proj_para.add_run("Projects").bold = True
            proj_para.style = 'Heading 1'
            
            tailored_projects = llm_client.tailor_resume_content(
                'projects',
                resume_sections.get('projects', ''),
                job_data
            )
            
            for line in tailored_projects.split('\n'):
                if line.strip():
                    if line.strip().startswith('•') or line.strip().startswith('-') or line.strip().startswith('*'):
                        # Add as bullet point
                        p = doc.add_paragraph(line.strip()[1:].strip(), style='List Bullet')
                    else:
                        # Add as regular paragraph
                        doc.add_paragraph(line.strip())
        
        # Add additional information
        if resume_sections.get('additional'):
            add_para = doc.add_paragraph()
            add_para.add_run("Additional Information").bold = True
            add_para.style = 'Heading 1'
            
            tailored_additional = llm_client.tailor_resume_content(
                'additional',
                resume_sections.get('additional', ''),
                job_data
            )
            
            for line in tailored_additional.split('\n'):
                if line.strip():
                    doc.add_paragraph(line.strip())
        
        # Save the tailored resume
        filename_parts = os.path.splitext(os.path.basename(resume_path))
        tailored_filename = f"{filename_parts[0]}_tailored_{provider}{filename_parts[1]}"
        
        # Determine the directory for the tailored resume
        uploads_dir = os.path.dirname(resume_path)
        tailored_path = os.path.join(uploads_dir, tailored_filename)
        
        # Save the document
        doc.save(tailored_path)
        
        logger.info(f"Tailored resume saved to: {tailored_path}")
        
        return tailored_filename, tailored_path
    
    except Exception as e:
        logger.error(f"Error tailoring resume with {provider.upper()}: {str(e)}")
        logger.error(traceback.format_exc())
        raise Exception(f"Error tailoring resume with {provider.upper()}: {str(e)}")
