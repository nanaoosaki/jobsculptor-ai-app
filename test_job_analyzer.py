#!/usr/bin/env python3
"""
Test script for LLM job analyzer
-------------------------------

This script tests the job analyzer functionality directly.
It parses a job URL and then analyzes the job description using the LLM job analyzer.
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv
from job_parser import parse_job_listing
from llm_job_analyzer import analyze_job_with_llm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def test_job_analyzer(job_url, provider="auto", output_file=None):
    """
    Test the job analyzer by parsing a job URL and analyzing the job description.
    
    Args:
        job_url: The URL of the job posting to analyze
        provider: The LLM provider to use ('claude', 'openai', or 'auto')
        output_file: Path to write the analysis results to (JSON format)
    """
    logger.info(f"Testing job analyzer with URL: {job_url}")
    
    # Get API keys from environment
    claude_api_key = os.environ.get('CLAUDE_API_KEY')
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    
    # Parse the job listing
    logger.info("Parsing job listing...")
    parse_result = parse_job_listing(job_url)
    
    if not parse_result['success']:
        logger.error(f"Failed to parse job listing: {parse_result.get('error')}")
        return
    
    logger.info(f"Successfully parsed job listing: {parse_result['job_title']} at {parse_result['company']}")
    
    # Determine which API key to use based on provider
    api_key = None
    if provider == "claude" or (provider == "auto" and claude_api_key):
        api_key = claude_api_key
        logger.info("Using Claude API for job analysis")
    elif provider == "openai" or (provider == "auto" and openai_api_key):
        api_key = openai_api_key
        logger.info("Using OpenAI API for job analysis")
    else:
        logger.error(f"No API key available for provider: {provider}")
        return
    
    # Create cache directory if it doesn't exist
    cache_dir = "job_analysis_cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    # Analyze the job posting
    logger.info("Analyzing job posting with LLM...")
    job_title = parse_result['job_title']
    company = parse_result['company']
    job_text = parse_result['complete_job_text']
    
    analysis_results = analyze_job_with_llm(
        job_title=job_title,
        company=company,
        job_text=job_text,
        api_key=api_key,
        provider=provider,
        cache_dir=cache_dir
    )
    
    if "error" in analysis_results:
        logger.error(f"Failed to analyze job posting: {analysis_results['error']}")
        return
    
    # Print analysis results
    logger.info("Job analysis results:")
    logger.info(f"Candidate Profile: {analysis_results['candidate_profile'][:100]}...")
    logger.info(f"Hard Skills: {', '.join(analysis_results['hard_skills'][:5])}...")
    logger.info(f"Soft Skills: {', '.join(analysis_results['soft_skills'][:5])}...")
    logger.info(f"Ideal Candidate: {analysis_results['ideal_candidate'][:100]}...")
    
    # Write results to file if requested
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Combine parse results and analysis results
            combined_results = {
                "job_title": job_title,
                "company": company,
                "job_url": job_url,
                "analysis": analysis_results,
                "parse_results": {
                    "requirements": parse_result.get('requirements', []),
                    "skills": parse_result.get('skills', []),
                    "sections": parse_result.get('sections', {})
                }
            }
            json.dump(combined_results, f, indent=2)
        logger.info(f"Results written to {output_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the LLM job analyzer")
    parser.add_argument("job_url", help="The URL of the job posting to analyze")
    parser.add_argument("--provider", choices=["claude", "openai", "auto"], default="auto", help="LLM provider to use")
    parser.add_argument("--output-file", help="Path to write the analysis results to (JSON format)")
    
    args = parser.parse_args()
    
    test_job_analyzer(args.job_url, args.provider, args.output_file) 