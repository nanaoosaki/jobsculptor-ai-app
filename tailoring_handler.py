import os
import json
import traceback
import logging
import uuid
from flask import request, jsonify, current_app
from claude_integration import tailor_resume_with_llm, generate_resume_preview, generate_preview_from_llm_responses
from pdf_exporter import create_pdf_from_html
from dotenv import load_dotenv
from resume_index import get_resume_index

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_tailoring_routes(app):
    """Set up routes for resume tailoring with Claude API"""
    
    @app.route('/tailor-resume', methods=['POST'])
    def tailor_resume():
        """Handle resume tailoring request"""
        try:
            # Log the start of the request
            logger.info("Received tailor-resume request")
            
            # Generate a unique request ID for this tailoring operation
            request_id = str(uuid.uuid4())
            logger.info(f"Generated unique request_id: {request_id}")
            
            # Safely parse JSON data
            try:
                data = request.get_json()
                logger.info(f"Request data: {data}")
            except Exception as e:
                logger.error(f"Error parsing JSON: {str(e)}")
                return jsonify({'success': False, 'error': 'Invalid JSON data'}), 400
            
            # Validate required fields
            if not data or 'resumeFilename' not in data:
                logger.error("Missing resumeFilename in request data")
                return jsonify({'success': False, 'error': 'Missing resume filename'}), 400
                
            if 'jobRequirements' not in data:
                logger.error("Missing jobRequirements in request data")
                return jsonify({'success': False, 'error': 'Missing job requirements'}), 400
            
            # Get LLM provider preference (default to openai)
            provider = data.get('llmProvider', 'openai').lower()
            logger.info(f"Using LLM provider: {provider}")
            
            resume_filename = data['resumeFilename']
            job_requirements = data['jobRequirements']
            
            logger.info(f"Processing resume: {resume_filename}")
            
            # Check if this is a formatted resume, if not, use the original
            if not resume_filename.endswith('_formatted.docx'):
                # We no longer need to format the resume since we're using 
                # YC-Eddie style directly without templates
                resume_path = os.path.join(current_app.config['UPLOAD_FOLDER'], resume_filename)
            else:
                resume_path = os.path.join(current_app.config['UPLOAD_FOLDER'], resume_filename)
            
            # Verify the resume file exists
            if not os.path.exists(resume_path):
                logger.error(f"Resume file not found: {resume_path}")
                return jsonify({
                    'success': False, 
                    'error': 'Resume file not found'
                }), 404
            
            # Process job data
            job_data = {}
            if isinstance(job_requirements, dict):
                # If it's already a complete job data object
                job_data = job_requirements
                logger.info("Using complete job data object")
                
                # Check for analysis data
                if 'analysis' in job_data:
                    logger.info("Job analysis data found and will be used for tailoring")
                    
                    # Log some info about the analysis for debugging
                    if isinstance(job_data['analysis'], dict):
                        analysis_keys = job_data['analysis'].keys()
                        logger.info(f"Analysis data contains the following keys: {', '.join(analysis_keys)}")
                        
                        # Log candidate profile length if available
                        if 'candidate_profile' in job_data['analysis']:
                            profile_len = len(job_data['analysis']['candidate_profile'])
                            logger.info(f"Candidate profile length: {profile_len} chars")
                        
                        # Log skills count if available
                        if 'hard_skills' in job_data['analysis']:
                            hard_skills_count = len(job_data['analysis']['hard_skills'])
                            logger.info(f"Hard skills count: {hard_skills_count}")
                        
                        if 'soft_skills' in job_data['analysis']:
                            soft_skills_count = len(job_data['analysis']['soft_skills'])
                            logger.info(f"Soft skills count: {soft_skills_count}")
                
            elif isinstance(job_requirements, list):
                # If it's just a list of requirements
                job_data = {'requirements': job_requirements, 'skills': []}
                logger.info("Created job data from requirements list")
            else:
                # If it's something else, try to extract requirements
                try:
                    if hasattr(job_requirements, 'requirements'):
                        job_data = {'requirements': job_requirements.requirements, 'skills': []}
                    else:
                        job_data = {'requirements': [str(job_requirements)], 'skills': []}
                    logger.info("Created job data from alternative format")
                except Exception as e:
                    logger.error(f"Error processing job requirements: {str(e)}")
                    job_data = {'requirements': ['No specific requirements found'], 'skills': []}
            
            # Get API key based on provider
            api_key = None
            api_url = None
            
            # Handle 'auto' provider by checking available API keys
            if provider == 'auto':
                logger.info("Auto provider selected - checking available API keys")
                
                # Reload .env file to ensure latest values
                load_dotenv(override=True)
                
                # First try Claude
                claude_api_key = current_app.config.get('CLAUDE_API_KEY') or os.environ.get('CLAUDE_API_KEY')
                
                # Then try OpenAI
                openai_api_key = current_app.config.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')
                
                if claude_api_key and claude_api_key.startswith('sk-ant'):
                    provider = 'claude'
                    api_key = claude_api_key
                    api_url = current_app.config.get('CLAUDE_API_URL', 'https://api.anthropic.com/v1/messages')
                    logger.info("Auto-selected Claude API based on available keys")
                elif openai_api_key and openai_api_key.startswith('sk-'):
                    provider = 'openai'
                    api_key = openai_api_key
                    logger.info("Auto-selected OpenAI API based on available keys")
                else:
                    logger.error("No valid API keys found for auto provider selection")
                    return jsonify({
                        'success': False,
                        'error': 'No valid API keys found. Please add either a Claude or OpenAI API key to the .env file.'
                    }), 400
            
            elif provider == 'claude':
                api_key = current_app.config.get('CLAUDE_API_KEY')
                api_url = current_app.config.get('CLAUDE_API_URL', 'https://api.anthropic.com/v1/messages')
                
                # Fallback to environment variable if not in config
                if not api_key:
                    # Reload .env file to ensure latest values
                    load_dotenv(override=True)
                    api_key = os.environ.get('CLAUDE_API_KEY')
                    
                # Validate Claude API key
                if not api_key or not api_key.startswith('sk-ant'):
                    logger.error("No valid Claude API key found - cannot use Claude")
                    return jsonify({
                        'success': False,
                        'error': 'No valid Claude API key found. Please add a Claude API key to the .env file or switch to OpenAI.'
                    }), 400
                
                logger.info(f"Using Claude API with key starting with: {api_key[:8]}...")
                
            elif provider == 'openai':
                api_key = current_app.config.get('OPENAI_API_KEY')
                
                # Fallback to environment variable if not in config
                if not api_key:
                    # Reload .env file to ensure latest values
                    load_dotenv(override=True)
                    api_key = os.environ.get('OPENAI_API_KEY')
                
                # Validate OpenAI API key
                if not api_key or not api_key.startswith('sk-'):
                    logger.error("No valid OpenAI API key found - cannot use OpenAI")
                    return jsonify({
                        'success': False,
                        'error': 'No valid OpenAI API key found. Please add an OpenAI API key to the .env file or switch to Claude.'
                    }), 400
                    
                logger.info(f"Using OpenAI API with key starting with: {api_key[:8]}...")
                
            else:
                logger.error(f"Unsupported LLM provider: {provider}")
                return jsonify({
                    'success': False,
                    'error': f'Unsupported LLM provider: {provider}. Please use "claude", "openai", or "auto".'
                }), 400
            
            # Tailor the resume with the selected provider
            logger.info(f"Using {provider.upper()} API for tailoring")
            try:
                # Get tailored content from LLM
                # tailor_resume_with_llm returns: output_filename, output_path, llm_client
                # - output_filename: The filename of the generated file (e.g., "resume_tailored_openai.pdf")
                # - output_path: The full path to the generated file
                # - llm_client: The LLM client instance used for tailoring
                tailored_sections, llm_client = tailor_resume_with_llm(
                    resume_path,
                    job_data,
                    api_key,
                    provider,
                    api_url,
                    request_id
                )
                
                # Get upload folder path from current app context
                upload_folder = current_app.config['UPLOAD_FOLDER']
                
                # Generate HTML preview for the screen
                preview_html_for_screen = generate_preview_from_llm_responses(request_id, upload_folder, for_screen=True)
                
                # Generate clean HTML body content for PDF export
                html_body_for_pdf = generate_preview_from_llm_responses(request_id, upload_folder, for_screen=False)
                
                # Extract only the content within the <body> tags for PDF generation
                # This is a simple regex approach, might need refinement
                import re
                body_match = re.search(r'<body.*?>(.*?)</body>', html_body_for_pdf, re.DOTALL | re.IGNORECASE)
                if body_match:
                    clean_html_body = body_match.group(1).strip()
                    # Further clean by removing the outer container if it exists
                    # clean_html_body = re.sub(r'^<div class="resume-preview-container">(.*)</div>$', r'\1', clean_html_body, flags=re.DOTALL).strip()
                else:
                    logger.warning("Could not extract body content for PDF generation. Using full HTML.")
                    clean_html_body = html_body_for_pdf # Fallback, might cause issues

                
                # Get original filename without extension
                filename_base = os.path.splitext(os.path.basename(resume_path))[0]
                
                # Create PDF output path
                pdf_output_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'], 
                    f"{filename_base}_tailored_{provider}.pdf"
                )
                
                # Skip PDF generation - just return preview with DOCX download option
                logger.info(f"Resume tailored successfully with {provider} - PDF generation disabled")
                
                # Get resume ID from filename
                resume_id = os.path.splitext(os.path.basename(resume_path))[0]
                
                # Log in resume index system
                try:
                    resume_index = get_resume_index()
                    resume_index.add_resume(resume_id, os.path.basename(resume_path))
                    
                    # If we get to this point, update the index with job details
                    job_title = job_data.get('job_title', 'Unknown Position')
                    company = job_data.get('company', 'Unknown Company')
                    resume_index.add_note(resume_id, f"Processing for job: {job_title} at {company}")
                    
                except Exception as e:
                    logger.warning(f"Error updating resume index: {e}")
                
                return jsonify({
                    'success': True,
                    'filename': None,  # No PDF file generated
                    'preview': preview_html_for_screen, # Return the version for the screen
                    'request_id': request_id,
                    'provider': provider,
                    'fileType': 'html',  # Indicate this is HTML preview only
                    'message': f'Resume tailored successfully using {provider.upper()}. Use "Generate DOCX" to download.'
                }), 200
                    
            except Exception as e:
                logger.error(f"Error tailoring resume with {provider.upper()} API: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Log API Key info (first few chars only for security)
                if api_key:
                    logger.error(f"API Key prefix: {api_key[:8]}... (length: {len(api_key)})")
                
                # Create a more descriptive error message for the frontend
                error_message = str(e)
                if "401" in error_message:
                    error_message = "Authentication failed - invalid API key. Please check your API key in the .env file."
                elif "429" in error_message:
                    error_message = "Rate limit exceeded. Please try again in a few minutes."
                elif "500" in error_message:
                    error_message = "API server error. Please try again later."
                elif "timeout" in error_message.lower():
                    error_message = "API request timed out. Please try again."
                elif "network" in error_message.lower():
                    error_message = "Network error connecting to API. Please check your internet connection."
                
                return jsonify({
                    'success': False,
                    'error': f'{provider.upper()} API Error: {error_message}'
                }), 500
                
        except Exception as e:
            # Catch-all for any unexpected errors
            logger.error(f"Unexpected error in tailor_resume: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }), 500
