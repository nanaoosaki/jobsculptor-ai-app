import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.environ.get("CLAUDE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")

if not api_key:
    print("Error: No Claude API key found in environment variables.")
    print("Make sure CLAUDE_API_KEY or ANTHROPIC_API_KEY is set in your .env file.")
    exit(1)

# Initialize the Anthropic client
claude = Anthropic(api_key=api_key)

# Sample resume section (experience)
resume_section = """
DIRECTV	LOS ANGELES, CA
Principal Data Scientist & Technical Lead, Video Analytics	Dec 2021 - Present
Strategic vision & execution for streaming platform video intelligence, 3M+ subscribers, ML initiatives with executives

Video content platform, 36% engagement increase, semantic analysis + behavior patterns, personalized recs.
Computer vision auto-tagging system, 85% manual effort reduction, 40% content discovery improvement.
Video quality assessment models, 40% streaming issues reduction, increased retention on underperforming devices.
Cross-functional partnerships (Product, UX, Content), next-gen video roadmap, secured $2.5M funding.
"""

# Sample job description
job_description = """
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
- Decision-making
- Interpersonal skills
"""

print("===== TESTING DIRECT CLAUDE API CALL =====")
print("\nSample Resume Section (Experience):")
print("-" * 50)
print(resume_section)
print("-" * 50)

print("\nSample Job Description:")
print("-" * 50)
print(job_description)
print("-" * 50)

# Create the prompt for Claude
prompt = f"""
You are an expert resume writer helping a job applicant tailor their resume to a specific job posting.
Your task is to significantly improve the following experience section to match the job requirements.

JOB REQUIREMENTS:
{job_description}

CURRENT EXPERIENCE SECTION:
{resume_section}

Please rewrite this experience section to:
1. Make BOLD, SIGNIFICANT changes that highlight relevant skills and experiences matching the job requirements
2. Use strong action verbs and quantify achievements where possible
3. Remove irrelevant information
4. Add relevant keywords from the job posting (even if not in the original resume)
5. Maintain a professional tone
6. Visibly reorganize and restructure content to better match the job requirements

IMPORTANT: Your changes should be significant and noticeable. A good tailored resume should look different from the original.

IMPROVED EXPERIENCE SECTION:
"""

# Send to Claude API
print("\nSending to Claude API...\n")
response = claude.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": prompt}
    ]
)

# Display results
print("\nCLAUDE API RESPONSE (TAILORED EXPERIENCE SECTION):")
print("=" * 50)
print(response.content[0].text)
print("=" * 50)

print("\nTOKEN USAGE:")
print(f"- Input tokens: {response.usage.input_tokens}")
print(f"- Output tokens: {response.usage.output_tokens}")
print(f"- Total tokens: {response.usage.input_tokens + response.usage.output_tokens}") 