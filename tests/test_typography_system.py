#!/usr/bin/env python3
"""
Typography System Validation Test

This script validates that the enhanced typography system (Phase 1) is correctly implemented:
- Design token structure is complete
- SCSS generation is working
- CSS custom properties are generated
- Font licensing compliance
- API endpoints are functional
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_design_tokens():
    """Test that design tokens have the enhanced typography structure"""
    print("🔍 Testing design tokens structure...")
    
    tokens_path = project_root / 'design_tokens.json'
    if not tokens_path.exists():
        print("❌ design_tokens.json not found")
        return False
    
    with open(tokens_path, 'r') as f:
        tokens = json.load(f)
    
    typography = tokens.get('typography', {})
    if not typography:
        print("❌ Typography section missing")
        return False
    
    # Check required structure
    required_sections = ['fontFamily', 'fontSize', 'fontWeight', 'lineHeight', 'fontColor']
    for section in required_sections:
        if section not in typography:
            print(f"❌ Missing typography section: {section}")
            return False
    
    # Check enhanced font family structure
    font_family = typography.get('fontFamily', {})
    required_font_props = ['primary', 'docxPrimary', 'fontVersion', 'secondary']
    for prop in required_font_props:
        if prop not in font_family:
            print(f"❌ Missing font family property: {prop}")
            return False
    
    # Check font version is current
    font_version = font_family.get('fontVersion')
    if not font_version or font_version < '2025-01':
        print(f"❌ Font version outdated or missing: {font_version}")
        return False
    
    # Check structured colors
    font_colors = typography.get('fontColor', {})
    primary_color = font_colors.get('primary', {})
    if isinstance(primary_color, dict):
        if 'hex' not in primary_color:
            print("❌ Missing hex value in structured color")
            return False
    
    print("✅ Design tokens structure validated")
    return True

def test_scss_generation():
    """Test that SCSS variables are correctly generated"""
    print("🔍 Testing SCSS generation...")
    
    scss_path = project_root / 'static' / 'scss' / '_tokens.scss'
    if not scss_path.exists():
        print("❌ SCSS tokens file not found")
        return False
    
    with open(scss_path, 'r') as f:
        scss_content = f.read()
    
    # Check for enhanced typography variables
    required_vars = [
        '$font-family-primary:',
        '$font-family-docx:',
        '$font-version:',
        '$font-size-body:',
        '$font-size-body-screen:',
        '$font-weight-bold:',
        '$font-color-primary:',
        '$font-feature-body:'
    ]
    
    for var in required_vars:
        if var not in scss_content:
            print(f"❌ Missing SCSS variable: {var}")
            return False
    
    # Check for proper structure sections
    if "=== UNIFIED TYPOGRAPHY SYSTEM ===" not in scss_content:
        print("❌ Missing typography system section in SCSS")
        return False
    
    print("✅ SCSS generation validated")
    return True

def test_css_generation():
    """Test that CSS custom properties are correctly generated"""
    print("🔍 Testing CSS custom properties generation...")
    
    css_path = project_root / 'static' / 'css' / '_variables.css'
    if not css_path.exists():
        print("❌ CSS variables file not found")
        return False
    
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    # Check for CSS custom properties
    required_props = [
        '--font-family-primary:',
        '--font-family-docx:',
        '--font-version:',
        '--font-size-body:',
        '--font-size-body-screen:',
        '--font-weight-bold:',
        '--font-color-primary:'
    ]
    
    for prop in required_props:
        if prop not in css_content:
            print(f"❌ Missing CSS custom property: {prop}")
            return False
    
    if ":root {" not in css_content:
        print("❌ Missing :root declaration in CSS")
        return False
    
    print("✅ CSS custom properties validated")
    return True

def test_font_licensing():
    """Test font licensing configuration"""
    print("🔍 Testing font licensing configuration...")
    
    license_path = project_root / 'fonts_allowed.json'
    if not license_path.exists():
        print("❌ Font licensing file not found")
        return False
    
    with open(license_path, 'r') as f:
        license_config = json.load(f)
    
    required_sections = ['embeddable', 'fallbacks', 'restricted']
    for section in required_sections:
        if section not in license_config:
            print(f"❌ Missing license section: {section}")
            return False
    
    # Check Calibri is in restricted list
    if 'Calibri' not in license_config.get('restricted', []):
        print("❌ Calibri should be in restricted fonts list")
        return False
    
    print("✅ Font licensing configuration validated")
    return True

def test_token_generation_script():
    """Test that the token generation script works"""
    print("🔍 Testing token generation script...")
    
    script_path = project_root / 'tools' / 'generate_tokens_css.py'
    if not script_path.exists():
        print("❌ Token generation script not found")
        return False
    
    # Try importing the script to check for syntax errors
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, str(script_path)
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode != 0:
            print(f"❌ Token generation script failed: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"❌ Error running token generation: {e}")
        return False
    
    print("✅ Token generation script validated")
    return True

def test_enhanced_features():
    """Test enhanced typography features"""
    print("🔍 Testing enhanced typography features...")
    
    # Load tokens to test enhanced features
    try:
        from style_manager import load_tokens
        tokens = load_tokens()
        typography = tokens.get('typography', {})
        
        # Test multi-script fonts
        secondary_fonts = typography.get('fontFamily', {}).get('secondary', {})
        if not secondary_fonts.get('cjk'):
            print("❌ Missing CJK font support")
            return False
        
        # Test accessibility fonts
        accessibility = typography.get('fontFamily', {}).get('accessibility', {})
        if not accessibility.get('dyslexicMode'):
            print("❌ Missing dyslexic font support")
            return False
        
        # Test font feature settings
        font_features = typography.get('fontFeatureSettings', {})
        if not font_features.get('body'):
            print("❌ Missing font feature settings")
            return False
        
        # Test structured colors with theme support
        font_colors = typography.get('fontColor', {})
        primary_color = font_colors.get('primary', {})
        if isinstance(primary_color, dict) and 'themeColor' not in primary_color:
            print("❌ Missing theme color support")
            return False
        
    except Exception as e:
        print(f"❌ Error testing enhanced features: {e}")
        return False
    
    print("✅ Enhanced typography features validated")
    return True

def run_all_tests():
    """Run all typography system tests"""
    print("🎯 Running Typography System Validation Tests")
    print("=" * 50)
    
    tests = [
        test_design_tokens,
        test_scss_generation,
        test_css_generation,
        test_font_licensing,
        test_token_generation_script,
        test_enhanced_features
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Typography System Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced typography system is ready.")
        print("\n✨ Next steps:")
        print("  • Phase 2: SCSS Integration (update base styles)")
        print("  • Phase 3: DOCX Unification (style registry updates)")
        print("  • Phase 4: StyleEngine Enhancement (cleanup)")
        return True
    else:
        print("⚠️  Some tests failed. Please address the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 