import os
import json
import logging
from flask import request, jsonify
from werkzeug.utils import secure_filename
from resume_processor import create_upload_directory, save_uploaded_file, analyze_resume, generate_resume_preview_html

# Configure logging
logger = logging.getLogger(__name__)

def setup_upload_routes(app):
    """Set up routes for resume upload and processing"""
    
    # Ensure upload directory exists
    create_upload_directory(app.config['UPLOAD_FOLDER'])
    
    @app.route('/upload-resume', methods=['POST'])
    def upload_resume():
        """Handle resume file upload"""
        if 'resume' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and file.filename.lower().endswith('.docx'):
            try:
                # Save the uploaded file
                filename, filepath = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
                
                # First try to use LLM parsing if available
                llm_sections = {}
                llm_parsed = False
                
                try:
                    # Import the LLM resume parser
                    from config import Config
                    from llm_resume_parser import parse_resume_with_llm
                    
                    # Check if LLM parsing is enabled
                    use_llm_parsing = Config.USE_LLM_RESUME_PARSING
                    
                    if use_llm_parsing:
                        logger.info(f"Attempting to parse resume with LLM during initial upload: {filename}")
                        
                        # Determine which LLM provider to use based on available API keys
                        llm_provider = Config.LLM_RESUME_PARSER_PROVIDER
                        if llm_provider == "auto":
                            if os.environ.get("OPENAI_API_KEY"):
                                llm_provider = "openai"
                            elif os.environ.get("CLAUDE_API_KEY"):
                                llm_provider = "claude"
                            else:
                                logger.warning("No LLM API keys found for resume parsing. Will use traditional parsing.")
                                raise ImportError("No LLM API keys available")
                                
                        # Try to parse with LLM
                        llm_sections = parse_resume_with_llm(filepath, llm_provider)
                        
                        # Check if LLM parsing was successful
                        if llm_sections and any(content for content in llm_sections.values()):
                            logger.info("LLM parsing successful during initial upload.")
                            llm_parsed = True
                            
                            # Convert LLM sections to the format expected by the frontend
                            formatted_sections = {}
                            for section_name, content in llm_sections.items():
                                if content:  # Only include non-empty sections
                                    # Map from Claude sections to UI sections
                                    if section_name == "contact":
                                        formatted_sections["contact_info"] = content
                                    elif section_name in ["summary", "experience", "education", "skills", "projects"]:
                                        formatted_sections[section_name] = content
                                    else:
                                        formatted_sections["other"] = content
                            
                            # Generate basic analysis data from LLM sections
                            analysis = {
                                'analysis': {
                                    'has_contact_info': bool(llm_sections.get('contact')),
                                    'has_summary': bool(llm_sections.get('summary')),
                                    'has_experience': bool(llm_sections.get('experience')),
                                    'has_education': bool(llm_sections.get('education')),
                                    'has_skills': bool(llm_sections.get('skills')),
                                    'has_projects': bool(llm_sections.get('projects')),
                                    'total_paragraphs': sum(1 for section, content in llm_sections.items() if content),
                                    'parser': 'llm'
                                }
                            }
                            
                            # Generate HTML preview based on LLM sections
                            preview_html = '<div class="resume-preview-container">'
                            preview_html += '<h3 class="preview-title">User Resume Parsed (LLM)</h3>'
                            preview_html += '<div class="resume-preview-content">'
                            
                            # Add each section to the preview
                            for orig_section, ui_section in [
                                ('contact', 'Contact Information'), 
                                ('summary', 'Summary'), 
                                ('experience', 'Experience'),
                                ('education', 'Education'), 
                                ('skills', 'Skills'), 
                                ('projects', 'Projects'),
                                ('additional', 'Additional Information')
                            ]:
                                if llm_sections.get(orig_section):
                                    preview_html += f'<div class="preview-section">'
                                    preview_html += f'<h4 class="preview-section-title">{ui_section}</h4>'
                                    
                                    # Split by newlines and format as paragraphs
                                    paragraphs = llm_sections[orig_section].split('\n')
                                    for para in paragraphs:
                                        if para.strip():
                                            preview_html += f'<p class="preview-text">{para}</p>'
                                    
                                    preview_html += '</div>'
                            
                            preview_html += '</div></div>'
                            
                            print("LLM-parsed sections for front-end:", formatted_sections.keys())
                            
                            # Save LLM analysis to a JSON file for later use
                            llm_analysis = {
                                'sections': llm_sections,
                                'analysis': analysis['analysis'],
                                'parser': 'llm'
                            }
                            
                            analysis_filename = filename.replace('.docx', '_llm_analysis.json')
                            analysis_filepath = os.path.join(app.config['UPLOAD_FOLDER'], analysis_filename)
                            
                            with open(analysis_filepath, 'w') as f:
                                json.dump(llm_analysis, f, indent=2)
                        else:
                            logger.warning("LLM parsing did not return usable results. Falling back to traditional parsing.")
                    
                except (ImportError, Exception) as e:
                    logger.warning(f"LLM parsing unavailable or failed during initial upload: {str(e)}. Using traditional parsing.")
                
                # If LLM parsing wasn't successful, fall back to traditional parsing
                if not llm_parsed:
                    logger.info("Using traditional resume parsing for initial upload.")
                    
                    # Analyze the resume with traditional parser
                    analysis = analyze_resume(filepath)
                    
                    # Generate HTML preview of the resume content
                    preview_html = generate_resume_preview_html(analysis)
                    
                    # Format sections for frontend display
                    formatted_sections = {}
                    for section_name, paragraphs in analysis['sections'].items():
                        if paragraphs:  # Only include non-empty sections
                            section_text = ""
                            for para in paragraphs:
                                section_text += para["text"] + "\n"
                            formatted_sections[section_name] = section_text.strip()
                    
                    print("Formatted sections for front-end:", formatted_sections.keys())
                    
                    # Save analysis to a JSON file for later use
                    analysis_filename = filename.replace('.docx', '_analysis.json')
                    analysis_filepath = os.path.join(app.config['UPLOAD_FOLDER'], analysis_filename)
                    
                    with open(analysis_filepath, 'w') as f:
                        json.dump(analysis, f, indent=2, default=str)
                
                return jsonify({
                    'success': True, 
                    'filename': filename,
                    'preview': preview_html,
                    'sections': formatted_sections,  # This is what our JavaScript expects
                    'analysis': {
                        'has_contact_info': formatted_sections.get('contact_info', '') != '',
                        'has_summary': formatted_sections.get('summary', '') != '',
                        'has_experience': formatted_sections.get('experience', '') != '',
                        'has_education': formatted_sections.get('education', '') != '',
                        'has_skills': formatted_sections.get('skills', '') != ''
                    },
                    'parser': 'llm' if llm_parsed else 'traditional'
                }), 200
                
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}", exc_info=True)
                return jsonify({'error': f'Error processing file: {str(e)}'}), 500
        
        return jsonify({'error': 'File type not allowed'}), 400
