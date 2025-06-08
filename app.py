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
import logging
from pathlib import Path

app = Flask(__name__)
app.config.from_object(Config)

# 🚨 O3 ARTIFACT LOGGING: Configure comprehensive DEBUG logging for web app
# This ensures we capture all the debugging info when users upload real resumes
def setup_o3_artifact_logging():
    """Configure comprehensive logging to capture O3 artifacts from real user uploads."""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger to DEBUG level
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler for comprehensive debugging
            logging.FileHandler(logs_dir / 'o3_real_user_debug.log', mode='a'),
            # Console handler for development
            logging.StreamHandler()
        ]
    )
    
    # Ensure key loggers are set to DEBUG
    logging.getLogger('utils.docx_builder').setLevel(logging.DEBUG)
    logging.getLogger('word_styles.numbering_engine').setLevel(logging.DEBUG)
    logging.getLogger('utils.docx_debug').setLevel(logging.DEBUG)
    
    app.logger.info("🚨 O3 ARTIFACT LOGGING ENABLED: Ready to capture real user resume artifacts")
    return logs_dir

# Enable O3 artifact logging
logs_dir = setup_o3_artifact_logging()

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

@app.context_processor
def inject_config():
    """Make config available in all templates"""
    return dict(config=app.config)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spacing-comparison')
def spacing_comparison():
    """Show before/after spacing comparison"""
    return render_template('compare_spacing.html')

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

# 🚨 O3 ARTIFACT ROUTES: Easy access to debugging artifacts from real user uploads
@app.route('/o3-artifacts/<request_id>')
def get_o3_artifacts(request_id):
    """Provide easy access to O3 debugging artifacts for a specific request."""
    try:
        artifacts = {}
        
        # Look for pre-reconciliation DOCX
        pre_reconciliation_path = Path(__file__).parent / f'pre_reconciliation_{request_id}.docx'
        if pre_reconciliation_path.exists():
            artifacts['pre_reconciliation_docx'] = f'/download-artifact/pre_reconciliation_{request_id}.docx'
            
        # Look for pre-reconciliation debug JSON
        pre_debug_path = Path(__file__).parent / f'pre_reconciliation_debug_{request_id}.json'
        if pre_debug_path.exists():
            artifacts['pre_reconciliation_debug'] = f'/download-artifact/pre_reconciliation_debug_{request_id}.json'
            
        # Look for final debug JSON
        debug_path = Path(__file__).parent / f'debug_{request_id}.json'
        if debug_path.exists():
            artifacts['final_debug'] = f'/download-artifact/debug_{request_id}.json'
            
        # Look for final debug DOCX
        debug_docx_path = Path(__file__).parent / f'debug_{request_id}.docx'
        if debug_docx_path.exists():
            artifacts['final_debug_docx'] = f'/download-artifact/debug_{request_id}.docx'
            
        # Check for logs
        log_path = logs_dir / 'o3_real_user_debug.log'
        if log_path.exists():
            artifacts['debug_log'] = '/download-artifact/o3_real_user_debug.log'
        
        return jsonify({
            'success': True,
            'request_id': request_id,
            'artifacts': artifacts,
            'artifact_count': len(artifacts),
            'message': f'Found {len(artifacts)} O3 debugging artifacts for request {request_id}'
        })
        
    except Exception as e:
        app.logger.error(f"Error retrieving O3 artifacts for {request_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error retrieving artifacts: {str(e)}'
        }), 500

@app.route('/download-artifact/<filename>')
def download_artifact(filename):
    """Download a specific O3 debugging artifact."""
    try:
        # Security check - only allow certain file patterns
        allowed_patterns = [
            'pre_reconciliation_',
            'debug_',
            'o3_real_user_debug.log'
        ]
        
        if not any(filename.startswith(pattern) for pattern in allowed_patterns):
            return jsonify({'error': 'Artifact not found or not accessible'}), 404
            
        # Look in project root first
        file_path = Path(__file__).parent / filename
        
        # If not found, try logs directory
        if not file_path.exists() and filename == 'o3_real_user_debug.log':
            file_path = logs_dir / filename
            
        if not file_path.exists():
            return jsonify({'error': 'Artifact file not found'}), 404
            
        # Determine MIME type
        if filename.endswith('.docx'):
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif filename.endswith('.json'):
            mimetype = 'application/json'
        elif filename.endswith('.log'):
            mimetype = 'text/plain'
        else:
            mimetype = 'application/octet-stream'
            
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        app.logger.error(f"Error downloading artifact {filename}: {str(e)}")
        return jsonify({'error': f'Error downloading artifact: {str(e)}'}), 500

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
