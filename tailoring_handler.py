import os
import json
import traceback
import logging
from flask import request, jsonify, current_app
from claude_integration import tailor_resume_with_claude, generate_resume_preview

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
            
            resume_filename = data['resumeFilename']
            job_requirements = data['jobRequirements']
            
            logger.info(f"Processing resume: {resume_filename}")
            
            # Check if this is a formatted resume, if not, use the original
            if not resume_filename.endswith('_formatted.docx'):
                formatted_filename = resume_filename.replace('.docx', '_formatted.docx')
                formatted_path = os.path.join(current_app.config['UPLOAD_FOLDER'], formatted_filename)
                
                # If formatted version doesn't exist, format it now
                if not os.path.exists(formatted_path):
                    try:
                        logger.info(f"Formatting resume: {resume_filename}")
                        from resume_formatter import create_formatted_resume
                        formatted_filename = create_formatted_resume(
                            resume_filename, 
                            current_app.config['UPLOAD_FOLDER']
                        )
                        formatted_path = os.path.join(current_app.config['UPLOAD_FOLDER'], formatted_filename)
                        logger.info(f"Resume formatted successfully: {formatted_filename}")
                    except Exception as e:
                        logger.error(f"Error formatting resume: {str(e)}")
                        return jsonify({
                            'success': False, 
                            'error': f'Error formatting resume: {str(e)}'
                        }), 400
                    
                resume_filename = formatted_filename
            
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
            
            # Get Claude API key from config
            api_key = current_app.config.get('CLAUDE_API_KEY', 'demo-api-key')
            api_url = current_app.config.get('CLAUDE_API_URL', 'https://api.anthropic.com/v1/messages')
            
            # Check if using demo key and provide appropriate response
            if api_key == 'demo-api-key' or not api_key:
                logger.info("Using demo mode (no API key)")
                try:
                    # Generate a mock preview without actually calling Claude API
                    from docx import Document
                    doc = Document(resume_path)
                    preview_html = generate_resume_preview(resume_path)
                    
                    # Create a copy of the formatted resume as the "tailored" version
                    import shutil
                    tailored_filename = resume_filename.replace('_formatted.docx', '_tailored.docx')
                    tailored_path = os.path.join(current_app.config['UPLOAD_FOLDER'], tailored_filename)
                    shutil.copy2(resume_path, tailored_path)
                    
                    logger.info(f"Demo mode: Created tailored resume at {tailored_path}")
                    
                    response_data = {
                        'success': True,
                        'filename': tailored_filename,
                        'preview': preview_html,
                        'message': 'Demo mode: Resume copied without actual tailoring. To enable real tailoring, please add a Claude API key to the .env file.'
                    }
                    
                    logger.info("Demo mode: Returning success response")
                    return jsonify(response_data), 200
                    
                except Exception as e:
                    logger.error(f"Error in demo mode: {str(e)}")
                    logger.error(traceback.format_exc())
                    return jsonify({
                        'success': False,
                        'error': f'Error in demo mode: {str(e)}'
                    }), 500
            
            # Tailor the resume with actual API key
            logger.info("Using Claude API for tailoring")
            try:
                tailored_filename, tailored_path = tailor_resume_with_claude(
                    resume_path,
                    job_data,
                    api_key,
                    api_url
                )
                
                # Generate HTML preview
                preview_html = generate_resume_preview(tailored_path)
                
                logger.info(f"Resume tailored successfully: {tailored_filename}")
                
                return jsonify({
                    'success': True,
                    'filename': tailored_filename,
                    'preview': preview_html,
                    'message': 'Resume tailored successfully'
                }), 200
            except Exception as e:
                logger.error(f"Error tailoring resume with Claude API: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({
                    'success': False,
                    'error': f'Error tailoring resume with Claude API: {str(e)}'
                }), 500
                
        except Exception as e:
            # Catch-all for any unexpected errors
            logger.error(f"Unexpected error in tailor_resume: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }), 500
