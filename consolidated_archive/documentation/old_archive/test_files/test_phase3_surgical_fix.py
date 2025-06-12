#!/usr/bin/env python3
"""
PHASE 3: SURGICAL FIX VALIDATION TEST

This test validates that the surgical fix implemented in Phase 3 successfully 
eliminates the race condition that was causing silent failures in native bullet 
creation, achieving 100% bullet consistency.

Key validation points:
1. All bullets get native numbering (no legacy fallbacks)  
2. No silent failures occur during bullet creation
3. Proper numPr elements exist for every bullet
4. All numId values are correct and consistent
5. Multiple test runs show stable results

Expected outcome: 100% consistency rate (12/12 bullets with native numbering)
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

# Configure logging to see all diagnostic output
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def load_test_data():
    """Load the test data that previously showed the consistency issue."""
    test_data_file = "994ef54e-cca8-4406-96ab-298109d84436_experience.json"
    
    if not os.path.exists(test_data_file):
        logger.error(f"❌ Test data file not found: {test_data_file}")
        return None
    
    try:
        with open(test_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ Loaded test data from {test_data_file}")
        return data
    except Exception as e:
        logger.error(f"❌ Failed to load test data: {e}")
        return None

def create_test_session_files(experience_data, temp_dir, test_id):
    """Create session files for the Phase 3 test."""
    request_id = f"phase3_test_{test_id}"
    
    # Convert experience data to expected format
    processed_experience = experience_data
    if isinstance(experience_data, dict) and 'jobs' in experience_data:
        processed_experience = {"experiences": experience_data['jobs']}
        logger.info(f"🔧 Converted {len(experience_data['jobs'])} jobs to experiences format")
    
    # Create experience.json
    experience_file = os.path.join(temp_dir, f"{request_id}_experience.json")
    with open(experience_file, 'w', encoding='utf-8') as f:
        json.dump(processed_experience, f, indent=2, ensure_ascii=False)
    
    # Create minimal contact.json
    contact_data = {
        "name": "Phase 3 Test User",
        "email": "phase3test@example.com",
        "phone": "555-PHASE3",
        "location": "Test City, ST"
    }
    contact_file = os.path.join(temp_dir, f"{request_id}_contact.json")
    with open(contact_file, 'w', encoding='utf-8') as f:
        json.dump(contact_data, f, indent=2)
    
    # Create minimal summary.json
    summary_data = {
        "content": "Phase 3 Surgical Fix Test - Validating 100% bullet consistency"
    }
    summary_file = os.path.join(temp_dir, f"{request_id}_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2)
    
    # Create empty files for other sections
    for section in ['education', 'skills', 'projects']:
        section_file = os.path.join(temp_dir, f"{request_id}_{section}.json")
        with open(section_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    
    logger.info(f"✅ Created test session files in {temp_dir} for {request_id}")
    return request_id

def analyze_test_results(test_id):
    """Analyze the diagnostic results from the Phase 3 test."""
    
    # Look for diagnostic files
    diagnostic_files = [
        f for f in os.listdir('.') 
        if f.startswith(f'diagnostic_phase3_test_{test_id}')
    ]
    
    if not diagnostic_files:
        logger.error(f"❌ No diagnostic files found for test {test_id}!")
        return False, {}
    
    logger.info(f"📁 Found diagnostic files: {diagnostic_files}")
    
    # Analyze the enhanced JSON diagnostic
    json_file = None
    for f in diagnostic_files:
        if f.endswith('_bullet_analysis_enhanced.json'):
            json_file = f
            break
    
    results = {
        'test_id': test_id,
        'total_bullets': 0,
        'bullets_with_numPr': 0,
        'consistency_rate': 0.0,
        'success': False,
        'issues': [],
        'bullet_details': []
    }
    
    if json_file:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                diagnostic_data = json.load(f)
            
            results['total_bullets'] = diagnostic_data.get('total_bullets', 0)
            results['bullets_with_numPr'] = diagnostic_data.get('bullets_with_numPr', 0)
            results['bullet_details'] = diagnostic_data.get('bullet_details', [])
            
            # Calculate consistency rate
            if results['total_bullets'] > 0:
                results['consistency_rate'] = (results['bullets_with_numPr'] / results['total_bullets']) * 100
            
            # Check for issues
            duplicate_numIds = diagnostic_data.get('duplicate_numIds', [])
            if duplicate_numIds:
                results['issues'].append(f"Duplicate numIds: {duplicate_numIds}")
            
            # Detailed bullet analysis
            for detail in results['bullet_details']:
                if not detail.get('has_numPr', False):
                    results['issues'].append(f"Missing numPr: {detail.get('text', '')[:50]}...")
            
            # Determine success
            results['success'] = (results['consistency_rate'] == 100.0 and len(results['issues']) == 0)
            
            logger.info(f"📊 Test {test_id} Results:")
            logger.info(f"   Total bullets: {results['total_bullets']}")
            logger.info(f"   Bullets with numPr: {results['bullets_with_numPr']}")
            logger.info(f"   Consistency rate: {results['consistency_rate']:.1f}%")
            logger.info(f"   Issues found: {len(results['issues'])}")
            
            if results['success']:
                logger.info(f"✅ TEST {test_id} PASSED: 100% bullet consistency achieved!")
            else:
                logger.error(f"❌ TEST {test_id} FAILED:")
                for issue in results['issues']:
                    logger.error(f"   - {issue}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to analyze diagnostic JSON for test {test_id}: {e}")
            return False, results
    
    return results['success'], results

def run_single_test(test_id, experience_data):
    """Run a single Phase 3 test iteration."""
    logger.info(f"🚀 RUNNING PHASE 3 TEST #{test_id}")
    
    # Create temporary directory for session files
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.info(f"📁 Using temporary directory: {temp_dir}")
        
        # Create session files
        request_id = create_test_session_files(experience_data, temp_dir, test_id)
        
        try:
            # Generate document with Phase 3 surgical fix
            logger.info(f"🔨 GENERATING DOCX WITH PHASE 3 SURGICAL FIX...")
            docx_buffer = build_docx(request_id, temp_dir, debug=True)
            
            logger.info(f"✅ Document generated: {len(docx_buffer.getvalue())} bytes")
            
            # Save the generated document
            output_file = f"phase3_test_{test_id}_{request_id}.docx"
            with open(output_file, 'wb') as f:
                f.write(docx_buffer.getvalue())
            logger.info(f"📁 Saved test document to {output_file}")
            
            # Analyze results
            success, results = analyze_test_results(test_id)
            return success, results
            
        except Exception as e:
            logger.error(f"❌ Test {test_id} failed with exception: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return False, {'test_id': test_id, 'error': str(e)}

def run_phase3_validation():
    """Run comprehensive Phase 3 validation with multiple test iterations."""
    logger.info("🎯 PHASE 3: SURGICAL FIX VALIDATION STARTING")
    logger.info(f"🔧 Native bullets enabled: {NATIVE_BULLETS_ENABLED}")
    
    if not NATIVE_BULLETS_ENABLED:
        logger.error("❌ Native bullets are disabled! Enable them for Phase 3 testing.")
        return False
    
    # Load test data
    experience_data = load_test_data()
    if not experience_data:
        logger.error("❌ Cannot proceed without test data")
        return False
    
    # Analyze test data
    if isinstance(experience_data, dict) and 'jobs' in experience_data:
        jobs = experience_data['jobs']
        logger.info(f"📋 Test data contains {len(jobs)} jobs")
        
        total_achievements = sum(len(job.get('achievements', [])) for job in jobs)
        logger.info(f"📋 Expected total bullets: {total_achievements}")
        
        # Show problematic companies from Phase 2
        target_companies = ["Landmark Health LLC", "Capital Blue Cross", "Pennsylvania Department of Education"]
        for job in jobs:
            company = job.get('company', 'Unknown')
            if company in target_companies:
                achievements = job.get('achievements', [])
                logger.info(f"🎯 TARGET: {company} - {len(achievements)} achievements")
    
    # Run multiple test iterations to validate consistency
    num_tests = 5  # Run 5 tests to ensure stability
    test_results = []
    passed_tests = 0
    
    for i in range(1, num_tests + 1):
        success, results = run_single_test(i, experience_data)
        test_results.append(results)
        
        if success:
            passed_tests += 1
            logger.info(f"✅ Test {i}/{num_tests}: PASSED")
        else:
            logger.error(f"❌ Test {i}/{num_tests}: FAILED")
    
    # Overall assessment
    logger.info(f"\n{'='*60}")
    logger.info(f"🎯 PHASE 3 SURGICAL FIX VALIDATION SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Tests passed: {passed_tests}/{num_tests}")
    logger.info(f"Success rate: {(passed_tests/num_tests)*100:.1f}%")
    
    if passed_tests == num_tests:
        logger.info(f"🎉 PHASE 3 SURGICAL FIX: COMPLETE SUCCESS!")
        logger.info(f"✅ Race condition eliminated - 100% bullet consistency achieved")
        logger.info(f"✅ All {num_tests} test iterations passed")
        
        # Show consistency rates from all tests
        for result in test_results:
            if 'consistency_rate' in result:
                logger.info(f"   Test {result['test_id']}: {result['consistency_rate']:.1f}% consistency")
        
        return True
    else:
        logger.error(f"❌ PHASE 3 SURGICAL FIX: PARTIAL SUCCESS")
        logger.error(f"❌ {num_tests - passed_tests} tests still show issues")
        
        # Show details of failed tests
        for result in test_results:
            if not result.get('success', False) and 'issues' in result:
                logger.error(f"   Test {result['test_id']}: {len(result['issues'])} issues")
                for issue in result['issues']:
                    logger.error(f"     - {issue}")
        
        return False

if __name__ == "__main__":
    success = run_phase3_validation()
    sys.exit(0 if success else 1) 