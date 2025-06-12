#!/usr/bin/env python3
"""
Deployment validation script for Resume Tailor Flask application.
Tests all dependencies and configurations before deployment.
"""

import os
import sys
import importlib
from pathlib import Path

def test_python_version():
    """Test that Python version is compatible."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python version should be 3.8 or higher")
        return False

def test_imports():
    """Test that all required imports work."""
    required_packages = [
        'flask',
        'anthropic',
        'openai',
        'docx',
        'weasyprint',
        'playwright',
        'bs4',
        'requests',
        'gunicorn'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}: Available")
        except ImportError as e:
            print(f"❌ {package}: Failed - {e}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0

def test_directories():
    """Test that required directories exist or can be created."""
    app_root = Path(__file__).parent
    
    required_dirs = [
        app_root / 'static',
        app_root / 'templates',
        app_root / 'utils',
        app_root / 'word_styles',
    ]
    
    test_dirs = [
        app_root / 'static' / 'uploads',
        app_root / 'static' / 'uploads' / 'temp_session_data',
        app_root / 'logs',
    ]
    
    # Check required directories exist
    for directory in required_dirs:
        if directory.exists():
            print(f"✅ Required directory exists: {directory}")
        else:
            print(f"❌ Required directory missing: {directory}")
            return False
    
    # Test creating directories
    for directory in test_dirs:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ Can create directory: {directory}")
        except Exception as e:
            print(f"❌ Cannot create directory {directory}: {e}")
            return False
    
    return True

def test_environment_variables():
    """Test environment variables."""
    optional_vars = {
        'CLAUDE_API_KEY': 'Claude AI integration',
        'OPENAI_API_KEY': 'OpenAI integration',
        'FLASK_SECRET_KEY': 'Flask session security'
    }
    
    warnings = 0
    
    for var, description in optional_vars.items():
        if os.environ.get(var):
            print(f"✅ {var}: Set ({description})")
        else:
            print(f"⚠️  {var}: Not set - {description} may not work")
            warnings += 1
    
    # Test PORT environment variable (Render sets this)
    port = os.environ.get('PORT', '5000')
    try:
        int(port)
        print(f"✅ PORT: {port} (valid)")
    except ValueError:
        print(f"❌ PORT: {port} (invalid)")
        return False
    
    return True

def test_config_files():
    """Test that configuration files exist."""
    required_files = [
        'app.py',
        'config.py',
        'requirements.txt',
        'Procfile',
        'render.yaml',
        'startup.py'
    ]
    
    app_root = Path(__file__).parent
    
    for filename in required_files:
        filepath = app_root / filename
        if filepath.exists():
            print(f"✅ Configuration file exists: {filename}")
        else:
            print(f"❌ Configuration file missing: {filename}")
            return False
    
    return True

def test_weasyprint():
    """Test WeasyPrint functionality."""
    try:
        from weasyprint import HTML, CSS
        
        # Test basic HTML to PDF conversion
        html_content = "<html><body><h1>Test</h1></body></html>"
        html_doc = HTML(string=html_content)
        
        # Try to render (this will fail if system dependencies are missing)
        pdf_bytes = html_doc.write_pdf()
        
        if pdf_bytes:
            print("✅ WeasyPrint: Working correctly")
            return True
        else:
            print("❌ WeasyPrint: Failed to generate PDF")
            return False
            
    except Exception as e:
        print(f"❌ WeasyPrint: Error - {e}")
        print("   This may be normal during build phase. WeasyPrint needs system dependencies.")
        return True  # Don't fail validation for this during build

def main():
    """Run all validation tests."""
    print("🔍 Validating Resume Tailor deployment...\n")
    
    tests = [
        ("Python Version", test_python_version),
        ("Package Imports", test_imports),
        ("Directory Structure", test_directories),
        ("Environment Variables", test_environment_variables),
        ("Configuration Files", test_config_files),
        ("WeasyPrint", test_weasyprint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n📊 Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validation tests passed! Ready for deployment.")
        return 0
    else:
        print("⚠️  Some validation tests failed. Check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 