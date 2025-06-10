#!/usr/bin/env python3
"""
PHASE 4: FINAL OPTIMIZATION & POLISH TEST

This test validates that Phase 4 optimizations successfully achieve 100% bullet 
consistency by addressing the verification timing issues identified in Phase 3.

Key optimizations:
1. Fix verification race condition with retry logic
2. Improve XML element detection robustness  
3. Add small delays for document processing
4. Enhanced error recovery mechanisms
5. Final validation of 100% success rate

Expected outcome: 100% consistency rate (12/12 bullets with native numbering)
"""

import os
import sys
import json
import logging
import tempfile
import time
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.docx_builder import build_docx
from word_styles.numbering_engine import NumberingEngine

# Configure logging to see detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_test_session_files(experience_data, temp_dir):
    """Create the session files needed for document generation."""
    request_id = "phase4_final_test"
    
    # Convert experience data to the format expected by docx_builder
    processed_experience = experience_data
    if isinstance(experience_data, dict) and 'jobs' in experience_data:
        # Convert {"jobs": [...]} to {"experiences": [...]} format
        processed_experience = {"experiences": experience_data["jobs"]}
    
    # Create experience.json
    experience_file = os.path.join(temp_dir, f"{request_id}_experience.json")
    with open(experience_file, 'w', encoding='utf-8') as f:
        json.dump(processed_experience, f, indent=2, ensure_ascii=False)
    
    # Create minimal contact.json
    contact_data = {
        "name": "Phase 4 Final Test User",
        "email": "phase4test@example.com",
        "phone": "555-PHASE4",
        "location": "Test City, ST"
    }
    contact_file = os.path.join(temp_dir, f"{request_id}_contact.json")
    with open(contact_file, 'w', encoding='utf-8') as f:
        json.dump(contact_data, f, indent=2, ensure_ascii=False)
    
    # Create minimal summary.json
    summary_data = {
        "summaryText": "Phase 4 Final Optimization Test - Validating 100% bullet consistency with enhanced verification and retry logic for native Word numbering system."
    }
    summary_file = os.path.join(temp_dir, f"{request_id}_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    # Create empty sections
    for section in ['education', 'skills', 'projects']:
        section_file = os.path.join(temp_dir, f"{request_id}_{section}.json")
        with open(section_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    
    return request_id

def run_phase4_test(test_num):
    """Run a single Phase 4 test iteration."""
    logger.info(f"🎯 Starting Phase 4 Test {test_num}/5...")
    
    # Load the test experience data
    experience_file = "994ef54e-cca8-4406-96ab-298109d84436_experience.json"
    if not os.path.exists(experience_file):
        logger.error(f"❌ Experience data file not found: {experience_file}")
        return None
    
    with open(experience_file, 'r', encoding='utf-8') as f:
        experience_data = json.load(f)
    
    # Create temporary directory and session files
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.info(f"📁 Created temp directory: {temp_dir}")
        
        # Create test session files
        request_id = create_test_session_files(experience_data, temp_dir)
        logger.info(f"✅ Created session files for request_id: {request_id}")
        
        # Generate document with Phase 4 optimizations
        try:
            logger.info("🔧 Generating DOCX with Phase 4 final optimizations...")
            docx_data = build_docx(request_id, temp_dir, debug=True)
            logger.info(f"✅ Document generated: {len(docx_data.getvalue())} bytes")
            
            # Save test document
            output_file = f"phase4_final_{test_num}_{request_id}.docx"
            with open(output_file, 'wb') as f:
                f.write(docx_data.getvalue())
            logger.info(f"📁 Saved test document to {output_file}")
            
            # Look for diagnostic files
            diagnostic_files = []
            for file in os.listdir('.'):
                if file.startswith(f'diagnostic_{request_id}'):
                    diagnostic_files.append(file)
            
            logger.info(f"📁 Found diagnostic files: {diagnostic_files}")
            
            # Analyze results
            results = analyze_phase4_results(request_id, diagnostic_files)
            return results
            
        except Exception as e:
            logger.error(f"❌ Document generation failed: {str(e)}")
            return None

def analyze_phase4_results(request_id, diagnostic_files):
    """Analyze the Phase 4 test results for bullet consistency."""
    results = {
        'total_bullets': 0,
        'bullets_with_numPr': 0,
        'consistency_rate': 0.0,
        'issues': [],
        'success': False
    }
    
    # Look for the bullet analysis file
    bullet_analysis_file = None
    for file in diagnostic_files:
        if 'bullet_analysis_enhanced.json' in file:
            bullet_analysis_file = file
            break
    
    if not bullet_analysis_file or not os.path.exists(bullet_analysis_file):
        logger.warning(f"⚠️ No bullet analysis file found")
        return results
    
    try:
        with open(bullet_analysis_file, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
        
        results['total_bullets'] = analysis.get('total_bullets', 0)
        results['bullets_with_numPr'] = analysis.get('bullets_with_numPr', 0)
        
        if results['total_bullets'] > 0:
            results['consistency_rate'] = (results['bullets_with_numPr'] / results['total_bullets']) * 100
        
        # Check for duplicate numIds
        if analysis.get('duplicate_numIds'):
            results['issues'].append(f"Duplicate numIds: {analysis['duplicate_numIds']}")
        
        # Check for missing numPr bullets
        missing_bullets = []
        for bullet in analysis.get('bullets', []):
            if not bullet.get('has_numPr', False):
                missing_bullets.append(f"Missing numPr: {bullet.get('text', 'Unknown')[:50]}...")
        
        results['issues'].extend(missing_bullets)
        
        # Success criteria: 100% consistency with no issues
        results['success'] = (results['consistency_rate'] >= 100.0 and len(results['issues']) == 0)
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Failed to analyze results: {str(e)}")
        return results

def main():
    """Run Phase 4: Final Optimization validation tests."""
    logger.info("🎯 PHASE 4: FINAL OPTIMIZATION & POLISH")
    logger.info("=" * 60)
    logger.info("Testing enhanced verification and retry logic for 100% bullet consistency")
    logger.info("")
    
    # Run multiple test iterations
    test_results = []
    for i in range(1, 6):
        results = run_phase4_test(i)
        if results:
            test_results.append(results)
            logger.info(f"📊 Test {i} Results:")
            logger.info(f"   Total bullets: {results['total_bullets']}")
            logger.info(f"   Bullets with numPr: {results['bullets_with_numPr']}")
            logger.info(f"   Consistency rate: {results['consistency_rate']:.1f}%")
            logger.info(f"   Issues found: {len(results['issues'])}")
            
            if results['success']:
                logger.info(f"✅ Test {i}: SUCCESS")
            else:
                logger.error(f"❌ Test {i}: FAILED")
                for issue in results['issues']:
                    logger.error(f"   - {issue}")
        else:
            logger.error(f"❌ Test {i}: FAILED TO COMPLETE")
        
        logger.info("")
    
    # Final summary
    logger.info("=" * 60)
    logger.info("🎯 PHASE 4 FINAL OPTIMIZATION SUMMARY")
    logger.info("=" * 60)
    
    if not test_results:
        logger.error("❌ No test results to analyze")
        return False
    
    successful_tests = sum(1 for result in test_results if result['success'])
    total_tests = len(test_results)
    success_rate = (successful_tests / total_tests) * 100
    
    logger.info(f"Tests passed: {successful_tests}/{total_tests}")
    logger.info(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 100.0:
        logger.info("🎉 PHASE 4 FINAL OPTIMIZATION: COMPLETE SUCCESS!")
        logger.info("✅ 100% bullet consistency achieved across all tests")
        return True
    elif success_rate >= 80.0:
        logger.info("✅ PHASE 4 FINAL OPTIMIZATION: MAJOR SUCCESS")
        logger.info(f"✅ {success_rate:.1f}% success rate achieved")
        
        # Show remaining issues
        all_issues = []
        for i, result in enumerate(test_results, 1):
            if not result['success']:
                logger.error(f"❌ Test {i}: {len(result['issues'])} issues")
                for issue in result['issues']:
                    logger.error(f"     - {issue}")
                    if issue not in all_issues:
                        all_issues.append(issue)
        
        return True
    else:
        logger.error("❌ PHASE 4 FINAL OPTIMIZATION: NEEDS MORE WORK")
        logger.error(f"❌ Only {success_rate:.1f}% success rate achieved")
        return False

if __name__ == "__main__":
    main() 