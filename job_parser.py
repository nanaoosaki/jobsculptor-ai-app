import requests
from bs4 import BeautifulSoup
import re
import json

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
        
        # Extract structured sections from the full description
        sections = extract_job_sections(full_description)
        
        # Extract requirements and skills using existing functions
        requirements = extract_linkedin_requirements(full_description)
        
        # If no requirements found with the improved method, try other approaches
        if not requirements:
            requirements = extract_requirements_from_description(full_description)
        
        # Extract skills
        skills = extract_skills_from_description(full_description)
        
        return {
            'success': True,
            'job_title': job_title,
            'company': company,
            'full_description': full_description,
            'sections': sections,
            'requirements': requirements,
            'skills': skills
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
    
    # Common section names and patterns
    section_patterns = [
        (r"About the job\s*(?::|\.|\n)", "About the job"),
        (r"Team Description\s*(?::|\.|\n)", "Team Description"),
        (r"In this role,?\s*you will\s*(?::|\.|\n)", "In this role"),
        (r"Responsibilities\s*(?::|\.|\n)", "Responsibilities"),
        (r"Requirements\s*(?::|\.|\n)", "Requirements"),
        (r"Qualifications\s*(?::|\.|\n)", "Qualifications"),
        (r"Basic Qualifications\s*(?::|\.|\n)", "Basic Qualifications"),
        (r"Preferred Qualifications\s*(?::|\.|\n)", "Preferred Qualifications"),
        (r"The Ideal Candidate is\s*(?::|\.|\n)", "Ideal Candidate"),
        (r"Our Tech Stack\s*(?::|\.|\n)", "Tech Stack"),
        (r"Benefits\s*(?::|\.|\n)", "Benefits"),
        (r"About the team\s*(?::|\.|\n)", "About the team"),
        (r"What You'll Need\s*(?::|\.|\n)", "What You'll Need"),
        (r"What You'll Do\s*(?::|\.|\n)", "What You'll Do"),
        (r"Required Skills\s*(?::|\.|\n)", "Required Skills"),
        (r"Required Experience\s*(?::|\.|\n)", "Required Experience"),
        (r"Required Education\s*(?::|\.|\n)", "Required Education")
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
    
    # If no sections were found, add the entire description as "Full Description"
    if not sections:
        sections["Full Description"] = description
    
    # Special handling for "About the job" if it wasn't found
    if "About the job" not in sections and description:
        # Try to get first paragraph or section
        first_paragraph_match = re.search(r"^(.*?)(?:\n\n|\n[A-Z])", description, re.DOTALL)
        if first_paragraph_match:
            sections["About the job"] = first_paragraph_match.group(1).strip()
    
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
    Extract specific skills from job description
    """
    # Common technical skills
    tech_skills = [
        'Python', 'Java', 'JavaScript', 'C\+\+', 'C#', 'Ruby', 'PHP', 'Swift', 'Kotlin',
        'SQL', 'NoSQL', 'MongoDB', 'MySQL', 'PostgreSQL', 'Oracle', 'AWS', 'Azure', 'GCP',
        'Docker', 'Kubernetes', 'Jenkins', 'Git', 'GitHub', 'GitLab', 'Bitbucket',
        'React', 'Angular', 'Vue', 'Node\.js', 'Express', 'Django', 'Flask', 'Spring',
        'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'R', 'MATLAB',
        'HTML', 'CSS', 'SASS', 'LESS', 'Bootstrap', 'Tailwind', 'jQuery',
        'REST', 'GraphQL', 'API', 'Microservices', 'Serverless', 'CI/CD',
        'Agile', 'Scrum', 'Kanban', 'Jira', 'Confluence', 'Trello',
        'Linux', 'Unix', 'Windows', 'MacOS', 'iOS', 'Android',
        'Machine Learning', 'Deep Learning', 'AI', 'NLP', 'Computer Vision',
        'Data Science', 'Data Analysis', 'Data Visualization', 'Big Data',
        'Hadoop', 'Spark', 'Kafka', 'Elasticsearch', 'Logstash', 'Kibana',
        'Tableau', 'Power BI', 'Looker', 'Grafana', 'Prometheus',
        'DevOps', 'MLOps', 'GenAI', 'LLM', 'Transformers', 'PySpark',
        'Reinforcement Learning', 'Recommender Systems', 'Information Retrieval'
    ]
    
    # Common soft skills
    soft_skills = [
        'Communication', 'Teamwork', 'Problem-solving', 'Critical thinking',
        'Creativity', 'Leadership', 'Time management', 'Adaptability',
        'Collaboration', 'Emotional intelligence', 'Conflict resolution',
        'Decision-making', 'Negotiation', 'Presentation', 'Public speaking',
        'Interpersonal skills'
    ]
    
    # Combine all skills
    all_skills = tech_skills + soft_skills
    
    # Find skills in description
    found_skills = []
    for skill in all_skills:
        if re.search(r'\b' + skill + r'\b', description, re.IGNORECASE):
            found_skills.append(skill.replace('\\', ''))
    
    return found_skills

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
        
        # Extract all text from the page
        all_text = soup.get_text()
        
        # Extract sections
        sections = extract_job_sections(all_text)
        
        # Extract requirements from text
        requirements = extract_requirements_from_description(all_text)
        
        # Extract skills
        skills = extract_skills_from_description(all_text)
        
        return {
            'success': True,
            'full_description': all_text,
            'sections': sections,
            'requirements': requirements,
            'skills': skills
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
