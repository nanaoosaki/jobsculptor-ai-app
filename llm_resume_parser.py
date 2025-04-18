import os
import json
import time
import uuid
import logging
import traceback
from typing import Dict, Tuple
import docx2txt

# Import PDF parser functions
from pdf_parser import read_pdf_file

# Initialize optional API clients
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Configure logging
logger = logging.getLogger(__name__)

class LLMResumeParser:
    """Use LLM to parse resume content into structured sections"""
    
    def __init__(self, llm_provider="claude"):
        """Initialize the resume parser with the specified LLM provider"""
        self.llm_provider = llm_provider
        self.anthropic_client = None
        self.openai_client = None
        
        # Initialize API clients based on available keys
        if llm_provider == "claude" or llm_provider == "auto":
            self._init_claude_client()
            
        if llm_provider == "openai" or llm_provider == "auto":
            self._init_openai_client()
    
    def _init_claude_client(self):
        """Initialize Claude API client"""
        claude_api_key = os.environ.get("CLAUDE_API_KEY")
        
        if claude_api_key and Anthropic:
            try:
                self.anthropic_client = Anthropic(api_key=claude_api_key)
                logger.info("Claude API client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Claude API client: {str(e)}")
        else:
            logger.warning("Claude API key not found or Anthropic package not installed")
    
    def _init_openai_client(self):
        """Initialize OpenAI API client"""
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        
        if openai_api_key and OpenAI:
            try:
                self.openai_client = OpenAI(api_key=openai_api_key)
                logger.info("OpenAI API client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI API client: {str(e)}")
        else:
            logger.warning("OpenAI API key not found or OpenAI package not installed")
            return None
    
    def parse_resume(self, doc_path: str) -> Tuple[Dict[str, str], Dict, bool]:
        """
        Parse a resume document using LLM and extract sections
        
        Args:
            doc_path: Path to the resume document
            
        Returns:
            Tuple containing:
            - Dictionary of sections (same format as original parser)
            - Metadata about the parsing process
            - Success flag (True if LLM parsing succeeded, False if fallback was used)
        """
        logger.info(f"Parsing resume with LLM: {doc_path}")
        
        try:
            # Extract text from resume based on file type
            file_ext = os.path.splitext(doc_path)[1].lower()
            
            if file_ext == '.docx':
                resume_text = docx2txt.process(doc_path)
            elif file_ext == '.pdf':
                # Extract text from PDF using pdfminer through our parser module
                pdf_content = read_pdf_file(doc_path)
                
                # Combine paragraphs into a single text
                resume_text = ""
                for para in pdf_content.get('paragraphs', []):
                    resume_text += para.get('text', '') + "\n\n"
            else:
                logger.error(f"Unsupported file format: {file_ext}")
                return {}, {}, False
            
            # Skip LLM parsing if text is too short
            if len(resume_text.strip()) < 50:
                logger.warning(f"Resume text too short ({len(resume_text)} chars). Skipping LLM parsing.")
                return {}, {}, False
            
            # Parse with the appropriate LLM
            if self.llm_provider == "claude" and self.anthropic_client:
                sections, metadata = self._parse_with_claude(resume_text)
            elif self.llm_provider == "openai" and self.openai_client:
                sections, metadata = self._parse_with_openai(resume_text)
            else:
                logger.warning(f"No valid LLM client for provider: {self.llm_provider}")
                return {}, {}, False
            
            # Validate the parsed sections
            if not self._validate_sections(sections):
                logger.warning("LLM parsing produced invalid sections structure")
                return {}, metadata, False
                
            # Format sections to match expected output format
            formatted_sections = self._format_sections(sections)
            
            logger.info(f"LLM parsing successful with {self.llm_provider}")
            for section, content in formatted_sections.items():
                if content:
                    logger.info(f"Parsed {section} section: {len(content)} chars")
                    
            return formatted_sections, metadata, True
            
        except Exception as e:
            logger.error(f"Error in LLM resume parsing: {str(e)}")
            logger.error(traceback.format_exc())
            return {}, {}, False
    
    def _parse_with_claude(self, resume_text: str) -> Tuple[Dict, Dict]:
        """Parse resume text using Claude API"""
        start_time = time.time()
        
        try:
            prompt = self._get_parsing_prompt(resume_text)
            
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse the response
            response_content = response.content[0].text
            try:
                sections = json.loads(response_content)
            except json.JSONDecodeError:
                # Try to extract JSON from text if not properly formatted
                json_start = response_content.find('{')
                json_end = response_content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_content[json_start:json_end]
                    sections = json.loads(json_str)
                else:
                    logger.error("Failed to extract JSON from Claude response")
                    return {}, {"error": "JSON parsing failed"}
            
            # Calculate metadata
            processing_time = time.time() - start_time
            metadata = {
                "processing_time": processing_time,
                "model": "claude-3-sonnet-20240229",
                "parser": "llm-claude",
                "parsed_date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            
            return sections, metadata
            
        except Exception as e:
            logger.error(f"Error parsing with Claude: {str(e)}")
            return {}, {"error": str(e)}
    
    def _parse_with_openai(self, resume_text: str) -> Tuple[Dict, Dict]:
        """Parse resume text using OpenAI API"""
        start_time = time.time()
        
        try:
            prompt = self._get_parsing_prompt(resume_text)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                temperature=0.1,
                messages=[
                    {"role": "system", "content": "You are a precise resume parser. Extract sections from resumes and format them as structured JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse the response
            response_content = response.choices[0].message.content
            sections = json.loads(response_content)
            
            # Calculate metadata
            processing_time = time.time() - start_time
            metadata = {
                "processing_time": processing_time,
                "model": "gpt-4o",
                "parser": "llm-openai",
                "parsed_date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            return sections, metadata
            
        except Exception as e:
            logger.error(f"Error parsing with OpenAI: {str(e)}")
            return {}, {"error": str(e)}
    
    def _get_parsing_prompt(self, resume_text: str) -> str:
        """Generate a prompt for the LLM to parse the resume"""
        return f"""
I need you to parse the following resume into structured sections. 
Extract the content exactly as written in the resume without adding, changing, or removing any information.
Identify and categorize the content into these standard resume sections:

1. contact: Contact information including name, email, phone, address, LinkedIn
2. summary: Professional summary or objective statement
3. experience: Work history and professional experience
4. education: Educational background, degrees, certifications
5. skills: Technical and professional skills
6. projects: Notable projects
7. additional: Additional information, interests, volunteer work

IMPORTANT: When parsing company information in the experience section, carefully separate:
- Company name (e.g., "DIRECTV") from 
- Location information (e.g., "LOS ANGELES, CA")

If you see patterns like "COMPANY CITY" or "COMPANY CITY STATE", parse them accordingly.
Common examples include:
- "DIRECTV LOS ANGELES" → Company: "DIRECTV", Location: "LOS ANGELES"
- "Amazon Seattle" → Company: "Amazon", Location: "Seattle"
- "Microsoft Redmond WA" → Company: "Microsoft", Location: "Redmond, WA"

Provide your response as a JSON object with these exact section names as keys, and the full text content of each section as the values.
Preserve all original text formatting and bullet points where possible (convert to plain text).

Here's the resume text to parse:

{resume_text}

Important: Return ONLY valid JSON containing the extracted sections, preserve the exact content from the resume, and do not add any explanations or commentary.
If a section is not present in the resume, include it with an empty string value.
        """
    
    def _validate_sections(self, sections: Dict) -> bool:
        """Validate that the parsed sections have the expected structure"""
        # Check if we have a valid dictionary
        if not isinstance(sections, dict):
            return False
            
        # Check if sections has at least one valid section
        required_sections = {"sections", "contact", "summary", "experience", "education", "skills", "projects", "additional"}
        found_sections = set(sections.keys())
        
        # Either we have a nested structure with "sections" key or direct section keys
        if "sections" in found_sections:
            if not isinstance(sections["sections"], dict):
                return False
            nested_sections = set(sections["sections"].keys())
            return len(nested_sections & required_sections) > 0
        else:
            return len(found_sections & required_sections) > 0
    
    def _format_sections(self, sections: Dict) -> Dict[str, str]:
        """Format the parsed sections to match the expected output structure"""
        # Initialize standard resume sections
        formatted_sections = {
            "contact": "",
            "summary": "",
            "experience": "",
            "education": "",
            "skills": "",
            "projects": "",
            "additional": ""
        }
        
        # Handle nested structure if present
        if "sections" in sections:
            section_data = sections["sections"]
        else:
            section_data = sections
            
        # Copy content from parsed sections
        for key in formatted_sections:
            if key in section_data:
                if isinstance(section_data[key], dict) and "content" in section_data[key]:
                    # Handle structure with content key
                    formatted_sections[key] = section_data[key]["content"]
                else:
                    # Handle direct string content
                    formatted_sections[key] = str(section_data[key])
        
        return formatted_sections


# Helper function to use in the main code
def parse_resume_with_llm(doc_path: str, llm_provider: str = "claude") -> Dict[str, str]:
    """
    Parse a resume with LLM and fall back to traditional parsing if needed
    
    Args:
        doc_path: Path to the resume document
        llm_provider: LLM provider to use ("claude" or "openai")
        
    Returns:
        Dictionary of parsed sections
    """
    parser = LLMResumeParser(llm_provider=llm_provider)
    sections, metadata, success = parser.parse_resume(doc_path)
    
    # Log metadata
    if metadata:
        logger.info(f"LLM parsing metadata: {json.dumps(metadata)}")
        
    # If LLM parsing succeeded, return the sections
    if success and sections:
        # Create a cache file to avoid repeated parsing
        cache_id = str(uuid.uuid4())
        cache_path = os.path.join(os.path.dirname(doc_path), f"{cache_id}_llm_parsed.json")
        
        try:
            with open(cache_path, 'w') as f:
                json.dump({
                    "sections": sections,
                    "metadata": metadata
                }, f, indent=2)
            logger.info(f"LLM parsing cached to: {cache_path}")
        except Exception as e:
            logger.error(f"Error caching LLM parsing results: {str(e)}")
            
        return sections
    
    # Otherwise, return empty dict to trigger fallback
    return {} 