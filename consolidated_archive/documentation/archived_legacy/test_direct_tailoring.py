import requests
import json
import os
import time

# Base URL of the Flask application
BASE_URL = "http://localhost:5000"

def test_direct_tailoring():
    print("Testing direct tailoring with existing files...")
    
    # Find an existing formatted resume
    resume_files = [f for f in os.listdir("static/uploads") if f.endswith(".docx") and not f.endswith("_formatted.docx") and not f.endswith("_tailored.docx") and not f == "template_resume.docx"]
    
    if not resume_files:
        print("No suitable resume files found. Please upload a resume first.")
        return
    
    resume_filename = resume_files[0]
    print(f"Using resume file: {resume_filename}")
    
    # Load job data
    print("\n1. Loading job data...")
    with open("static/uploads/job_data_4203145291.json", "r") as f:
        job_data = json.load(f)
    
    # First format the resume
    print("\n2. Formatting resume...")
    format_data = {"resumeFilename": resume_filename}
    format_response = requests.post(f"{BASE_URL}/format-resume", json=format_data)
    
    if format_response.status_code != 200:
        print(f"Error formatting resume: {format_response.text}")
        return
    
    format_result = format_response.json()
    formatted_resume_filename = format_result.get('filename')
    print(f"Resume formatted successfully: {formatted_resume_filename}")
    
    # Now tailor the formatted resume
    print("\n3. Tailoring resume...")
    tailor_data = {
        "resumeFilename": formatted_resume_filename,
        "jobRequirements": job_data
    }
    tailor_response = requests.post(f"{BASE_URL}/tailor-resume", json=tailor_data)
    
    if tailor_response.status_code != 200:
        print(f"Error tailoring resume: {tailor_response.text}")
        return
    
    tailor_result = tailor_response.json()
    tailored_resume_filename = tailor_result.get('filename')
    print(f"Resume tailored successfully: {tailored_resume_filename}")
    
    # Get and display the preview HTML
    preview_html = tailor_result.get('preview', '')
    
    # Save preview HTML to a file for inspection
    with open("tailored_preview.html", "w") as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tailored Resume Preview</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                .resume-preview { max-width: 800px; margin: 0 auto; padding: 20px; }
                .resume-heading-1 { color: #2c3e50; margin-top: 20px; }
                .resume-heading-2 { color: #3498db; margin-top: 15px; }
                .resume-paragraph { margin: 8px 0; }
                .resume-bullet-list { margin: 8px 0; padding-left: 20px; }
                .resume-bullet-item { margin: 5px 0; }
            </style>
        </head>
        <body>
            <h1>Tailored Resume Preview</h1>
            """ + preview_html + """
        </body>
        </html>
        """)
    
    print(f"\nPreview HTML saved to tailored_preview.html")
    print("Open this file in a browser to view the formatted preview")
    
    # Check logs
    print("\n4. Checking logs for Claude API responses...")
    time.sleep(3)  # Give more time for logs to be written
    
    log_dir = "logs"
    log_files = [f for f in os.listdir(log_dir) if f.startswith("claude_api_log_")]
    
    if log_files:
        print(f"\nLog files found:")
        for log_file in log_files:
            log_path = os.path.join(log_dir, log_file)
            print(f" - {log_path}")
            
            # Read and display log content
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    log_content = f.read().strip()
                    if log_content and log_content != "[]":
                        logs = json.loads(log_content)
                        print(f"   Log entries: {len(logs)}")
                        
                        # Look for logs created in the last minute
                        recent_time = time.time() - 300  # Last 5 minutes
                        recent_logs = []
                        
                        for log in logs:
                            log_time = log.get('timestamp', '')
                            if log_time:
                                try:
                                    # Convert ISO timestamp to seconds since epoch
                                    log_time = time.mktime(time.strptime(log_time.split('.')[0], '%Y-%m-%dT%H:%M:%S'))
                                    if log_time > recent_time:
                                        recent_logs.append(log)
                                except:
                                    pass
                        
                        print(f"   Recent log entries (last 5 minutes): {len(recent_logs)}")
                        
                        for i, log in enumerate(recent_logs):
                            print(f"\n   Recent log entry #{i+1}:")
                            print(f"   - Timestamp: {log.get('timestamp')}")
                            print(f"   - Section: {log.get('section')}")
                            print(f"   - Resume ID: {log.get('resume_id')}")
                            
                            # Check if we have tailored content
                            response_data = log.get('response', {})
                            if 'tailored_content' in response_data:
                                content = response_data['tailored_content']
                                print(f"\n   TAILORED CONTENT PREVIEW:\n   {content[:300]}...")
                                print(f"\n   Token usage: {log.get('token_usage', {})}")
                    else:
                        print("   Empty log file")
            except Exception as e:
                print(f"   Error reading log: {str(e)}")
    else:
        print("\nNo log files were found.")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_direct_tailoring() 