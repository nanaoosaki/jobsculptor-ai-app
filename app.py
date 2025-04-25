import os
# import ssl
from flask import Flask, render_template, request, jsonify, send_from_directory, session, send_file, redirect, url_for
from config import Config
from upload_handler import setup_upload_routes
from format_handler import setup_formatting_routes
from job_parser_handler import setup_job_parser_routes
from tailoring_handler import setup_tailoring_routes
from werkzeug.utils import secure_filename
from pdf_exporter import generate_pdf_from_html
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
        pdf_buffer = generate_pdf_from_html(resume_data)
        
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
    pdf_buffer = generate_pdf_from_html(resume_data)
    
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
