import os
from flask import request, jsonify, render_template
import json
from job_parser import parse_job_listing

# Try to import the job analyzer
try:
    from llm_job_analyzer import analyze_job_with_llm
    LLM_JOB_ANALYZER_AVAILABLE = True
except ImportError:
    print("Warning: LLM job analyzer not found. Job analysis will be limited.")
    LLM_JOB_ANALYZER_AVAILABLE = False

def setup_job_parser_routes(app):
    """Set up routes for job listing parsing"""
    
    @app.route('/parse-job', methods=['POST'])
    def parse_job():
        """Handle job listing parsing request"""
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'No job URL provided'}), 400
        
        job_url = data['url']
        
        try:
            # Parse the job listing
            result = parse_job_listing(job_url)
            
            if result['success']:
                # Save the parsed job data to a file for later use
                job_data_filename = f"job_data_{os.path.basename(job_url).replace('.', '_')}.json"
                job_data_filepath = os.path.join(app.config['UPLOAD_FOLDER'], job_data_filename)
                
                with open(job_data_filepath, 'w') as f:
                    json.dump(result, f, indent=2)
                
                # Create standardized response data
                response_data = {
                    'success': True,
                    'job_title': result.get('job_title', 'Unknown Position'),
                    'company': result.get('company', 'Unknown Company'),
                    'requirements': result.get('requirements', []),
                    'skills': result.get('skills', []),
                    # Include the complete job text for LLM processing
                    'complete_job_text': result.get('complete_job_text', '')
                }
                
                # Add sections if available
                if 'sections' in result:
                    # Map section keys to standard format for frontend
                    section_mapping = {
                        # Map from new standardized keys to structure expected by frontend
                        'about_the_job': 'about_the_job',
                        'about_team': 'about_team',
                        'about_us': 'about_us',
                        'job_responsibilities': 'job_responsibilities',
                        'required_qualifications': 'required_qualifications',
                        'preferred_qualifications': 'preferred_qualifications',
                        'tech_stack': 'tech_stack',
                        'benefits': 'benefits',
                        'ideal_candidate': 'ideal_candidate',
                        'application_process': 'application_process',
                        'diversity': 'diversity',
                        'full_description': 'full_description'
                    }
                    
                    # Create sections object for response
                    response_data['sections'] = {}
                    
                    # Add all sections to response with standardized keys
                    for orig_key, content in result['sections'].items():
                        # Use the mapped key if available, otherwise use original
                        if orig_key in section_mapping:
                            mapped_key = section_mapping[orig_key]
                        else:
                            mapped_key = orig_key
                            
                        response_data['sections'][mapped_key] = content
                    
                    # Extract specific sections for convenient access in frontend
                    # About the job section
                    if 'about_the_job' in result['sections']:
                        response_data['about_the_job'] = result['sections']['about_the_job']
                    
                    # Job responsibilities section
                    if 'job_responsibilities' in result['sections']:
                        response_data['job_responsibilities'] = result['sections']['job_responsibilities']
                    
                    # Required qualifications section
                    if 'required_qualifications' in result['sections']:
                        response_data['required_qualifications'] = result['sections']['required_qualifications']
                        
                        # If requirements list is empty but we have required_qualifications, parse it
                        if not response_data['requirements'] and result['sections']['required_qualifications']:
                            # Try to extract bullet points from the section
                            import re
                            bullet_items = re.findall(r'[•■◦⦿⚫⚪○●★☆▪▫-]\s*(.*?)(?=\n[•■◦⦿⚫⚪○●★☆▪▫-]|\n\n|\Z)', 
                                                     result['sections']['required_qualifications'], re.DOTALL)
                            if bullet_items:
                                response_data['requirements'] = [item.strip() for item in bullet_items if item.strip()]
                    
                    # Preferred qualifications section
                    if 'preferred_qualifications' in result['sections']:
                        response_data['preferred_qualifications'] = result['sections']['preferred_qualifications']
                
                return jsonify(response_data), 200
            else:
                return jsonify({'error': result.get('error', 'Failed to parse job listing')}), 500
                
        except Exception as e:
            return jsonify({'error': f'Error parsing job listing: {str(e)}'}), 500
    
    @app.route('/job-analyzer')
    def job_analyzer_page():
        """Render the job analyzer page"""
        return render_template('analyze_job.html')
    
    @app.route('/api/analyze-job', methods=['POST'])
    def analyze_job_api():
        """API endpoint for job analysis with LLM"""
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'No job URL provided'}), 400
        
        job_url = data['url']
        # Default to OpenAI instead of auto
        provider = data.get('provider', 'openai')
        
        try:
            # Parse the job listing first
            parse_result = parse_job_listing(job_url)
            
            if not parse_result['success']:
                return jsonify({'error': parse_result.get('error', 'Failed to parse job listing')}), 500
            
            # Basic response with parsing results
            response_data = {
                'success': True,
                'job_title': parse_result.get('job_title', 'Unknown Position'),
                'company': parse_result.get('company', 'Unknown Company'),
                'requirements': parse_result.get('requirements', []),
                'skills': parse_result.get('skills', []),
                'sections': parse_result.get('sections', {})
            }
            
            # Include LLM analysis if available
            if LLM_JOB_ANALYZER_AVAILABLE:
                # Use OpenAI API key directly
                api_key = app.config.get('OPENAI_API_KEY')
                
                if not api_key:
                    return jsonify({'error': 'OpenAI API key not configured'}), 500
                
                # Analyze the job posting with LLM
                job_text = parse_result.get('complete_job_text', '')
                job_title = parse_result.get('job_title', 'Unknown Position')
                company = parse_result.get('company', 'Unknown Company')
                
                # Create cache directory if it doesn't exist
                cache_dir = app.config.get('JOB_ANALYSIS_CACHE_DIR', os.path.join(app.config['UPLOAD_FOLDER'], 'job_analysis_cache'))
                os.makedirs(cache_dir, exist_ok=True)
                
                analysis_results = analyze_job_with_llm(
                    job_title=job_title,
                    company=company,
                    job_text=job_text,
                    api_key=api_key,
                    provider='openai',  # Explicitly use OpenAI
                    cache_dir=cache_dir
                )
                
                # Add analysis results to response
                response_data['analysis'] = analysis_results
                response_data['analysis_provider'] = 'openai'
            else:
                # If LLM analysis is not available, create basic analysis from parsed data
                response_data['analysis'] = {
                    'candidate_profile': 'LLM analysis not available',
                    'hard_skills': parse_result.get('skills', []),
                    'soft_skills': [],
                    'ideal_candidate': 'LLM analysis not available',
                    'metadata': {
                        'analyzed': False,
                        'reason': 'LLM job analyzer not available'
                    }
                }
                response_data['analysis_provider'] = 'none'
            
            return jsonify(response_data), 200
                
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return jsonify({'error': f'Error analyzing job: {str(e)}'}), 500
