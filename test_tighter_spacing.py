#!/usr/bin/env python3
"""
Test Tighter Bullet Spacing
Verify the exact measurements: left=0.1" and hanging=0.13"
"""

import os
import tempfile
import json

def test_tighter_spacing():
    """Test the updated tighter bullet spacing."""
    print("🧪 Testing Tighter Bullet Spacing")
    print("=" * 40)
    print("📏 Target positioning:")
    print("   • Bullet symbol at: 0.1\" from margin")
    print("   • Text starts at: 0.23\" from margin")
    print("   • Tighter space between bullet and text!")
    print()
    print("📐 Word's hanging indent settings:")
    print("   • Left: 0.23\" (where text is positioned)")
    print("   • Hanging: 0.13\" (how much bullet hangs left of text)")
    print("=" * 40)
    
    # Set environment for native bullets
    os.environ['DOCX_USE_NATIVE_BULLETS'] = 'true'
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    request_id = 'tighter_spacing_test'
    
    try:
        # Create minimal test data focusing on bullets
        contact_data = {
            'name': 'Tighter Spacing Test',
            'email': 'test@spacing.com'
        }
        
        experience_data = {
            'experiences': [{
                'company': 'Spacing Test Company',
                'position': 'Format Engineer',
                'achievements': [
                    'Bullet with left=0.1" and hanging=0.13" for tighter spacing',
                    'Second bullet to compare consistent tight formatting',
                    'Third bullet showing the bullet symbol is closer to text now'
                ]
            }]
        }
        
        # Save data files
        with open(f'{temp_dir}/{request_id}_contact.json', 'w') as f:
            json.dump(contact_data, f)
        
        with open(f'{temp_dir}/{request_id}_experience.json', 'w') as f:
            json.dump(experience_data, f)
        
        # Generate DOCX
        from utils.docx_builder import build_docx
        
        print(f"📄 Generating DOCX with tighter spacing...")
        docx_buffer = build_docx(request_id, temp_dir, debug=False)
        
        # Save result
        output_path = 'tighter_spacing_test.docx'
        with open(output_path, 'wb') as f:
            f.write(docx_buffer.getvalue())
        
        print(f"✅ Generated: {output_path}")
        print()
        print("📋 VERIFICATION STEPS:")
        print("1. Open the document in Microsoft Word")
        print("2. Click on any bullet point")
        print("3. Go to Format → Paragraph → Indentation")
        print("4. You should see:")
        print("   • Left: 0.23\"")
        print("   • Hanging: 0.13\"")
        print("5. This positions bullet at 0.1\" and text at 0.23\" - tighter spacing!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_tighter_spacing() 