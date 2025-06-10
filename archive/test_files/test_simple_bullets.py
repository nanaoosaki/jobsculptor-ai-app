#!/usr/bin/env python3
"""Simple test to verify bullet creation and nuclear cleanup"""

import os
import tempfile
import json
from pathlib import Path

# Set environment for native bullets
os.environ['DOCX_USE_NATIVE_BULLETS'] = 'true'

# Add project root to path
project_root = Path(__file__).parent
import sys
sys.path.insert(0, str(project_root))

def test_simple_bullets():
    """Test bullet creation through build_docx with minimal setup."""
    
    # Create test data
    temp_dir = tempfile.mkdtemp()
    request_id = 'test_simple'
    
    # Create experience data directly as list (as expected by build_docx)
    experience_data = [{
        'company': 'Test Company', 
        'position': 'Test Position', 
        'achievements': [
            'First bullet point for testing',
            'Second bullet point for testing'
        ]
    }]
    
    with open(f'{temp_dir}/{request_id}_experience.json', 'w') as f:
        json.dump(experience_data, f)
    
    print(f'📁 Created test data in: {temp_dir}')
    print(f'📋 Experience data: {experience_data}')
    
    # Build DOCX
    from utils.docx_builder import build_docx
    
    print('\n📄 Building DOCX...')
    docx_buffer = build_docx(request_id, temp_dir, debug=False)
    
    # Save result
    with open('test_simple_bullets.docx', 'wb') as f:
        f.write(docx_buffer.getvalue())
    
    print('✅ Document created: test_simple_bullets.docx')
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_simple_bullets() 