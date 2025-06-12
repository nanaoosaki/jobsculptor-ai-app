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
import time

# A-Series Improvements: Testing and Correlation
from utils.bullet_testing_framework import BulletTestingFramework, TestScenario
from utils.bullet_error_categorizer import BulletErrorCategorizer
from utils.request_correlation import (
    start_request, end_request, get_current_request_id, 
    correlation_manager, set_metadata
)
from utils.memory_manager import memory_manager, get_memory_status, estimate_document_memory_mb
from utils.staged_testing import StagedTestingPipeline, TestPipelineConfig

# B-Series Improvements: Edge Cases and Core Fixes
from utils.unicode_bullet_sanitizer import (
    unicode_sanitizer, sanitize_bullet_text, analyze_bullet_characters,
    get_supported_bullet_types
)
from utils.numid_collision_manager import (
    collision_manager, allocate_safe_numid, get_numid_allocation_summary
)
from utils.xml_repair_system import (
    xml_repair_system, analyze_docx_xml_issues, repair_docx_xml,
    get_xml_repair_summary
)
from utils.style_collision_handler import (
    style_handler, register_document_style, validate_style_for_bullets,
    get_style_collision_summary
)

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

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring services"""
    try:
        # Basic health checks
        upload_dir_exists = os.path.exists(app.config['UPLOAD_FOLDER'])
        temp_dir_exists = os.path.exists(TEMP_SESSION_DATA_PATH)
        
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'upload_dir': upload_dir_exists,
            'temp_dir': temp_dir_exists,
            'api_keys': {
                'claude': bool(app.config.get('CLAUDE_API_KEY')),
                'openai': bool(app.config.get('OPENAI_API_KEY'))
            }
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

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

        # PDF generation disabled - redirect to DOCX download instead
        app.logger.info(f"PDF download requested for {request_id}, redirecting to DOCX")
        return redirect(url_for('download_docx_resume', request_id=request_id))

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
    """PDF generation disabled - redirect to DOCX instead"""
    app.logger.info("PDF generation request received, but PDF generation is disabled")
    return jsonify({
        'error': 'PDF generation is disabled. Please use DOCX download instead.',
        'redirect': '/download/docx'
    }), 410  # 410 Gone - service no longer available

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    """PDF download disabled - use DOCX instead"""
    app.logger.info("PDF download request received, but PDF generation is disabled")
    return jsonify({
        'error': 'PDF download is disabled. Please use "Generate DOCX" button instead.',
        'alternative': 'Use the Generate DOCX button to download your tailored resume.'
    }), 410  # 410 Gone - service no longer available

# ==== A-SERIES IMPROVEMENTS: TESTING AND MONITORING ROUTES ====

@app.route('/api/test-framework/run')
def run_bullet_testing():
    """Run comprehensive bullet testing framework (A1)."""
    try:
        request_id = start_request(user_id="test_user", session_id="test_session")
        set_metadata("feature_native_bullets", True, request_id)
        set_metadata("feature_testing_framework", True, request_id)
        
        # Initialize testing framework
        testing_framework = BulletTestingFramework(request_id)
        
        # Run comprehensive tests
        results = testing_framework.run_comprehensive_tests()
        
        # Generate report
        report = testing_framework.generate_test_report()
        
        end_request(request_id)
        
        return jsonify({
            'success': True,
            'request_id': request_id,
            'test_results': report,
            'tests_run': len(results),
            'message': f'A1: Comprehensive testing completed with {len(results)} test scenarios'
        })
        
    except Exception as e:
        app.logger.error(f"A1: Error running bullet testing framework: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Testing framework error: {str(e)}'
        }), 500

@app.route('/api/test-framework/scenario/<scenario_name>')
def run_single_test_scenario(scenario_name):
    """Run a single test scenario (A1)."""
    try:
        # Validate scenario name
        scenario_map = {
            'basic_bullets': TestScenario.BASIC_BULLETS,
            'edge_cases': TestScenario.EDGE_CASES,
            'unicode_content': TestScenario.UNICODE_CONTENT,
            'large_document': TestScenario.LARGE_DOCUMENT,
            'malformed_data': TestScenario.MALFORMED_DATA
        }
        
        if scenario_name not in scenario_map:
            return jsonify({
                'success': False,
                'error': f'Unknown test scenario: {scenario_name}',
                'available_scenarios': list(scenario_map.keys())
            }), 400
        
        request_id = start_request(user_id="test_user")
        set_metadata("feature_single_test", True, request_id)
        
        # Initialize testing framework
        testing_framework = BulletTestingFramework(request_id)
        
        # Run single test
        scenario = scenario_map[scenario_name]
        result = testing_framework.run_test(scenario, f"single_{scenario_name}")
        
        end_request(request_id)
        
        return jsonify({
            'success': True,
            'request_id': request_id,
            'scenario': scenario_name,
            'result': {
                'success': result.success,
                'total_bullets': result.total_bullets,
                'consistent_bullets': result.consistent_bullets,
                'inconsistent_bullets': result.inconsistent_bullets,
                'duration_ms': result.duration_ms,
                'errors': result.errors,
                'consistency_rate': result.details.get('consistency_rate', 0)
            }
        })
        
    except Exception as e:
        app.logger.error(f"A1: Error running single test scenario {scenario_name}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Single test error: {str(e)}'
        }), 500

@app.route('/api/analytics/summary')
def get_analytics_summary():
    """Get request analytics summary (A8)."""
    try:
        lookback_hours = request.args.get('hours', default=24, type=int)
        summary = correlation_manager.get_analytics_summary(lookback_hours)
        
        return jsonify({
            'success': True,
            'analytics': summary,
            'lookback_hours': lookback_hours
        })
        
    except Exception as e:
        app.logger.error(f"A8: Error generating analytics summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Analytics error: {str(e)}'
        }), 500

@app.route('/api/analytics/user/<user_id>')
def get_user_analytics(user_id):
    """Get analytics for a specific user (A8)."""
    try:
        limit = request.args.get('limit', default=10, type=int)
        user_requests = correlation_manager.get_user_request_history(user_id, limit)
        
        # Convert to serializable format
        request_data = []
        for req in user_requests:
            request_data.append({
                'request_id': req.request_id,
                'start_time': req.start_time,
                'end_time': req.end_time,
                'total_bullets': req.total_bullets,
                'successful_bullets': req.successful_bullets,
                'failed_bullets': req.failed_bullets,
                'total_duration_ms': req.total_duration_ms,
                'errors': req.errors,
                'warnings': req.warnings,
                'features_enabled': req.features_enabled
            })
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'request_count': len(request_data),
            'requests': request_data
        })
        
    except Exception as e:
        app.logger.error(f"A8: Error getting user analytics for {user_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'User analytics error: {str(e)}'
        }), 500

@app.route('/api/error-categorizer/summary')
def get_error_categorizer_summary():
    """Get error categorization summary (A7)."""
    try:
        # For now, create a test categorizer since we don't have persistent state
        # In production, this would be integrated with the main request flow
        categorizer = BulletErrorCategorizer("demo_categorizer")
        
        # Add some demo error contexts for demonstration
        demo_errors = [
            {
                'paragraph_index': 0,
                'paragraph_text': 'Sample bullet point text',
                'error_message': 'Missing numPr element in paragraph',
                'xml_element': None
            },
            {
                'paragraph_index': 1,
                'paragraph_text': '• Pre-existing bullet character',
                'error_message': 'Sanitization failure detected',
                'xml_element': None
            }
        ]
        
        for error_context in demo_errors:
            categorizer.categorize_error(error_context)
        
        summary = categorizer.get_error_summary()
        recommendations = categorizer.get_fix_recommendations()
        
        return jsonify({
            'success': True,
            'error_summary': summary,
            'fix_recommendations': recommendations,
            'message': 'A7: Error categorization summary (demo data)'
        })
        
    except Exception as e:
        app.logger.error(f"A7: Error getting error categorizer summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error categorizer error: {str(e)}'
        }), 500

@app.route('/api/memory/status')
def get_memory_status_endpoint():
    """Get current memory status (A5)."""
    try:
        status = get_memory_status()
        return jsonify({
            'success': True,
            'memory_status': status
        })
    except Exception as e:
        app.logger.error(f"A5: Error getting memory status: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Memory status error: {str(e)}'
        }), 500

@app.route('/api/memory/estimate')
def estimate_memory_usage():
    """Estimate memory usage for document parameters (A5)."""
    try:
        paragraphs = request.args.get('paragraphs', default=50, type=int)
        bullets = request.args.get('bullets', default=20, type=int)
        has_images = request.args.get('images', default=False, type=bool)
        
        estimated_mb = estimate_document_memory_mb(paragraphs, bullets, has_images)
        strategy = memory_manager.get_optimization_strategy(estimated_mb)
        is_large = memory_manager.is_large_document(estimated_mb)
        
        return jsonify({
            'success': True,
            'estimation': {
                'estimated_memory_mb': round(estimated_mb, 2),
                'optimization_strategy': strategy,
                'is_large_document': is_large,
                'parameters': {
                    'paragraphs': paragraphs,
                    'bullets': bullets,
                    'has_images': has_images
                }
            }
        })
        
    except Exception as e:
        app.logger.error(f"A5: Error estimating memory: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Memory estimation error: {str(e)}'
        }), 500

@app.route('/api/staged-testing/run')
def run_staged_testing_pipeline():
    """Run comprehensive staged testing pipeline (A11)."""
    try:
        # Get optional configuration parameters
        skip_on_failure = request.args.get('skip_on_failure', default=False, type=bool)
        min_consistency = request.args.get('min_consistency', default=95.0, type=float)
        
        # Create pipeline configuration
        config = TestPipelineConfig(
            skip_on_failure=skip_on_failure,
            min_consistency_rate=min_consistency
        )
        
        # Initialize and run pipeline
        pipeline = StagedTestingPipeline(config)
        results = pipeline.run_full_pipeline()
        
        return jsonify({
            'success': True,
            'pipeline_results': results,
            'message': 'A11: Staged testing pipeline completed'
        })
        
    except Exception as e:
        app.logger.error(f"A11: Error running staged testing pipeline: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Staged testing error: {str(e)}'
        }), 500

@app.route('/api/phase2-summary')
def get_phase2_summary():
    """Get comprehensive Phase 2 A-series implementation summary."""
    try:
        return jsonify({
            'success': True,
            'phase2_summary': {
                'title': 'Phase 2: A-Series Improvements Implementation',
                'status': 'COMPLETED',
                'implementation_date': '2025-06-08',
                'total_improvements': 5,
                'completed_improvements': [
                    {
                        'id': 'A1',
                        'name': 'Comprehensive Testing Framework',
                        'status': 'IMPLEMENTED',
                        'description': 'Systematic test automation across multiple scenarios',
                        'endpoints': ['/api/test-framework/run', '/api/test-framework/scenario/<name>'],
                        'features': ['Automated bullet consistency validation', 'Edge case testing', 'Performance benchmarking']
                    },
                    {
                        'id': 'A5',
                        'name': 'Memory Guard Rails',
                        'status': 'IMPLEMENTED', 
                        'description': 'Memory monitoring and resource management',
                        'endpoints': ['/api/memory/status', '/api/memory/estimate'],
                        'features': ['Memory usage monitoring', 'Large document detection', 'Resource cleanup']
                    },
                    {
                        'id': 'A7',
                        'name': 'Error Categorization System',
                        'status': 'IMPLEMENTED',
                        'description': 'Systematic error classification and analysis',
                        'endpoints': ['/api/error-categorizer/summary'],
                        'features': ['Automatic error classification', 'Root cause analysis', 'Fix recommendations']
                    },
                    {
                        'id': 'A8',
                        'name': 'Request Correlation IDs',
                        'status': 'IMPLEMENTED',
                        'description': 'Cross-request tracking and analytics',
                        'endpoints': ['/api/analytics/summary', '/api/analytics/user/<id>'],
                        'features': ['Request tracking', 'Performance analytics', 'User session correlation']
                    },
                    {
                        'id': 'A11',
                        'name': 'Staged Testing Pipeline',
                        'status': 'IMPLEMENTED',
                        'description': 'Multi-stage validation and quality gates',
                        'endpoints': ['/api/staged-testing/run'],
                        'features': ['Multi-stage validation', 'Quality gates', 'Regression testing']
                    }
                ],
                'architecture_benefits': [
                    'Systematic identification of bullet consistency patterns',
                    'Real-time performance and error monitoring',
                    'Comprehensive test coverage and validation',
                    'Memory-aware processing for large documents',
                    'Detailed analytics and trending capabilities'
                ],
                'next_phase': {
                    'name': 'Phase 3: B-Series Edge Cases',
                    'description': 'Implementation of edge case handling and advanced features',
                    'priority_items': ['B1: Style collisions', 'B3: Unicode bullet handling', 'B9: numId collision prevention']
                },
                'testing_dashboard': '/debug/testing-dashboard'
            }
        })
        
    except Exception as e:
        app.logger.error(f"Error generating Phase 2 summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Summary generation error: {str(e)}'
        }), 500

@app.route('/debug/testing-dashboard')
def testing_dashboard():
    """Debugging dashboard for A-series improvements."""
    return render_template('testing_dashboard.html')

# ==== END A-SERIES IMPROVEMENTS ====

# ===== B-SERIES ENDPOINTS: Edge Cases and Core Fixes =====

@app.route('/api/unicode-sanitizer/analyze', methods=['POST'])
def analyze_unicode_bullets():
    """Analyze text for bullet characters without modifying it (B3)."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # B3: Analyze bullet characters
        detections = analyze_bullet_characters(text)
        
        result = {
            'original_text': text,
            'detections_found': len(detections),
            'bullet_types_detected': list(set(d.bullet_type.value for d in detections)),
            'detections': [
                {
                    'bullet_type': d.bullet_type.value,
                    'character': d.character,
                    'position': d.position,
                    'confidence': d.confidence,
                    'should_remove': d.should_remove,
                    'replacement_suggestion': d.replacement_suggestion
                }
                for d in detections
            ],
            'supported_types': get_supported_bullet_types()
        }
        
        return jsonify({
            'success': True,
            'analysis': result
        })
        
    except Exception as e:
        app.logger.error(f"B3: Unicode bullet analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/unicode-sanitizer/sanitize', methods=['POST'])
def sanitize_unicode_bullets():
    """Sanitize text by removing bullet characters (B3)."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        locale = data.get('locale', None)
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # B3: Sanitize bullet characters
        sanitized_text, detections = unicode_sanitizer.sanitize_text(text, locale)
        
        result = {
            'original_text': text,
            'sanitized_text': sanitized_text,
            'changes_made': sanitized_text != text,
            'detections': [
                {
                    'bullet_type': d.bullet_type.value,
                    'character': d.character,
                    'removed': d.should_remove
                }
                for d in detections
            ],
            'sanitization_stats': unicode_sanitizer.get_sanitization_stats()
        }
        
        return jsonify({
            'success': True,
            'sanitization': result
        })
        
    except Exception as e:
        app.logger.error(f"B3: Unicode bullet sanitization failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Sanitization failed: {str(e)}'
        }), 500

@app.route('/api/unicode-sanitizer/stats')
def get_unicode_sanitizer_stats():
    """Get unicode sanitizer statistics (B3)."""
    try:
        stats = unicode_sanitizer.get_sanitization_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        app.logger.error(f"B3: Failed to get unicode sanitizer stats: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get stats: {str(e)}'
        }), 500

@app.route('/api/numid-manager/allocate', methods=['POST'])
def allocate_numid():
    """Allocate a safe numId for a document section (B9)."""
    try:
        data = request.get_json()
        document_id = data.get('document_id')
        section_name = data.get('section_name')
        style_name = data.get('style_name', None)
        
        if not document_id or not section_name:
            return jsonify({'error': 'document_id and section_name are required'}), 400
        
        # B9: Allocate safe numId
        num_id, abstract_num_id = allocate_safe_numid(document_id, section_name, style_name)
        
        result = {
            'allocated': True,
            'num_id': num_id,
            'abstract_num_id': abstract_num_id,
            'document_id': document_id,
            'section_name': section_name,
            'style_name': style_name
        }
        
        return jsonify({
            'success': True,
            'allocation': result
        })
        
    except Exception as e:
        app.logger.error(f"B9: NumId allocation failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Allocation failed: {str(e)}'
        }), 500

@app.route('/api/numid-manager/summary')
def get_numid_summary():
    """Get numId allocation summary (B9)."""
    try:
        summary = get_numid_allocation_summary()
        return jsonify({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        app.logger.error(f"B9: Failed to get numId summary: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get summary: {str(e)}'
        }), 500

@app.route('/api/xml-repair/analyze', methods=['POST'])
def analyze_xml_issues():
    """Analyze DOCX file for XML issues (B6)."""
    try:
        # Check if file was uploaded
        if 'docx_file' not in request.files:
            return jsonify({'error': 'No DOCX file provided'}), 400
        
        file = request.files['docx_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # B6: Analyze XML issues
        issues = analyze_docx_xml_issues(file)
        
        result = {
            'filename': file.filename,
            'total_issues': len(issues),
            'critical_issues': len([i for i in issues if i.severity == 'critical']),
            'auto_fixable_issues': len([i for i in issues if i.auto_fixable]),
            'issues_by_type': {},
            'issues': [
                {
                    'type': issue.issue_type.value,
                    'element_path': issue.element_path,
                    'description': issue.description,
                    'severity': issue.severity,
                    'auto_fixable': issue.auto_fixable,
                    'suggested_fix': issue.suggested_fix,
                    'line_number': issue.line_number
                }
                for issue in issues
            ]
        }
        
        # Count issues by type
        for issue in issues:
            issue_type = issue.issue_type.value
            if issue_type not in result['issues_by_type']:
                result['issues_by_type'][issue_type] = 0
            result['issues_by_type'][issue_type] += 1
        
        return jsonify({
            'success': True,
            'analysis': result
        })
        
    except Exception as e:
        app.logger.error(f"B6: XML analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/xml-repair/summary')
def get_xml_repair_summary_endpoint():
    """Get XML repair system summary (B6)."""
    try:
        summary = get_xml_repair_summary()
        return jsonify({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        app.logger.error(f"B6: Failed to get XML repair summary: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get summary: {str(e)}'
        }), 500

@app.route('/api/style-handler/validate', methods=['POST'])
def validate_style():
    """Validate style usage for bullets (B1)."""
    try:
        data = request.get_json()
        style_name = data.get('style_name')
        numbering_id = data.get('numbering_id')
        
        if not style_name:
            return jsonify({'error': 'style_name is required'}), 400
        
        # B1: Validate style
        is_valid = validate_style_for_bullets(style_name, numbering_id)
        
        result = {
            'style_name': style_name,
            'numbering_id': numbering_id,
            'is_valid': is_valid,
            'validation_time': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'validation': result
        })
        
    except Exception as e:
        app.logger.error(f"B1: Style validation failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Validation failed: {str(e)}'
        }), 500

@app.route('/api/style-handler/summary')
def get_style_summary():
    """Get style collision handler summary (B1)."""
    try:
        summary = get_style_collision_summary()
        return jsonify({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        app.logger.error(f"B1: Failed to get style summary: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get summary: {str(e)}'
        }), 500

@app.route('/api/phase3-summary')
def get_phase3_summary():
    """Get comprehensive Phase 3 B-series implementation summary."""
    try:
        # B3: Unicode Sanitizer Status
        unicode_stats = unicode_sanitizer.get_sanitization_stats()
        
        # B9: NumId Manager Status
        numid_summary = get_numid_allocation_summary()
        
        # B6: XML Repair Status
        xml_summary = get_xml_repair_summary()
        
        # B1: Style Handler Status
        style_summary = get_style_collision_summary()
        
        phase3_summary = {
            'title': 'Phase 3: B-Series Edge Cases Implementation',
            'status': 'COMPLETED',
            'implementation_date': '2025-06-08',
            'total_improvements': 4,
            'completed_improvements': [
                {
                    'id': 'B3',
                    'name': 'Unicode Bullet Sanitization',
                    'status': 'IMPLEMENTED',
                    'description': 'Comprehensive detection and removal of bullet characters',
                    'endpoints': ['/api/unicode-sanitizer/analyze', '/api/unicode-sanitizer/sanitize', '/api/unicode-sanitizer/stats'],
                    'features': ['Multi-locale bullet detection', 'Context-aware sanitization', 'False positive prevention'],
                    'statistics': unicode_stats
                },
                {
                    'id': 'B9',
                    'name': 'NumId Collision Prevention',
                    'status': 'IMPLEMENTED',
                    'description': 'Global numbering ID management and collision detection',
                    'endpoints': ['/api/numid-manager/allocate', '/api/numid-manager/summary'],
                    'features': ['Thread-safe ID allocation', 'Collision detection', 'Document-scoped tracking'],
                    'summary': numid_summary
                },
                {
                    'id': 'B6',
                    'name': 'XML Structure Repair',
                    'status': 'IMPLEMENTED',
                    'description': 'Detection and repair of malformed XML in DOCX documents',
                    'endpoints': ['/api/xml-repair/analyze', '/api/xml-repair/summary'],
                    'features': ['XML validation', 'Automatic repair', 'Namespace checking'],
                    'summary': xml_summary
                },
                {
                    'id': 'B1',
                    'name': 'Style Collision Handling',
                    'status': 'IMPLEMENTED',
                    'description': 'Prevention and resolution of style conflicts',
                    'endpoints': ['/api/style-handler/validate', '/api/style-handler/summary'],
                    'features': ['Style conflict detection', 'Automatic resolution', 'Hierarchy management'],
                    'summary': style_summary
                }
            ],
            'core_fixes_implemented': [
                'Unicode bullet character sanitization with locale awareness',
                'Thread-safe numId allocation and collision prevention',
                'Comprehensive XML structure validation and repair',
                'Style conflict detection and automatic resolution'
            ],
            'integration_points': [
                'Document generation pipeline integration',
                'Bullet reconciliation system enhancement',
                'Error categorization framework extension',
                'Testing and monitoring infrastructure expansion'
            ],
            'architecture_benefits': [
                'Proactive edge case handling',
                'Real-time conflict detection and resolution',
                'Comprehensive XML validation',
                'Robust numbering ID management'
            ],
            'next_phase': {
                'name': 'Phase 4: O3 Core Implementation',
                'description': 'Implementation of final O3 bullet consistency fixes',
                'priority_items': ['Final bullet reconciliation', 'Document state management', 'Production optimization']
            }
        }
        
        return jsonify({
            'success': True,
            'phase3_summary': phase3_summary
        })
        
    except Exception as e:
        app.logger.error(f"Error generating Phase 3 summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Summary generation error: {str(e)}'
        }), 500

# ==== END B-SERIES IMPROVEMENTS ====

# O3 Core Implementation API Endpoints

@app.route('/api/o3-core/summary/<doc_id>')
def o3_core_summary(doc_id):
    """Get O3 core engine summary for a document."""
    try:
        from utils.o3_bullet_core_engine import get_o3_engine
        
        engine = get_o3_engine(doc_id)
        summary = engine.get_engine_summary()
        
        return jsonify({
            'success': True,
            'doc_id': doc_id,
            'summary': summary,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/o3-core/all-engines')
def o3_core_all_engines():
    """Get summary of all active O3 engines."""
    try:
        from utils.o3_bullet_core_engine import get_all_engines_summary
        
        summary = get_all_engines_summary()
        
        return jsonify({
            'success': True,
            'engines_summary': summary,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/o3-core/cleanup/<doc_id>', methods=['POST'])
def o3_core_cleanup(doc_id):
    """Clean up O3 engine for a document."""
    try:
        from utils.o3_bullet_core_engine import cleanup_o3_engine
        
        cleanup_o3_engine(doc_id)
        
        return jsonify({
            'success': True,
            'doc_id': doc_id,
            'message': f'O3 engine cleaned up for document {doc_id}',
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/o3-core/test-engine', methods=['POST'])
def o3_core_test_engine():
    """Test O3 engine functionality with sample data."""
    try:
        from utils.o3_bullet_core_engine import get_o3_engine
        from docx import Document
        from word_styles.numbering_engine import NumberingEngine
        
        # Create test data
        test_doc_id = f"test_{int(time.time())}"
        test_doc = Document()
        test_numbering_engine = NumberingEngine()
        
        # Initialize O3 engine
        engine = get_o3_engine(test_doc_id)
        
        # Test bullet creation
        test_bullets = [
            "First test bullet point",
            "Second test bullet with special characters: •",
            "Third test bullet with numbers 123"
        ]
        
        created_bullets = []
        for i, bullet_text in enumerate(test_bullets):
            try:
                para, bullet_id = engine.create_bullet_trusted(
                    doc=test_doc,
                    text=bullet_text,
                    section_name="test_section",
                    numbering_engine=test_numbering_engine,
                    docx_styles={}
                )
                created_bullets.append({
                    'bullet_id': bullet_id,
                    'text': bullet_text,
                    'created': True
                })
            except Exception as e:
                created_bullets.append({
                    'text': bullet_text,
                    'created': False,
                    'error': str(e)
                })
        
        # Test reconciliation
        reconciliation_stats = engine.reconcile_document_bullets(test_doc, test_numbering_engine)
        
        # Get engine summary
        summary = engine.get_engine_summary()
        
        # Cleanup
        from utils.o3_bullet_core_engine import cleanup_o3_engine
        cleanup_o3_engine(test_doc_id)
        
        return jsonify({
            'success': True,
            'test_doc_id': test_doc_id,
            'created_bullets': created_bullets,
            'reconciliation_stats': reconciliation_stats,
            'engine_summary': summary,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Phase 4 Summary Endpoint
@app.route('/api/phase4-summary')
def phase4_summary():
    """Get comprehensive Phase 4 O3 Core Implementation summary."""
    try:
        from utils.o3_bullet_core_engine import get_all_engines_summary
        
        # Get O3 engines summary
        o3_summary = get_all_engines_summary()
        
        # Combine with system status
        summary = {
            'phase': 'Phase 4: O3 Core Implementation',
            'status': 'Active',
            'implementation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'features': {
                'o3_core_engine': {
                    'description': 'O3 enhanced bullet consistency engine with build-then-reconcile architecture',
                    'active_engines': o3_summary.get('active_engines', 0),
                    'capabilities': [
                        'Document-level bullet state management',
                        'Atomic bullet operations with validation',
                        'Comprehensive post-generation reconciliation',
                        'Integration with B-series edge case handling',
                        'Production-ready bullet consistency guarantee'
                    ]
                },
                'enhanced_reconciliation': {
                    'description': 'Multi-pass reconciliation with nuclear cleanup capabilities',
                    'features': [
                        'State-aware bullet validation',
                        'Comprehensive XML repair',
                        'Performance-optimized processing',
                        'Error recovery and retry logic'
                    ]
                },
                'integration_status': {
                    'docx_builder': 'Integrated',
                    'flask_endpoints': 'Active',
                    'b_series_modules': 'Connected',
                    'testing_framework': 'Available'
                }
            },
            'api_endpoints': [
                '/api/o3-core/summary/<doc_id>',
                '/api/o3-core/all-engines',
                '/api/o3-core/cleanup/<doc_id>',
                '/api/o3-core/test-engine',
                '/api/phase4-summary'
            ],
            'o3_engines': o3_summary,
            'compatibility': {
                'phases_1_3': 'Backward compatible',
                'b_series_integration': 'Active',
                'legacy_fallback': 'Available'
            }
        }
        
        return jsonify(summary)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Configure Flask session
    # A secret key is required for session management
    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-please-change') # Use environment variable or generate one
    if app.secret_key == 'dev-secret-key-please-change':
        print("WARNING: Using default Flask secret key. Set FLASK_SECRET_KEY environment variable for production.")

    # Get port from environment variable (for Render deployment) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Disable debug mode in production
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # Run with HTTP only
    print(f"Running with HTTP on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
    
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
