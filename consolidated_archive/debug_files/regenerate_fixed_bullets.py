#!/usr/bin/env python3
"""
Regenerate Test Document with Fixed Bullet Spacing

This script regenerates the complete test document with the fixed bullet spacing
implementation that ensures zero spacing between bullets.
"""

import os
import sys
import tempfile
import json
import shutil
from pathlib import Path
from docx import Document

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_test_data_files(temp_dir: str, request_id: str):
    """Create test JSON files for complete document generation."""
    
    # Contact data
    contact_data = {
        "name": "Alex Johnson",
        "email": "alex.johnson@email.com",
        "phone": "(555) 123-4567",
        "location": "San Francisco, CA",
        "linkedin": "linkedin.com/in/alexjohnson"
    }
    
    # Experience data with achievements (more bullets to test spacing)
    experience_data = {
        "experiences": [
            {
                "company": "Tech Corp",
                "title": "Senior Software Engineer",
                "start_date": "2022-01",
                "end_date": "Present",
                "location": "San Francisco, CA",
                "achievements": [
                    "Built scalable microservices handling 10M+ requests daily",
                    "Led team of 5 engineers in modernizing legacy systems", 
                    "Reduced deployment time by 70% through CI/CD optimization",
                    "Implemented real-time analytics dashboard for business intelligence",
                    "Designed and deployed containerized applications using Docker and Kubernetes",
                    "Established comprehensive monitoring and alerting systems with Prometheus"
                ]
            },
            {
                "company": "Startup Inc",
                "title": "Full Stack Developer",
                "start_date": "2020-03", 
                "end_date": "2021-12",
                "location": "Remote",
                "achievements": [
                    "Developed React frontend with 99.9% uptime SLA",
                    "Optimized database queries reducing response time by 50%",
                    "Integrated payment processing for $2M+ annual revenue",
                    "Built responsive user interface with modern CSS Grid and Flexbox",
                    "Implemented automated testing pipeline with Jest and Cypress"
                ]
            }
        ]
    }
    
    # Education data with highlights
    education_data = {
        "education": [
            {
                "institution": "University of California, Berkeley",
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "start_date": "2016-08",
                "end_date": "2020-05", 
                "location": "Berkeley, CA",
                "highlights": [
                    "Magna Cum Laude, GPA: 3.8/4.0",
                    "Dean's List for 6 semesters",
                    "Captain of Programming Competition Team",
                    "Teaching Assistant for Data Structures course",
                    "Published research paper on distributed computing algorithms"
                ]
            }
        ]
    }
    
    # Projects data with details
    projects_data = {
        "projects": [
            {
                "name": "E-Commerce Platform",
                "technologies": "React, Node.js, MongoDB",
                "start_date": "2023-01",
                "end_date": "2023-06",
                "details": [
                    "Built responsive web application with React and TypeScript",
                    "Implemented secure authentication with JWT tokens", 
                    "Created RESTful API with comprehensive error handling",
                    "Deployed on AWS with auto-scaling configuration",
                    "Integrated Stripe payment processing with webhook handling",
                    "Achieved 99.9% uptime with comprehensive monitoring"
                ]
            }
        ]
    }
    
    # Summary data
    summary_data = {
        "summary": "Experienced software engineer with 4+ years building scalable web applications. Expertise in full-stack development, cloud architecture, and team leadership. Passionate about clean code, performance optimization, and mentoring junior developers."
    }
    
    # Write all test files
    test_files = {
        "contact": contact_data,
        "experience": experience_data,
        "education": education_data,
        "projects": projects_data,
        "summary": summary_data
    }
    
    for section, data in test_files.items():
        file_path = os.path.join(temp_dir, f"{request_id}_{section}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Created: {file_path}")
    
    return temp_dir

def main():
    """Generate complete document with fixed bullet spacing."""
    print("🚀 REGENERATING COMPLETE DOCUMENT - FIXED BULLET SPACING")
    print("=" * 60)
    
    # Enable native bullets for testing
    os.environ['DOCX_USE_NATIVE_BULLETS'] = 'true'
    
    try:
        # Create temporary directory and test data
        temp_dir = tempfile.mkdtemp()
        request_id = "test_fixed_spacing"
        print(f"📂 Using temp directory: {temp_dir}")
        
        create_test_data_files(temp_dir, request_id)
        
        # Import and generate document
        from utils.docx_builder import build_docx, NATIVE_BULLETS_ENABLED
        
        print(f"🎯 Native bullets enabled: {NATIVE_BULLETS_ENABLED}")
        print("📄 Generating complete document with fixed bullet spacing...")
        
        # Generate complete document
        docx_buffer = build_docx(request_id, temp_dir, debug=False)
        
        # Save the generated document
        output_path = "test_complete_document_fixed.docx"
        with open(output_path, 'wb') as f:
            f.write(docx_buffer.getvalue())
        
        print(f"✅ Saved: {output_path}")
        
        # Also create a backup copy with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"test_bullets_fixed_{timestamp}.docx"
        with open(backup_path, 'wb') as f:
            f.write(docx_buffer.getvalue())
        
        print(f"✅ Backup saved: {backup_path}")
        
        # Cleanup temp directory
        shutil.rmtree(temp_dir)
        
        print("\n🎉 COMPLETE DOCUMENT REGENERATED WITH FIXED BULLET SPACING!")
        print("📋 Generated documents:")
        print(f"   📄 {output_path} - Main test document")
        print(f"   📄 {backup_path} - Timestamped backup")
        print("\n✨ Ready for testing - bullet spacing should now be zero!")
        
        # Also test bullet flag combinations
        print("\n🧪 Testing bullet flag combinations...")
        
        # Test with native bullets disabled
        os.environ['DOCX_USE_NATIVE_BULLETS'] = 'false'
        
        # Reload module to pick up environment change
        import importlib
        import utils.docx_builder
        importlib.reload(utils.docx_builder)
        
        from utils.docx_builder import build_docx as build_docx_legacy
        
        temp_dir_legacy = tempfile.mkdtemp()
        create_test_data_files(temp_dir_legacy, "test_legacy_fixed")
        
        docx_buffer_legacy = build_docx_legacy("test_legacy_fixed", temp_dir_legacy, debug=False)
        
        legacy_path = "test_complete_document_legacy_fixed.docx"
        with open(legacy_path, 'wb') as f:
            f.write(docx_buffer_legacy.getvalue())
        
        print(f"✅ Legacy version saved: {legacy_path}")
        
        shutil.rmtree(temp_dir_legacy)
        
        print("\n📊 COMPARISON TEST:")
        print(f"   📄 {output_path} - Native bullets with zero spacing")
        print(f"   📄 {legacy_path} - Legacy bullets with zero spacing")
        print("\n🔍 Both should now have tight bullet spacing!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main() 