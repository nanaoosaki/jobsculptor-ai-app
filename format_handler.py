import os
from flask import request, jsonify
from resume_formatter import create_formatted_resume

def setup_formatting_routes(app):
    """Set up routes for resume formatting"""
    
    @app.route('/format-resume', methods=['POST'])
    def format_resume():
        """Handle resume formatting request"""
        data = request.get_json()
        
        if not data or 'resumeFilename' not in data:
            return jsonify({'error': 'No resume filename provided'}), 400
        
        resume_filename = data['resumeFilename']
        
        try:
            # Format the resume according to template
            formatted_filename = create_formatted_resume(
                resume_filename, 
                app.config['UPLOAD_FOLDER']
            )
            
            return jsonify({
                'success': True,
                'filename': formatted_filename,
                'message': 'Resume formatted successfully'
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Error formatting resume: {str(e)}'}), 500
