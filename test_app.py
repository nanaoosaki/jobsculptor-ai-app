#!/usr/bin/env python3
"""
Test script for the Resume Tailor application
--------------------------------------------

This script tests the basic functionality of the job parser and job analyzer.
"""

import unittest
import json
import os
import hashlib
from dotenv import load_dotenv
from job_parser import parse_job_listing, extract_job_sections, extract_skills_from_description
from unittest.mock import patch, MagicMock

# Load environment variables
load_dotenv()

class TestJobParser(unittest.TestCase):
    """Test the job parser functionality"""
    
    def test_extract_sections(self):
        """Test extraction of job sections"""
        # Sample job description with sections
        job_description = """
        About the job:
        We are looking for a Python developer to join our team.
        
        Responsibilities:
        - Write clean, maintainable code
        - Participate in code reviews
        - Collaborate with other team members
        
        Requirements:
        - 3+ years of experience with Python
        - Experience with web frameworks like Flask or Django
        - Good understanding of databases
        
        Nice to have:
        - Experience with AWS
        - Knowledge of React
        """
        
        sections = extract_job_sections(job_description)
        
        # Check if sections were properly extracted
        self.assertIn('about_the_job', sections)
        self.assertIn('job_responsibilities', sections)
        self.assertIn('required_qualifications', sections)
        self.assertIn('preferred_qualifications', sections)
        
        # Check content of sections
        self.assertIn('Python developer', sections['about_the_job'])
        self.assertIn('Write clean', sections['job_responsibilities'])
        self.assertIn('3+ years', sections['required_qualifications'])
        self.assertIn('AWS', sections['preferred_qualifications'])
    
    def test_extract_skills(self):
        """Test extraction of skills from job description"""
        job_description = """
        We are looking for a developer with the following skills:
        - Python
        - Flask
        - Django
        - React
        - AWS
        - SQL
        - Git
        - Docker
        - Communication
        - Teamwork
        """
        
        skills = extract_skills_from_description(job_description)
        
        # Check if skills were properly extracted
        self.assertIn('Python', skills)
        self.assertIn('React', skills)
        self.assertIn('Communication', skills)
        
        # Check a few common technical skills
        tech_skills = ['Flask', 'Django', 'AWS', 'SQL', 'Git', 'Docker']
        for skill in tech_skills:
            self.assertIn(skill, skills)
        
        # Check a few soft skills
        soft_skills = ['Communication', 'Teamwork']
        for skill in soft_skills:
            self.assertIn(skill, skills)

class TestJobAnalyzer(unittest.TestCase):
    """Test the job analyzer functionality with mocked API calls"""
    
    @patch('llm_job_analyzer.analyze_with_claude')
    def test_analyze_job_with_mock(self, mock_analyze):
        """Test LLM job analysis with mocked API call"""
        # Import the module here to ensure the patch is applied correctly
        from llm_job_analyzer import analyze_job_with_llm
        
        # Sample job title, company, and description
        job_title = "Senior Python Developer"
        company = "Test Company"
        job_text = """
        About the job:
        We are looking for a Senior Python Developer to join our team.
        """
        
        # Create a mock response
        mock_response = {
            "candidate_profile": "Experienced Python developer with 5+ years of experience",
            "hard_skills": ["Python", "Django", "Flask", "SQL", "Git", "Docker"],
            "soft_skills": ["Communication", "Teamwork", "Problem-solving"],
            "ideal_candidate": "Someone with strong Python skills and experience with web frameworks",
            "metadata": {
                "analyzed": True,
                "provider": "claude",
                "model": "claude-3-sonnet-20240229",
                "input_tokens": 500,
                "output_tokens": 300,
                "total_tokens": 800
            }
        }
        
        # Configure the mock to return our mock response
        mock_analyze.return_value = mock_response
        
        # Create cache directory if it doesn't exist
        cache_dir = "test_job_analysis_cache"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Call the function we're testing
        analysis_results = analyze_job_with_llm(
            job_title=job_title,
            company=company,
            job_text=job_text,
            api_key="mock_api_key",
            provider="claude",
            cache_dir=cache_dir
        )
        
        # Check that our mock was called with the right arguments
        mock_analyze.assert_called_once_with(job_title, company, job_text, "mock_api_key", None)
        
        # Check if analysis results have the expected structure
        self.assertIn('candidate_profile', analysis_results)
        self.assertIn('hard_skills', analysis_results)
        self.assertIn('soft_skills', analysis_results)
        self.assertIn('ideal_candidate', analysis_results)
        
        # Check specific values from our mock response
        self.assertEqual(analysis_results['hard_skills'], 
                        ["Python", "Django", "Flask", "SQL", "Git", "Docker"])
        self.assertEqual(analysis_results['soft_skills'], 
                        ["Communication", "Teamwork", "Problem-solving"])
        
        # Test caching functionality with a second call
        mock_analyze.reset_mock()  # Reset the mock call count
        
        # Call again with the same parameters
        cached_results = analyze_job_with_llm(
            job_title=job_title,
            company=company,
            job_text=job_text,
            api_key="mock_api_key",
            provider="claude",
            cache_dir=cache_dir
        )
        
        # The mock should not have been called again since we're using the cache
        mock_analyze.assert_not_called()
        
        # Check that we got the same results
        self.assertEqual(cached_results['hard_skills'], analysis_results['hard_skills'])
        self.assertEqual(cached_results['soft_skills'], analysis_results['soft_skills'])
        
        # Clean up the cache file
        # Generate the same hash as in the get_cache_path function from llm_job_analyzer.py
        filename = hashlib.md5(f"{job_title}_{company}".encode('utf-8')).hexdigest()
        cache_path = os.path.join(cache_dir, f"{filename}_job_analysis.json")
        if os.path.exists(cache_path):
            os.remove(cache_path)

if __name__ == '__main__':
    unittest.main() 