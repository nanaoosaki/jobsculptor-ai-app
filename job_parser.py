import requests
from bs4 import BeautifulSoup
import re
import json
import os
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import config
try:
    from config import Config
    USE_LLM_JOB_ANALYSIS = Config.USE_LLM_JOB_ANALYSIS
    LLM_JOB_ANALYZER_PROVIDER = Config.LLM_JOB_ANALYZER_PROVIDER
    JOB_ANALYSIS_CACHE_DIR = Config.JOB_ANALYSIS_CACHE_DIR
except ImportError:
    logger.warning("Config import failed, using default values for LLM job analysis")
    USE_LLM_JOB_ANALYSIS = True
    LLM_JOB_ANALYZER_PROVIDER = "auto"
    JOB_ANALYSIS_CACHE_DIR = "static/uploads/job_analysis_cache"

# Try to import the job analyzer
try:
    from llm_job_analyzer import analyze_job_with_llm
    LLM_JOB_ANALYZER_AVAILABLE = True
except ImportError:
    logger.warning("LLM job analyzer not found. Will use traditional parsing only.")
    LLM_JOB_ANALYZER_AVAILABLE = False

def analyze_job_posting_with_llm(job_title: str, company: str, job_text: str, api_key: str, provider: str = "openai", api_url: str = None) -> Dict[str, Any]:
    """
    Analyze a job posting with LLM to extract structured insights.
    
    Args:
        job_title: The title of the job
        company: The company offering the job
        job_text: The complete text of the job posting
        api_key: The API key for the LLM provider
        provider: The LLM provider to use ('claude', 'openai', or 'auto')
        api_url: Optional API URL for Claude
    
    Returns:
        A dictionary containing the analysis results
    """
    # Check if LLM job analysis is enabled and available
    if not USE_LLM_JOB_ANALYSIS or not LLM_JOB_ANALYZER_AVAILABLE:
        logger.info("LLM job analysis is disabled or unavailable. Skipping analysis.")
        return {
            "candidate_profile": "",
            "hard_skills": [],
            "soft_skills": [],
            "ideal_candidate": "",
            "metadata": {
                "analyzed": False,
                "reason": "LLM job analysis is disabled or unavailable"
            }
        }
    
    try:
        # Import config to get API keys
        from config import Config
        
        # Determine which API key to use based on provider
        if provider == "openai" or (provider == "auto" and LLM_JOB_ANALYZER_PROVIDER == "openai"):
            api_key = api_key or Config.OPENAI_API_KEY
            provider = "openai"
        elif provider == "claude" or (provider == "auto" and LLM_JOB_ANALYZER_PROVIDER == "claude"):
            api_key = api_key or Config.CLAUDE_API_KEY
            api_url = api_url or Config.CLAUDE_API_URL
            provider = "claude"
        elif provider == "auto":
            # Try to determine provider based on available API keys
            # Prioritize OpenAI over Claude
            if Config.OPENAI_API_KEY:
                api_key = Config.OPENAI_API_KEY
                provider = "openai"
                logger.info("Auto provider selected - using OpenAI")
            elif Config.CLAUDE_API_KEY:
                api_key = Config.CLAUDE_API_KEY
                api_url = Config.CLAUDE_API_URL
                provider = "claude"
                logger.info("Auto provider selected - using Claude (OpenAI not available)")
            else:
                logger.warning("No API keys found for LLM job analysis")
                return {
                    "candidate_profile": "",
                    "hard_skills": [],
                    "soft_skills": [],
                    "ideal_candidate": "",
                    "metadata": {
                        "analyzed": False,
                        "reason": "No API keys available"
                    }
                }
        
        # Check if we have a valid API key
        if not api_key:
            logger.warning(f"No API key available for {provider}")
            return {
                "candidate_profile": "",
                "hard_skills": [],
                "soft_skills": [],
                "ideal_candidate": "",
                "metadata": {
                    "analyzed": False,
                    "reason": f"No API key available for {provider}"
                }
            }
        
        # Make sure the cache directory exists
        if not os.path.exists(JOB_ANALYSIS_CACHE_DIR):
            os.makedirs(JOB_ANALYSIS_CACHE_DIR, exist_ok=True)
        
        # Analyze the job posting with LLM
        logger.info(f"Analyzing job posting for {job_title} at {company} with {provider}")
        analysis_results = analyze_job_with_llm(
            job_title=job_title,
            company=company,
            job_text=job_text,
            api_key=api_key,
            provider=provider,
            api_url=api_url,
            cache_dir=JOB_ANALYSIS_CACHE_DIR
        )
        
        # Check if analysis was successful
        if "error" in analysis_results:
            logger.warning(f"LLM job analysis failed: {analysis_results['error']}")
        else:
            logger.info(f"LLM job analysis successful for {job_title} at {company}")
        
        return analysis_results
    
    except Exception as e:
        logger.error(f"Error during LLM job analysis: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            "candidate_profile": "",
            "hard_skills": [],
            "soft_skills": [],
            "ideal_candidate": "",
            "metadata": {
                "analyzed": False,
                "reason": f"Error during analysis: {str(e)}"
            }
        }

def parse_linkedin_job(url):
    """
    Parse a LinkedIn job listing URL to extract key requirements and all sections
    """
    try:
        # Make request to the job listing page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'Failed to access URL: Status code {response.status_code}'
            }
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract job title
        job_title_elem = soup.find('h1', class_='top-card-layout__title')
        job_title = job_title_elem.text.strip() if job_title_elem else 'Unknown Position'
        
        # Extract company name
        company_elem = soup.find('a', class_='topcard__org-name-link')
        company = company_elem.text.strip() if company_elem else 'Unknown Company'
        
        # Extract job description
        description_elem = soup.find('div', class_='show-more-less-html__markup')
        full_description = description_elem.text.strip() if description_elem else ''
        
        # Extract the complete job text for LLM processing
        complete_job_text = extract_complete_job_text(full_description)
        
        # Extract structured sections from the full description
        sections = extract_job_sections(full_description)
        
        # Extract requirements and skills using existing functions
        requirements = extract_linkedin_requirements(full_description)
        
        # If no requirements found with the improved method, try other approaches
        if not requirements:
            requirements = extract_requirements_from_description(full_description)
        
        # Extract skills
        skills = extract_skills_from_description(full_description)
        
        # Analyze the job posting with LLM if enabled
        llm_analysis = analyze_job_posting_with_llm(job_title, company, complete_job_text, None)
        
        # If LLM analysis found skills and we don't have any, use those
        if not skills and llm_analysis and "hard_skills" in llm_analysis and llm_analysis["hard_skills"]:
            skills = llm_analysis["hard_skills"]
            logger.info(f"Using {len(skills)} skills from LLM analysis")
        
        # If LLM analysis found requirements and we don't have any, use the candidate_profile as a requirement
        if not requirements and llm_analysis and "candidate_profile" in llm_analysis and llm_analysis["candidate_profile"]:
            requirements = [llm_analysis["candidate_profile"]]
            logger.info(f"Using candidate profile from LLM analysis as a requirement")
        
        # Add additional requirements from LLM analysis if available
        if llm_analysis and "ideal_candidate" in llm_analysis and llm_analysis["ideal_candidate"]:
            ideal_candidate_req = f"Ideal Candidate: {llm_analysis['ideal_candidate']}"
            requirements.append(ideal_candidate_req)
            logger.info(f"Added ideal candidate description from LLM analysis as a requirement")
        
        return {
            'success': True,
            'job_title': job_title,
            'company': company,
            'full_description': full_description,
            'complete_job_text': complete_job_text,
            'sections': sections,
            'requirements': requirements,
            'skills': skills,
            'llm_analysis': llm_analysis
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error parsing job listing: {str(e)}'
        }

def extract_job_sections(description):
    """
    Extract sections from LinkedIn job description
    """
    sections = {}
    
    # Common section names and patterns - expanded with more variations
    section_patterns = [
        # About sections
        (r"About the job\s*(?::|\.|\n)", "about_the_job"),
        (r"About the role\s*(?::|\.|\n)", "about_the_job"),
        (r"Job description\s*(?::|\.|\n)", "about_the_job"),
        (r"Position summary\s*(?::|\.|\n)", "about_the_job"),
        (r"Overview\s*(?::|\.|\n)", "about_the_job"),
        
        # Team sections
        (r"Team description\s*(?::|\.|\n)", "about_team"),
        (r"Our team\s*(?::|\.|\n)", "about_team"),
        (r"The team\s*(?::|\.|\n)", "about_team"),
        (r"About the team\s*(?::|\.|\n)", "about_team"),
        (r"Team overview\s*(?::|\.|\n)", "about_team"),
        
        # Company sections
        (r"About us\s*(?::|\.|\n)", "about_us"),
        (r"About the company\s*(?::|\.|\n)", "about_us"),
        (r"Company description\s*(?::|\.|\n)", "about_us"),
        (r"Who we are\s*(?::|\.|\n)", "about_us"),
        
        # Role description sections
        (r"In this role,?\s*you will\s*(?::|\.|\n)", "job_responsibilities"),
        (r"In this position,?\s*you will\s*(?::|\.|\n)", "job_responsibilities"),
        (r"Responsibilities\s*(?::|\.|\n)", "job_responsibilities"),
        (r"Job responsibilities\s*(?::|\.|\n)", "job_responsibilities"),
        (r"Duties\s*(?::|\.|\n)", "job_responsibilities"),
        (r"What you['']ll do\s*(?::|\.|\n)", "job_responsibilities"),
        (r"Your responsibilities\s*(?::|\.|\n)", "job_responsibilities"),
        (r"Key responsibilities\s*(?::|\.|\n)", "job_responsibilities"),
        
        # Requirements sections
        (r"Requirements\s*(?::|\.|\n)", "required_qualifications"),
        (r"Required [Qq]ualifications\s*(?::|\.|\n)", "required_qualifications"),
        (r"Minimum [Qq]ualifications\s*(?::|\.|\n)", "required_qualifications"),
        (r"Basic [Qq]ualifications\s*(?::|\.|\n)", "required_qualifications"),
        (r"Qualifications\s*(?::|\.|\n)", "required_qualifications"),
        (r"What you['']ll need\s*(?::|\.|\n)", "required_qualifications"),
        (r"Required [Ss]kills\s*(?::|\.|\n)", "required_qualifications"),
        (r"Required [Ee]xperience\s*(?::|\.|\n)", "required_qualifications"),
        (r"Required [Ee]ducation\s*(?::|\.|\n)", "required_qualifications"),
        (r"Who you are\s*(?::|\.|\n)", "required_qualifications"),
        
        # Preferred qualifications sections
        (r"Preferred [Qq]ualifications\s*(?::|\.|\n)", "preferred_qualifications"),
        (r"Preferred [Ss]kills\s*(?::|\.|\n)", "preferred_qualifications"),
        (r"Nice to have\s*(?::|\.|\n)", "preferred_qualifications"),
        (r"Bonus [Qq]ualifications\s*(?::|\.|\n)", "preferred_qualifications"),
        (r"Bonus [Pp]oints\s*(?::|\.|\n)", "preferred_qualifications"),
        (r"Additionally, it would be great if\s*(?::|\.|\n)", "preferred_qualifications"),
        
        # Tech stack sections
        (r"Our [Tt]ech [Ss]tack\s*(?::|\.|\n)", "tech_stack"),
        (r"Technology [Ss]tack\s*(?::|\.|\n)", "tech_stack"),
        (r"Technologies we use\s*(?::|\.|\n)", "tech_stack"),
        (r"Technologies\s*(?::|\.|\n)", "tech_stack"),
        
        # Benefits sections
        (r"Benefits\s*(?::|\.|\n)", "benefits"),
        (r"What we offer\s*(?::|\.|\n)", "benefits"),
        (r"Perks\s*(?::|\.|\n)", "benefits"),
        (r"Why work (?:for|with) us\s*(?::|\.|\n)", "benefits"),
        (r"Compensation\s*(?::|\.|\n)", "benefits"),
        (r"Salary and [Bb]enefits\s*(?::|\.|\n)", "benefits"),
        
        # Candidate sections
        (r"The [Ii]deal [Cc]andidate\s*(?::|\.|\n)", "ideal_candidate"),
        (r"About you\s*(?::|\.|\n)", "ideal_candidate"),
        (r"You are\s*(?::|\.|\n)", "ideal_candidate"),
        
        # Misc sections
        (r"Application [Pp]rocess\s*(?::|\.|\n)", "application_process"),
        (r"Next [Ss]teps\s*(?::|\.|\n)", "application_process"),
        (r"Diversity [Ss]tatement\s*(?::|\.|\n)", "diversity"),
        (r"Equal [Oo]pportunity\s*(?::|\.|\n)", "diversity")
    ]
    
    # Find all potential section headings
    section_matches = []
    for pattern, section_name in section_patterns:
        matches = re.finditer(pattern, description, re.IGNORECASE)
        for match in matches:
            section_matches.append((match.start(), section_name))
    
    # Sort matches by position
    section_matches.sort(key=lambda x: x[0])
    
    # Extract content between section headings
    for i, (pos, section_name) in enumerate(section_matches):
        # Find the end of the current section (start of next section or end of text)
        if i < len(section_matches) - 1:
            next_pos = section_matches[i+1][0]
            section_text = description[pos:next_pos].strip()
        else:
            section_text = description[pos:].strip()
        
        # Remove the heading from the section text
        section_heading_match = re.search(r"^.*?(?::|\.|\n)", section_text)
        if section_heading_match:
            section_text = section_text[section_heading_match.end():].strip()
        
        sections[section_name] = section_text
    
    # If no sections were found, try looking for common patterns without explicit headings
    if not sections:
        # Try to find paragraphs separated by double newlines and make best guess at sections
        paragraphs = [p.strip() for p in description.split('\n\n') if p.strip()]
        
        # If we have multiple paragraphs, try to categorize them
        if len(paragraphs) >= 3:
            # First paragraph is usually about the job
            sections["about_the_job"] = paragraphs[0]
            
            # Check for bullets in other paragraphs to identify requirements
            for i, para in enumerate(paragraphs[1:], 1):
                if re.search(r'[•■◦⦿⚫⚪○●★☆▪▫-]\s', para):
                    if "required_qualifications" not in sections:
                        sections["required_qualifications"] = para
                    elif "job_responsibilities" not in sections:
                        sections["job_responsibilities"] = para
                    else:
                        sections[f"section_{i}"] = para
                else:
                    sections[f"section_{i}"] = para
    
    # If still no sections were found, add the entire description as "Full Description"
    if not sections:
        sections["full_description"] = description
    
    # Special handling for "About the job" if it wasn't found but we have other sections
    if "about_the_job" not in sections and description and sections:
        # Try to get first paragraph or section
        first_paragraph_match = re.search(r"^(.*?)(?:\n\n|\n[A-Z])", description, re.DOTALL)
        if first_paragraph_match:
            sections["about_the_job"] = first_paragraph_match.group(1).strip()
    
    return sections

def extract_linkedin_requirements(description):
    """
    Extract requirements from LinkedIn job description with improved patterns
    specifically targeting "Role Description" and "In this role, you will:" sections
    """
    requirements = []
    
    # Look for role description sections
    role_patterns = [
        r'Role Description.*?In this role, you will:(.*?)(?=\n\n[A-Z]|\Z)',
        r'In this role, you will:(.*?)(?=\n\n[A-Z]|\Z)',
        r'What you\'ll do:(.*?)(?=\n\n[A-Z]|\Z)',
        r'Responsibilities:(.*?)(?=\n\n[A-Z]|\Z)',
        r'Job Description:(.*?)(?=\n\n[A-Z]|\Z)',
        r'About the job:(.*?)(?=\n\n[A-Z]|\Z)',
        r'About the role:(.*?)(?=\n\n[A-Z]|\Z)'
    ]
    
    for pattern in role_patterns:
        matches = re.findall(pattern, description, re.DOTALL | re.IGNORECASE)
        for match in matches:
            # Extract bullet points
            bullet_items = re.findall(r'[•■◦⦿⚫⚪○●★☆▪▫]\s*(.*?)(?=\n[•■◦⦿⚫⚪○●★☆▪▫]|\n\n|\Z)', match, re.DOTALL)
            
            # If no bullet points with symbols, try with dash or asterisk
            if not bullet_items:
                bullet_items = re.findall(r'[-*+]\s*(.*?)(?=\n[-*+]|\n\n|\Z)', match, re.DOTALL)
            
            # If still no bullet points, try with numbered list
            if not bullet_items:
                bullet_items = re.findall(r'\d+\.\s*(.*?)(?=\n\d+\.|\n\n|\Z)', match, re.DOTALL)
            
            # Clean and add the bullet points
            for item in bullet_items:
                item = item.strip()
                if item and len(item) > 5 and item not in requirements:
                    requirements.append(item)
    
    # If no requirements found with bullet points, try to extract paragraphs
    if not requirements:
        for pattern in role_patterns:
            matches = re.findall(pattern, description, re.DOTALL | re.IGNORECASE)
            for match in matches:
                paragraphs = [p.strip() for p in match.split('\n\n') if p.strip()]
                for para in paragraphs:
                    if len(para) > 20 and para not in requirements:
                        requirements.append(para)
    
    # Also check "Basic Qualifications" and "Requirements" sections
    qual_patterns = [
        r'Basic Qualifications:(.*?)(?=\n\n[A-Z]|\Z)',
        r'Requirements:(.*?)(?=\n\n[A-Z]|\Z)',
        r'Qualifications:(.*?)(?=\n\n[A-Z]|\Z)',
        r'What You\'ll Need:(.*?)(?=\n\n[A-Z]|\Z)',
        r'Required Skills:(.*?)(?=\n\n[A-Z]|\Z)',
        r'Required Experience:(.*?)(?=\n\n[A-Z]|\Z)'
    ]
    
    for pattern in qual_patterns:
        matches = re.findall(pattern, description, re.DOTALL | re.IGNORECASE)
        for match in matches:
            # Extract bullet points with various symbols
            items = re.findall(r'[•■◦⦿⚫⚪○●★☆▪▫-]\s*(.*?)(?=\n[•■◦⦿⚫⚪○●★☆▪▫-]|\n\n|\Z)', match, re.DOTALL)
            
            # If no bullet points, try with numbered list
            if not items:
                items = re.findall(r'\d+\.\s*(.*?)(?=\n\d+\.|\n\n|\Z)', match, re.DOTALL)
            
            # Clean and add the items
            for item in items:
                item = item.strip()
                if item and len(item) > 5 and item not in requirements:
                    requirements.append(item)
    
    return requirements

def extract_requirements_from_description(description):
    """
    Extract requirements from job description text
    """
    requirements = []
    
    # Look for common requirement section indicators
    requirement_sections = [
        r'Requirements:.*?(?=\n\n[A-Z]|\Z)',
        r'Qualifications:.*?(?=\n\n[A-Z]|\Z)',
        r'What You\'ll Need:.*?(?=\n\n[A-Z]|\Z)',
        r'Required Skills:.*?(?=\n\n[A-Z]|\Z)',
        r'Required Experience:.*?(?=\n\n[A-Z]|\Z)',
        r'Required Qualifications:.*?(?=\n\n[A-Z]|\Z)',
        r'Basic Qualifications:.*?(?=\n\n[A-Z]|\Z)',
        r'Minimum Qualifications:.*?(?=\n\n[A-Z]|\Z)',
        r'Skills & Experience:.*?(?=\n\n[A-Z]|\Z)',
        r'Skills and Qualifications:.*?(?=\n\n[A-Z]|\Z)'
    ]
    
    for pattern in requirement_sections:
        matches = re.findall(pattern, description, re.DOTALL | re.IGNORECASE)
        for match in matches:
            # Extract bullet points with various symbols
            items = re.findall(r'[•■◦⦿⚫⚪○●★☆▪▫+*-]\s*(.*?)(?=\n[•■◦⦿⚫⚪○●★☆▪▫+*-]|\n\n|\Z)', match, re.DOTALL)
            
            # If no bullet points, try with numbered list
            if not items:
                items = re.findall(r'\d+\.\s*(.*?)(?=\n\d+\.|\n\n|\Z)', match, re.DOTALL)
            
            # If still no structured items, try to extract sentences
            if not items:
                sentences = re.findall(r'([^.\n]+\.[^\n]*)', match)
                items = sentences
            
            # Clean and add the items
            for item in items:
                item = item.strip()
                if item and len(item) > 5 and item not in requirements:
                    requirements.append(item)
    
    # If no structured requirements found, look for key phrases
    if not requirements:
        key_phrases = [
            r'(?:must|should) have .*?(?=\.|$)',
            r'(?:we are|we\'re) looking for .*?(?=\.|$)',
            r'experience (?:with|in) .*?(?=\.|$)',
            r'knowledge of .*?(?=\.|$)',
            r'familiarity with .*?(?=\.|$)',
            r'proficiency in .*?(?=\.|$)',
            r'background in .*?(?=\.|$)',
            r'degree in .*?(?=\.|$)'
        ]
        
        for phrase in key_phrases:
            matches = re.findall(phrase, description, re.IGNORECASE)
            for match in matches:
                match = match.strip()
                if match and len(match) > 10 and match not in requirements:
                    requirements.append(match)
    
    return requirements

def extract_skills_from_description(description):
    """
    Extract specific skills from job description with enhanced modern skills
    """
    # Common technical skills
    tech_skills = [
        # Programming Languages
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C\\+\\+', 'C#', 'Ruby', 'Go', 'Rust', 'PHP', 'Swift', 'Kotlin',
        'Scala', 'Perl', 'R', 'MATLAB', 'Julia', 'Dart', 'Groovy', 'Bash', 'PowerShell', 'Assembly',
        
        # Databases
        'SQL', 'NoSQL', 'MongoDB', 'MySQL', 'PostgreSQL', 'Oracle', 'SQLite', 'DynamoDB', 'Cassandra', 'Redis',
        'Elasticsearch', 'Neo4j', 'CosmosDB', 'Firebase', 'Supabase', 'CouchDB', 'MariaDB', 'Teradata',
        
        # Cloud Platforms
        'AWS', 'Azure', 'GCP', 'Google Cloud', 'Alibaba Cloud', 'IBM Cloud', 'Oracle Cloud', 'DigitalOcean',
        'Heroku', 'Vercel', 'Netlify', 'CloudFlare', 'Linode', 'Vultr',
        
        # DevOps & Tools
        'Docker', 'Kubernetes', 'K8s', 'Jenkins', 'Git', 'GitHub', 'GitLab', 'Bitbucket', 'CircleCI', 'TravisCI',
        'ArgoCD', 'Terraform', 'Ansible', 'Puppet', 'Chef', 'Prometheus', 'Grafana', 'ELK Stack', 'EFK Stack',
        'Datadog', 'New Relic', 'Splunk', 'Istio', 'Helm', 'Pulumi',
        
        # Frameworks & Libraries
        'React', 'Angular', 'Vue', 'Svelte', 'Node\\.js', 'Express', 'Django', 'Flask', 'Spring', 'Spring Boot',
        'Ruby on Rails', 'Laravel', 'ASP\\.NET', 'FastAPI', 'Symfony', 'Next\\.js', 'Nuxt\\.js', 'Gatsby', 'Deno',
        'jQuery', 'Ember', 'Backbone', 'Meteor', 'Redux', 'MobX', 'RxJS', 'HTMX',
        
        # AI & Machine Learning
        'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas', 'NumPy', 'SciPy', 'Matplotlib', 'Seaborn',
        'Hugging Face', 'Transformers', 'BERT', 'GPT', 'LLM', 'Large Language Models', 'LangChain', 'OpenAI',
        'Diffusion Models', 'Stable Diffusion', 'JAX', 'ONNX', 'MXNet', 'Caffe', 'MLflow', 'Ray',
        'Reinforcement Learning', 'Recommender Systems', 'Information Retrieval', 'NLP', 'Computer Vision',
        'GenAI', 'Generative AI', 'Prompt Engineering', 'Vector Database', 'PySpark', 'Snowflake',
        'LLaMA', 'Mistral', 'Claude', 'DALL-E', 'Midjourney', 'Embedding', 'Vector Search', 'RAG',
        
        # Frontend Tech
        'HTML', 'CSS', 'SASS', 'LESS', 'Bootstrap', 'Tailwind', 'Material UI', 'Chakra UI', 'Styled Components',
        'Emotion', 'Webpack', 'Vite', 'Rollup', 'Parcel', 'esbuild', 'Storybook', 'Jest', 'Cypress', 'Playwright',
        'PWA', 'WebAssembly', 'WASM', 'TypeScript', 'WebGL', 'Three.js', 'D3.js',
        
        # Backend & Architecture
        'REST', 'GraphQL', 'gRPC', 'API', 'Microservices', 'Serverless', 'CI/CD', 'Event-Driven', 'Message Queue',
        'RabbitMQ', 'Kafka', 'NATS', 'ZeroMQ', 'WebSockets', 'Socket.IO', 'MQTT', 'Pub/Sub',
        
        # Project Management
        'Agile', 'Scrum', 'Kanban', 'Jira', 'Confluence', 'Trello', 'Asana', 'Monday', 'ClickUp', 'Notion',
        
        # Operating Systems
        'Linux', 'Unix', 'Windows', 'MacOS', 'iOS', 'Android',
        
        # Data & Analytics
        'Data Science', 'Data Analysis', 'Data Visualization', 'Big Data', 'ETL', 'Data Pipeline',
        'Hadoop', 'Spark', 'Kafka', 'Elasticsearch', 'Logstash', 'Kibana', 'Tableau', 'Power BI',
        'Looker', 'Grafana', 'Superset', 'Airflow', 'Luigi', 'dbt', 'Prefect', 'Pinot', 'Druid',
        
        # DevOps & MLOps
        'DevOps', 'MLOps', 'DataOps', 'GitOps', 'DevSecOps', 'SRE', 'Infrastructure as Code', 'IaC',
        
        # Security
        'Cybersecurity', 'SAST', 'DAST', 'Penetration Testing', 'Ethical Hacking', 'SOC', 'SIEM', 'IAM',
        'Zero Trust', 'OAuth', 'SAML', 'SSO', 'MFA', '2FA',
        
        # Blockchain
        'Blockchain', 'Smart Contracts', 'Ethereum', 'Solidity', 'Web3', 'DApp', 'NFT', 'DAO',
        
        # Mobile
        'iOS', 'Android', 'React Native', 'Flutter', 'Xamarin', 'SwiftUI', 'Kotlin Multiplatform', 'Ionic',
        'Cordova', 'Capacitor', 'Progressive Web App', 'PWA'
    ]
    
    # Common soft skills
    soft_skills = [
        'Communication', 'Teamwork', 'Problem-solving', 'Critical thinking',
        'Creativity', 'Leadership', 'Time management', 'Adaptability',
        'Collaboration', 'Emotional intelligence', 'Conflict resolution',
        'Decision-making', 'Negotiation', 'Presentation', 'Public speaking',
        'Interpersonal skills', 'Analytical thinking', 'Attention to detail',
        'Organization', 'Planning', 'Prioritization', 'Self-motivation',
        'Self-discipline', 'Customer service', 'Client relationship',
        'Mentoring', 'Coaching', 'Feedback', 'Active listening',
        'Written communication', 'Verbal communication', 'Cross-functional collaboration',
        'Remote work', 'Virtual collaboration', 'Agile mindset', 'Growth mindset'
    ]
    
    # Combine all skills
    all_skills = tech_skills + soft_skills
    
    # Find skills in description
    found_skills = []
    for skill in all_skills:
        pattern = r'\b' + re.escape(skill.replace('\\', '')) + r'\b'
        if re.search(pattern, description, re.IGNORECASE):
            # Add the skill without any escape characters that may have been in the pattern
            found_skills.append(skill.replace('\\', ''))
    
    return found_skills

def extract_complete_job_text(description):
    """
    Extract the complete job description text between "About the job" and "Benefits" sections,
    or the entire document if those markers aren't found.
    This provides a complete raw text that can be processed by an LLM for more accurate parsing.
    """
    # Try to find the beginning marker - look for variations
    start_markers = [
        r"About the [Jj]ob\s*(?::|\.|\n)",
        r"[Jj]ob [Dd]escription\s*(?::|\.|\n)",
        r"[Pp]osition [Ss]ummary\s*(?::|\.|\n)",
        r"[Oo]verview\s*(?::|\.|\n)"
    ]
    
    # Try to find the ending marker - look for variations
    end_markers = [
        r"[Bb]enefits\s*(?::|\.|\n)",
        r"[Ww]hat [Ww]e [Oo]ffer\s*(?::|\.|\n)",
        r"[Pp]erks\s*(?::|\.|\n)",
        r"[Aa]bout [Uu]s\s*(?::|\.|\n)",
        r"[Cc]ompensation\s*(?::|\.|\n)",
        r"[Ss]alary\s*(?::|\.|\n)"
    ]
    
    # Find the start of the job description
    start_pos = 0
    for marker in start_markers:
        match = re.search(marker, description, re.DOTALL)
        if match:
            # Get the end position of the matched marker
            start_pos = match.start()
            break
    
    # Find the end of the job description
    end_pos = len(description)
    for marker in end_markers:
        match = re.search(marker, description, re.DOTALL)
        if match and match.start() > start_pos:
            end_pos = match.start()
            break
    
    # Extract the text between the markers
    job_text = description[start_pos:end_pos].strip()
    
    # If we got nothing, return the whole text
    if not job_text:
        return description
    
    return job_text

def parse_generic_job(url):
    """
    Parse a generic job listing URL to extract key information
    """
    try:
        # Make request to the job listing page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'Failed to access URL: Status code {response.status_code}'
            }
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to extract job title
        job_title = 'Unknown Position'
        title_elements = soup.find_all(['h1', 'h2'], class_=lambda c: c and any(x in c.lower() for x in ['title', 'position', 'job']))
        if title_elements:
            job_title = title_elements[0].text.strip()
        
        # Try to extract company name
        company = 'Unknown Company'
        company_elements = soup.find_all(['h1', 'h2', 'h3', 'div'], class_=lambda c: c and any(x in c.lower() for x in ['company', 'organization', 'employer']))
        if company_elements:
            company = company_elements[0].text.strip()
        
        # Extract all text from the page
        all_text = soup.get_text()
        
        # Extract the complete job text for LLM processing
        complete_job_text = extract_complete_job_text(all_text)
        
        # Extract sections
        sections = extract_job_sections(all_text)
        
        # Extract requirements from text
        requirements = extract_requirements_from_description(all_text)
        
        # Extract skills
        skills = extract_skills_from_description(all_text)
        
        # Analyze the job posting with LLM if enabled
        llm_analysis = analyze_job_posting_with_llm(job_title, company, complete_job_text, None)
        
        # If LLM analysis found skills and we don't have any, use those
        if not skills and llm_analysis and "hard_skills" in llm_analysis and llm_analysis["hard_skills"]:
            skills = llm_analysis["hard_skills"]
            logger.info(f"Using {len(skills)} skills from LLM analysis")
        
        # If LLM analysis found requirements and we don't have any, use the candidate_profile as a requirement
        if not requirements and llm_analysis and "candidate_profile" in llm_analysis and llm_analysis["candidate_profile"]:
            requirements = [llm_analysis["candidate_profile"]]
            logger.info(f"Using candidate profile from LLM analysis as a requirement")
        
        # Add additional requirements from LLM analysis if available
        if llm_analysis and "ideal_candidate" in llm_analysis and llm_analysis["ideal_candidate"]:
            ideal_candidate_req = f"Ideal Candidate: {llm_analysis['ideal_candidate']}"
            requirements.append(ideal_candidate_req)
            logger.info(f"Added ideal candidate description from LLM analysis as a requirement")
        
        return {
            'success': True,
            'job_title': job_title,
            'company': company,
            'full_description': all_text,
            'complete_job_text': complete_job_text,
            'sections': sections,
            'requirements': requirements,
            'skills': skills,
            'llm_analysis': llm_analysis
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error parsing job listing: {str(e)}'
        }

def parse_job_listing(url):
    """
    Parse a job listing URL based on the domain
    """
    if 'linkedin.com' in url:
        return parse_linkedin_job(url)
    else:
        return parse_generic_job(url)
