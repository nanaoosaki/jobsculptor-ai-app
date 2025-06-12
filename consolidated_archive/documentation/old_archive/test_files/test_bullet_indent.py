from utils.docx_builder import build_docx
import tempfile
import os
import json

def test_bullet_indent():
    # Create test data
    temp_dir = tempfile.mkdtemp()
    request_id = 'bullet_indent_test'

    # Create minimal test files
    contact_data = {'name': 'Test User', 'email': 'test@example.com'}
    experience_data = {
        'experiences': [{
            'company': 'Test Company', 
            'position': 'Test Role', 
            'achievements': [
                'Test bullet that should be indented 0.13 inches from left margin',
                'Another bullet to verify consistent indentation',
                'Third bullet to confirm all bullets move right together'
            ]
        }]
    }

    with open(os.path.join(temp_dir, f'{request_id}_contact.json'), 'w') as f:
        json.dump(contact_data, f)
    with open(os.path.join(temp_dir, f'{request_id}_experience.json'), 'w') as f:
        json.dump(experience_data, f)

    # Generate DOCX
    docx_output = build_docx(request_id, temp_dir)

    # Save test file
    with open('bullet_indent_test.docx', 'wb') as f:
        f.write(docx_output.getvalue())

    print('✅ Generated bullet_indent_test.docx with new left indent formatting')
    print('📋 Expected result: Bullets show "Left: 0.13"" in Word\'s paragraph dialog')
    print('🎯 Both bullet symbols and text should be moved 0.13" from left margin')

if __name__ == "__main__":
    test_bullet_indent() 