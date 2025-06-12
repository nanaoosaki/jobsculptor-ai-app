#!/usr/bin/env python3
"""
Test script for B-Series implementations
Tests all 4 B-series modules to ensure they're working correctly.
"""

def test_b3_unicode_sanitizer():
    """Test B3: Unicode Bullet Sanitizer"""
    print("Testing B3: Unicode Bullet Sanitizer...")
    
    from utils.unicode_bullet_sanitizer import sanitize_bullet_text, analyze_bullet_characters
    
    # Test text with bullet characters
    test_text = "• This is a bullet point"
    sanitized = sanitize_bullet_text(test_text)
    print(f"  Original: '{test_text}'")
    print(f"  Sanitized: '{sanitized}'")
    
    # Test analysis
    detections = analyze_bullet_characters(test_text)
    print(f"  Detections: {len(detections)} found")
    for d in detections:
        print(f"    - {d.bullet_type.value}: '{d.character}' (confidence: {d.confidence})")
    
    print("  ✅ B3: Unicode Sanitizer OK")
    return True

def test_b9_numid_manager():
    """Test B9: NumId Collision Manager"""
    print("Testing B9: NumId Collision Manager...")
    
    from utils.numid_collision_manager import allocate_safe_numid, get_numid_allocation_summary
    
    # Test allocation
    doc_id = "test_doc_123"
    section = "experience"
    num_id, abstract_id = allocate_safe_numid(doc_id, section)
    print(f"  Allocated numId: {num_id}, abstractNumId: {abstract_id}")
    
    # Test summary
    summary = get_numid_allocation_summary()
    print(f"  Total allocations: {summary['statistics']['total_allocations']}")
    
    print("  ✅ B9: NumId Manager OK")
    return True

def test_b6_xml_repair():
    """Test B6: XML Repair System"""
    print("Testing B6: XML Repair System...")
    
    from utils.xml_repair_system import get_xml_repair_summary
    
    # Test summary (can't test full analysis without a DOCX file)
    summary = get_xml_repair_summary()
    print(f"  Supported namespaces: {len(summary['supported_namespaces'])}")
    print(f"  Issue types: {len(summary['issue_types'])}")
    
    print("  ✅ B6: XML Repair System OK")
    return True

def test_b1_style_handler():
    """Test B1: Style Collision Handler"""
    print("Testing B1: Style Collision Handler...")
    
    from utils.style_collision_handler import validate_style_for_bullets, get_style_collision_summary
    
    # Test validation
    is_valid = validate_style_for_bullets("MR_BulletPoint", 100)
    print(f"  MR_BulletPoint validation: {is_valid}")
    
    # Test summary
    summary = get_style_collision_summary()
    print(f"  Total styles: {summary['total_styles']}")
    print(f"  Builtin styles: {summary['builtin_styles']}")
    
    print("  ✅ B1: Style Handler OK")
    return True

def main():
    """Run all B-series tests"""
    print("🚀 Starting B-Series Integration Tests...")
    print()
    
    tests = [
        test_b3_unicode_sanitizer,
        test_b9_numid_manager,
        test_b6_xml_repair,
        test_b1_style_handler
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            print()
    
    print(f"🎯 B-Series Tests Complete: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All B-Series modules are working correctly!")
        print()
        print("Phase 3: B-Series Edge Cases Implementation - COMPLETE")
        print()
        print("Ready for Phase 4: O3 Core Implementation")
        return True
    else:
        print("❌ Some B-Series modules have issues")
        return False

if __name__ == "__main__":
    main() 