#!/usr/bin/env python3
"""
Phase 1 Enhanced Diagnostic Test - O3's Bullet Consistency Analysis

This test validates the enhanced diagnostic instrumentation added in Phase 1,
using the actual user data that exhibits the bullet consistency issue.

Test data: 994ef54e-cca8-4406-96ab-298109d84436_experience.json
Expected behavior: Should detect mixed native/legacy bullet formatting
"""

import os
import sys
import json
import logging
import tempfile
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.docx_builder import build_docx, NATIVE_BULLETS_ENABLED
from word_styles.numbering_engine import NumberingEngine

# Configure logging to see all the enhanced diagnostic output
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def load_user_test_data():
    """Load the actual user data that shows the bullet consistency issue."""
    test_data_file = "994ef54e-cca8-4406-96ab-298109d84436_experience.json"
    
    if not os.path.exists(test_data_file):
        logger.error(f"❌ Test data file not found: {test_data_file}")
        logger.error("Please ensure the user's experience.json file is in the current directory")
        return None
    
    try:
        with open(test_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ Loaded test data from {test_data_file}")
        return data
    except Exception as e:
        logger.error(f"❌ Failed to load test data: {e}")
        return None

def create_test_session_files(experience_data, temp_dir):
    """Create the session files needed for document generation."""
    request_id = "phase1_diagnostic_test"
    
    # Convert experience data to the format expected by docx_builder
    processed_experience = experience_data
    if isinstance(experience_data, dict) and 'jobs' in experience_data:
        # Convert {"jobs": [...]} to {"experiences": [...]} format
        processed_experience = {"experiences": experience_data['jobs']}
        logger.info(f"🔧 Converted {len(experience_data['jobs'])} jobs to experiences format")
    elif isinstance(experience_data, list):
        # Convert [...] to {"experiences": [...]} format
        processed_experience = {"experiences": experience_data}
        logger.info(f"🔧 Converted {len(experience_data)} experiences to dict format")
    
    # Create experience.json
    experience_file = os.path.join(temp_dir, f"{request_id}_experience.json")
    with open(experience_file, 'w', encoding='utf-8') as f:
        json.dump(processed_experience, f, indent=2, ensure_ascii=False)
    
    # Create minimal summary.json
    summary_data = {
        "content": "Senior Software Engineer with expertise in Python, cloud technologies, and data analytics."
    }
    summary_file = os.path.join(temp_dir, f"{request_id}_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2)
    
    # Create minimal contact.json
    contact_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "555-0123",
        "location": "City, State"
    }
    contact_file = os.path.join(temp_dir, f"{request_id}_contact.json")
    with open(contact_file, 'w', encoding='utf-8') as f:
        json.dump(contact_data, f, indent=2)
    
    # Create empty files for other sections to avoid errors
    for section in ['education', 'skills', 'projects']:
        section_file = os.path.join(temp_dir, f"{request_id}_{section}.json")
        with open(section_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    
    logger.info(f"✅ Created test session files in {temp_dir}")
    return request_id

def analyze_diagnostic_results():
    """Analyze the diagnostic files created during document generation."""
    
    # Look for diagnostic files
    diagnostic_files = [
        f for f in os.listdir('.') 
        if f.startswith('diagnostic_phase1_diagnostic_test')
    ]
    
    if not diagnostic_files:
        logger.error("❌ No diagnostic files found!")
        return False
    
    logger.info(f"📁 Found diagnostic files: {diagnostic_files}")
    
    # Analyze the enhanced JSON diagnostic
    json_file = None
    for f in diagnostic_files:
        if f.endswith('_bullet_analysis_enhanced.json'):
            json_file = f
            break
    
    if json_file:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                diagnostic_data = json.load(f)
            
            logger.info("📊 DIAGNOSTIC ANALYSIS RESULTS:")
            logger.info(f"   Total bullets: {diagnostic_data.get('total_bullets', 0)}")
            logger.info(f"   Bullets with numPr: {diagnostic_data.get('bullets_with_numPr', 0)}")
            logger.info(f"   Unique numIds: {diagnostic_data.get('unique_numIds', [])}")
            logger.info(f"   Duplicate numIds: {diagnostic_data.get('duplicate_numIds', [])}")
            
            # Check consistency
            total_bullets = diagnostic_data.get('total_bullets', 0)
            bullets_with_numPr = diagnostic_data.get('bullets_with_numPr', 0)
            
            if total_bullets > 0:
                consistency_rate = (bullets_with_numPr / total_bullets) * 100
                logger.info(f"📊 CONSISTENCY RATE: {consistency_rate:.1f}%")
                
                if consistency_rate < 100:
                    logger.error(f"🚨 DETECTED BULLET CONSISTENCY ISSUE!")
                    logger.error(f"   {total_bullets - bullets_with_numPr} bullets missing numPr")
                    
                    # Show details of problematic bullets
                    for detail in diagnostic_data.get('bullet_details', []):
                        if not detail.get('has_numPr', False):
                            logger.error(f"   ❌ Missing numPr: {detail.get('text', '')}")
                    
                    return True  # Successfully detected the issue
                else:
                    logger.info(f"✅ All bullets have consistent native numbering")
                    return True  # Working correctly
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze diagnostic JSON: {e}")
            return False
    
    return False

def main():
    """Run Phase 1 enhanced diagnostic test."""
    logger.info("🚀 PHASE 1 ENHANCED DIAGNOSTIC TEST STARTING")
    logger.info(f"🔧 Native bullets enabled: {NATIVE_BULLETS_ENABLED}")
    
    # Load user test data
    experience_data = load_user_test_data()
    if not experience_data:
        logger.error("❌ Cannot proceed without test data")
        return False
    
    # Analyze the data structure
    if isinstance(experience_data, dict) and 'jobs' in experience_data:
        jobs = experience_data['jobs']
        logger.info(f"📋 Found {len(jobs)} jobs in experience data")
        
        # Focus on companies mentioned in the user's issue
        target_companies = ["Landmark Health LLC", "Capital Blue Cross", "Pennsylvania Department of Education"]
        for job in jobs:
            company = job.get('company', 'Unknown')
            if company in target_companies:
                achievements = job.get('achievements', [])
                logger.info(f"🎯 TARGET COMPANY: {company} has {len(achievements)} achievements")
                for i, achievement in enumerate(achievements):
                    logger.info(f"   {i+1}. {achievement[:60]}{'...' if len(achievement) > 60 else ''}")
    
    # Create temporary directory for session files
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.info(f"📁 Using temporary directory: {temp_dir}")
        
        # Create session files
        request_id = create_test_session_files(experience_data, temp_dir)
        
        try:
            # Generate document with enhanced diagnostics
            logger.info("🔨 GENERATING DOCX WITH ENHANCED DIAGNOSTICS...")
            docx_buffer = build_docx(request_id, temp_dir, debug=True)
            
            logger.info(f"✅ Document generated successfully: {len(docx_buffer.getvalue())} bytes")
            
            # Save the generated document for inspection
            output_file = f"phase1_diagnostic_test_{request_id}.docx"
            with open(output_file, 'wb') as f:
                f.write(docx_buffer.getvalue())
            logger.info(f"📁 Saved test document to {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Document generation failed: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return False
    
    # Analyze diagnostic results
    logger.info("🔍 ANALYZING DIAGNOSTIC RESULTS...")
    success = analyze_diagnostic_results()
    
    if success:
        logger.info("✅ PHASE 1 DIAGNOSTIC TEST COMPLETED SUCCESSFULLY")
        logger.info("✅ Enhanced diagnostic instrumentation is working correctly")
        return True
    else:
        logger.error("❌ PHASE 1 DIAGNOSTIC TEST FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 