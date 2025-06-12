import requests
import json
import os
import time

# Base URL of the Flask application
BASE_URL = "http://localhost:5000"

def test_full_flow():
    print("Starting full resume tailoring flow test...")
    
    # Step 1: Upload Resume
    print("\n1. Uploading resume...")
    with open("static/uploads/f82fd54d-087b-491e-bf11-614311cf842e.docx", "rb") as f:
        files = {"resume": f}
        response = requests.post(f"{BASE_URL}/upload-resume", files=files)
    
    if response.status_code != 200:
        print(f"Error uploading resume: {response.text}")
        return
    
    upload_result = response.json()
    print(f"Resume uploaded successfully: {upload_result.get('filename')}")
    resume_filename = upload_result.get('filename')
    
    # Step 2: Format Resume
    print("\n2. Formatting resume...")
    format_data = {"resumeFilename": resume_filename}
    response = requests.post(f"{BASE_URL}/format-resume", json=format_data)
    
    if response.status_code != 200:
        print(f"Error formatting resume: {response.text}")
        return
    
    format_result = response.json()
    print(f"Resume formatted successfully: {format_result.get('filename')}")
    formatted_resume_filename = format_result.get('filename')
    
    # Step 3: Use pre-parsed job data
    print("\n3. Loading job data...")
    with open("static/uploads/job_data_4203145291.json", "r") as f:
        job_data = json.load(f)
    
    # Step 4: Tailor Resume
    print("\n4. Tailoring resume...")
    tailor_data = {
        "resumeFilename": formatted_resume_filename,
        "jobRequirements": job_data
    }
    response = requests.post(f"{BASE_URL}/tailor-resume", json=tailor_data)
    
    if response.status_code != 200:
        print(f"Error tailoring resume: {response.text}")
        return
    
    tailor_result = response.json()
    print(f"Resume tailored successfully: {tailor_result.get('filename')}")
    tailored_resume_filename = tailor_result.get('filename')
    
    # Step 5: Check logs
    print("\n5. Checking logs for Claude API responses...")
    time.sleep(2)  # Give time for logs to be written
    
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
                        
                        if len(logs) > 0:
                            # Display the most recent log entries
                            recent_logs = logs[-3:] if len(logs) >= 3 else logs
                            for i, log in enumerate(recent_logs):
                                print(f"\n   Recent log entry #{i+1}:")
                                print(f"   - Timestamp: {log.get('timestamp')}")
                                print(f"   - Section: {log.get('section')}")
                                print(f"   - Resume ID: {log.get('resume_id')}")
                                
                                # Check if we have tailored content
                                response_data = log.get('response', {})
                                if 'tailored_content' in response_data:
                                    content = response_data['tailored_content']
                                    print(f"\n   TAILORED CONTENT:\n{content[:500]}...")
                                    print(f"\n   Token usage: {log.get('token_usage', {})}")
                    else:
                        print("   Empty log file")
            except Exception as e:
                print(f"   Error reading log: {str(e)}")
    else:
        print("\nNo log files were found.")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_full_flow() 