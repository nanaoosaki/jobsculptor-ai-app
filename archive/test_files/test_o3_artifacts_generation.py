#!/usr/bin/env python3
"""
O3 Artifacts Generation Script

This script generates the three critical artifacts O3 needs to fix the bullet consistency issue:

1. A failing DOCX file BEFORE any reconciliation runs
2. Full DEBUG logs showing the first place apply_native_bullet() throws
3. Documentation of all post-processing utilities that run after the main build

Usage:
    python test_o3_artifacts_generation.py

Outputs:
    - o3_artifact_1_failing_before_reconciliation.docx
    - o3_artifact_2_full_debug_log.txt  
    - o3_artifact_3_post_processing_analysis.md
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure comprehensive DEBUG logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('o3_artifact_2_full_debug_log.txt', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_test_resume_data():
    """Create comprehensive test resume data that includes problematic bullets."""
    
    # Create a realistic experience section with multiple companies and achievements
    # This should trigger the consistency issue
    experience_data = {
        "companies": [
            {
                "company": "Landmark Health LLC",
                "location": "Remote",
                "position": "Senior Software Engineer", 
                "dates": "Jan 2022 - Present",
                "role_description": "Lead development of healthcare data processing systems",
                "achievements": [
                    "Developed RESTful APIs using Django Rest Framework, serving over 1 million requests per day",
                    "Optimized database queries resulting in 30% performance improvement",
                    "Implemented CI/CD pipeline using GitHub Actions reducing deployment time by 50%",
                    "Led migration of legacy systems to microservices architecture",
                    "Mentored 3 junior developers on best practices and code review processes",
                    "Built automated testing suite achieving 95% code coverage"
                ]
            },
            {
                "company": "TechCorp Solutions",
                "location": "San Francisco, CA",
                "position": "Software Engineer",
                "dates": "Mar 2020 - Dec 2021", 
                "role_description": "Full-stack development for enterprise applications",
                "achievements": [
                    "Built responsive web applications using React and Node.js",
                    "Designed and implemented MySQL database schemas for multiple projects",
                    "Collaborated with cross-functional teams to deliver features on schedule",
                    "Created comprehensive documentation for APIs and system architecture",
                    "Participated in code reviews and contributed to team coding standards"
                ]
            },
            {
                "company": "DataTech Innovations",
                "location": "Austin, TX",
                "position": "Junior Developer",
                "dates": "Jun 2019 - Feb 2020",
                "role_description": "Entry-level development role focusing on data analysis tools",
                "achievements": [
                    "Developed data visualization dashboards using Python and Matplotlib",
                    "Wrote ETL scripts to process large datasets from various sources",
                    "Automated manual reporting processes saving 10 hours per week",
                    "Learned agile development methodologies and participated in sprint planning"
                ]
            }
        ]
    }
    
    education_data = {
        "institutions": [
            {
                "institution": "University of California, Berkeley",
                "location": "Berkeley, CA",
                "degree": "Bachelor of Science in Computer Science",
                "dates": "2015 - 2019",
                "highlights": [
                    "GPA: 3.8/4.0",
                    "Dean's List: Fall 2017, Spring 2018, Fall 2018",
                    "Relevant coursework: Data Structures, Algorithms, Database Systems, Software Engineering"
                ]
            }
        ]
    }
    
    projects_data = {
        "projects": [
            {
                "title": "Personal Finance Tracker",
                "dates": "2021",
                "details": [
                    "Built full-stack web application using React, Express, and PostgreSQL",
                    "Implemented user authentication and authorization with JWT tokens", 
                    "Created RESTful API for managing financial transactions and budgets",
                    "Deployed application to AWS using Docker containers"
                ]
            }
        ]
    }
    
    return {
        "experience": experience_data,
        "education": education_data, 
        "projects": projects_data,
        "contact": {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "(555) 123-4567",
            "location": "San Francisco, CA"
        },
        "summary": {
            "content": "Experienced software engineer with 5+ years of expertise in full-stack development, database optimization, and cloud infrastructure. Proven track record of delivering scalable solutions and leading technical teams."
        },
        "skills": {
            "Programming Languages": ["Python", "JavaScript", "Java", "SQL"],
            "Frameworks & Tools": ["Django", "React", "Node.js", "Docker", "AWS"],
            "Databases": ["PostgreSQL", "MySQL", "MongoDB"]
        }
    }

def save_test_data_files(test_data, request_id, temp_dir):
    """Save test data to individual JSON files as the application expects."""
    
    temp_dir_path = Path(temp_dir)
    temp_dir_path.mkdir(exist_ok=True)
    
    # Save each section to its own file
    for section_name, section_data in test_data.items():
        file_path = temp_dir_path / f"{request_id}_{section_name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(section_data, f, indent=2)
        logger.info(f"Saved test data: {file_path}")

def analyze_post_processing_utilities():
    """
    Analyze and document all post-processing utilities that run after the main build.
    This provides O3 Artifact 3.
    """
    
    analysis = f"""# O3 Artifact 3: Post-Processing Utilities Analysis

Generated: {datetime.now().isoformat()}

## Overview
This document analyzes all post-processing utilities that run after the main DOCX build process in `utils/docx_builder.py`.

## Post-Processing Sequence in build_docx()

Based on analysis of the `build_docx()` function, the following post-processing utilities run AFTER all content has been generated:

### 1. tighten_before_headers(doc)
- **Location**: Line 1626 in utils/docx_builder.py  
- **Purpose**: Finds paragraphs before section headers and sets spacing to zero
- **Bullet Impact**: ⚠️ **POTENTIAL ISSUE** - Modifies paragraph spacing which could affect bullet formatting
- **Details**:
  - Removes existing spacing elements: `p_pr.remove(existing)` for `'./w:spacing'`
  - Adds new spacing XML: `<w:spacing w:after="0"/>`
  - Also sets via API: `prev_para.paragraph_format.space_after = Pt(0)`
  - **CRITICAL**: This utility directly modifies XML and paragraph formatting AFTER bullets are created

### 2. _cleanup_bullet_direct_formatting(doc)  
- **Location**: Called as "o3's Nuclear Option"
- **Purpose**: Remove all direct indentation from bullet paragraphs
- **Bullet Impact**: 🎯 **DIRECTLY AFFECTS BULLETS** - This is reconciliation, not post-processing
- **Details**:
  - Sets `para.paragraph_format.left_indent = None`
  - Sets `para.paragraph_format.first_line_indent = None`
  - Only affects paragraphs with `style.name == "MR_BulletPoint"`

### 3. Style Registry Utilities (if USE_STYLE_REGISTRY=True)
- **remove_empty_paragraphs(doc)**: Called within `tighten_before_headers`
- **Purpose**: Removes unwanted empty paragraphs
- **Bullet Impact**: ⚠️ **POTENTIAL ISSUE** - Could affect document structure and paragraph references

### 4. _create_robust_company_style(doc)
- **Location**: Called as backup if MR_Company style missing
- **Purpose**: Creates/updates MR_Company style with XML manipulation
- **Bullet Impact**: ❓ **UNKNOWN** - Style creation could have side effects

## Critical Findings

### Post-Processing That Could Affect Bullets:

1. **tighten_before_headers()** - This utility runs AFTER all bullets are created and:
   - Modifies XML spacing elements on paragraphs
   - Could potentially interfere with bullet paragraph formatting
   - Uses both XML manipulation AND API calls which could conflict

2. **remove_empty_paragraphs()** - This utility:
   - Actually removes paragraphs from the document
   - Could cause `doc.paragraphs` list to become stale
   - Runs during `tighten_before_headers()` which is after bullet creation

### Potential Root Cause:
The `tighten_before_headers()` utility runs AFTER bullets are created and modifies paragraph formatting. This could be interfering with the native numbering system.

## Recommendation for O3:
Test disabling `tighten_before_headers()` to see if bullet consistency improves. This utility modifies paragraph XML after bullets are applied, which could be causing the failures.

## Code References:
- `tighten_before_headers()`: lines 795-882 in utils/docx_builder.py
- `remove_empty_paragraphs()`: imported from word_styles.section_builder
- `_cleanup_bullet_direct_formatting()`: lines 1002-1033 in utils/docx_builder.py
- `_create_robust_company_style()`: lines 1837-1874 in utils/docx_builder.py

## Test Suggestion:
Create a version of `build_docx()` that skips `tighten_before_headers()` and see if bullet consistency is maintained.
"""
    
    with open('o3_artifact_3_post_processing_analysis.md', 'w', encoding='utf-8') as f:
        f.write(analysis)
    
    logger.info("✅ Generated O3 Artifact 3: Post-processing analysis")
    return analysis

def main():
    """Main function to generate all O3 artifacts."""
    
    logger.info("🚨 Starting O3 Artifacts Generation")
    logger.info("=" * 60)
    
    # Generate test data
    request_id = "o3_test_artifacts_2025"
    temp_dir = "static/uploads/temp_session_data"
    
    logger.info(f"Creating test data for request_id: {request_id}")
    test_data = create_test_resume_data()
    save_test_data_files(test_data, request_id, temp_dir)
    
    # Generate O3 Artifact 3 first (post-processing analysis)
    logger.info("🚨 Generating O3 Artifact 3: Post-processing analysis")
    analyze_post_processing_utilities()
    
    # Import and run the DOCX builder with full DEBUG logging
    logger.info("🚨 Generating O3 Artifacts 1 & 2: DOCX and DEBUG logs")
    
    try:
        from utils.docx_builder import build_docx
        
        # This will generate:
        # - O3 Artifact 1: Pre-reconciliation DOCX (saved automatically by our modified build_docx)
        # - O3 Artifact 2: Full DEBUG logs (captured by our logging configuration)
        
        logger.info(f"🚨 Calling build_docx with request_id: {request_id}")
        logger.info(f"🚨 This should capture the first apply_native_bullet() failure")
        
        docx_output = build_docx(request_id, temp_dir, debug=True)
        
        # Save the final DOCX as well for comparison
        final_docx_path = f"o3_artifact_final_docx_{request_id}.docx"
        with open(final_docx_path, 'wb') as f:
            f.write(docx_output.getvalue())
        
        logger.info(f"✅ Generated final DOCX: {final_docx_path}")
        
    except Exception as e:
        logger.error(f"🚨 Exception during build_docx: {type(e).__name__}: {e}")
        logger.error(f"🚨 This exception should be captured in the DEBUG log")
        logger.error(f"🚨 Full traceback:")
        import traceback
        logger.error(traceback.format_exc())
    
    logger.info("=" * 60)
    logger.info("🚨 O3 Artifacts Generation Complete")
    logger.info("")
    logger.info("Generated artifacts:")
    logger.info("  1. o3_artifact_2_full_debug_log.txt - Complete DEBUG log")
    logger.info("  2. o3_artifact_3_post_processing_analysis.md - Post-processing analysis") 
    logger.info("  3. pre_reconciliation_*.docx - DOCX before reconciliation (auto-generated)")
    logger.info("  4. pre_reconciliation_debug_*.json - Debug analysis (auto-generated)")
    logger.info(f"  5. o3_artifact_final_docx_{request_id}.docx - Final DOCX for comparison")
    logger.info("")
    logger.info("These artifacts can now be provided to O3 for final analysis.")

if __name__ == "__main__":
    main() 