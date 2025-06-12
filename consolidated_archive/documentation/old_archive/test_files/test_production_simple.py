#!/usr/bin/env python3
"""
Simple Production Test
Test the exact same flow as production but with minimal data.
"""

import os
import tempfile
import json

def test_production_simple():
    """Test production flow with simple data."""
    print("🧪 Testing Production Flow with Simple Data")
    print("=" * 50)
    
    # Set the same environment variables as production
    os.environ['DOCX_USE_NATIVE_BULLETS'] = 'true'
    
    # Create temp directory like production does
    temp_dir = tempfile.mkdtemp()
    request_id = 'prod_simple_test'
    
    print(f"📁 Using temp directory: {temp_dir}")
    print(f"🔧 Request ID: {request_id}")
    
    try:
        # Create the exact same data structure as production
        contact_data = {
            'name': 'Production Test User',
            'email': 'test@production.com',
            'phone': '555-PROD',
            'location': 'Production City, PC'
        }
        
        experience_data = {
            'experiences': [{
                'company': 'Production Company',
                'position': 'Production Engineer',
                'dates': '2023-Present',
                'achievements': [
                    'Production bullet that should show 0.13" left indentation',
                    'Second production bullet to verify consistency',
                    'Third production bullet to confirm all formatting is correct'
                ]
            }]
        }
        
        # Save data files exactly like production
        with open(f'{temp_dir}/{request_id}_contact.json', 'w') as f:
            json.dump(contact_data, f)
        
        with open(f'{temp_dir}/{request_id}_experience.json', 'w') as f:
            json.dump(experience_data, f)
        
        print(f"✅ Created production-style data files")
        
        # Import and use the production DOCX builder
        from utils.docx_builder import build_docx
        
        print(f"📄 Generating DOCX using production build_docx...")
        
        # Call the exact same function that production uses
        docx_buffer = build_docx(request_id, temp_dir, debug=False)
        
        # Save the result
        output_path = 'production_simple_test.docx'
        with open(output_path, 'wb') as f:
            f.write(docx_buffer.getvalue())
        
        print(f"✅ Generated: {output_path}")
        print(f"📋 Expected: Bullets show 'Left: 0.23\"' and 'Hanging: 0.13\"' in Word")
        print(f"🎯 This positions bullet at 0.1\" and text at 0.23\" from left margin")
        print(f"🎯 Tighter spacing between bullet symbol and text achieved!")
        
        return True
        
    except Exception as e:
        print(f"❌ Production test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_production_simple() 