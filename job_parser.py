import requests
from bs4 import BeautifulSoup
import re
import json

def parse_linkedin_job(url):
    """
    Parse a LinkedIn job listing URL to extract key requirements
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
        description = description_elem.text.strip() if description_elem else ''
        
        # Extract requirements from description with improved patterns
        requirements = extract_linkedin_requirements(description)
        
        # If no requirements found with the improved method, fall back to the original method
        if not requirements:
            requirements = extract_requirements_from_description(description)
        
        # Extract skills
        skills = extract_skills_from_description(description)
        
        return {
            'success': True,
            'job_title': job_title,
            'company': company,
            'description': description,
            'requirements': requirements,
            'skills': skills
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error parsing job listing: {str(e)}'
        }

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
            items = re.findall(r'[•■◦⦿⚫⚪○●★☆▪▫-*+]\s*(.*?)(?=\n[•■◦⦿⚫⚪○●★☆▪▫-*+]|\n\n|\Z)', match, re.DOTALL)
            
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
        'H2O', 'Conda'
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
        
        # Extract requirements from text
        requirements = extract_requirements_from_description(all_text)
        
        # Extract skills
        skills = extract_skills_from_description(all_text)
        
        return {
            'success': True,
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
