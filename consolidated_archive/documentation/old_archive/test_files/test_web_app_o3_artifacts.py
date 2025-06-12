#!/usr/bin/env python3
"""
Test Web App O3 Artifacts Integration

This script tests that the O3 artifact generation infrastructure works
when a user uploads a real resume through the web application.

Usage:
    1. Start the Flask app: python app.py
    2. Run this test: python test_web_app_o3_artifacts.py
"""

import requests
import json
import os
import tempfile
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
TEST_RESUME_PATH = "NanaWangResume_v1.docx"  # Update this to an actual resume file

def test_o3_artifacts_via_web_app():
    """Test that O3 artifacts are generated when using the web app normally."""
    
    print("🧪 Testing O3 Artifact Generation via Web App")
    print("=" * 60)
    
    # Check if test resume exists
    if not os.path.exists(TEST_RESUME_PATH):
        print(f"❌ Test resume not found: {TEST_RESUME_PATH}")
        print("Please update TEST_RESUME_PATH to point to an actual resume file.")
        return False
        
    print(f"📄 Using test resume: {TEST_RESUME_PATH}")
    
    # Step 1: Upload resume
    print("\n1. Uploading resume...")
    with open(TEST_RESUME_PATH, 'rb') as f:
        files = {'resume': f}
        response = requests.post(f"{BASE_URL}/upload-resume", files=files)
    
    if response.status_code != 200:
        print(f"❌ Resume upload failed: {response.status_code}")
        print(response.text)
        return False
        
    upload_data = response.json()
    print(f"✅ Resume uploaded: {upload_data.get('filename')}")
    resume_filename = upload_data.get('filename')
    
    # Step 2: Create simple job data (simulate job parsing)
    print("\n2. Creating test job requirements...")
    test_job_data = {
        "job_title": "Senior Software Engineer",
        "company": "Test Company Inc.",
        "complete_job_text": """
We are seeking a Senior Software Engineer to join our dynamic team.

Requirements:
• 5+ years of software development experience
• Proficiency in Python, JavaScript, or Java
• Experience with cloud platforms (AWS, GCP, Azure)
• Strong problem-solving skills
• Excellent communication abilities

Responsibilities:
• Design and implement scalable software solutions
• Collaborate with cross-functional teams
• Mentor junior developers
• Participate in code reviews and technical discussions
        """,
        "analysis": {
            "hard_skills": ["Python", "JavaScript", "Java", "AWS", "Cloud Platforms"],
            "soft_skills": ["Problem-solving", "Communication", "Leadership"],
            "candidate_profile": "Senior-level software engineer with cloud experience"
        }
    }
    
    # Step 3: Tailor resume (this should trigger O3 artifact generation)
    print("\n3. Tailoring resume (should generate O3 artifacts)...")
    tailor_data = {
        "resumeFilename": resume_filename,
        "jobRequirements": test_job_data,
        "llmProvider": "claude"  # Use Claude for testing
    }
    
    response = requests.post(f"{BASE_URL}/tailor-resume", json=tailor_data)
    
    if response.status_code != 200:
        print(f"❌ Resume tailoring failed: {response.status_code}")
        print(response.text)
        return False
        
    tailor_result = response.json()
    if not tailor_result.get('success'):
        print(f"❌ Tailoring reported failure: {tailor_result.get('error')}")
        return False
        
    request_id = tailor_result.get('request_id')
    print(f"✅ Resume tailored successfully. Request ID: {request_id}")
    
    # Step 4: Check for O3 artifacts
    print("\n4. Checking for O3 artifacts...")
    response = requests.get(f"{BASE_URL}/o3-artifacts/{request_id}")
    
    if response.status_code != 200:
        print(f"❌ Failed to check O3 artifacts: {response.status_code}")
        return False
        
    artifacts_data = response.json()
    if not artifacts_data.get('success'):
        print(f"❌ No O3 artifacts found: {artifacts_data.get('error')}")
        return False
        
    artifacts = artifacts_data.get('artifacts', {})
    print(f"✅ Found {artifacts_data.get('artifact_count')} O3 artifacts:")
    
    for artifact_name, artifact_url in artifacts.items():
        print(f"   📁 {artifact_name}: {artifact_url}")
        
        # Try to download each artifact to verify it exists
        artifact_response = requests.get(f"{BASE_URL}{artifact_url}")
        if artifact_response.status_code == 200:
            file_size = len(artifact_response.content)
            print(f"      ✅ Downloadable ({file_size:,} bytes)")
        else:
            print(f"      ❌ Download failed ({artifact_response.status_code})")
    
    # Step 5: Test the normal downloads still work
    print("\n5. Testing normal DOCX download...")
    docx_response = requests.get(f"{BASE_URL}/download/docx/{request_id}")
    if docx_response.status_code == 200:
        print(f"✅ DOCX download works ({len(docx_response.content):,} bytes)")
    else:
        print(f"❌ DOCX download failed: {docx_response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎉 O3 Artifact Integration Test Complete!")
    print(f"Request ID for manual testing: {request_id}")
    print(f"Web UI artifacts URL: {BASE_URL}/o3-artifacts/{request_id}")
    
    return True

def check_app_running():
    """Check if the Flask app is running."""
    try:
        response = requests.get(BASE_URL, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

if __name__ == "__main__":
    # Check if Flask app is running
    if not check_app_running():
        print("❌ Flask app is not running!")
        print(f"Please start the app first: python app.py")
        print(f"Expected URL: {BASE_URL}")
        exit(1)
    
    # Run the test
    success = test_o3_artifacts_via_web_app()
    
    if success:
        print("\n✅ All tests passed! O3 artifacts are working in the web app.")
    else:
        print("\n❌ Some tests failed. Check the output above.") 