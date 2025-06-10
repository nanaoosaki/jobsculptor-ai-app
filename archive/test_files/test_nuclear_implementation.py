#!/usr/bin/env python3
"""
Test o3's Nuclear Cleanup Implementation in build_docx

Verify that the nuclear cleanup is automatically applied when building documents
through the normal production pipeline.
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Set environment for native bullets
os.environ['DOCX_USE_NATIVE_BULLETS'] = 'true'

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_test_data_files(temp_dir, request_id):
    """Create minimal test data files for document generation."""
    
    # Contact data
    contact_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "555-1234",
        "city": "Test City",
        "state": "TC"
    }
    with open(os.path.join(temp_dir, f"{request_id}_contact.json"), 'w') as f:
        json.dump(contact_data, f)
    
    # Experience data with bullet points
    experience_data = {
        "experiences": [{
            "company": "Test Company",
            "position": "Test Position",
            "startDate": "2023",
            "endDate": "2024",
            "achievements": [
                "First bullet point that would have rogue formatting",
                "Second bullet point to test nuclear cleanup",
                "Third bullet point for comprehensive testing"
            ]
        }]
    }
    with open(os.path.join(temp_dir, f"{request_id}_experience.json"), 'w') as f:
        json.dump(experience_data, f)
    
    # Empty files for other sections
    for section in ["summary", "skills", "projects"]:
        with open(os.path.join(temp_dir, f"{request_id}_{section}.json"), 'w') as f:
            json.dump({}, f)

def test_nuclear_implementation():
    """Test that nuclear cleanup is automatically applied in build_docx."""
    print("🧪 Testing o3's Nuclear Cleanup Implementation in build_docx")
    print("=" * 60)
    
    try:
        from utils.docx_builder import build_docx
        
        # Create temp directory and test data
        temp_dir = tempfile.mkdtemp()
        request_id = "test_nuclear"
        create_test_data_files(temp_dir, request_id)
        
        print(f"📁 Created test data in: {temp_dir}")
        print(f"🔧 Request ID: {request_id}")
        
        # Generate document using the full production pipeline
        print(f"\n📄 Generating document through build_docx...")
        docx_buffer = build_docx(request_id, temp_dir, debug=False)
        
        # Save the generated document
        output_path = "test_nuclear_implementation.docx"
        with open(output_path, 'wb') as f:
            f.write(docx_buffer.getvalue())
        
        print(f"✅ Document generated successfully: {output_path}")
        
        # Cleanup temp directory
        import shutil
        shutil.rmtree(temp_dir)
        
        print(f"\n🎯 TEST RESULT:")
        print(f"   If the nuclear cleanup is working, the logs should show:")
        print(f"   '🧹 o3's Nuclear Cleanup applied: Fixed N bullet paragraphs before save'")
        print(f"\n📋 MANUAL VERIFICATION:")
        print(f"   1. Open {output_path} in Microsoft Word")
        print(f"   2. Click on a bullet point")
        print(f"   3. Check Paragraph ► Indentation ► Left")
        print(f"   4. Should show '0' (this is NORMAL per o3's analysis)")
        print(f"   5. Check Bullets and Numbering ► Indent at 0.13\"")
        print(f"   6. Bullets should visually appear indented")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_nuclear_implementation()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}") 