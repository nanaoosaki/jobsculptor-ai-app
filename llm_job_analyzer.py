#!/usr/bin/env python3
"""
LLM-based job posting analyzer
------------------------------

This module provides functions to analyze job postings using LLMs (either Claude or OpenAI).
The analysis includes:
- Candidate profile
- Hard skills required
- Soft skills required
- Ideal candidate description

Results are cached to avoid repeated API calls for the same job posting.
"""

import os
import json
import logging
import hashlib
import time
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import the necessary packages
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    logger.warning("Anthropic package not available. Claude API will not be usable.")
    CLAUDE_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI package not available. OpenAI API will not be usable.")
    OPENAI_AVAILABLE = False

# Default prompt template for job analysis
JOB_ANALYSIS_PROMPT_TEMPLATE = """
You are an expert job market analyst and career advisor. I'll share a job description, and I need you to analyze it thoroughly to help job seekers understand what the employer is looking for.

JOB TITLE: {job_title}
COMPANY: {company}

JOB DESCRIPTION:
{job_text}

Please analyze this job description and provide the following information in a structured JSON format:

1. Candidate Profile: Summarize what type of candidate the employer is looking for (experience level, background, role focus)
2. Hard Skills: List the specific technical skills, tools, platforms, languages, or certifications required
3. Soft Skills: List the interpersonal, communication, and character traits they're seeking
4. Ideal Candidate: Describe what the perfect candidate for this role would look like

Return your answer in the following JSON format:
{{
    "candidate_profile": "Detailed description of the type of candidate they're looking for",
    "hard_skills": ["skill1", "skill2", "skill3", ...],
    "soft_skills": ["skill1", "skill2", "skill3", ...],
    "ideal_candidate": "Description of the ideal candidate for this position"
}}
"""

def get_cache_path(job_title: str, company: str, cache_dir: str) -> str:
    """Generate a cache file path based on job title and company."""
    # Create a hash of the job title and company for the filename
    filename = hashlib.md5(f"{job_title}_{company}".encode('utf-8')).hexdigest()
    return os.path.join(cache_dir, f"{filename}_job_analysis.json")

def cache_results(job_title: str, company: str, results: Dict[str, Any], cache_dir: str) -> None:
    """Cache the analysis results to a file."""
    try:
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
        
        # Get cache file path
        cache_path = get_cache_path(job_title, company, cache_dir)
        
        # Add metadata
        results.setdefault("metadata", {})
        results["metadata"]["cached_at"] = time.time()
        results["metadata"]["job_title"] = job_title
        results["metadata"]["company"] = company
        
        # Write to cache file
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Job analysis results cached at {cache_path}")
    except Exception as e:
        logger.error(f"Error caching job analysis results: {str(e)}")

def get_cached_results(job_title: str, company: str, cache_dir: str) -> Optional[Dict[str, Any]]:
    """Get cached analysis results if available."""
    try:
        cache_path = get_cache_path(job_title, company, cache_dir)
        
        # Check if cache file exists
        if not os.path.exists(cache_path):
            return None
        
        # Read from cache file
        with open(cache_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
            
        logger.info(f"Found cached job analysis results for {job_title} at {company}")
        
        # Add metadata about cache retrieval
        results.setdefault("metadata", {})
        results["metadata"]["retrieved_from_cache"] = True
        results["metadata"]["cache_path"] = cache_path
        
        return results
    except Exception as e:
        logger.error(f"Error retrieving cached job analysis results: {str(e)}")
        return None

def analyze_with_claude(job_title: str, company: str, job_text: str, api_key: str, api_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a job posting using Claude API.
    
    Args:
        job_title: The title of the job
        company: The company offering the job
        job_text: The complete text of the job posting
        api_key: The Claude API key
        api_url: Optional Claude API URL
    
    Returns:
        A dictionary containing the analysis results
    """
    if not CLAUDE_AVAILABLE:
        return {
            "error": "Anthropic package not available. Please install it with 'pip install anthropic'."
        }
    
    try:
        # Initialize Claude client
        client = anthropic.Anthropic(api_key=api_key)
        
        # Prepare the prompt
        prompt = JOB_ANALYSIS_PROMPT_TEMPLATE.format(
            job_title=job_title,
            company=company,
            job_text=job_text
        )
        
        logger.info(f"Sending job analysis request to Claude API for {job_title} at {company}")
        
        # Call Claude API
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=0.1,
            system="You are an expert job market analyst and career advisor. Your task is to analyze job descriptions and extract structured information to help job seekers understand what employers are looking for.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Log token usage
        logger.info(f"Claude API response received. Input tokens: {response.usage.input_tokens}, output tokens: {response.usage.output_tokens}")
        
        # Parse the JSON response
        try:
            content = response.content[0].text
            # Extract just the JSON part (in case there's any additional text)
            if '{' in content and '}' in content:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_content = content[json_start:json_end]
                analysis_results = json.loads(json_content)
            else:
                analysis_results = json.loads(content)
                
            # Add metadata
            analysis_results["metadata"] = {
                "analyzed": True,
                "provider": "claude",
                "model": "claude-3-sonnet-20240229",
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
            
            # Validate the response structure
            expected_keys = ["candidate_profile", "hard_skills", "soft_skills", "ideal_candidate"]
            missing_keys = [key for key in expected_keys if key not in analysis_results]
            
            if missing_keys:
                logger.warning(f"Claude response missing expected keys: {missing_keys}")
                # Add any missing keys with empty values
                for key in missing_keys:
                    if key in ["hard_skills", "soft_skills"]:
                        analysis_results[key] = []
                    else:
                        analysis_results[key] = ""
            
            return analysis_results
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Claude response as JSON: {str(e)}")
            logger.error(f"Raw response: {response.content[0].text}")
            return {
                "error": f"Failed to parse Claude response as JSON: {str(e)}",
                "raw_response": response.content[0].text,
                "metadata": {
                    "analyzed": False,
                    "provider": "claude",
                    "model": "claude-3-sonnet-20240229"
                }
            }
            
    except Exception as e:
        logger.error(f"Error calling Claude API: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "error": f"Failed to analyze job with Claude: {str(e)}",
            "metadata": {
                "analyzed": False,
                "provider": "claude"
            }
        }

def analyze_with_openai(job_title: str, company: str, job_text: str, api_key: str) -> Dict[str, Any]:
    """
    Analyze a job posting using OpenAI API.
    
    Args:
        job_title: The title of the job
        company: The company offering the job
        job_text: The complete text of the job posting
        api_key: The OpenAI API key
    
    Returns:
        A dictionary containing the analysis results
    """
    if not OPENAI_AVAILABLE:
        return {
            "error": "OpenAI package not available. Please install it with 'pip install openai'."
        }
    
    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Prepare the prompt
        prompt = JOB_ANALYSIS_PROMPT_TEMPLATE.format(
            job_title=job_title,
            company=company,
            job_text=job_text
        )
        
        logger.info(f"Sending job analysis request to OpenAI API for {job_title} at {company}")
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are an expert job market analyst and career advisor. Your task is to analyze job descriptions and extract structured information to help job seekers understand what employers are looking for."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Log token usage
        logger.info(f"OpenAI API response received. Input tokens: {response.usage.prompt_tokens}, output tokens: {response.usage.completion_tokens}")
        
        # Parse the JSON response
        try:
            content = response.choices[0].message.content
            # Extract just the JSON part (in case there's any additional text)
            if '{' in content and '}' in content:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_content = content[json_start:json_end]
                analysis_results = json.loads(json_content)
            else:
                analysis_results = json.loads(content)
                
            # Add metadata
            analysis_results["metadata"] = {
                "analyzed": True,
                "provider": "openai",
                "model": "gpt-4o",
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.prompt_tokens + response.usage.completion_tokens
            }
            
            # Validate the response structure
            expected_keys = ["candidate_profile", "hard_skills", "soft_skills", "ideal_candidate"]
            missing_keys = [key for key in expected_keys if key not in analysis_results]
            
            if missing_keys:
                logger.warning(f"OpenAI response missing expected keys: {missing_keys}")
                # Add any missing keys with empty values
                for key in missing_keys:
                    if key in ["hard_skills", "soft_skills"]:
                        analysis_results[key] = []
                    else:
                        analysis_results[key] = ""
            
            return analysis_results
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing OpenAI response as JSON: {str(e)}")
            logger.error(f"Raw response: {content}")
            return {
                "error": f"Failed to parse OpenAI response as JSON: {str(e)}",
                "raw_response": content,
                "metadata": {
                    "analyzed": False,
                    "provider": "openai",
                    "model": "gpt-4o"
                }
            }
            
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "error": f"Failed to analyze job with OpenAI: {str(e)}",
            "metadata": {
                "analyzed": False,
                "provider": "openai"
            }
        }

def analyze_job_with_llm(job_title: str, company: str, job_text: str, api_key: str, provider: str = "openai", api_url: str = None, cache_dir: str = "job_analysis_cache") -> Dict[str, Any]:
    """
    Analyze a job posting with the specified LLM provider.
    
    Args:
        job_title: The title of the job
        company: The company offering the job
        job_text: The complete text of the job posting
        api_key: The API key for the LLM provider
        provider: The LLM provider to use ('claude', 'openai', or 'auto')
        api_url: Optional API URL for Claude
        cache_dir: Directory to cache results
    
    Returns:
        A dictionary containing the analysis results
    """
    # Check for cached results first
    cached_results = get_cached_results(job_title, company, cache_dir)
    if cached_results:
        return cached_results
    
    # Determine which provider to use
    if provider == "auto":
        # Try OpenAI first, fall back to Claude
        if OPENAI_AVAILABLE and api_key:
            provider = "openai"
            logger.info("Auto provider selected - using OpenAI")
        elif CLAUDE_AVAILABLE and api_key:
            provider = "claude"
            logger.info("Auto provider selected - using Claude (OpenAI not available)")
        else:
            return {
                "error": "No available LLM providers found. Please install 'anthropic' or 'openai' packages.",
                "metadata": {
                    "analyzed": False,
                    "reason": "No available providers"
                }
            }
    
    # Call the appropriate provider
    if provider == "openai":
        if not OPENAI_AVAILABLE:
            return {
                "error": "OpenAI API not available. Please install the 'openai' package.",
                "metadata": {
                    "analyzed": False,
                    "provider": "openai",
                    "reason": "Package not installed"
                }
            }
        results = analyze_with_openai(job_title, company, job_text, api_key)
    elif provider == "claude":
        if not CLAUDE_AVAILABLE:
            return {
                "error": "Claude API not available. Please install the 'anthropic' package.",
                "metadata": {
                    "analyzed": False,
                    "provider": "claude",
                    "reason": "Package not installed"
                }
            }
        results = analyze_with_claude(job_title, company, job_text, api_key, api_url)
    else:
        return {
            "error": f"Unknown provider: {provider}. Use 'claude', 'openai', or 'auto'.",
            "metadata": {
                "analyzed": False,
                "reason": "Invalid provider"
            }
        }
    
    # If analysis was successful, cache the results
    if "error" not in results:
        cache_results(job_title, company, results, cache_dir)
    
    return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze a job posting with LLM")
    parser.add_argument("--job-title", required=True, help="Job title")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--job-text-file", required=True, help="Path to a file containing the job description text")
    parser.add_argument("--api-key", required=True, help="API key for the LLM provider")
    parser.add_argument("--provider", choices=["claude", "openai", "auto"], default="auto", help="LLM provider to use")
    parser.add_argument("--api-url", help="API URL for Claude (optional)")
    parser.add_argument("--cache-dir", default="job_analysis_cache", help="Directory to store cached results")
    parser.add_argument("--output-file", help="Path to write the analysis results to (JSON format)")
    
    args = parser.parse_args()
    
    # Read job text from file
    with open(args.job_text_file, 'r', encoding='utf-8') as f:
        job_text = f.read()
    
    # Analyze the job
    results = analyze_job_with_llm(
        job_title=args.job_title,
        company=args.company,
        job_text=job_text,
        api_key=args.api_key,
        provider=args.provider,
        api_url=args.api_url,
        cache_dir=args.cache_dir
    )
    
    # Write results to output file if specified
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
    else:
        # Print results to stdout
        print(json.dumps(results, indent=2)) 