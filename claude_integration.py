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
                "You are an expert resume writer specializing in crafting powerful, achievement-focused bullet points "
                "while preserving the original structure of resume sections. "
                "Your task is to rewrite ONLY the bullet points while maintaining all structural elements like "
                "company names, job titles, dates, education institutions, degrees, and section headings. "
                "Transform each bullet point into a concise statement that follows: "
                "[Action verb] + [What you did] + [How you did it] + [The result or measurable impact]. "
                "Each bullet point MUST be 85-100 characters to ensure it fits on a single line. "
                "Focus on bullet points that are most relevant to the target position.\n\n"
                "CRITICAL: Your response MUST contain ONLY the tailored resume content. "
                "DO NOT include any job requirements, job descriptions, expected skills, or any other "
                "information from the job posting in your response. NEVER include job analysis text or candidate profiles in your output. "
                "Your output should look exactly like a resume section with no trace of the job requirements or analysis used to tailor it. "
                "Output ONLY the tailored resume content with no meta-text, explanations, or job information.\n\n"
                "IMPORTANT FOR SUMMARY SECTION: If you are tailoring the summary section, format it as a SINGLE COHESIVE PARAGRAPH (3-4 sentences total), not as bullet points. "
                "If the original summary contains bullet points, convert them into flowing sentences in paragraph form."
            )
            
            # Format requirements and skills as bullet points for clearer prompting
            requirements_text = "\n".join([f"• {req}" for req in job_data.get('requirements', [])])
            skills_text = "\n".join([f"• {skill}" for skill in job_data.get('skills', [])])
            
            # Include AI analysis if available
            ai_analysis_text = ""
            if 'analysis' in job_data and isinstance(job_data['analysis'], dict):
                analysis = job_data['analysis']
                
                # Add candidate profile if available
                if 'candidate_profile' in analysis and analysis['candidate_profile']:
                    ai_analysis_text += f"\n## Candidate Profile\n{analysis['candidate_profile']}\n"
                
                # Add hard skills if available
                if 'hard_skills' in analysis and analysis['hard_skills']:
                    hard_skills = "\n".join([f"• {skill}" for skill in analysis['hard_skills']])
                    ai_analysis_text += f"\n## Required Hard Skills\n{hard_skills}\n"
                    
                # Add soft skills if available
                if 'soft_skills' in analysis and analysis['soft_skills']:
                    soft_skills = "\n".join([f"• {skill}" for skill in analysis['soft_skills']])
                    ai_analysis_text += f"\n## Required Soft Skills\n{soft_skills}\n"
                
                # Add ideal candidate description if available
                if 'ideal_candidate' in analysis and analysis['ideal_candidate']:
                    ai_analysis_text += f"\n## Ideal Candidate\n{analysis['ideal_candidate']}\n"
            
            # Create the user prompt
            user_prompt = f"""
            # Job Requirements (REFERENCE ONLY - DO NOT INCLUDE IN YOUR RESPONSE)
            {requirements_text}

            # Desired Skills (REFERENCE ONLY - DO NOT INCLUDE IN YOUR RESPONSE)
            {skills_text}
            
            {ai_analysis_text}

            # Current Resume Section: {section_name}
            {content}

            # Strong Action Verbs for Impact
            Achievement: Achieved, Attained, Completed, Established, Exceeded, Improved, Pioneered, Reduced, Resolved, Succeeded
            Leadership: Administered, Coordinated, Delegated, Directed, Executed, Led, Managed, Orchestrated, Oversaw, Supervised
            Communication: Authored, Collaborated, Consulted, Influenced, Negotiated, Persuaded, Presented, Promoted, Represented
            Analysis: Analyzed, Assessed, Calculated, Evaluated, Examined, Identified, Investigated, Researched, Studied, Tested
            Development: Architected, Created, Designed, Developed, Engineered, Formulated, Implemented, Integrated, Programmed
            Efficiency: Accelerated, Automated, Enhanced, Leveraged, Maximized, Optimized, Streamlined, Transformed, Upgraded

            # Example Bullet Points (properly formatted)
            • Managed cross-functional team of 8 engineers by implementing agile methods, reducing delivery time by 30%
            • Developed scalable API architecture using microservices pattern, increasing system throughput by 45%
            • Analyzed customer feedback data through sentiment analysis, identifying 5 key improvement areas

            # IMPORTANT STRUCTURAL INSTRUCTIONS:
            1. PRESERVE ALL structural elements of the original content - company names, job titles, dates, education details
            2. DO NOT alter any headers, company names, job titles, dates, or educational institution names
            3. ONLY rewrite the bullet points for experience/project descriptions
            4. Keep the document structure IDENTICAL to the original - maintain all sections, headings, and hierarchy
            5. For lines that already follow the format [Company/Title] and [Date Range], preserve them exactly as is
            6. If a line isn't a bullet point, preserve it exactly as written

            ## Section-Specific Structure Guidelines:
            
            ### For EXPERIENCE sections:
            - First line is typically the company name or role - PRESERVE EXACTLY
            - Second line often has dates and location - PRESERVE EXACTLY
            - Only enhance the bullet points that describe responsibilities and achievements
            - Example:
              Senior Data Scientist, ABC Company
              January 2018 - Present, San Francisco, CA
              • [REWRITE THIS BULLET WITH ACTION VERB + IMPACT]
              • [REWRITE THIS BULLET WITH ACTION VERB + IMPACT]
            
            ### For EDUCATION sections:
            - School name, degree, graduation date should remain UNCHANGED
            - Only enhance descriptions of academic achievements or relevant coursework
            - Example:
              Stanford University
              BS in Computer Science, May 2017
              • [REWRITE ONLY IF THIS IS A BULLET DESCRIBING ACADEMIC ACHIEVEMENT]
            
            ### For SKILLS sections:
            - You may reorganize skills to prioritize those matching job requirements
            - Keep all original skills but put most relevant ones first
            - Use original wording for technical skills, tools, and programming languages
            
            ### For SUMMARY sections:
            - Maintain paragraph structure but enhance language
            - Keep same length but make more impactful and relevant to this position
            
            # IMPORTANT WARNING
            # DO NOT include any of the job requirements or desired skills in your output.
            # Your output MUST contain ONLY resume content, not job listings or requirements.
            # NEVER return job requirements text in your response.
            
            Rewrite ONLY the bullet points in the "{section_name}" section following these requirements:
            1. Follow this EXACT structure for each bullet point: [Action verb] + [What you did] + [How you did it] + [The result/impact]
            2. Ensure each bullet point is 85-100 characters ONLY - this is critical for single-line display
            3. Focus ONLY on factual information from the original resume - do not invent achievements
            4. Prioritize experiences and skills that are MOST RELEVANT to the target position requirements
            5. Use strong action verbs from the list above that reflect the level of responsibility
            6. Quantify results and impact whenever possible with specific metrics and percentages
            
            Format your response with the exact same structure as the input, maintaining all headings, company names, 
            titles and dates exactly as they appear in the original, only replacing the bullet points with enhanced ones.
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
                "You are an expert resume writer specializing in crafting powerful, achievement-focused bullet points "
                "while preserving the original structure of resume sections. "
                "Your task is to rewrite ONLY the bullet points while maintaining all structural elements like "
                "company names, job titles, dates, education institutions, degrees, and section headings. "
                "Transform each bullet point into a concise statement that follows: "
                "[Action verb] + [What you did] + [How you did it] + [The result or measurable impact]. "
                "Each bullet point MUST be 85-100 characters to ensure it fits on a single line. "
                "Focus on bullet points that are most relevant to the target position.\n\n"
                "CRITICAL: Your response MUST contain ONLY the tailored resume content. "
                "DO NOT include any job requirements, job descriptions, expected skills, or any other "
                "information from the job posting in your response. NEVER include job analysis text or candidate profiles in your output. "
                "Your output should look exactly like a resume section with no trace of the job requirements or analysis used to tailor it. "
                "Output ONLY the tailored resume content with no meta-text, explanations, or job information.\n\n"
                "IMPORTANT FOR SUMMARY SECTION: If you are tailoring the summary section, format it as a SINGLE COHESIVE PARAGRAPH (3-4 sentences total), not as bullet points. "
                "If the original summary contains bullet points, convert them into flowing sentences in paragraph form."
            )
            
            # Format requirements and skills as bullet points for clearer prompting
            requirements_text = "\n".join([f"• {req}" for req in job_data.get('requirements', [])])
            skills_text = "\n".join([f"• {skill}" for skill in job_data.get('skills', [])])
            
            # Include AI analysis if available
            ai_analysis_text = ""
            if 'analysis' in job_data and isinstance(job_data['analysis'], dict):
                analysis = job_data['analysis']
                
                # Add candidate profile if available
                if 'candidate_profile' in analysis and analysis['candidate_profile']:
                    ai_analysis_text += f"\n## Candidate Profile\n{analysis['candidate_profile']}\n"
                
                # Add hard skills if available
                if 'hard_skills' in analysis and analysis['hard_skills']:
                    hard_skills = "\n".join([f"• {skill}" for skill in analysis['hard_skills']])
                    ai_analysis_text += f"\n## Required Hard Skills\n{hard_skills}\n"
                    
                # Add soft skills if available
                if 'soft_skills' in analysis and analysis['soft_skills']:
                    soft_skills = "\n".join([f"• {skill}" for skill in analysis['soft_skills']])
                    ai_analysis_text += f"\n## Required Soft Skills\n{soft_skills}\n"
                
                # Add ideal candidate description if available
                if 'ideal_candidate' in analysis and analysis['ideal_candidate']:
                    ai_analysis_text += f"\n## Ideal Candidate\n{analysis['ideal_candidate']}\n"
            
            # Create the user prompt
            user_prompt = f"""
            # Job Requirements (REFERENCE ONLY - DO NOT INCLUDE IN YOUR RESPONSE)
            {requirements_text}

            # Desired Skills (REFERENCE ONLY - DO NOT INCLUDE IN YOUR RESPONSE)
            {skills_text}
            
            {ai_analysis_text}

            # Current Resume Section: {section_name}
            {content}

            # Strong Action Verbs for Impact
            Achievement: Achieved, Attained, Completed, Established, Exceeded, Improved, Pioneered, Reduced, Resolved, Succeeded
            Leadership: Administered, Coordinated, Delegated, Directed, Executed, Led, Managed, Orchestrated, Oversaw, Supervised
            Communication: Authored, Collaborated, Consulted, Influenced, Negotiated, Persuaded, Presented, Promoted, Represented
            Analysis: Analyzed, Assessed, Calculated, Evaluated, Examined, Identified, Investigated, Researched, Studied, Tested
            Development: Architected, Created, Designed, Developed, Engineered, Formulated, Implemented, Integrated, Programmed
            Efficiency: Accelerated, Automated, Enhanced, Leveraged, Maximized, Optimized, Streamlined, Transformed, Upgraded

            # Example Bullet Points (properly formatted)
            • Managed cross-functional team of 8 engineers by implementing agile methods, reducing delivery time by 30%
            • Developed scalable API architecture using microservices pattern, increasing system throughput by 45%
            • Analyzed customer feedback data through sentiment analysis, identifying 5 key improvement areas

            # IMPORTANT STRUCTURAL INSTRUCTIONS:
            1. PRESERVE ALL structural elements of the original content - company names, job titles, dates, education details
            2. DO NOT alter any headers, company names, job titles, dates, or educational institution names
            3. ONLY rewrite the bullet points for experience/project descriptions
            4. Keep the document structure IDENTICAL to the original - maintain all sections, headings, and hierarchy
            5. For lines that already follow the format [Company/Title] and [Date Range], preserve them exactly as is
            6. If a line isn't a bullet point, preserve it exactly as written

            ## Section-Specific Structure Guidelines:
            
            ### For EXPERIENCE sections:
            - First line is typically the company name or role - PRESERVE EXACTLY
            - Second line often has dates and location - PRESERVE EXACTLY
            - Only enhance the bullet points that describe responsibilities and achievements
            - Example:
              Senior Data Scientist, ABC Company
              January 2018 - Present, San Francisco, CA
              • [REWRITE THIS BULLET WITH ACTION VERB + IMPACT]
              • [REWRITE THIS BULLET WITH ACTION VERB + IMPACT]
            
            ### For EDUCATION sections:
            - School name, degree, graduation date should remain UNCHANGED
            - Only enhance descriptions of academic achievements or relevant coursework
            - Example:
              Stanford University
              BS in Computer Science, May 2017
              • [REWRITE ONLY IF THIS IS A BULLET DESCRIBING ACADEMIC ACHIEVEMENT]
            
            ### For SKILLS sections:
            - You may reorganize skills to prioritize those matching job requirements
            - Keep all original skills but put most relevant ones first
            - Use original wording for technical skills, tools, and programming languages
            
            ### For SUMMARY sections:
            - Maintain paragraph structure but enhance language
            - Keep same length but make more impactful and relevant to this position
            
            # IMPORTANT WARNING
            # DO NOT include any of the job requirements or desired skills in your output.
            # Your output MUST contain ONLY resume content, not job listings or requirements.
            # NEVER return job requirements text in your response.
            
            Rewrite ONLY the bullet points in the "{section_name}" section following these requirements:
            1. Follow this EXACT structure for each bullet point: [Action verb] + [What you did] + [How you did it] + [The result/impact]
            2. Ensure each bullet point is 85-100 characters ONLY - this is critical for single-line display
            3. Focus ONLY on factual information from the original resume - do not invent achievements
            4. Prioritize experiences and skills that are MOST RELEVANT to the target position requirements
            5. Use strong action verbs from the list above that reflect the level of responsibility
            6. Quantify results and impact whenever possible with specific metrics and percentages
            
            Format your response with the exact same structure as the input, maintaining all headings, company names, 
            titles and dates exactly as they appear in the original, only replacing the bullet points with enhanced ones.
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
                    formatted_lines.append("<ul class='dot-bullets'>")
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
    
    # Contact information at the top (usually not tailored)
    if "contact" in llm_client.tailored_content:
        contact_lines = llm_client.tailored_content["contact"].strip().split('\n')
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
        html_parts.append(f'<div class="resume-section"><h2>Professional Summary</h2><div class="summary-content">{summary_html}</div></div>')
    
    # Experience section with improved formatting
    if "experience" in llm_client.tailored_content:
        experience_content = llm_client.tailored_content["experience"]
        formatted_experience = format_experience_content(experience_content)
        html_parts.append(f'<div class="resume-section"><h2>Work Experience</h2>{formatted_experience}</div>')
    
    # Education section with improved formatting
    if "education" in llm_client.tailored_content:
        education_content = llm_client.tailored_content["education"]
        formatted_education = format_education_content(education_content)
        html_parts.append(f'<div class="resume-section"><h2>Education</h2>{formatted_education}</div>')
    
    # Skills section
    if "skills" in llm_client.tailored_content:
        skills_html = format_section_content(llm_client.tailored_content["skills"])
        html_parts.append(f'<div class="resume-section"><h2>Skills</h2>{skills_html}</div>')
    
    # Projects section with improved formatting
    if "projects" in llm_client.tailored_content:
        projects_content = llm_client.tailored_content["projects"]
        formatted_projects = format_projects_content(projects_content)
        html_parts.append(f'<div class="resume-section"><h2>Projects</h2>{formatted_projects}</div>')
    
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
    
    print(f"DEBUG: generate_resume_preview called for doc_path: {doc_path}")
    
    # Try to generate preview from direct LLM responses if available
    if last_llm_client:
        preview_html = generate_preview_from_llm_responses(last_llm_client)
        if preview_html:
            logger.info("Using direct LLM responses for preview")
            return preview_html
    
    logger.info("No direct LLM responses available, generating preview from DOCX file")
    print(f"DEBUG: Will now process DOCX file for preview: {doc_path}")
    
    try:
        # Extract plain text from the document
        text = docx2txt.process(doc_path)
        
        # Parse the document object
        doc = Document(doc_path)
        
        html_parts = []
        current_section = None
        section_content = []
        is_contact_section = False
        
        for para in doc.paragraphs:
            text = para.text.strip()
            
            # Skip empty paragraphs
            if not text:
                continue
            
            # Check if this is a heading (section title)
            if para.style.name.startswith('Heading') or any(p.bold for p in para.runs) or para.style.name == 'SectionHeader':
                # Add previous section to HTML
                if current_section and section_content:
                    section_html = "\n".join(section_content)
                    if is_contact_section:
                        html_parts.append(f'<div class="resume-section"><h2>{current_section}</h2>{section_html}<hr class="contact-divider"/></div>')
                        is_contact_section = False
                    else:
                        html_parts.append(f'<div class="resume-section"><h2>{current_section}</h2>{section_html}</div>')
                    section_content = []
                
                # Set new section
                current_section = text
                # Check if this is the contact section
                if current_section.lower().find("contact") >= 0 or len(html_parts) == 0:
                    is_contact_section = True
                
            else:
                # Process content based on if it's a bullet point
                if text.startswith('•') or text.startswith('-') or text.startswith('*') or text.startswith('▸'):
                    if not section_content or not section_content[-1].startswith('<ul'):
                        section_content.append('<ul class="dot-bullets">')
                    
                    # Remove the bullet point character and format as list item
                    item_text = re.sub(r'^[•\-*▸]\s*', '', text).strip()
                    section_content.append(f'<li>{item_text}</li>')
                    
                    # Check if we need to close the list
                    next_is_bullet = False
                    for next_para in doc.paragraphs:
                        if next_para.text.strip() and (next_para.text.strip().startswith('•') or 
                                                      next_para.text.strip().startswith('-') or 
                                                      next_para.text.strip().startswith('*') or
                                                      next_para.text.strip().startswith('▸')):
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
            if is_contact_section:
                html_parts.append(f'<div class="resume-section"><h2>{current_section}</h2>{section_html}<hr class="contact-divider"/></div>')
            else:
                html_parts.append(f'<div class="resume-section"><h2>{current_section}</h2>{section_html}</div>')
        
        # Combine all HTML parts
        preview_html = "\n".join(html_parts)
        
        logger.info(f"Generated tailored resume preview HTML from DOCX: {len(preview_html)} characters")
        
        return preview_html
    
    except Exception as e:
        logger.error(f"Error generating resume preview: {str(e)}")
        return f"<p>Error generating preview: {str(e)}</p>"

def tailor_resume_sections(resume_sections, job_data, api_key, provider='claude', api_url=None):
    """
    Tailor each section of the resume based on job requirements.
    Uses the specified LLM provider (claude or openai).
    
    Args:
        resume_sections (dict): Dictionary of resume sections
        job_data (dict): Job data including requirements and skills
        api_key (str): API key for the LLM service
        provider (str): LLM provider to use ('claude' or 'openai')
        api_url (str, optional): API URL for Claude API
        
    Returns:
        dict: Dictionary containing tailored resume sections
    """
    logger.info(f"Tailoring resume sections using {provider}")
    
    if not api_key:
        logger.error("No API key provided for tailoring resume")
        raise ValueError(f"Missing API key for {provider}")
    
    # Create the client for the chosen provider
    if provider.lower() == 'claude':
        client = ClaudeClient(api_key, api_url)
        logger.info("Created Claude client for tailoring")
    elif provider.lower() == 'openai':
        client = OpenAIClient(api_key)
        logger.info("Created OpenAI client for tailoring")
    else:
        logger.error(f"Unsupported provider: {provider}")
        raise ValueError(f"Unsupported provider: {provider}")
    
    # Extract job requirements
    requirements = job_data.get('requirements', [])
    skills = job_data.get('skills', [])
    
    # Get AI analysis data if available
    analysis_data = job_data.get('analysis', {})
    candidate_profile = analysis_data.get('candidate_profile', '')
    hard_skills = analysis_data.get('hard_skills', [])
    soft_skills = analysis_data.get('soft_skills', [])
    ideal_candidate = analysis_data.get('ideal_candidate', '')
    
    # Convert lists to string for easier handling in prompts
    requirements_text = "\n".join([f"• {req}" for req in requirements]) if requirements else "No specific requirements provided."
    skills_text = "\n".join([f"• {skill}" for skill in skills]) if skills else "No specific skills provided."
    
    # Format AI analysis data for prompt inclusion
    has_analysis = bool(candidate_profile or hard_skills or soft_skills or ideal_candidate)
    
    analysis_prompt = ""
    if has_analysis:
        analysis_prompt += "\n\n=== AI ANALYSIS OF THE JOB POSTING ===\n\n"
        
        if candidate_profile:
            analysis_prompt += f"CANDIDATE PROFILE:\n{candidate_profile}\n\n"
            
        if hard_skills:
            hard_skills_text = "\n".join([f"• {skill}" for skill in hard_skills])
            analysis_prompt += f"HARD SKILLS REQUIRED:\n{hard_skills_text}\n\n"
            
        if soft_skills:
            soft_skills_text = "\n".join([f"• {skill}" for skill in soft_skills])
            analysis_prompt += f"SOFT SKILLS REQUIRED:\n{soft_skills_text}\n\n"
            
        if ideal_candidate:
            analysis_prompt += f"IDEAL CANDIDATE DESCRIPTION:\n{ideal_candidate}\n\n"
    
    # Log analysis data usage
    if has_analysis:
        logger.info("Including AI analysis data in tailoring prompts")
    else:
        logger.info("No AI analysis data available for tailoring")
    
    # Tailor each section
    tailored_sections = {}
    
    # Define the sections to tailor
    sections_to_tailor = ['summary', 'experience', 'education', 'skills', 'projects', 'additional']
    
    # Copy sections that should not be modified
    for section, content in resume_sections.items():
        if section not in sections_to_tailor:
            tailored_sections[section] = content
            logger.info(f"Copied section '{section}' without modification")
    
    # Tailor the resume summary
    if 'summary' in resume_sections and resume_sections['summary']:
        summary_prompt = f"""
You are an expert resume tailoring assistant. Your task is to write a compelling professional summary that positions the candidate as an ideal match for the target job.

ORIGINAL RESUME SUMMARY:
{resume_sections['summary']}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Please write a powerful professional summary following this specific 3-4 sentence paragraph structure (NOT bullet points):

1. Recognition and Impact: Start with key achievements or recognitions that set the candidate apart in their field. Mention promotions, awards, or significant results they've driven.

2. Personal Attributes: Highlight qualities, skills, and strengths that make them effective, focusing on those most relevant to this job posting. Include adaptability, leadership, creativity, analytical ability, or collaboration skills that align with the job requirements.

3. Future Goals: End with a statement of career direction that shows how the candidate wants to make an impact in this specific role and how they want to grow.

IMPORTANT: Format your response as a SINGLE COHESIVE PARAGRAPH (3-4 sentences total), not as bullet points. If the original summary contains bullet points, convert them into flowing sentences that fit the 3-part structure above.

The tone should be confident, clear, and forward-looking. Ensure each sentence is impactful and directly relevant to the target position.

Example of expected format:
"[Field] professional with [X years] of experience [specific achievement that increased metrics by X%]. Known for [2-3 key attributes most relevant to job]. Looking to apply this expertise in [specific type of environment] focused on [key aspects of the target role]."

Make bold improvements that will help the candidate stand out for this specific position. Focus on emphasizing experience and skills that directly match the job requirements while maintaining authenticity.
"""
        try:
            tailored_summary = client.tailor_resume_content(summary_prompt, "summary")
            tailored_sections['summary'] = tailored_summary
            logger.info(f"Tailored 'summary' section - Original: {len(resume_sections['summary'])} chars, Tailored: {len(tailored_summary)} chars")
        except Exception as e:
            logger.error(f"Error tailoring summary: {str(e)}")
            tailored_sections['summary'] = resume_sections['summary']
    else:
        tailored_sections['summary'] = resume_sections.get('summary', '')
        logger.info("No 'summary' section to tailor or section is empty")
    
    # Tailor the experience section
    if 'experience' in resume_sections and resume_sections['experience']:
        experience_prompt = f"""
You are an expert resume tailoring assistant. Your task is to tailor the professional experience section to make it more appealing for a specific job.

ORIGINAL EXPERIENCE SECTION:
{resume_sections['experience']}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Please rewrite the experience section to better match the job requirements. Make significant improvements that highlight relevant experience and skills.
Don't just make minor word changes - make bold improvements by:
1. Enhancing bullet points to emphasize achievements relevant to this job
2. Adding quantifiable metrics where possible (estimates are acceptable if they sound realistic)
3. Using strong action verbs and industry terminology from the job description
4. Prioritizing experiences that match the job requirements
5. Highlighting transferable skills for any experience that isn't directly related

Keep approximately the same number of bullet points, but make them more impactful and targeted to this specific position.
Maintain the same job titles, companies, and dates - only modify the descriptions and bullet points.
"""
        try:
            tailored_experience = client.tailor_resume_content(experience_prompt, "experience")
            tailored_sections['experience'] = tailored_experience
            logger.info(f"Tailored 'experience' section - Original: {len(resume_sections['experience'])} chars, Tailored: {len(tailored_experience)} chars")
        except Exception as e:
            logger.error(f"Error tailoring experience: {str(e)}")
            tailored_sections['experience'] = resume_sections['experience']
    else:
        tailored_sections['experience'] = resume_sections.get('experience', '')
        logger.info("No 'experience' section to tailor or section is empty")
    
    # Tailor the education section
    if 'education' in resume_sections and resume_sections['education']:
        education_prompt = f"""
You are an expert resume tailoring assistant. Your task is to tailor the education section to make it more appealing for a specific job.

ORIGINAL EDUCATION SECTION:
{resume_sections['education']}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Please rewrite the education section to better match the job requirements. Focus on:
1. Highlighting relevant coursework, projects, or achievements that match the job requirements
2. Emphasizing academic accomplishments that demonstrate skills needed for this position
3. Formatting in a way that emphasizes the most relevant educational experiences
4. Including any certifications or training that matches required skills

Keep the degree names, institutions, and dates exactly the same - only enhance descriptions to make them more relevant.
Be concise and impactful, focusing on qualifications that match the job requirements.
"""
        try:
            tailored_education = client.tailor_resume_content(education_prompt, "education")
            tailored_sections['education'] = tailored_education
            logger.info(f"Tailored 'education' section - Original: {len(resume_sections['education'])} chars, Tailored: {len(tailored_education)} chars")
        except Exception as e:
            logger.error(f"Error tailoring education: {str(e)}")
            tailored_sections['education'] = resume_sections['education']
    else:
        tailored_sections['education'] = resume_sections.get('education', '')
        logger.info("No 'education' section to tailor or section is empty")
    
    # Tailor the skills section
    if 'skills' in resume_sections and resume_sections['skills']:
        skills_prompt = f"""
You are an expert resume tailoring assistant. Your task is to tailor the skills section to make it more appealing for a specific job.

ORIGINAL SKILLS SECTION:
{resume_sections['skills']}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Please rewrite the skills section to better match the job requirements. Focus on:
1. Reordering skills to prioritize those mentioned in the job description
2. Adding any missing skills that the candidate likely has based on their experience (must be reasonable to infer from other sections)
3. Grouping skills into relevant categories that align with the job posting
4. Rephrasing skills using the exact terminology from the job description
5. Removing skills that are irrelevant to this position if the list is very long

Only include skills that are authentic to the candidate based on their resume.
Format the skills section clearly and concisely for easy scanning.
"""
        try:
            tailored_skills = client.tailor_resume_content(skills_prompt, "skills")
            tailored_sections['skills'] = tailored_skills
            logger.info(f"Tailored 'skills' section - Original: {len(resume_sections['skills'])} chars, Tailored: {len(tailored_skills)} chars")
        except Exception as e:
            logger.error(f"Error tailoring skills: {str(e)}")
            tailored_sections['skills'] = resume_sections['skills']
    else:
        tailored_sections['skills'] = resume_sections.get('skills', '')
        logger.info("No 'skills' section to tailor or section is empty")
    
    # Tailor the projects section if it exists
    if 'projects' in resume_sections and resume_sections['projects']:
        projects_prompt = f"""
You are an expert resume tailoring assistant. Your task is to tailor the projects section to make it more appealing for a specific job.

ORIGINAL PROJECTS SECTION:
{resume_sections['projects']}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Please rewrite the projects section to better match the job requirements. Focus on:
1. Highlighting projects that demonstrate skills required for this job
2. Emphasizing tools, technologies, and methodologies that match the job description
3. Quantifying project outcomes and impacts where possible
4. Rephrasing project descriptions to use terminology from the job posting
5. Focusing on the candidate's specific contributions and leadership roles

Keep the project titles and timelines the same, but enhance descriptions to better align with the job requirements.
Be concise and impactful, prioritizing projects most relevant to this position.
"""
        try:
            tailored_projects = client.tailor_resume_content(projects_prompt, "projects")
            tailored_sections['projects'] = tailored_projects
            logger.info(f"Tailored 'projects' section - Original: {len(resume_sections['projects'])} chars, Tailored: {len(tailored_projects)} chars")
        except Exception as e:
            logger.error(f"Error tailoring projects: {str(e)}")
            tailored_sections['projects'] = resume_sections['projects']
    else:
        tailored_sections['projects'] = resume_sections.get('projects', '')
        logger.info("No 'projects' section to tailor or section is empty")
    
    # Tailor additional information if it exists
    if 'additional' in resume_sections and resume_sections['additional']:
        additional_prompt = f"""
You are an expert resume tailoring assistant. Your task is to tailor the additional information section to make it more appealing for a specific job.

ORIGINAL ADDITIONAL INFORMATION:
{resume_sections['additional']}

JOB REQUIREMENTS:
{requirements_text}

REQUIRED SKILLS:
{skills_text}{analysis_prompt}

Please rewrite the additional information to better match the job requirements. Focus on:
1. Highlighting relevant certifications, awards, or accomplishments
2. Including language skills, volunteer work, or other information that relates to the job
3. Emphasizing professional memberships or activities relevant to this position
4. Keeping only the most relevant points that add value to your application

Be concise and selective, only including information that strengthens the application for this specific position.
"""
        try:
            tailored_additional = client.tailor_resume_content(additional_prompt, "additional")
            tailored_sections['additional'] = tailored_additional
            logger.info(f"Tailored 'additional' section - Original: {len(resume_sections['additional'])} chars, Tailored: {len(tailored_additional)} chars")
        except Exception as e:
            logger.error(f"Error tailoring additional information: {str(e)}")
            tailored_sections['additional'] = resume_sections['additional']
    else:
        tailored_sections['additional'] = resume_sections.get('additional', '')
        logger.info("No 'additional' section to tailor or section is empty")
    
    return tailored_sections

def tailor_resume_with_llm(resume_path: str, job_data: Dict, api_key: str, provider: str = 'openai', api_url: str = None) -> Tuple[Dict, Union[ClaudeClient, OpenAIClient]]:
    """
    Tailor a resume using an LLM API (Claude or OpenAI)
    
    The tailoring process preserves the original structure of the resume including:
    - Company names, job titles, and date ranges
    - Education institutions and degrees
    - Section headings and hierarchical structure
    
    Only the descriptive bullet points are enhanced to be more targeted for the specific job.
    Each bullet point is rewritten to follow the format:
    [Action verb] + [What you did] + [How you did it] + [The result/impact]
    
    Args:
        resume_path: Path to the resume file
        job_data: Job data including requirements and skills
        api_key: API key for the LLM provider
        provider: LLM provider ('claude' or 'openai')
        api_url: API URL for Claude
        
    Returns:
        Tuple with tailored sections dictionary and LLM client instance
    """
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
        
        # Dictionary to store tailored sections
        tailored_sections = {}
        
        # Add contact information (not tailored)
        tailored_sections['contact'] = resume_sections.get('contact', '')
        
        # Tailor the professional summary
        if resume_sections.get('summary'):
            tailored_sections['summary'] = llm_client.tailor_resume_content(
                'summary', 
                resume_sections.get('summary', ''),
                job_data
            )
        
        # Tailor the work experience
        if resume_sections.get('experience'):
            tailored_sections['experience'] = llm_client.tailor_resume_content(
                'experience', 
                resume_sections.get('experience', ''),
                job_data
            )
        
        # Tailor education section
        if resume_sections.get('education'):
            tailored_sections['education'] = llm_client.tailor_resume_content(
                'education',
                resume_sections.get('education', ''),
                job_data
            )
        
        # Tailor the skills section
        if resume_sections.get('skills'):
            tailored_sections['skills'] = llm_client.tailor_resume_content(
                'skills', 
                resume_sections.get('skills', ''),
                job_data
            )
        
        # Tailor projects section
        if resume_sections.get('projects'):
            tailored_sections['projects'] = llm_client.tailor_resume_content(
                'projects',
                resume_sections.get('projects', ''),
                job_data
            )
        
        # Tailor additional information
        if resume_sections.get('additional'):
            tailored_sections['additional'] = llm_client.tailor_resume_content(
                'additional',
                resume_sections.get('additional', ''),
                job_data
            )
        
        logger.info(f"Resume tailoring completed successfully with {provider.upper()}")
        
        # Return tailored sections and LLM client
        return tailored_sections, llm_client
    
    except Exception as e:
        logger.error(f"Error tailoring resume with {provider.upper()}: {str(e)}")
        logger.error(traceback.format_exc())
        raise Exception(f"Error tailoring resume with {provider.upper()}: {str(e)}")

def generate_tailored_document(resume_path, tailored_sections):
    """Generate a tailored resume document using YC/Eddie style

    Args:
        resume_path (str): Path to the original resume
        tailored_sections (dict): Dictionary containing tailored resume sections

    Returns:
        str: Path to the new tailored resume
    """
    try:
        logger.info(f"Generating tailored document from {resume_path}")
        
        # Create output path for tailored resume
        filename = os.path.basename(resume_path)
        base_name, ext = os.path.splitext(filename)
        
        # Use modern style for the output
        output_path = os.path.join(os.path.dirname(resume_path), f"{base_name}_tailored_modern.docx")
        
        # Import the resume styler module
        from resume_styler import create_resume_document
        
        # Generate tailored resume with modern style
        output_path = create_resume_document(
            contact=tailored_sections.get('contact', ''),
            summary=tailored_sections.get('summary', ''),
            experience=tailored_sections.get('experience', ''),
            education=tailored_sections.get('education', ''),
            skills=tailored_sections.get('skills', ''),
            projects=tailored_sections.get('projects', ''),
            additional=tailored_sections.get('additional', ''),
            output_path=output_path
        )
        
        logger.info(f"Successfully generated tailored document at {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating tailored document: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def format_job_entry(company, location, position, dates, bullets):
    """Format a job entry with proper company/location and position/date layout"""
    html = []
    
    # Split location into city and state if possible
    city = ""
    state = ""
    if location:
        # Look for common patterns like "City, State" or "City State"
        location_parts = re.split(r',\s*|\s+(?=[A-Z]{2}$)', location)
        if len(location_parts) > 1:
            city = location_parts[0].strip()
            state = location_parts[1].strip()
        else:
            # If no obvious split, keep everything as state
            state = location
    
    # Add company and location in a flex layout
    html.append('<div class="company-line">')
    html.append(f'<div class="company-name">{company}</div>')
    if city or state:
        location_text = f"{city + ' ' if city else ''}{state}"
        html.append(f'<div class="company-location">{location_text}</div>')
    html.append('</div>')
    
    # Add position and dates in a flex layout
    if position:
        html.append('<div class="position-line">')
        html.append(f'<div class="position-title">{position}</div>')
        if dates:
            html.append(f'<div class="position-date">{dates}</div>')
        html.append('</div>')
    
    # Add bullets if any
    if bullets:
        html.append('<ul class="dot-bullets">')
        for bullet in bullets:
            html.append(f'<li>{bullet}</li>')
        html.append('</ul>')
    
    return '\n'.join(html)

def format_education_entry(institution, location, degree, dates, bullets):
    """Format an education entry with proper institution/location and degree/date layout"""
    html = []
    
    # Split location into city and state if possible
    city = ""
    state = ""
    if location:
        # Look for common patterns like "City, State" or "City State"
        location_parts = re.split(r',\s*|\s+(?=[A-Z]{2}$)', location)
        if len(location_parts) > 1:
            city = location_parts[0].strip()
            state = location_parts[1].strip()
        else:
            # If no obvious split, keep everything as state
            state = location
    
    # Add institution and location in a flex layout
    html.append('<div class="company-line">')
    html.append(f'<div class="company-name">{institution}</div>')
    if city or state:
        location_text = f"{city + ' ' if city else ''}{state}"
        html.append(f'<div class="company-location">{location_text}</div>')
    html.append('</div>')
    
    # Add degree and dates in a flex layout
    if degree:
        html.append('<div class="position-line">')
        html.append(f'<div class="position-title">{degree}</div>')
        if dates:
            html.append(f'<div class="position-date">{dates}</div>')
        html.append('</div>')
    
    # Add bullets if any
    if bullets:
        html.append('<ul class="dot-bullets">')
        for bullet in bullets:
            html.append(f'<li>{bullet}</li>')
        html.append('</ul>')
    
    return '\n'.join(html)

def format_project_entry(project, dates, bullets):
    """Format a project entry with proper project/date layout"""
    html = []
    
    # Add project and dates in a flex layout
    html.append('<div class="company-line">')
    html.append(f'<div class="company-name">{project}</div>')
    if dates:
        html.append(f'<div class="company-location">{dates}</div>')
    html.append('</div>')
    
    # Add bullets if any
    if bullets:
        html.append('<ul class="dot-bullets">')
        for bullet in bullets:
            html.append(f'<li>{bullet}</li>')
        html.append('</ul>')
    
    return '\n'.join(html)

def format_experience_content(content: str) -> str:
    """Format experience content with company/location and position/date layout"""
    if not content:
        return ""
    
    # Filter job requirements as in format_section_content
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
    
    # Split into paragraphs for processing
    paragraphs = content.strip().split('\n\n')
    if not paragraphs:
        return ""
    
    formatted_parts = []
    current_company = None
    current_location = None
    current_position = None
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
                # Add bullet to current position
                bullet_content = re.sub(r'^[•\-\*]\s*', '', line).strip()
                bullets.append(bullet_content)
            elif i == 0 and (i == len(lines) - 1 or not any(l.startswith(('•', '-', '*')) for l in lines[1:])):
                # This is likely a standalone line (like a job title or company)
                # First, check for explicitly formatted company and location with separators
                if ',' in line or ' | ' in line or ' - ' in line:
                    # Output previous position if exists
                    if current_company is not None:
                        formatted_parts.append(format_job_entry(current_company, current_location, current_position, current_dates, bullets))
                        bullets = []
                    
                    # Try to split company and location
                    if ',' in line:
                        parts = line.split(',', 1)
                    elif ' | ' in line:
                        parts = line.split(' | ', 1)
                    else:
                        parts = line.split(' - ', 1)
                    
                    current_company = parts[0].strip()
                    current_location = parts[1].strip() if len(parts) > 1 else ""
                    current_position = None
                    current_dates = None
                else:
                    # Try to detect if the line has a company name followed by a city name
                    # Common pattern: "COMPANY NAME CITY STATE" or "COMPANY NAME CITY"
                    # Check for common US city names or try to infer based on spacing
                    city_pattern = r'(.*?)(\b(?:LOS ANGELES|NEW YORK|CHICAGO|HOUSTON|SAN FRANCISCO|BOSTON|SEATTLE|MIAMI|DENVER|ATLANTA|DALLAS|PHILADELPHIA|PORTLAND|SAN DIEGO|SAN JOSE|WASHINGTON|AUSTIN|NASHVILLE)\b)(.*?)?$'
                    city_match = re.search(city_pattern, line, re.IGNORECASE)
                    
                    if city_match:
                        # Output previous position if exists
                        if current_company is not None:
                            formatted_parts.append(format_job_entry(current_company, current_location, current_position, current_dates, bullets))
                            bullets = []
                        
                        # Extract company, city, and state
                        company = city_match.group(1).strip()
                        city = city_match.group(2).strip()
                        state = city_match.group(3).strip() if city_match.group(3) else ""
                        
                        # Set the current values
                        current_company = company
                        current_location = f"{city}{', ' + state if state else ''}"
                        current_position = None
                        current_dates = None
                    else:
                        # Just a company without location or might be a header
                        # Output previous position if exists
                        if current_company is not None:
                            formatted_parts.append(format_job_entry(current_company, current_location, current_position, current_dates, bullets))
                            bullets = []
                        
                        current_company = line
                        current_location = ""
                        current_position = None
                        current_dates = None
            elif current_company is not None and current_position is None:
                # This is likely the position and dates line
                # Try to identify if it has dates (often in parentheses or after a dash)
                date_match = re.search(r'\(([^)]+)\)|\s-\s([^-]+)$', line)
                if date_match:
                    date_part = date_match.group(1) or date_match.group(2)
                    position_part = line.replace(f"({date_part})", "").replace(f" - {date_part}", "").strip()
                    current_position = position_part
                    current_dates = date_part
                else:
                    # No clear date format, assume entire line is position
                    current_position = line
                    current_dates = ""
    
    # Add the last job entry
    if current_company is not None:
        formatted_parts.append(format_job_entry(current_company, current_location, current_position, current_dates, bullets))
    
    # If no structured entries were found, fall back to simple formatting
    if not formatted_parts and content.strip():
        return format_section_content(content)
    
    return "\n".join(formatted_parts)

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
