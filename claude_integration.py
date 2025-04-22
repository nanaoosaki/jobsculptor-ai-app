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
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime
from flask import current_app

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

# Import our YC Resume Generator
from yc_resume_generator import YCResumeGenerator

def clean_bullet_points(text: str) -> str:
    """
    Removes bullet point markers from text to prevent duplicate bullet points.
    
    Handles various bullet point formats:
    - Unicode bullets (•, ◦, ▪, ▫, etc.)
    - ASCII bullets (*, -, +, o)
    - Numbered bullets (1., 1), (1), etc.)
    
    Args:
        text (str): Text containing bullet points to clean
        
    Returns:
        str: Cleaned text with bullet point markers removed
    """
    if not text:
        return ""
    
    logger.info(f"Cleaning bullet points from text ({len(text)} chars)")
    
    # Split into lines to process each line individually
    lines = text.split('\n')
    cleaned_lines = []
    bullet_count = 0
    
    # Define comprehensive bullet point patterns
    # Unicode bullet symbols
    unicode_bullets = [
        '•', '◦', '▪', '▫', '■', '□', '▸', '►', '▹', '▻', '▷', '▶', '→', '⇒', '⟹', '⟶',
        '⇢', '⇨', '⟾', '➔', '➜', '➙', '➛', '➝', '➞', '➟', '➠', '➡', '➢', '➣', '➤', '➥', 
        '➦', '➧', '➨', '➩', '➪', '➫', '➬', '➭', '➮', '➯', '➱', '➲', '➳', '➵', '➸', '➼',
        '⦿', '⦾', '⧫', '⧮', '⧠', '⧔', '∙', '◆', '◇', '◈'
    ]
    
    # ASCII/common bullet symbols for regex
    ascii_bullets = r'[\*\-\+o~=#>]'
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            cleaned_lines.append('')
            continue
        
        # Check for Unicode bullet symbols at the beginning
        if line and line[0] in unicode_bullets:
            # Find where the content starts after the bullet and any spaces
            content_start = 1
            while content_start < len(line) and line[content_start].isspace():
                content_start += 1
                
            # Extract just the content, removing the bullet and leading spaces
            if content_start < len(line):
                cleaned_line = line[content_start:]
                cleaned_lines.append(cleaned_line)
                bullet_count += 1
                continue
        
        # Check for ASCII bullet symbols (*, -, +, etc.) at the beginning
        ascii_bullet_match = re.match(r'^\s*[-*•]\s+', line)
        if ascii_bullet_match:
            cleaned_line = line[ascii_bullet_match.end():]
            cleaned_lines.append(cleaned_line)
            bullet_count += 1
            continue
            
        # Check for numbered bullets like "1.", "1)", "(1)", etc.
        numbered_match = re.match(r'^\s*(?:\(?\d+[\.\)\]]\s+|\d+[\.\)\]]\s+|\[\d+\]\s+)', line)
        if numbered_match:
            cleaned_line = line[numbered_match.end():]
            cleaned_lines.append(cleaned_line)
            bullet_count += 1
            continue
            
        # No bullet point found, keep the line as is
        cleaned_lines.append(line)
    
    # Join the cleaned lines back into a single string
    cleaned_text = '\n'.join(cleaned_lines)
    
    # Validate the cleaning
    if bullet_count > 0:
        logger.info(f"Removed {bullet_count} bullet point markers from text")
    
    return cleaned_text

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
        """Initialize the Claude API client"""
        super().__init__(api_key)
        self.api_key = api_key
        self.api_url = api_url
        self.client = None
        self.tailored_content = {}
        
        try:
            # Validate API key format for Claude
            if not api_key:
                raise ValueError("Claude API key is missing")
                
            # Import anthropic library (lazy import to handle missing dependency)
            try:
                from anthropic import Anthropic
                logger.info("Using anthropic SDK for Claude API")
            except ImportError:
                logger.error("Failed to import anthropic SDK. Make sure it's installed with 'pip install anthropic'")
                raise
                
            # Initialize Claude client
            self.client = Anthropic(api_key=api_key)
            logger.info(f"Claude API client initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing Claude API client: {str(e)}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Failed to initialize Claude client: {str(e)}")
    
    def tailor_resume_content(self, section_name: str, content: str, job_data: Dict) -> str:
        """
        Tailor resume content using Claude API
        
        Args:
            section_name: Name of the section to tailor
            content: Content of the section
            job_data: Job data including requirements and skills
            
        Returns:
            Tailored content as string
        """
        logger.info(f"Tailoring {section_name} with Claude API")
        
        if not content or not content.strip():
            logger.warning(f"Empty {section_name} content provided, skipping tailoring")
            return ""
            
        if not self.client:
            logger.error("Claude client not initialized")
            return content
            
        try:
            # Extract job data
            job_title = job_data.get('job_title', 'the position')
            company = job_data.get('company', 'the company')
            requirements = job_data.get('requirements', [])
            skills = job_data.get('skills', [])

            # Prepare requirements and skills text
            requirements_text = "\n".join([f"- {req}" for req in requirements]) if requirements else "Not specified"
            skills_text = ", ".join(skills) if skills else "Not specified"
            
            # Get job analysis if available
            analysis_prompt = ""
            if 'analysis' in job_data and isinstance(job_data['analysis'], dict):
                analysis = job_data['analysis']
                
                # Add candidate profile if available
                if 'candidate_profile' in analysis and analysis['candidate_profile']:
                    analysis_prompt += f"\n\nCANDIDATE PROFILE:\n{analysis['candidate_profile']}"
                
                # Add hard skills if available
                if 'hard_skills' in analysis and analysis['hard_skills']:
                    hard_skills = ", ".join(analysis['hard_skills'])
                    analysis_prompt += f"\n\nKEY HARD SKILLS:\n{hard_skills}"
                    
                # Add soft skills if available
                if 'soft_skills' in analysis and analysis['soft_skills']:
                    soft_skills = ", ".join(analysis['soft_skills'])
                    analysis_prompt += f"\n\nKEY SOFT SKILLS:\n{soft_skills}"
                
                # Add ideal candidate if available
                if 'ideal_candidate' in analysis and analysis['ideal_candidate']:
                    analysis_prompt += f"\n\nIDEAL CANDIDATE:\n{analysis['ideal_candidate']}"

            # Build section-specific prompts
            if section_name == "experience":
                prompt = f"""
You are an expert resume tailoring assistant. Your task is to tailor the work experience section to better match the requirements for a {job_title} position at {company}.

ORIGINAL EXPERIENCE SECTION:
{content}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Return your response as a structured JSON object with the following format:

```json
{{
  "experience": [
    {{
      "company": "Company Name",
      "location": "City, State",
      "position": "Job Title",
      "dates": "Time Period",
      "achievements": [
        "Achievement 1",
        "Achievement 2"
      ]
    }}
  ]
}}
```

Please restructure the experience section to better match the job requirements by:
1. Highlighting relevant experience that demonstrates skills required for this job
2. Focusing on achievements and results rather than just responsibilities
3. Quantifying accomplishments with metrics where possible
4. Using terminology from the job description where appropriate
5. Maintaining the original company names, job titles, and dates

Do not add any fictional experiences or embellish beyond what is reasonable based on the original content.
"""

            elif section_name == "education":
                prompt = f"""
You are an expert resume tailoring assistant. Your task is to tailor the education section to better match the requirements for a {job_title} position at {company}.

ORIGINAL EDUCATION SECTION:
{content}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Return your response as a structured JSON object with the following format:

```json
{{
  "education": [
    {{
      "institution": "University Name",
      "location": "City, State",
      "degree": "Degree Name",
      "dates": "Time Period",
      "highlights": [
        "Highlight 1",
        "Highlight 2"
      ]
    }}
  ]
}}
```

Please rewrite the education section to better match the job requirements. Focus on:
1. Highlighting relevant coursework, projects, or achievements that match the job requirements
2. Emphasizing academic accomplishments that demonstrate skills needed for this position
3. Formatting in a way that emphasizes the most relevant educational experiences
4. Including any certifications or training that matches required skills

Keep the degree names, institutions, and dates exactly the same - only enhance descriptions to make them more relevant.
"""

            elif section_name == "skills":
                prompt = f"""
You are an expert resume tailoring assistant. Your task is to tailor the skills section to better match the requirements for a {job_title} position at {company}.

ORIGINAL SKILLS SECTION:
{content}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Return your response as a structured JSON object with the following format:

```json
{{
  "skills": {{
    "technical": ["Skill 1", "Skill 2"],
    "soft": ["Skill 1", "Skill 2"],
    "other": ["Skill 1", "Skill 2"]
  }}
}}
```

Please rewrite the skills section to better match the job requirements. Focus on:
1. Reordering skills to prioritize those mentioned in the job description
2. Adding any missing skills that the candidate likely has based on their experience (must be reasonable to infer from other sections)
3. Grouping skills into relevant categories that align with the job posting
4. Rephrasing skills using the exact terminology from the job description
5. Removing skills that are irrelevant to this position if the list is very long

Only include skills that are authentic to the candidate based on their resume.
"""

            elif section_name == "projects":
                prompt = f"""
You are an expert resume tailoring assistant. Your task is to tailor the projects section to better match the requirements for a {job_title} position at {company}.

ORIGINAL PROJECTS SECTION:
{content}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Return your response as a structured JSON object with the following format:

```json
{{
  "projects": [
    {{
      "title": "Project Name",
      "dates": "Time Period",
      "details": [
        "Detail 1",
        "Detail 2"
      ]
    }}
  ]
}}
```

Please rewrite the projects section to better match the job requirements. Focus on:
1. Highlighting projects that demonstrate skills required for this job
2. Emphasizing tools, technologies, and methodologies that match the job description
3. Quantifying project outcomes and impacts where possible
4. Rephrasing project descriptions to use terminology from the job posting
5. Focusing on the candidate's specific contributions and leadership roles

Keep the project titles and timelines the same, but enhance descriptions to better align with the job requirements.
"""

            else:
                # For other sections, use a generic prompt
                prompt = f"""
You are an expert resume tailoring assistant. Your task is to tailor the {section_name} section to better match the requirements for a {job_title} position at {company}.

ORIGINAL SECTION:
{content}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Return your response as a structured JSON object with the following format:

```json
{{
  "{section_name}": "The tailored content goes here as a single string"
}}
```

Please rewrite this section to better match the job requirements while maintaining the same basic structure and information.
Focus on emphasizing elements most relevant to this job opportunity.
"""

            # Make the API call
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": "You are an expert resume tailor. Return only valid JSON responses in the specified format."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Get the response content
            response_content = response.content[0].text.strip()
            logger.info(f"Claude API response for {section_name}: {len(response_content)} chars")
            
            # Parse JSON response
            try:
                # First try to extract JSON if not properly formatted
                json_str = response_content
                if not json_str.startswith('{'):
                    # Try to extract JSON from text
                    json_start = response_content.find('{')
                    json_end = response_content.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = response_content[json_start:json_end]
                
                json_response = json.loads(json_str)
                
                # Process JSON based on section type
                if section_name == "experience" and "experience" in json_response:
                    return self._format_experience_json(json_response["experience"])
                elif section_name == "education" and "education" in json_response:
                    return self._format_education_json(json_response["education"])
                elif section_name == "skills" and "skills" in json_response:
                    return self._format_skills_json(json_response["skills"])
                elif section_name == "projects" and "projects" in json_response:
                    return self._format_projects_json(json_response["projects"])
                elif section_name in json_response:
                    # For other sections, just return the string content
                    formatted_text = json_response[section_name]
                    # Store for preview generation
                    self.tailored_content[section_name] = formatted_text
                    return formatted_text
                else:
                    logger.warning(f"JSON response missing expected '{section_name}' key")
                    return content
                    
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from Claude response: {response_content[:100]}...")
                # Store as raw text for fallback
                self.tailored_content[section_name] = response_content
                return response_content
            
        except Exception as e:
            logger.error(f"Error in Claude API call: {str(e)}")
            return content
    
    def _format_experience_json(self, experience_data: List[Dict]) -> str:
        """Format experience JSON data into HTML"""
        if not experience_data:
            return ""
            
        formatted_text = ""
        for job in experience_data:
            company = job.get('company', '')
            location = job.get('location', '')
            position = job.get('position', '')
            dates = job.get('dates', '')
            achievements = job.get('achievements', [])
            
            # Filter out empty or whitespace-only achievements
            if achievements:
                achievements = [a for a in achievements if a and a.strip()]
            
            # New format: company/location on first line, position/dates on second line
            # Company name (left) and location (right)
            formatted_text += f"<p class='job-header'><span class='company'>{company.upper()}</span><span class='location'>{location}</span></p>\n"
            
            # Position (left) and dates (right)
            formatted_text += f"<p class='job-subheader'><span class='position'>{position}</span><span class='dates'>{dates}</span></p>\n"
            
            # Add achievements as bullet points
            if achievements:
                formatted_text += "<ul>\n"
                for achievement in achievements:
                    formatted_text += f"<li>{achievement}</li>\n"
                formatted_text += "</ul>\n"
        
        # Store formatted content for preview generation
        self.tailored_content["experience"] = formatted_text
        return formatted_text
        
    def _format_education_json(self, education_data: List[Dict]) -> str:
        """Format education JSON data into HTML"""
        if not education_data:
            return ""
            
        formatted_text = ""
        for edu in education_data:
            institution = edu.get('institution', '')
            location = edu.get('location', '')
            degree = edu.get('degree', '')
            dates = edu.get('dates', '')
            highlights = edu.get('highlights', [])
            
            # Filter out empty or whitespace-only highlights
            if highlights:
                highlights = [h for h in highlights if h and h.strip()]
            
            # New format: institution/location on first line, degree/dates on second line
            # Institution name (left) and location (right)
            formatted_text += f"<p class='education-header'><span class='institution'>{institution.upper()}</span><span class='location'>{location}</span></p>\n"
            
            # Degree (left) and dates (right)
            formatted_text += f"<p class='education-subheader'><span class='degree'>{degree}</span><span class='dates'>{dates}</span></p>\n"
            
            # Add highlights as bullet points
            if highlights:
                formatted_text += "<ul>\n"
                for highlight in highlights:
                    formatted_text += f"<li>{highlight}</li>\n"
                formatted_text += "</ul>\n"
        
        # Store formatted content for preview generation
        self.tailored_content["education"] = formatted_text
        return formatted_text
        
    def _format_skills_json(self, skills_data: Dict) -> str:
        """Format skills JSON data into HTML"""
        if not skills_data:
            return ""
            
        formatted_text = ""
        
        # Process technical skills
        if 'technical' in skills_data and skills_data['technical']:
            # Filter out empty or whitespace-only skills
            technical_skills = [s for s in skills_data['technical'] if s and s.strip()]
            if technical_skills:
                formatted_text += "<p><strong>Technical Skills:</strong> "
                formatted_text += ", ".join(technical_skills)
                formatted_text += "</p>\n"
            
        # Process soft skills
        if 'soft' in skills_data and skills_data['soft']:
            # Filter out empty or whitespace-only skills
            soft_skills = [s for s in skills_data['soft'] if s and s.strip()]
            if soft_skills:
                formatted_text += "<p><strong>Soft Skills:</strong> "
                formatted_text += ", ".join(soft_skills)
                formatted_text += "</p>\n"
            
        # Process other skills
        if 'other' in skills_data and skills_data['other']:
            # Filter out empty or whitespace-only skills
            other_skills = [s for s in skills_data['other'] if s and s.strip()]
            if other_skills:
                formatted_text += "<p><strong>Other Skills:</strong> "
                formatted_text += ", ".join(other_skills)
                formatted_text += "</p>\n"
        
        # Store formatted content for preview generation
        self.tailored_content["skills"] = formatted_text
        return formatted_text
        
    def _format_projects_json(self, projects_data: List[Dict]) -> str:
        """Format projects JSON data into HTML"""
        if not projects_data:
            return ""
            
        formatted_text = ""
        for project in projects_data:
            title = project.get('title', '')
            dates = project.get('dates', '')
            details = project.get('details', [])
            
            # Filter out empty or whitespace-only details
            if details:
                details = [d for d in details if d and d.strip()]
            
            # New format: project title (left) and dates (right)
            formatted_text += f"<p class='project-header'><span class='project-title'>{title.upper()}</span>"
            if dates:
                formatted_text += f"<span class='dates'>{dates}</span>"
            formatted_text += "</p>\n"
            
            # Add details as bullet points
            if details:
                formatted_text += "<ul>\n"
                for detail in details:
                    formatted_text += f"<li>{detail}</li>\n"
                formatted_text += "</ul>\n"
        
        # Store formatted content for preview generation
        self.tailored_content["projects"] = formatted_text
        return formatted_text

class OpenAIClient(LLMClient):
    """OpenAI API client for resume tailoring"""
    
    def __init__(self, api_key: str):
        """Initialize the OpenAI API client"""
        super().__init__(api_key)
        self.api_key = api_key
        self.client = None
        self.raw_responses = {}  # Store raw JSON responses from API
        self.initialize_client()

    def initialize_client(self):
        """Initialize the OpenAI client"""
        try:
            print(f"Initializing OpenAI client with API key starting with: {self.api_key[:8]}...")
            print(f"API key length: {len(self.api_key)} characters")
            print("Testing OpenAI API connection...")
            
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            
            # Test connection with a simple request - removed limit parameter
            self.client.models.list()
            print("OpenAI client initialized successfully")
            
        except Exception as e:
            print(f"Error initializing OpenAI client: {str(e)}")
            self.client = None
            raise
    
    def tailor_resume_content(self, section_name: str, content: str, job_data: Dict) -> str:
        """
        Tailor resume content using OpenAI API
        
        Args:
            section_name: Name of the section to tailor
            content: Content of the section
            job_data: Job data including requirements and skills
            
        Returns:
            Tailored content as string
        """
        logger.info(f"Tailoring {section_name} with OpenAI API")
            
        if not content or not content.strip():
            logger.warning(f"Empty {section_name} content provided, skipping tailoring")
            return ""
            
        if not self.client:
            logger.error("OpenAI client not initialized")
            return content
        
        try:
            # Extract job data
            job_title = job_data.get('job_title', 'the position')
            company = job_data.get('company', 'the company')
            requirements = job_data.get('requirements', [])
            skills = job_data.get('skills', [])

            # Prepare requirements and skills text
            requirements_text = "\n".join([f"- {req}" for req in requirements]) if requirements else "Not specified"
            skills_text = ", ".join(skills) if skills else "Not specified"
            
            # Get job analysis if available
            analysis_prompt = ""
            if 'analysis' in job_data and isinstance(job_data['analysis'], dict):
                analysis = job_data['analysis']
                
                # Add candidate profile if available
                if 'candidate_profile' in analysis and analysis['candidate_profile']:
                    analysis_prompt += f"\n\nCANDIDATE PROFILE:\n{analysis['candidate_profile']}"
                
                # Add hard skills if available
                if 'hard_skills' in analysis and analysis['hard_skills']:
                    hard_skills = ", ".join(analysis['hard_skills'])
                    analysis_prompt += f"\n\nKEY HARD SKILLS:\n{hard_skills}"
                    
                # Add soft skills if available
                if 'soft_skills' in analysis and analysis['soft_skills']:
                    soft_skills = ", ".join(analysis['soft_skills'])
                    analysis_prompt += f"\n\nKEY SOFT SKILLS:\n{soft_skills}"
                
                # Add ideal candidate if available
                if 'ideal_candidate' in analysis and analysis['ideal_candidate']:
                    analysis_prompt += f"\n\nIDEAL CANDIDATE:\n{analysis['ideal_candidate']}"

            # Build section-specific prompts
            if section_name == "experience":
                prompt = f"""
You are an expert resume tailoring assistant. Your task is to tailor the work experience section to better match the requirements for a {job_title} position at {company}.

ORIGINAL EXPERIENCE SECTION:
{content}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Return your response as a structured JSON object with the following format:

```json
{{
  "experience": [
    {{
      "company": "Company Name",
      "location": "City, State",
      "position": "Job Title",
      "dates": "Time Period",
      "achievements": [
        "Achievement 1",
        "Achievement 2"
      ]
    }}
  ]
}}
```

Please restructure the experience section to better match the job requirements by:
1. Highlighting relevant experience that demonstrates skills required for this job
2. Focusing on achievements and results rather than just responsibilities
3. Quantifying accomplishments with metrics where possible
4. Using terminology from the job description where appropriate
5. Maintaining the original company names, job titles, and dates

IMPORTANT:
1. Do not include empty strings or whitespace-only strings in any arrays
2. Every achievement must contain meaningful content
3. Do not split single achievements into multiple entries
4. Make sure each bullet point contains complete, meaningful content

Do not add any fictional experiences or embellish beyond what is reasonable based on the original content.
"""

            elif section_name == "education":
                prompt = f"""
You are an expert resume tailoring assistant. Your task is to tailor the education section to better match the requirements for a {job_title} position at {company}.

ORIGINAL EDUCATION SECTION:
{content}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Return your response as a structured JSON object with the following format:

```json
{{
  "education": [
    {{
      "institution": "University Name",
      "location": "City, State",
      "degree": "Degree Name",
      "dates": "Time Period",
      "highlights": [
        "Highlight 1",
        "Highlight 2"
      ]
    }}
  ]
}}
```

Please rewrite the education section to better match the job requirements. Focus on:
1. Highlighting relevant coursework, projects, or achievements that match the job requirements
2. Emphasizing academic accomplishments that demonstrate skills needed for this position
3. Formatting in a way that emphasizes the most relevant educational experiences
4. Including any certifications or training that matches required skills

IMPORTANT:
1. Do not include empty strings or whitespace-only strings in any arrays
2. Every highlight must contain meaningful content
3. Do not split single highlights into multiple entries
4. Make sure each bullet point contains complete, meaningful content
5. Ensure all education entries from the original resume are preserved

Keep the degree names, institutions, and dates exactly the same - only enhance descriptions to make them more relevant.
"""

            elif section_name == "skills":
                prompt = f"""
You are an expert resume tailoring assistant. Your task is to tailor the skills section to better match the requirements for a {job_title} position at {company}.

ORIGINAL SKILLS SECTION:
{content}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Return your response as a structured JSON object with the following format:

```json
{{
  "skills": {{
    "technical": ["Skill 1", "Skill 2"],
    "soft": ["Skill 1", "Skill 2"],
    "other": ["Skill 1", "Skill 2"]
  }}
}}
```

Please rewrite the skills section to better match the job requirements. Focus on:
1. Reordering skills to prioritize those mentioned in the job description
2. Adding any missing skills that the candidate likely has based on their experience (must be reasonable to infer from other sections)
3. Grouping skills into relevant categories that align with the job posting
4. Rephrasing skills using the exact terminology from the job description
5. Removing skills that are irrelevant to this position if the list is very long

IMPORTANT:
1. Do not include empty strings or whitespace-only strings in any arrays
2. Every skill must contain meaningful content
3. Do not create duplicate skills
4. Skills should be concise - typically one to three words each
"""

            elif section_name == "projects":
                prompt = f"""
You are an expert resume tailoring assistant. Your task is to tailor the projects section to better match the requirements for a {job_title} position at {company}.

ORIGINAL PROJECTS SECTION:
{content}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Return your response as a structured JSON object with the following format:

```json
{{
  "projects": [
    {{
      "title": "Project Name",
      "dates": "Time Period (optional)",
      "details": [
        "Detail 1",
        "Detail 2"
      ]
    }}
  ]
}}
```

Please rewrite the projects section to better match the job requirements. Focus on:
1. Highlighting projects that demonstrate skills relevant to this position
2. Emphasizing technical achievements and technologies that align with the job description
3. Quantifying impact and results wherever possible
4. Using terminology from the job description where appropriate

IMPORTANT:
1. Do not include empty strings or whitespace-only strings in any arrays
2. Every detail must contain meaningful content
3. Do not split single project descriptions into multiple entries
4. Make sure each bullet point contains complete, meaningful content
5. Ensure all project entries from the original resume are preserved

Maintain the original project names and dates - only enhance descriptions to make them more relevant.
"""

            else:
                # For other sections, use a generic prompt
                prompt = f"""
You are an expert resume tailoring assistant. Your task is to tailor the {section_name} section to better match the requirements for a {job_title} position at {company}.

ORIGINAL SECTION:
{content}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Return your response as a structured JSON object with the following format:

```json
{{
  "{section_name}": "The tailored content goes here as a single string"
}}
```

Please rewrite this section to better match the job requirements while maintaining the same basic structure and information.
Focus on emphasizing elements most relevant to this job opportunity.
"""

            # Send the request to OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o" if "4" in os.environ.get('OPENAI_MODEL_NAME', 'gpt-4') else "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert resume tailoring assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4096,
                top_p=1.0
            )
            
            # Get response text and extract JSON
            response_text = response.choices[0].message.content
            
            # Save raw response for debugging
            self.raw_responses[section_name] = response_text
            
            # Save to file
            try:
                # Create api_responses directory if it doesn't exist
                api_responses_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'api_responses')
                if not os.path.exists(api_responses_dir):
                    os.makedirs(api_responses_dir)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{section_name}_response_{timestamp}.json"
                filepath = os.path.join(api_responses_dir, filename)
                
                # Write response to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(response_text)
                
                logger.info(f"Saved raw API response for {section_name} to {filepath}")
            except Exception as e:
                logger.error(f"Error saving raw API response: {str(e)}")
            
            logger.info(f"OpenAI API response for {section_name}: {len(response_text)} chars")
            
            # Log token usage
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            logger.info(f"Completion tokens: {completion_tokens}, Prompt tokens: {prompt_tokens}")
            
            # Extract JSON from the response
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                
            if json_match:
                json_str = json_match.group(1)
            else:
                # If no json code block, try to find JSON object directly
                json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # No JSON found, return the original content
                    logger.error(f"No JSON found in OpenAI response for {section_name}")
                    return content
            
            # Parse the JSON string
            try:
                json_response = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from OpenAI response: {e}")
                logger.error(f"JSON string: {json_str[:100]}...")
                # Store the raw response as fallback
                self.tailored_content[section_name] = response_text
                return response_text

            # Process JSON based on section type
            if section_name == "experience" and "experience" in json_response:
                return self._format_experience_json(json_response["experience"])
            elif section_name == "education" and "education" in json_response:
                return self._format_education_json(json_response["education"])
            elif section_name == "skills" and "skills" in json_response:
                return self._format_skills_json(json_response["skills"])
            elif section_name == "projects" and "projects" in json_response:
                return self._format_projects_json(json_response["projects"])
            elif section_name in json_response:
                # For other sections, just return the string content 
                formatted_text = json_response[section_name]
                # Store for preview generation
                self.tailored_content[section_name] = formatted_text
                return formatted_text
            else:
                logger.warning(f"JSON response missing expected '{section_name}' key")
                return content
                
        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}")
            return content
            
    def _format_experience_json(self, experience_data: List[Dict]) -> str:
        """Format experience JSON data into HTML"""
        if not experience_data:
            return ""
            
        formatted_text = ""
        for job in experience_data:
            company = job.get('company', '')
            location = job.get('location', '')
            position = job.get('position', '')
            dates = job.get('dates', '')
            achievements = job.get('achievements', [])
            
            # Filter out empty or whitespace-only achievements
            if achievements:
                achievements = [a for a in achievements if a and a.strip()]
            
            # New format: company/location on first line, position/dates on second line
            # Company name (left) and location (right)
            formatted_text += f"<p class='job-header'><span class='company'>{company.upper()}</span><span class='location'>{location}</span></p>\n"
            
            # Position (left) and dates (right)
            formatted_text += f"<p class='job-subheader'><span class='position'>{position}</span><span class='dates'>{dates}</span></p>\n"
            
            # Add achievements as bullet points
            if achievements:
                formatted_text += "<ul>\n"
                for achievement in achievements:
                    formatted_text += f"<li>{achievement}</li>\n"
                formatted_text += "</ul>\n"
        
        # Store formatted content for preview generation
        self.tailored_content["experience"] = formatted_text
        return formatted_text
        
    def _format_education_json(self, education_data: List[Dict]) -> str:
        """Format education JSON data into HTML"""
        if not education_data:
            return ""
            
        formatted_text = ""
        for edu in education_data:
            institution = edu.get('institution', '')
            location = edu.get('location', '')
            degree = edu.get('degree', '')
            dates = edu.get('dates', '')
            highlights = edu.get('highlights', [])
            
            # Filter out empty or whitespace-only highlights
            if highlights:
                highlights = [h for h in highlights if h and h.strip()]
            
            # New format: institution/location on first line, degree/dates on second line
            # Institution name (left) and location (right)
            formatted_text += f"<p class='education-header'><span class='institution'>{institution.upper()}</span><span class='location'>{location}</span></p>\n"
            
            # Degree (left) and dates (right)
            formatted_text += f"<p class='education-subheader'><span class='degree'>{degree}</span><span class='dates'>{dates}</span></p>\n"
            
            # Add highlights as bullet points
            if highlights:
                formatted_text += "<ul>\n"
                for highlight in highlights:
                    formatted_text += f"<li>{highlight}</li>\n"
                formatted_text += "</ul>\n"
        
        # Store formatted content for preview generation
        self.tailored_content["education"] = formatted_text
        return formatted_text
        
    def _format_skills_json(self, skills_data: Dict) -> str:
        """Format skills JSON data into HTML"""
        if not skills_data:
            return ""
            
        formatted_text = ""
        
        # Process technical skills
        if 'technical' in skills_data and skills_data['technical']:
            # Filter out empty or whitespace-only skills
            technical_skills = [s for s in skills_data['technical'] if s and s.strip()]
            if technical_skills:
                formatted_text += "<p><strong>Technical Skills:</strong> "
                formatted_text += ", ".join(technical_skills)
                formatted_text += "</p>\n"
            
        # Process soft skills
        if 'soft' in skills_data and skills_data['soft']:
            # Filter out empty or whitespace-only skills
            soft_skills = [s for s in skills_data['soft'] if s and s.strip()]
            if soft_skills:
                formatted_text += "<p><strong>Soft Skills:</strong> "
                formatted_text += ", ".join(soft_skills)
                formatted_text += "</p>\n"
            
        # Process other skills
        if 'other' in skills_data and skills_data['other']:
            # Filter out empty or whitespace-only skills
            other_skills = [s for s in skills_data['other'] if s and s.strip()]
            if other_skills:
                formatted_text += "<p><strong>Other Skills:</strong> "
                formatted_text += ", ".join(other_skills)
                formatted_text += "</p>\n"
        
        # Store formatted content for preview generation
        self.tailored_content["skills"] = formatted_text
        return formatted_text
        
    def _format_projects_json(self, projects_data: List[Dict]) -> str:
        """Format projects JSON data into HTML"""
        if not projects_data:
            return ""
            
        formatted_text = ""
        for project in projects_data:
            title = project.get('title', '')
            dates = project.get('dates', '')
            details = project.get('details', [])
            
            # Filter out empty or whitespace-only details
            if details:
                details = [d for d in details if d and d.strip()]
            
            # New format: project title (left) and dates (right)
            formatted_text += f"<p class='project-header'><span class='project-title'>{title.upper()}</span>"
            if dates:
                formatted_text += f"<span class='dates'>{dates}</span>"
            formatted_text += "</p>\n"
            
            # Add details as bullet points
            if details:
                formatted_text += "<ul>\n"
                for detail in details:
                    formatted_text += f"<li>{detail}</li>\n"
                formatted_text += "</ul>\n"
        
        # Store formatted content for preview generation
        self.tailored_content["projects"] = formatted_text
        return formatted_text

    # Add a method to save all raw responses to a single file
    def save_all_raw_responses(self, resume_filename):
        """Save all raw API responses to a single file"""
        try:
            # Create api_responses directory if it doesn't exist
            api_responses_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'api_responses')
            if not os.path.exists(api_responses_dir):
                os.makedirs(api_responses_dir)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(resume_filename))[0]
            filename = f"{base_name}_all_responses_{timestamp}.json"
            filepath = os.path.join(api_responses_dir, filename)
            
            # Write all responses to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.raw_responses, f, indent=2)
            
            logger.info(f"Saved all raw API responses to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving all raw API responses: {str(e)}")
            return None

def format_section_content(content: str) -> str:
    """Format section content for HTML display, handling bullet points and markdown"""
    if not content:
        return ""
    
    # Remove markdown bold formatting (don't convert to HTML bold)
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
    
    # Filter out job requirements that might be included by the LLM
    filtered_lines = []
    
    # Check for job requirement phrases and patterns
    requirement_patterns = [
        r'job requirement', r'required skill', r'desired skill',
        r'job description', r'key qualification', r'qualification',
        r'requirements:', r'skills required:', r'responsibilities:',
        r'what you\'ll do:', r'what you\'ll need:', r'looking for',
        r'ideal candidate', r'candidate profile', r'about the job',
        r'the role requires', r'will be responsible for',
        r'machine learning', r'and deep learning', r'with the ability to tackle',
        r'complex challenges', r'collaborate with diverse teams',
        r'candidate should be passionate', r'analytical thinking',
        r'candidate profile', r'hard skills', r'soft skills', 
        r'required hard skills', r'required soft skills',
        r'the employer is looking for', r'the position requires'
    ]
    
    skip_section = False
    for line in content.strip().split('\n'):
        line_lower = line.strip().lower()
        
        # Check for job requirements headers or sections
        if any(pattern in line_lower for pattern in requirement_patterns):
            skip_section = True
            continue
            
        # Check for numbered list items that might be requirements
        if re.match(r'^\d+\.\s+', line) and skip_section:
            continue
            
        # Reset after a section break
        if line.strip() == '' or line.startswith('---') or line.startswith('=='):
            skip_section = False
            
        # Skip sections that look like job requirements
        if skip_section:
            continue
            
        # Skip LLM note lines or prompt instruction leakage
        if line.strip().startswith('#') or 'instructions:' in line_lower or 'action verbs' in line_lower:
            continue
            
        filtered_lines.append(line)
    
    # Use the filtered content
    content = '\n'.join(filtered_lines)
    
    # The following patterns are used to identify if lines were originally bullet points
    # before clean_bullet_points was applied
    # Check for short phrases that likely were bullet points originally
    lines = content.strip().split('\n')
    
    # Characteristics that suggest a line was originally a bullet point:
    # 1. Starts with a capital letter and ends with a period (sentence format)
    # 2. Short to medium length (typical for bullet points)
    # 3. Starts with an action verb (common in resume bullet points)
    
    # Common action verbs in resumes
    action_verbs = [
        'developed', 'created', 'implemented', 'designed', 'built', 'managed',
        'led', 'coordinated', 'established', 'initiated', 'launched', 'conducted',
        'generated', 'produced', 'architected', 'engineered', 'integrated',
        'optimized', 'enhanced', 'improved', 'increased', 'reduced', 'secured',
        'utilized', 'analyzed', 'researched'
    ]
    
    # Check if lines have bullet point characteristics
    should_be_bullets = []
    for line in lines:
        line = line.strip()
        if not line:
            should_be_bullets.append(False)
            continue
            
        # Check for actual bullet characters (these should already be removed, but check anyway)
        if re.match(r'^[\s]*[•\-\*][\s]', line):
            should_be_bullets.append(True)
            continue
            
        # Check for sentence format and reasonable length for bullet points
        is_sentence_format = (line[0].isupper() if line else False) and (line.endswith('.') or line.endswith('!') or line.endswith(':'))
        reasonable_length = 10 <= len(line) <= 200  # Typical bullet point length in characters
        
        # Check for action verbs at the beginning
        starts_with_action_verb = any(line.lower().startswith(verb) for verb in action_verbs)
        
        # Check for integration phrases (common in tech experience bullet points)
        contains_integration_terms = any(term in line.lower() for term in ['aws', 'api', 'integrated', 'using', 'leveraging', 'utilizing'])
        
        # If several characteristics match, likely it was a bullet point
        if (starts_with_action_verb or is_sentence_format) and (reasonable_length or contains_integration_terms):
            should_be_bullets.append(True)
        else:
            should_be_bullets.append(False)
    
    # Format content based on our analysis
    formatted_lines = []
    is_in_list = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        if should_be_bullets[i]:
            if not is_in_list:
                formatted_lines.append("<ul class='dot-bullets' style='text-align: left;'>")
                is_in_list = True
                
            # Proper content without bullet character (already cleaned)
            formatted_lines.append(f"<li style='text-align: left;'>{line}</li>")
        else:
            if is_in_list:
                formatted_lines.append("</ul>")
                is_in_list = False
            formatted_lines.append(f"<p style='text-align: left;'>{line}</p>")
    
    # Close any open list
    if is_in_list:
        formatted_lines.append("</ul>")
        
    return "\n".join(formatted_lines)

def extract_resume_sections(doc_path: str) -> Dict[str, str]:
    """Extract sections from a resume document"""
    try:
        logger.info(f"Extracting sections from resume: {doc_path}")
        print(f"DEBUG: extract_resume_sections called with doc_path: {doc_path}")
        
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
                
                # If LLM parsing succeeded, clean bullet points from each section
                if llm_sections and any(content for content in llm_sections.values()):
                    logger.info("LLM parsing successful. Cleaning bullet points from LLM-parsed sections.")
                    
                    # Clean bullet points from each section
                    cleaned_sections = {}
                    for section, content in llm_sections.items():
                        if content:
                            cleaned_content = clean_bullet_points(content)
                            cleaned_sections[section] = cleaned_content
                            logger.info(f"LLM extracted and cleaned {section} section: {len(cleaned_content)} chars")
                        else:
                            cleaned_sections[section] = ""
                            logger.info(f"LLM found no content for {section} section")
                    
                    # Validate the cleaning was successful
                    validation_success = validate_bullet_point_cleaning(cleaned_sections)
                    if not validation_success:
                        logger.warning("Bullet point cleaning validation failed. There may still be bullet markers in the text.")
                    
                    return cleaned_sections
                else:
                    logger.warning("LLM parsing did not return usable results. Falling back to traditional parsing.")
            except (ImportError, Exception) as e:
                logger.warning(f"LLM parsing unavailable or failed: {str(e)}. Using traditional parsing.")
        else:
            logger.info("LLM parsing is disabled by configuration. Using traditional parsing.")
        
        # If LLM parsing failed, is unavailable, or is disabled, fall back to traditional parsing
        logger.info("Using traditional resume section extraction...")
        print(f"DEBUG: fallback to traditional parsing - will examine document: {doc_path}")
        
        # Extract plain text content from the DOCX file
        text = docx2txt.process(doc_path)
        
        # Parse the document into sections
        print(f"DEBUG: About to create Document object from: {doc_path}")
        doc = Document(doc_path)
        print(f"DEBUG: Document object created successfully - examining sections")
        
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
        
        # Clean bullet points from traditional parsing results
        cleaned_sections = {}
        for section, content in sections.items():
            if content:
                cleaned_content = clean_bullet_points(content)
                cleaned_sections[section] = cleaned_content
                logger.info(f"Traditional parsing: cleaned {section} section: {len(cleaned_content)} chars")
            else:
                cleaned_sections[section] = ""
        
        # Validate the cleaning was successful
        validation_success = validate_bullet_point_cleaning(cleaned_sections)
        if not validation_success:
            logger.warning("Bullet point cleaning validation failed. There may still be bullet markers in the text.")
        
        return cleaned_sections
    
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

def validate_bullet_point_cleaning(sections: Dict[str, str]) -> bool:
    """
    Validates that bullet points have been properly cleaned from resume sections.
    
    Args:
        sections (Dict[str, str]): Dictionary of resume sections
        
    Returns:
        bool: True if validation passed, False if bullet points were found
    """
    bullet_patterns = [
        # Unicode bullets
        r'^[•◦▪▫■□▸►▹▻▷▶→⇒⟹⟶⇢⇨⟾➔➜➙➛➝➞➟➠➡➢➣➤➥➦➧➨➩➪➫➬➭➮➯➱➲➳➵➸➼⦿⦾⧫⧮⧠⧔∙◆◇◈]',
        # ASCII bullets at beginning of line (after any whitespace)
        r'^\s*[\*\-\+o~=#>]\s+',
        # Numbered bullets
        r'^\s*(?:\(?\d+[\.\)\]]\s+|\d+[\.\)\]]\s+|\[\d+\]\s+)'
    ]
    
    for section, content in sections.items():
        if not content:
            continue
            
        lines = content.split('\n')
        for i, line in enumerate(lines):
            for pattern in bullet_patterns:
                if re.search(pattern, line):
                    logger.warning(f"Validation found bullet marker in {section} section, line {i+1}: '{line[:30]}...'")
                    return False
    
    return True

def validate_html_content(html_content: str) -> str:
    """Remove any empty bullet points from HTML content"""
    if not html_content:
        return ""
    
    # Replace empty list items with nothing
    html_content = re.sub(r'<li>\s*</li>\n?', '', html_content)
    
    # Remove empty unordered lists (lists with no items)
    html_content = re.sub(r'<ul>\s*</ul>\n?', '', html_content)
    
    return html_content

def generate_preview_from_llm_responses(llm_client: Union[ClaudeClient, OpenAIClient]) -> str:
    """Generate HTML preview directly from LLM API responses"""
    if not llm_client or not llm_client.tailored_content:
        logger.warning("No direct LLM responses available for preview generation")
        return None
        
    logger.info(f"Generating preview from direct LLM responses: {len(llm_client.tailored_content)} sections")
    
    html_parts = []
    
    # Contact information at the top (usually not tailored)
    # Always include contact information from the original resume
    from resume_processor import extract_resume_sections as extract_original_sections
    
    # First try to get contact from the LLM responses
    if "contact" in llm_client.tailored_content and llm_client.tailored_content["contact"]:
        contact_text = llm_client.tailored_content["contact"].strip()
    else:
        # If contact info wasn't included in LLM responses, try to get it from the original parsed resume
        try:
            # Since we don't have direct access to the original resume path here,
            # we'll use the cached data from when we last parsed the resume
            from llm_resume_parser import get_cached_parsed_resume
            cached_resume = get_cached_parsed_resume()
            if cached_resume and "contact_info" in cached_resume:
                contact_text = cached_resume["contact_info"]
                logger.info("Using contact information from cached resume parsing")
            else:
                # Fallback: Use empty contact section
                contact_text = ""
                logger.warning("No contact information found in cached resume or LLM responses")
        except Exception as e:
            logger.error(f"Error retrieving contact information: {str(e)}")
            contact_text = ""
    
    # Format contact section if we have content
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
        html_parts.append(contact_html)
    
    # Summary section
    if "summary" in llm_client.tailored_content:
        summary_html = format_section_content(llm_client.tailored_content["summary"])
        summary_html = validate_html_content(summary_html)  # Remove empty bullet points
        if summary_html.strip():
            html_parts.append(f'<div class="resume-section"><h2>Professional Summary</h2><div class="summary-content">{summary_html}</div></div>')
    
    # Experience section with improved formatting using format_job_entry
    if "experience" in llm_client.tailored_content:
        experience_content = llm_client.tailored_content["experience"]
        experience_content = validate_html_content(experience_content)  # Remove empty bullet points
        
        # Process the experience content to extract job entries
        experience_entries = []
        current_entry = {}
        current_bullets = []
        
        # Split content into lines for processing
        lines = experience_content.strip().split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
                
            # Check if this is a company line (often in all caps or bold)
            if line.isupper() or (i == 0) or (i > 0 and not lines[i-1].strip()):
                # If we have a current entry, add it to our list
                if current_entry and 'company' in current_entry:
                    # Add bullets to current entry
                    if current_bullets:
                        current_entry['content'] = current_bullets
                    
                    # Add entry to our list
                    experience_entries.append(current_entry)
                    
                # Start a new entry
                current_entry = {}
                current_bullets = []
                
                # Try to split company and location
                company_parts = re.split(r'\s*[,|-]\s*|\s{2,}', line, 1)
                if len(company_parts) > 1:
                    current_entry['company'] = company_parts[0].strip()
                    current_entry['location'] = company_parts[1].strip()
                else:
                    current_entry['company'] = line
                    current_entry['location'] = ""
                    
            # Check if this is a position and date line
            elif 'company' in current_entry and 'position' not in current_entry:
                # Try to identify position and dates
                date_match = re.search(r'\d{4}\s*[-–—]\s*(?:\d{4}|Present|Current|Now)', line, re.IGNORECASE)
                
                if date_match:
                    # Get the position and dates
                    date_part = line[date_match.start():date_match.end()]
                    position_part = line[:date_match.start()].strip()
                    
                    # Clean up extra characters
                    position_part = re.sub(r'[|,]\s*$', '', position_part).strip()
                    date_part = date_part.strip()
                    
                    current_entry['position'] = position_part
                    current_entry['dates'] = date_part
                else:
                    # Just use the whole line as position
                    current_entry['position'] = line
                    current_entry['dates'] = ""
            
            # Bullet points or description
            elif 'position' in current_entry and line:
                # Check if it's a bullet point
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    bullet_content = re.sub(r'^[•\-*]\s*', '', line).strip()
                    if bullet_content:  # Only add non-empty bullet points
                        current_bullets.append(bullet_content)
                else:
                    # Regular text, just add as a bullet for now if it's not empty
                    if line.strip():
                        current_bullets.append(line)
            
            i += 1
        
        # Add the last entry if we have one
        if current_entry and 'company' in current_entry:
            if current_bullets:
                current_entry['content'] = current_bullets
            experience_entries.append(current_entry)
        
        # Now format each entry using format_job_entry
        formatted_entries = []
        for entry in experience_entries:
            company = entry.get('company', '')
            location = entry.get('location', '')
            position = entry.get('position', '')
            dates = entry.get('dates', '')
            content = entry.get('content', [])
            
            # Filter out empty content items
            content = [c for c in content if c and c.strip()]
            
            if content:  # Only add entries with actual content
                formatted_entries.append(format_job_entry(company, location, position, dates, content))
        
        # Combine all formatted entries
        formatted_experience = "\n".join(formatted_entries)
        if formatted_experience.strip():
            html_parts.append(f'<div class="resume-section"><h2>Work Experience</h2><div class="experience-content">{formatted_experience}</div></div>')
    
    # Education section with improved formatting
    if "education" in llm_client.tailored_content:
        education_content = llm_client.tailored_content["education"]
        education_content = validate_html_content(education_content)  # Remove empty bullet points
        if education_content.strip():
            formatted_education = format_education_content(education_content)
            html_parts.append(f'<div class="resume-section"><h2>Education</h2><div class="education-content">{formatted_education}</div></div>')
    
    # Skills section
    if "skills" in llm_client.tailored_content:
        skills_html = format_section_content(llm_client.tailored_content["skills"])
        skills_html = validate_html_content(skills_html)  # Remove empty bullet points
        if skills_html.strip():
            html_parts.append(f'<div class="resume-section"><h2>Skills</h2><div class="skills-content">{skills_html}</div></div>')
    
    # Projects section with improved formatting
    if "projects" in llm_client.tailored_content:
        projects_content = llm_client.tailored_content["projects"]
        projects_content = validate_html_content(projects_content)  # Remove empty bullet points
        if projects_content.strip():
            formatted_projects = format_projects_content(projects_content)
            html_parts.append(f'<div class="resume-section"><h2>Projects</h2><div class="projects-content">{formatted_projects}</div></div>')
    
    # Additional information section
    if "additional" in llm_client.tailored_content:
        additional_html = format_section_content(llm_client.tailored_content["additional"])
        additional_html = validate_html_content(additional_html)  # Remove empty bullet points
        if additional_html.strip():
            html_parts.append(f'<div class="resume-section"><h2>Additional Information</h2><div class="additional-content">{additional_html}</div></div>')
    
    # Combine all HTML parts
    preview_html = "\n".join(html_parts)
    
    # Final validation to remove any remaining empty bullet points
    preview_html = validate_html_content(preview_html)
    
    logger.info(f"Generated tailored resume preview HTML from direct LLM responses: {len(preview_html)} characters")
    
    # Debug output - log the first 500 characters of the generated HTML
    logger.debug(f"HTML Preview first 500 chars: {preview_html[:500]}")
    
    return preview_html

def format_education_content(content: str) -> str:
    """Format education content with institution/location and degree/date layout"""
    # The education formatting is similar to experience formatting
    # but with slightly different naming and expectations
    if not content:
        return ""
    
    # Filter content as in format_experience_content
    filtered_lines = []
    for line in content.strip().split('\n'):
        line_lower = line.strip().lower()
        if (line.strip().startswith('#') or 
            'instructions:' in line_lower or 
            'action verbs' in line_lower):
            continue
        filtered_lines.append(line)
    
    content = '\n'.join(filtered_lines)
    
    # Split into paragraphs for processing
    paragraphs = content.strip().split('\n\n')
    if not paragraphs:
        return ""
    
    formatted_parts = []
    current_institution = None
    current_location = None
    current_degree = None
    current_dates = None
    bullets = []
    
    for para in paragraphs:
        lines = para.strip().split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check if it's a bullet point
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # Add bullet to current education entry
                bullet_content = re.sub(r'^[•\-\*]\s*', '', line).strip()
                bullets.append(bullet_content)
            elif i == 0 and (i == len(lines) - 1 or not any(l.startswith(('•', '-', '*')) for l in lines[1:])):
                # This is likely a standalone line (like institution name)
                # First, check for explicitly formatted institution and location with separators
                if ',' in line or ' | ' in line or ' - ' in line:
                    # Output previous education if exists
                    if current_institution is not None:
                        formatted_parts.append(format_education_entry(current_institution, current_location, current_degree, current_dates, bullets))
                        bullets = []
                    
                    # Try to split institution and location
                    if ',' in line:
                        parts = line.split(',', 1)
                    elif ' | ' in line:
                        parts = line.split(' | ', 1)
                    else:
                        parts = line.split(' - ', 1)
                    
                    current_institution = parts[0].strip()
                    current_location = parts[1].strip() if len(parts) > 1 else ""
                    current_degree = None
                    current_dates = None
                else:
                    # Try to detect if the line has an institution name followed by a city name
                    # Common pattern: "UNIVERSITY NAME CITY STATE" or "UNIVERSITY NAME CITY"
                    city_pattern = r'(.*?)(\b(?:LOS ANGELES|NEW YORK|CHICAGO|HOUSTON|SAN FRANCISCO|BOSTON|SEATTLE|MIAMI|DENVER|ATLANTA|DALLAS|PHILADELPHIA|PORTLAND|SAN DIEGO|SAN JOSE|WASHINGTON|AUSTIN|NASHVILLE)\b)(.*?)?$'
                    city_match = re.search(city_pattern, line, re.IGNORECASE)
                    
                    if city_match:
                        # Output previous education if exists
                        if current_institution is not None:
                            formatted_parts.append(format_education_entry(current_institution, current_location, current_degree, current_dates, bullets))
                            bullets = []
                        
                        # Extract institution, city, and state
                        institution = city_match.group(1).strip()
                        city = city_match.group(2).strip()
                        state = city_match.group(3).strip() if city_match.group(3) else ""
                        
                        # Set the current values
                        current_institution = institution
                        current_location = f"{city}{', ' + state if state else ''}"
                        current_degree = None
                        current_dates = None
                    else:
                        # Just an institution without location
                        # Output previous education if exists
                        if current_institution is not None:
                            formatted_parts.append(format_education_entry(current_institution, current_location, current_degree, current_dates, bullets))
                            bullets = []
                        
                        current_institution = line
                        current_location = ""
                        current_degree = None
                        current_dates = None
            elif current_institution is not None and current_degree is None:
                # This is likely the degree and dates line
                # Try to identify if it has dates
                date_match = re.search(r'\(([^)]+)\)|\s-\s([^-]+)$|,\s*([^,]+)$', line)
                if date_match:
                    date_part = date_match.group(1) or date_match.group(2) or date_match.group(3)
                    degree_part = line.replace(f"({date_part})", "").replace(f" - {date_part}", "").replace(f", {date_part}", "").strip()
                    current_degree = degree_part
                    current_dates = date_part
                else:
                    # No clear date format, assume entire line is degree
                    current_degree = line
                    current_dates = ""
    
    # Add the last education entry
    if current_institution is not None:
        formatted_parts.append(format_education_entry(current_institution, current_location, current_degree, current_dates, bullets))
    
    # If no structured entries were found, fall back to simple formatting
    if not formatted_parts and content.strip():
        return format_section_content(content)
    
    return "\n".join(formatted_parts)

def format_projects_content(content: str) -> str:
    """Format projects content with project name/date and description layout"""
    if not content:
        return ""
    
    # Filter content as in format_experience_content
    filtered_lines = []
    for line in content.strip().split('\n'):
        line_lower = line.strip().lower()
        if (line.strip().startswith('#') or 
            'instructions:' in line_lower or 
            'action verbs' in line_lower):
            continue
        filtered_lines.append(line)
    
    content = '\n'.join(filtered_lines)
    
    # Split into paragraphs for processing
    paragraphs = content.strip().split('\n\n')
    if not paragraphs:
        return ""
    
    formatted_parts = []
    current_project = None
    current_dates = None
    bullets = []
    
    for para in paragraphs:
        lines = para.strip().split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check if it's a bullet point
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # Add bullet to current project
                bullet_content = re.sub(r'^[•\-\*]\s*', '', line).strip()
                bullets.append(bullet_content)
            elif i == 0:
                # This is likely a project title, possibly with dates
                # Check if it has dates
                date_match = re.search(r'\(([^)]+)\)|\s-\s([^-]+)$', line)
                if date_match:
                    # Output previous project if exists
                    if current_project is not None:
                        formatted_parts.append(format_project_entry(current_project, current_dates, bullets))
                        bullets = []
                    
                    date_part = date_match.group(1) or date_match.group(2)
                    project_part = line.replace(f"({date_part})", "").replace(f" - {date_part}", "").strip()
                    current_project = project_part
                    current_dates = date_part
                else:
                    # No dates, just project name
                    # Output previous project if exists
                    if current_project is not None:
                        formatted_parts.append(format_project_entry(current_project, current_dates, bullets))
                        bullets = []
                    
                    current_project = line
                    current_dates = ""
    
    # Add the last project entry
    if current_project is not None:
        formatted_parts.append(format_project_entry(current_project, current_dates, bullets))
    
    # If no structured entries were found, fall back to simple formatting
    if not formatted_parts and content.strip():
        return format_section_content(content)
    
    return "\n".join(formatted_parts)

def format_job_entry(company: str, location: str, position: str, dates: str, content: List[str]) -> str:
    """Format a job entry with company, location, position, dates, and content"""
    # Format the header with company (left) and location (right)
    header = f"<p class='job-header'><span class='company'>{company.upper()}</span><span class='location'>{location}</span></p>\n"
    
    # Format the subheader with position (left) and dates (right)
    subheader = f"<p class='job-subheader'><span class='position'>{position}</span><span class='dates'>{dates}</span></p>\n"
    
    # Format the content as bullet points
    content_html = ""
    if content:
        content_html = "<ul>\n"
        for item in content:
            if item and item.strip():
                content_html += f"<li>{item.strip()}</li>\n"
        content_html += "</ul>\n"
    
    return header + subheader + content_html

def format_education_entry(institution: str, location: str, degree: str, dates: str, highlights: List[str]) -> str:
    """Format an education entry with institution, location, degree, dates, and highlights"""
    # Format the header with institution (left) and location (right)
    header = f"<p class='education-header'><span class='institution'>{institution.upper()}</span><span class='location'>{location}</span></p>\n"
    
    # Format the subheader with degree (left) and dates (right)
    subheader = f"<p class='education-subheader'><span class='degree'>{degree}</span><span class='dates'>{dates}</span></p>\n"
    
    # Format the highlights as bullet points
    content_html = ""
    if highlights:
        content_html = "<ul>\n"
        for item in highlights:
            if item and item.strip():
                content_html += f"<li>{item.strip()}</li>\n"
        content_html += "</ul>\n"
    
    return header + subheader + content_html

def format_project_entry(title: str, dates: str, details: List[str]) -> str:
    """Format a project entry with title, dates, and details"""
    # Format the header with title (left) and dates (right)
    header = f"<p class='project-header'><span class='project-title'>{title.upper()}</span>"
    if dates:
        header += f"<span class='dates'>{dates}</span>"
    header += "</p>\n"
    
    # Format the details as bullet points
    content_html = ""
    if details:
        content_html = "<ul>\n"
        for item in details:
            if item and item.strip():
                content_html += f"<li>{item.strip()}</li>\n"
        content_html += "</ul>\n"
    
    return header + content_html

def tailor_resume_with_llm(resume_path: str, job_data: Dict, api_key: str, provider: str = "openai", api_url: str = None) -> Tuple[str, str, Union[ClaudeClient, OpenAIClient]]:
    """
    Tailor resume with LLM (Claude or OpenAI)
    
    Args:
        resume_path: Path to resume file
        job_data: Job data including requirements and skills
        api_key: API key for the LLM provider
        provider: LLM provider (claude or openai)
        api_url: Optional API URL for Claude
        
    Returns:
        Tuple of (output_filename, output_path, llm_client)
    """
    global last_llm_client
    
    logger.info(f"Tailoring resume with {provider} LLM")
    
    # Extract resume sections
    resume_sections = extract_resume_sections(resume_path)
    
    # Initialize the appropriate LLM client
    llm_client = None
    if provider.lower() == "claude":
        llm_client = ClaudeClient(api_key, api_url)
    elif provider.lower() == "openai":
        llm_client = OpenAIClient(api_key)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
    # Tailor each section
    for section_name, content in resume_sections.items():
        if content.strip() and section_name in ["summary", "experience", "education", "skills", "projects"]:
            logger.info(f"Tailoring {section_name} section")
            tailored_content = llm_client.tailor_resume_content(section_name, content, job_data)
            resume_sections[section_name] = tailored_content
    
    # Generate output filename
    resume_filename = os.path.basename(resume_path)
    base_name = os.path.splitext(resume_filename)[0]
    output_filename = f"{base_name}_tailored_{provider}.pdf"
    output_dir = os.path.dirname(resume_path)
    output_path = os.path.join(output_dir, output_filename)
    
    # Store LLM client for preview generation
    last_llm_client = llm_client
    
    # Return info without generating YC-style PDF
    return output_filename, output_path, llm_client

def generate_resume_preview(resume_path: str) -> str:
    """
    Generate HTML preview from resume
    
    Args:
        resume_path: Path to resume file
        
    Returns:
        HTML preview
    """
    logger.info(f"Generating resume preview for {resume_path}")
    
    # Check if we have direct LLM responses from last tailoring
    global last_llm_client
    if last_llm_client:
        logger.info("Using direct LLM responses for preview generation")
        preview_html = generate_preview_from_llm_responses(last_llm_client)
        if preview_html:
            return preview_html
    
    # Otherwise extract sections from file
    resume_sections = extract_resume_sections(resume_path)
    
    # Generate preview HTML
    preview_html = ""
    for section_name, content in resume_sections.items():
        if content.strip():
            formatted_content = format_section_content(content)
            preview_html += f'<div class="resume-section"><h2>{section_name.title()}</h2>{formatted_content}</div>'
    
    return preview_html
