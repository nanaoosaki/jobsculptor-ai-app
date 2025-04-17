import os
import json
import time
from dotenv import load_dotenv
from claude_integration import ClaudeClient
from claude_api_logger import api_logger
import traceback

# Load environment variables
load_dotenv()

# Get API key
api_key = os.environ.get("CLAUDE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")

if not api_key:
    print("Error: No Claude API key found in environment variables.")
    print("Make sure CLAUDE_API_KEY or ANTHROPIC_API_KEY is set in your .env file.")
    exit(1)

# Sample data for testing
sample_resume_content = """
DIRECTV	LOS ANGELES, CA
Principal Data Scientist & Technical Lead, Video Analytics	Dec 2021 - Present
Strategic vision & execution for streaming platform video intelligence, 3M+ subscribers, ML initiatives with executives

Video content platform, 36% engagement increase, semantic analysis + behavior patterns, personalized recs.
Computer vision auto-tagging system, 85% manual effort reduction, 40% content discovery improvement.
Video quality assessment models, 40% streaming issues reduction, increased retention on underperforming devices.
Cross-functional partnerships (Product, UX, Content), next-gen video roadmap, secured $2.5M funding.
"""

sample_job_requirements = """
Job Title: Principal Data Scientist - AI Foundations, Specialist Models
Company: Capital One

Requirements:
- Experience with Python, AWS, PyTorch, Machine Learning, Deep Learning, AI, NLP
- Experience working with cross-functional teams to deliver data science solutions

Skills:
- Python
- AWS
- PyTorch
- Machine Learning
- Deep Learning
- AI
- NLP
- Data Science
- Big Data
- Spark
- H2O
- Conda
"""

# First, let's directly test our logging function
print("Testing Claude API logger directly...")
try:
    # Clear any existing log file
    log_dir = "logs"
    log_file = os.path.join(log_dir, f"claude_api_log_{time.strftime('%Y-%m-%d')}.json")
    with open(log_file, 'w') as f:
        f.write("[]")
    
    # Test logging function
    test_log = api_logger.log_api_call(
        request_data={"test": "Direct test request data", "prompt": "Sample prompt"},
        response_data={"test": "Direct test response data", "tailored_content": "Sample tailored content"},
        resume_id="test-logger",
        section="direct-test",
        token_usage={"input_tokens": 100, "output_tokens": 50}
    )
    print(f"Direct logger test successful: {test_log}")
    
    # Now read back the log to verify
    with open(log_file, 'r') as f:
        log_content = f.read()
        logs = json.loads(log_content)
        print(f"Log file now has {len(logs)} entries")
        
        # Verify the latest entry
        latest_log = logs[-1]
        print(f"Latest log entry:")
        print(f"- Timestamp: {latest_log.get('timestamp')}")
        print(f"- Section: {latest_log.get('section')}")
        print(f"- Resume ID: {latest_log.get('resume_id')}")
        
        response_data = latest_log.get('response', {})
        if 'tailored_content' in response_data:
            print(f"- Has tailored content: Yes")
            print(f"- Content: {response_data['tailored_content']}")
        else:
            print(f"- Has tailored content: No")
except Exception as e:
    print(f"Error in direct logger test: {str(e)}")
    print(traceback.format_exc())

# Now test the Claude client with logging
print("\n\nTesting Claude client with logging...")
try:
    # Create Claude client
    claude_client = ClaudeClient(api_key)
    
    # Call the Claude API with the sample data
    print(f"Calling Claude API to tailor resume content...")
    tailored_content = claude_client.tailor_resume_content(
        sample_resume_content,
        sample_job_requirements,
        "experience",
        "test-client"
    )
    
    print(f"\nTailored content received:")
    print("=" * 50)
    print(tailored_content[:500] + "..." if len(tailored_content) > 500 else tailored_content)
    print("=" * 50)
    
    # Check for log entries
    print("\nChecking log file for Claude API call...")
    time.sleep(1)  # Give time for logs to be written
    
    with open(log_file, 'r') as f:
        log_content = f.read()
        logs = json.loads(log_content)
        print(f"Log file now has {len(logs)} entries")
        
        # Find the entry with resume_id == "test-client"
        client_logs = [log for log in logs if log.get('resume_id') == "test-client"]
        if client_logs:
            print(f"Found {len(client_logs)} logs for test-client")
            latest = client_logs[-1]
            
            print(f"Latest client log entry:")
            print(f"- Timestamp: {latest.get('timestamp')}")
            print(f"- Section: {latest.get('section')}")
            
            response_data = latest.get('response', {})
            if 'tailored_content' in response_data:
                print(f"- Has tailored content: Yes")
                print(f"- Content preview: {response_data['tailored_content'][:100]}...")
                print(f"- Token usage: {latest.get('token_usage')}")
            else:
                print(f"- Has tailored content: No")
                print(f"- Full response data: {response_data}")
        else:
            print("No logs found for test-client")
    
except Exception as e:
    print(f"Error in Claude client test: {str(e)}")
    print(traceback.format_exc()) 