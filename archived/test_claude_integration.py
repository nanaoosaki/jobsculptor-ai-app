import os
import json
import traceback
from dotenv import load_dotenv
from claude_integration import ClaudeClient, extract_resume_content, tailor_resume_with_claude
from claude_api_logger import api_logger

# Load environment variables (including CLAUDE_API_KEY/ANTHROPIC_API_KEY)
load_dotenv()

# 1. Path to a resume DOCX
resume_path = "static/uploads/f82fd54d-087b-491e-bf11-614311cf842e.docx"

# 2. Load job data from the JSON file
with open("static/uploads/job_data_4203145291.json", "r") as f:
    job_data = json.load(f)

# 3. API Key from environment
api_key = os.environ.get("CLAUDE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")

if not api_key:
    print("Error: No Claude API key found in environment variables.")
    print("Make sure CLAUDE_API_KEY or ANTHROPIC_API_KEY is set in your .env file.")
    exit(1)

print(f"Using API key: {api_key[:5]}...")
print(f"Job Title: {job_data.get('job_title')}")
print(f"Company: {job_data.get('company')}")
print(f"Skills: {', '.join(job_data.get('skills', []))[:50]}...")
print(f"\nProcessing resume: {resume_path}")

# Initialize Claude client and test
try:
    # Format job requirements as text
    job_requirements_text = "Job Title: " + job_data.get('job_title', 'Unknown Position') + "\n"
    job_requirements_text += "Company: " + job_data.get('company', 'Unknown Company') + "\n\n"
    job_requirements_text += "Requirements:\n"
    for req in job_data.get('requirements', [])[:2]:  # Just first 2 for brevity
        job_requirements_text += f"- {req[:100]}...\n"
    job_requirements_text += "\nSkills:\n"
    for skill in job_data.get('skills', []):
        job_requirements_text += f"- {skill}\n"
    
    # Extract content from resume and print sections for debugging
    resume_sections = extract_resume_content(resume_path)
    print("\nResume sections found:")
    for section, content in resume_sections.items():
        if content.strip():
            print(f" - {section}: {len(content)} characters")
    
    # Choose a non-empty section
    test_section = None
    for section in ["summary", "experience", "skills"]:
        if resume_sections.get(section, "").strip():
            test_section = section
            break
    
    if not test_section:
        print("No suitable non-empty sections found in resume")
        exit(1)
        
    print(f"\nTesting with {test_section} section")
    
    # Get content for the test section
    original_content = resume_sections.get(test_section, "")
    
    print(f"\nORIGINAL {test_section.upper()} SECTION:")
    print("="*50)
    print(original_content[:500] + "..." if len(original_content) > 500 else original_content)
    print("="*50)
    
    # Create Claude client
    claude_client = ClaudeClient(api_key)
    
    # Call Claude API directly for this section
    print(f"\nSending to Claude API...")
    tailored_content = claude_client.tailor_resume_content(
        original_content,
        job_requirements_text,
        test_section,
        "test-direct-call"
    )
    
    print(f"\nTAILORED {test_section.upper()} SECTION (CLAUDE'S RESPONSE):")
    print("="*50)
    print(tailored_content)
    print("="*50)
    
    # Also call the full tailor_resume_with_claude function
    print("\n\nRUNNING FULL RESUME TAILORING PROCESS...")
    output_filename, output_path = tailor_resume_with_claude(
        resume_path,
        job_data,
        api_key,
        None  # API URL is optional
    )
    print(f"Resume tailored successfully!")
    print(f"Output file: {output_path}")
        
except Exception as e:
    print(f"\nError in test: {str(e)}")
    print(traceback.format_exc())

# Test the logger directly
print("\nTesting Claude API logger...")
try:
    test_log = api_logger.log_api_call(
        request_data={"test": "Request data"},
        response_data={"test": "Response data"},
        resume_id="test-resume",
        section="test-section",
        token_usage={"input_tokens": 100, "output_tokens": 50}
    )
    print(f"Test log successful: {test_log}")
except Exception as e:
    print(f"Error testing logger: {str(e)}")
    print(traceback.format_exc())

# Check if log file was created
log_dir = "logs"
log_files = [f for f in os.listdir(log_dir) if f.startswith("claude_api_log_")]

if log_files:
    print(f"\nLog files created:")
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
                        # Display the first log entry's timestamp and section
                        print(f"   Latest entry: {logs[-1].get('timestamp')} - Section: {logs[-1].get('section')}")
                else:
                    print("   Empty log file")
        except Exception as e:
            print(f"   Error reading log: {str(e)}")
else:
    print("\nNo log files were created.") 