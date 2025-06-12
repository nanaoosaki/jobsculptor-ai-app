#!/usr/bin/env python3
"""
Production startup script for Resume Tailor Flask application.
Handles environment setup and directory creation for deployment.
"""

import os
import logging
from pathlib import Path

def setup_production_environment():
    """Set up directories and environment for production deployment."""
    
    # Get the application root directory
    app_root = Path(__file__).parent
    
    # Define required directories
    required_dirs = [
        app_root / 'static' / 'uploads',
        app_root / 'static' / 'uploads' / 'temp_session_data',
        app_root / 'static' / 'uploads' / 'job_analysis_cache',
        app_root / 'logs',
    ]
    
    # Create directories if they don't exist
    for directory in required_dirs:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Ensured directory exists: {directory}")
    
    # Set up logging directory permissions (if needed)
    logs_dir = app_root / 'logs'
    if logs_dir.exists():
        # Make sure the logs directory is writable
        os.chmod(logs_dir, 0o755)
        print(f"✓ Set permissions for logs directory: {logs_dir}")
    
    # Check environment variables
    required_env_vars = ['FLASK_SECRET_KEY']
    optional_env_vars = ['CLAUDE_API_KEY', 'OPENAI_API_KEY']
    
    print("\n🔧 Environment Variables Check:")
    for var in required_env_vars:
        if os.environ.get(var):
            print(f"✓ {var}: Set")
        else:
            print(f"⚠️  {var}: Not set (using default)")
    
    for var in optional_env_vars:
        if os.environ.get(var):
            print(f"✓ {var}: Set")
        else:
            print(f"ℹ️  {var}: Not set (limited functionality)")
    
    # Check if we're in production
    flask_env = os.environ.get('FLASK_ENV', 'development')
    port = os.environ.get('PORT', '5000')
    
    print(f"\n🚀 Application Configuration:")
    print(f"Environment: {flask_env}")
    print(f"Port: {port}")
    print(f"Debug mode: {'disabled' if flask_env == 'production' else 'enabled'}")
    
    return True

if __name__ == '__main__':
    # Run setup
    setup_production_environment()
    
    # Import and run the Flask app
    from app import app
    
    # Get port from environment variable (for Render deployment) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Disable debug mode in production
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"\n🌐 Starting Flask application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug) 