import os
# import ssl
from flask import Flask, render_template, request, jsonify, send_from_directory, session, send_file, redirect, url_for, current_app
from config import Config
from upload_handler import setup_upload_routes
from format_handler import setup_formatting_routes
from job_parser_handler import setup_job_parser_routes
from tailoring_handler import setup_tailoring_routes
from werkzeug.utils import secure_filename
from pdf_exporter import create_pdf_from_html
from html_generator import generate_preview_from_llm_responses
import json
import uuid
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Check if API key is available and log status
if app.config.get('CLAUDE_API_KEY'):
    print(f"\n===== Claude API Key found! =====")
    print(f"API Key starts with: {app.config['CLAUDE_API_KEY'][:5]}...")
    print(f"Length: {len(app.config['CLAUDE_API_KEY'])} characters")
    print(f"API URL: {app.config.get('CLAUDE_API_URL', 'Not set')}")
    print("Resume tailoring will use Claude AI")
else:
    print("\n===== WARNING: No Claude API Key found! =====")
    print("The application will run in demo mode.")
    print("To enable Claude AI tailoring, add CLAUDE_API_KEY to your .env file")

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Ensure temporary session data directory exists
TEMP_SESSION_DATA_PATH = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_session_data')
os.makedirs(TEMP_SESSION_DATA_PATH, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

# Setup resume upload routes
setup_upload_routes(app)

# Setup resume formatting routes
setup_formatting_routes(app)

# Setup job parser routes
setup_job_parser_routes(app)

# Setup resume tailoring routes
setup_tailoring_routes(app)

# --- New Routes for Preview and Download using request_id ---

@app.route('/preview/<request_id>')
def preview_tailored_resume(request_id):
    """Provide HTML preview for a specific tailoring request_id"""
    try:
        # Get upload folder path
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # Font family override escape-hatch
        font_override = request.args.get('ff')
        if font_override:
            # Validate against allowed fonts for security
            allowed_fonts = ['Times New Roman', 'Arial', 'Georgia', 'Verdana', 'Helvetica']
            if font_override in allowed_fonts:
                # Store override in session for this request
                session['font_override'] = font_override
                app.logger.info(f"Font override applied: {font_override}")
            else:
                app.logger.warning(f"Invalid font override attempted: {font_override}")
        
        # Generate HTML fragment using the request_id and upload_folder
        html_fragment = generate_preview_from_llm_responses(request_id, upload_folder, for_screen=True)
        return html_fragment # Return just the HTML content
    except FileNotFoundError:
        app.logger.error(f"Preview data not found for request_id: {request_id}")
        return jsonify({'success': False, 'error': 'Preview data not found. Please tailor the resume again.'}), 404
    except Exception as e:
        app.logger.error(f"Error generating preview for request_id {request_id}: {str(e)}")
        return jsonify({'success': False, 'error': f'Error generating preview: {str(e)}'}), 500

@app.route('/download/<request_id>')
def download_tailored_resume(request_id):
    """Generate and download PDF for a specific tailoring request_id"""
    try:
        # Get upload folder path
        upload_folder = current_app.config['UPLOAD_FOLDER']
        # Generate the full HTML document needed for PDF conversion
        full_html = generate_preview_from_llm_responses(request_id, upload_folder, for_screen=False)

        # Define the output path for the PDF within the temp directory (or uploads)
        # Let's put final PDFs in the main uploads folder for consistency with downloads
        output_dir = app.config['UPLOAD_FOLDER']
        # We need a base filename, maybe derive from request_id or fetch original filename if stored
        # For now, use request_id
        pdf_filename = f"tailored_resume_{request_id}.pdf"
        pdf_output_path = os.path.join(output_dir, pdf_filename)

        # Generate the PDF file
        pdf_path = create_pdf_from_html(
            full_html,
            pdf_output_path,
            metadata={
                'title': f'Tailored Resume {request_id}',
                'author': 'Resume Tailoring App'
            }
        )

        # Send the generated PDF file for download
        return send_from_directory(
            output_dir,
            pdf_filename,
            as_attachment=True,
            mimetype='application/pdf'
        )

    except FileNotFoundError:
        app.logger.error(f"Data not found for generating PDF for request_id: {request_id}")
        # Provide a user-friendly error page or response
        return "<html><body><h1>Error</h1><p>Could not find the data needed to generate the PDF. Please try tailoring the resume again.</p></body></html>", 404
    except Exception as e:
        app.logger.error(f"Error generating or downloading PDF for request_id {request_id}: {str(e)}")
        return "<html><body><h1>Error</h1><p>An unexpected error occurred while generating the PDF.</p></body></html>", 500

@app.route('/download/docx/<request_id>')
def download_docx_resume(request_id):
    """Generate and download DOCX for a specific tailoring request_id"""
    try:
        # Get temp directory path
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_session_data')
        
        # Check for debug flag
        debug = request.args.get('debug', '').lower() == 'true'
        
        # Import the docx builder
        from utils.docx_builder import build_docx
        
        # Build the DOCX file with debug flag
        docx_bytes = build_docx(request_id, temp_dir, debug=debug)
        
        # Set the output filename
        filename = f"tailored_resume_{request_id}.docx"
        
        # Send the file for download
        return send_file(
            docx_bytes,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except FileNotFoundError:
        app.logger.error(f"Data not found for generating DOCX for request_id: {request_id}")
        return jsonify({
            'success': False, 
            'error': 'Could not find the data needed to generate the DOCX. Please try tailoring the resume again.'
        }), 404
    except Exception as e:
        app.logger.error(f"Error generating DOCX for request_id {request_id}: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Error generating DOCX: {str(e)}'
        }), 500

# --- End New Routes ---

@app.route('/download/<filename>')
def download_file(filename):
    """
    Download a file from the upload folder
    
    Handles both DOCX and PDF file downloads with appropriate MIME types
    """
    # Determine the MIME type based on file extension
    mime_type = None
    if filename.lower().endswith('.pdf'):
        mime_type = 'application/pdf'
    elif filename.lower().endswith('.docx'):
        mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    
    return send_from_directory(
        app.config['UPLOAD_FOLDER'], 
        filename, 
        as_attachment=True,
        mimetype=mime_type
    )

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    """Generate a PDF from the current tailored resume"""
    try:
        # Get resume data from session or request
        resume_data = session.get('tailored_resume')
        
        if not resume_data:
            # If not in session, try to get from request
            resume_data = request.json.get('resume')
            
        if not resume_data:
            return jsonify({'error': 'No resume data found'}), 400
        
        # Generate unique filename
        filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Generate PDF in memory
        pdf_buffer = create_pdf_from_html(resume_data)
        
        # Return PDF for download
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        app.logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    """Generate and download a PDF version of the tailored resume"""
    # Get resume data from the request
    resume_data = request.json
    
    if not resume_data:
        return jsonify({"error": "No resume data provided"}), 400
    
    # Generate PDF from resume data
    pdf_buffer = create_pdf_from_html(resume_data)
    
    # Get file name from the person's name or use a default
    filename = f"{resume_data.get('name', 'Tailored_Resume').replace(' ', '_')}.pdf"
    
    # Send PDF file to the client
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/font-features', methods=['POST'])
def update_font_features():
    """API endpoint for dynamic font feature updates"""
    try:
        data = request.get_json()
        feature_type = data.get('type', 'numbers')
        feature_value = data.get('value', 'default')
        
        # Map UI selections to OpenType features
        feature_map = {
            'numbers': {
                'tabular': "'tnum' 1, 'lnum' 1",
                'oldstyle': "'onum' 1, 'pnum' 1", 
                'default': "'liga' 1"
            },
            'ligatures': {
                'enabled': "'liga' 1, 'kern' 1",
                'disabled': "'liga' 0",
                'default': "'liga' 1"
            }
        }
        
        if feature_type in feature_map and feature_value in feature_map[feature_type]:
            # Store in session for immediate effect
            if 'font_features' not in session:
                session['font_features'] = {}
            session['font_features'][feature_type] = feature_map[feature_type][feature_value]
            
            app.logger.info(f"Font feature updated: {feature_type} = {feature_value}")
            return jsonify({
                'success': True, 
                'feature': feature_map[feature_type][feature_value],
                'type': feature_type,
                'value': feature_value
            })
        
        return jsonify({'success': False, 'error': 'Invalid feature selection'})
        
    except Exception as e:
        app.logger.error(f"Error updating font features: {str(e)}")
        return jsonify({'success': False, 'error': f'Font feature update failed: {str(e)}'}), 500

@app.route('/api/accessibility', methods=['POST'])
def toggle_accessibility_mode():
    """Toggle accessibility font mode"""
    try:
        data = request.get_json()
        mode = data.get('mode', 'standard')
        
        if mode == 'dyslexic':
            # Store accessibility mode in session
            session['accessibility_mode'] = mode
            app.logger.info(f"Accessibility mode enabled: {mode}")
            return jsonify({'success': True, 'mode': mode})
        else:
            # Clear accessibility mode
            session.pop('accessibility_mode', None)
            app.logger.info("Accessibility mode disabled")
            return jsonify({'success': True, 'mode': 'standard'})
            
    except Exception as e:
        app.logger.error(f"Error toggling accessibility mode: {str(e)}")
        return jsonify({'success': False, 'error': f'Accessibility toggle failed: {str(e)}'}), 500

@app.route('/api/typography-test')
def typography_test():
    """Test endpoint to verify enhanced typography system is working"""
    try:
        from style_manager import load_tokens
        
        # Load design tokens
        tokens = load_tokens()
        typography = tokens.get('typography', {})
        
        # Test data
        test_info = {
            'typography_system': 'enhanced' if typography else 'legacy',
            'font_version': typography.get('fontFamily', {}).get('fontVersion', 'unknown'),
            'available_fonts': {
                'primary': typography.get('fontFamily', {}).get('primary', 'not_set'),
                'docx': typography.get('fontFamily', {}).get('docxPrimary', 'not_set'),
                'fallback': typography.get('fontFamily', {}).get('fallback', 'not_set')
            },
            'font_sizes': typography.get('fontSize', {}),
            'session_overrides': {
                'font_override': session.get('font_override'),
                'accessibility_mode': session.get('accessibility_mode'),
                'font_features': session.get('font_features', {})
            }
        }
        
        return jsonify(test_info)
        
    except Exception as e:
        app.logger.error(f"Error in typography test: {str(e)}")
        return jsonify({'error': f'Typography test failed: {str(e)}'}), 500

if __name__ == '__main__':
    # Configure Flask session
    # A secret key is required for session management
    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-please-change') # Use environment variable or generate one
    if app.secret_key == 'dev-secret-key-please-change':
        print("WARNING: Using default Flask secret key. Set FLASK_SECRET_KEY environment variable for production.")

    # Run with HTTP only
    print("Running with HTTP on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    # # Check if certificates exist
    # cert_path = 'certs/cert.pem'
    # key_path = 'certs/key.pem'
    
    # if os.path.exists(cert_path) and os.path.exists(key_path):
    #     # Create SSL context
    #     context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    #     context.load_cert_chain(cert_path, key_path)
        
    #     # Run with HTTPS
    #     print("Running with HTTPS on https://0.0.0.0:5000")
    #     app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=context)
    # else:
    #     # Fall back to HTTP if certificates are not found
    #     print("Certificates not found. Running with HTTP on http://0.0.0.0:5000")
    #     print("To enable HTTPS, run generate_cert.py to create SSL certificates")
    #     app.run(host='0.0.0.0', port=5000, debug=True)
