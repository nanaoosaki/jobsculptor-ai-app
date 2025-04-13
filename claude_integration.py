import os
import json
import docx
from docx.shared import Pt
import time
import traceback
from claude_api_logger import api_logger
from anthropic import Anthropic, AI_PROMPT

class ClaudeClient:
    """Client for interacting with Claude API to tailor resumes"""
    
    def __init__(self, api_key, api_url=None):
        self.api_key = api_key
        self.api_url = api_url  # Not used with SDK but kept for compatibility
        self.client = Anthropic(api_key=api_key)
    
    def tailor_resume_content(self, resume_content, job_requirements, section_name, resume_id=None):
        """
        Use Claude API to tailor a specific section of resume content based on job requirements
        """
        if not resume_content.strip():
            return resume_content
        
        # Use a placeholder resume ID if none provided
        if resume_id is None:
            resume_id = f"unknown-{int(time.time())}"
            
        prompt = f"""
You are an expert resume writer helping a job applicant tailor their resume to a specific job posting.
Your task is to significantly improve the following {section_name} section to match the job requirements.

JOB REQUIREMENTS:
{job_requirements}

CURRENT {section_name.upper()} SECTION:
{resume_content}

Please rewrite this {section_name} section to:
1. Make BOLD, SIGNIFICANT changes that highlight relevant skills and experiences matching the job requirements
2. Use strong action verbs and quantify achievements where possible
3. Remove irrelevant information
4. Add relevant keywords from the job posting (even if not in the original resume)
5. Maintain a professional tone
6. Visibly reorganize and restructure content to better match the job requirements

IMPORTANT: Your changes should be significant and noticeable. A good tailored resume should look different from the original.

IMPROVED {section_name.upper()} SECTION:
"""

        try:
            print(f"\n\n========== TAILORING {section_name.upper()} SECTION ==========")
            print(f"Input length: {len(prompt)} characters")
            
            print(f"Sending request to Claude API...")
            
            # Use the official SDK instead of raw HTTP requests
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            print(f"API call successful!")
            
            # Extract response text
            tailored_content = response.content[0].text
            print(f"Original length: {len(resume_content)} | Tailored length: {len(tailored_content)}")
            
            # Check if content actually changed
            if tailored_content.strip() == resume_content.strip():
                print("WARNING: Tailored content is identical to original content")
            else:
                print("Content was modified by Claude API")
            
            # Extract token usage
            token_usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
            
            # Log the API call
            try:
                # Simple, safe request/response summary for logging
                request_summary = {
                    "model": "claude-3-opus-20240229",
                    "prompt_length": len(prompt),
                    "section": section_name,
                    "resume_id": resume_id
                }
                
                response_summary = {
                    "content_length": len(tailored_content),
                    "was_modified": tailored_content.strip() != resume_content.strip(),
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                }
                
                api_logger.log_api_call(
                    request_data=request_summary,
                    response_data=response_summary,
                    resume_id=resume_id,
                    section=section_name,
                    token_usage=token_usage
                )
                print("API call logged successfully")
            except Exception as log_error:
                print(f"Warning: Failed to log API call: {str(log_error)}")
                
            return tailored_content
                
        except Exception as e:
            print(f"Error calling Claude API: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            
            # Log exception
            try:
                api_logger.log_api_call(
                    request_data={"prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt},
                    response_data={"error": str(e)},
                    resume_id=resume_id,
                    section=section_name,
                    token_usage={"error": True}
                )
            except Exception as log_error:
                print(f"Warning: Failed to log API error: {str(log_error)}")
            
            # Return original content but also re-raise so it's properly logged
            raise

def extract_resume_content(filepath):
    """Extract content from a resume DOCX file by section"""
    doc = docx.Document(filepath)
    
    sections = {
        'contact_info': [],
        'summary': [],
        'experience': [],
        'education': [],
        'skills': [],
        'projects': [],
        'other': []
    }
    
    current_section = 'other'
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        # Determine section based on heading text
        if any(run.bold for run in para.runs) or para.style.name.startswith('Heading'):
            text_lower = text.lower()
            if any(term in text_lower for term in ['contact', 'email', 'phone', 'address']):
                current_section = 'contact_info'
            elif any(term in text_lower for term in ['summary', 'objective', 'profile']):
                current_section = 'summary'
            elif any(term in text_lower for term in ['experience', 'employment', 'work']):
                current_section = 'experience'
            elif any(term in text_lower for term in ['education', 'academic']):
                current_section = 'education'
            elif any(term in text_lower for term in ['skill', 'technology', 'competenc']):
                current_section = 'skills'
            elif any(term in text_lower for term in ['project', 'portfolio']):
                current_section = 'projects'
            else:
                current_section = 'other'
        
        # Add paragraph to current section
        sections[current_section].append(text)
    
    # Convert lists to strings
    section_texts = {}
    for section, paragraphs in sections.items():
        section_texts[section] = '\n'.join(paragraphs)
    
    return section_texts

def tailor_resume_with_claude(formatted_resume_path, job_data, api_key, api_url):
    """
    Use Claude API to tailor a resume based on job requirements
    """
    # Get resume ID from filename (strip extension)
    resume_id = os.path.basename(formatted_resume_path).split('.')[0]
    
    # Initialize Claude client
    claude_client = ClaudeClient(api_key, api_url)
    
    # Extract content from formatted resume
    resume_sections = extract_resume_content(formatted_resume_path)
    
    # Format job requirements as text
    job_requirements_text = "Job Title: " + job_data.get('job_title', 'Unknown Position') + "\n"
    job_requirements_text += "Company: " + job_data.get('company', 'Unknown Company') + "\n\n"
    job_requirements_text += "Requirements:\n"
    for req in job_data.get('requirements', []):
        job_requirements_text += f"- {req}\n"
    job_requirements_text += "\nSkills:\n"
    for skill in job_data.get('skills', []):
        job_requirements_text += f"- {skill}\n"
    
    # Tailor each section
    tailored_sections = {}
    
    # Don't tailor contact info
    tailored_sections['contact_info'] = resume_sections['contact_info']
    
    # Initialize all sections with empty strings if they don't exist
    for section in ['summary', 'experience', 'education', 'skills', 'projects', 'other']:
        if section not in tailored_sections:
            tailored_sections[section] = ''
    
    # Tailor summary
    if resume_sections.get('summary'):
        print("Tailoring summary section...")
        tailored_sections['summary'] = claude_client.tailor_resume_content(
            resume_sections['summary'], 
            job_requirements_text,
            "summary",
            resume_id
        )
        # Add a small delay to avoid rate limiting
        time.sleep(1)
    
    # Tailor experience
    if resume_sections.get('experience'):
        print("Tailoring experience section...")
        tailored_sections['experience'] = claude_client.tailor_resume_content(
            resume_sections['experience'], 
            job_requirements_text,
            "experience",
            resume_id
        )
        time.sleep(1)
    
    # Tailor skills
    if resume_sections.get('skills'):
        print("Tailoring skills section...")
        tailored_sections['skills'] = claude_client.tailor_resume_content(
            resume_sections['skills'], 
            job_requirements_text,
            "skills",
            resume_id
        )
        time.sleep(1)
    
    # Other sections remain unchanged
    tailored_sections['education'] = resume_sections.get('education', '')
    tailored_sections['projects'] = resume_sections.get('projects', '')
    tailored_sections['other'] = resume_sections.get('other', '')
    
    # Create new document with tailored content
    doc = docx.Document(formatted_resume_path)
    
    # Clear existing content
    for i in range(len(doc.paragraphs)-1, -1, -1):
        p = doc.paragraphs[i]
        p_element = p._element
        p_element.getparent().remove(p_element)
    
    # Add tailored content
    # Contact Information
    if tailored_sections['contact_info']:
        p = doc.add_paragraph()
        p.style = 'Heading 1'
        p.alignment = 1  # Center
        run = p.add_run("CONTACT INFORMATION")
        run.bold = True
        
        for line in tailored_sections['contact_info'].split('\n'):
            if "CONTACT INFORMATION" not in line:  # Skip the heading
                p = doc.add_paragraph()
                p.style = 'Normal'
                p.alignment = 1  # Center
                p.add_run(line)
    
    # Summary
    if tailored_sections['summary'] and tailored_sections['summary'].strip():
        p = doc.add_paragraph()
        p.style = 'Heading 1'
        run = p.add_run("PROFESSIONAL SUMMARY")
        run.bold = True
        
        for line in tailored_sections['summary'].split('\n'):
            if "PROFESSIONAL SUMMARY" not in line:  # Skip the heading
                p = doc.add_paragraph()
                p.style = 'Normal'
                p.add_run(line)
    
    # Experience
    if tailored_sections['experience'] and tailored_sections['experience'].strip():
        p = doc.add_paragraph()
        p.style = 'Heading 1'
        run = p.add_run("WORK EXPERIENCE")
        run.bold = True
        
        in_job_title = False
        for line in tailored_sections['experience'].split('\n'):
            if "WORK EXPERIENCE" in line:  # Skip the heading
                continue
                
            if line.isupper() or all(run.isupper() for run in line.split()):
                # This is likely a job title
                p = doc.add_paragraph()
                p.style = 'Heading 2'
                run = p.add_run(line)
                run.bold = True
                in_job_title = True
            elif in_job_title and line.strip() and not line.startswith('-'):
                # This is likely a company/date line
                p = doc.add_paragraph()
                p.style = 'Normal'
                p.add_run(line)
                in_job_title = False
            else:
                # Regular content
                p = doc.add_paragraph()
                p.style = 'Normal'
                p.add_run(line)
    
    # Education
    if tailored_sections['education'] and tailored_sections['education'].strip():
        p = doc.add_paragraph()
        p.style = 'Heading 1'
        run = p.add_run("EDUCATION")
        run.bold = True
        
        for line in tailored_sections['education'].split('\n'):
            if "EDUCATION" in line:  # Skip the heading
                continue
                
            if any(term in line.lower() for term in ['university', 'college', 'school']):
                p = doc.add_paragraph()
                p.style = 'Heading 2'
                run = p.add_run(line)
                run.bold = True
            else:
                p = doc.add_paragraph()
                p.style = 'Normal'
                p.add_run(line)
    
    # Skills
    if tailored_sections['skills'] and tailored_sections['skills'].strip():
        p = doc.add_paragraph()
        p.style = 'Heading 1'
        run = p.add_run("SKILLS")
        run.bold = True
        
        for line in tailored_sections['skills'].split('\n'):
            if "SKILLS" in line:  # Skip the heading
                continue
                
            p = doc.add_paragraph()
            p.style = 'Normal'
            p.add_run(line)
    
    # Projects
    if tailored_sections['projects'] and tailored_sections['projects'].strip():
        p = doc.add_paragraph()
        p.style = 'Heading 1'
        run = p.add_run("PROJECTS")
        run.bold = True
        
        for line in tailored_sections['projects'].split('\n'):
            if "PROJECTS" in line:  # Skip the heading
                continue
                
            if any(run.bold for run in p.runs):
                p = doc.add_paragraph()
                p.style = 'Heading 2'
                run = p.add_run(line)
                run.bold = True
            else:
                p = doc.add_paragraph()
                p.style = 'Normal'
                p.add_run(line)
    
    # Other sections
    if tailored_sections['other'] and tailored_sections['other'].strip():
        p = doc.add_paragraph()
        p.style = 'Heading 1'
        run = p.add_run("ADDITIONAL INFORMATION")
        run.bold = True
        
        for line in tailored_sections['other'].split('\n'):
            p = doc.add_paragraph()
            p.style = 'Normal'
            p.add_run(line)
    
    # Generate output filename
    output_filename = os.path.basename(formatted_resume_path).replace('.docx', '_tailored.docx')
    output_path = os.path.join(os.path.dirname(formatted_resume_path), output_filename)
    
    # Save the tailored resume
    doc.save(output_path)
    
    return output_filename, output_path

def generate_resume_preview(docx_path):
    """Generate HTML preview of resume content"""
    doc = docx.Document(docx_path)
    
    html = "<div class='resume-preview'>"
    
    for para in doc.paragraphs:
        if not para.text.strip():
            continue
            
        if para.style.name.startswith('Heading 1'):
            html += f"<h2 class='resume-heading-1'>{para.text}</h2>"
        elif para.style.name.startswith('Heading 2'):
            html += f"<h3 class='resume-heading-2'>{para.text}</h3>"
        else:
            html += f"<p class='resume-paragraph'>{para.text}</p>"
    
    html += "</div>"
    
    return html
