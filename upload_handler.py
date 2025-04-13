import os
import json
from flask import request, jsonify
from werkzeug.utils import secure_filename
from resume_processor import create_upload_directory, save_uploaded_file, analyze_resume, generate_resume_preview_html

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
                
                # Analyze the resume
                analysis = analyze_resume(filepath)
                
                # Generate HTML preview of the resume content
                preview_html = generate_resume_preview_html(analysis)
                
                # Save analysis to a JSON file for later use
                analysis_filename = filename.replace('.docx', '_analysis.json')
                analysis_filepath = os.path.join(app.config['UPLOAD_FOLDER'], analysis_filename)
                
                with open(analysis_filepath, 'w') as f:
                    json.dump(analysis, f, indent=2, default=str)
                
                return jsonify({
                    'success': True, 
                    'filename': filename,
                    'preview': preview_html,
                    'analysis': {
                        'has_contact_info': analysis['analysis']['has_contact_info'],
                        'has_summary': analysis['analysis']['has_summary'],
                        'has_experience': analysis['analysis']['has_experience'],
                        'has_education': analysis['analysis']['has_education'],
                        'has_skills': analysis['analysis']['has_skills']
                    }
                }), 200
                
            except Exception as e:
                return jsonify({'error': f'Error processing file: {str(e)}'}), 500
        
        return jsonify({'error': 'File type not allowed'}), 400
