import os
from flask import request, jsonify
from job_parser import parse_job_listing

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
                    import json
                    json.dump(result, f, indent=2)
                
                return jsonify({
                    'success': True,
                    'job_title': result.get('job_title', 'Unknown Position'),
                    'company': result.get('company', 'Unknown Company'),
                    'requirements': result.get('requirements', []),
                    'skills': result.get('skills', [])
                }), 200
            else:
                return jsonify({'error': result.get('error', 'Failed to parse job listing')}), 500
                
        except Exception as e:
            return jsonify({'error': f'Error parsing job listing: {str(e)}'}), 500
