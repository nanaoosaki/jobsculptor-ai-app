#!/usr/bin/env python3
"""
o3's DRAMATIC INTEGRATION TEST: Test through real Flask route
This test goes through the actual production path to catch rogue formatting
that only appears in the full application context, not in unit tests.
"""

import os
import sys
import tempfile
import shutil
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Set environment for native bullets and enhanced logging
os.environ['DOCX_USE_NATIVE_BULLETS'] = 'true'
os.environ['DOCX_DISABLE_LEGACY_BULLETS'] = 'false'  # Keep legacy for detection

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_complete_test_data(temp_dir, request_id):
    """Create complete test data that will trigger bullet creation."""
    
    # Contact data
    contact_data = {
        "name": "Integration Test User",
        "email": "test@example.com",
        "phone": "555-1234",
        "location": "Test City, TC"
    }
    with open(os.path.join(temp_dir, f"{request_id}_contact.json"), 'w') as f:
        json.dump(contact_data, f)
    
    # Summary data
    summary_data = {
        "summary": "Test summary for integration testing of bullet formatting systems."
    }
    with open(os.path.join(temp_dir, f"{request_id}_summary.json"), 'w') as f:
        json.dump(summary_data, f)
    
    # Experience data with multiple jobs and bullets
    experience_data = {
        "experiences": [
            {
                "company": "Integration Test Corp",
                "position": "Senior Test Engineer",
                "startDate": "2023",
                "endDate": "2024",
                "location": "Remote",
                "achievements": [
                    "First achievement that should trigger native bullets with proper 0.13 inch indentation",
                    "Second achievement to test multiple bullet creation and potential legacy fallbacks",
                    "Third achievement with complex formatting to stress-test the numbering system"
                ]
            },
            {
                "company": "Legacy Fallback Inc",
                "position": "Bullet Test Specialist", 
                "startDate": "2022",
                "endDate": "2023",
                "location": "Local",
                "achievements": [
                    "Fourth achievement that might trigger different code paths in production",
                    "Fifth achievement to test style repair loops and second-pass formatting"
                ]
            }
        ]
    }
    with open(os.path.join(temp_dir, f"{request_id}_experience.json"), 'w') as f:
        json.dump(experience_data, f)
    
    # Education data with bullets
    education_data = {
        "institutions": [
            {
                "institution": "Test University",
                "degree": "BS in Testing",
                "dates": "2018-2022",
                "location": "Test City",
                "highlights": [
                    "Education bullet that tests numbering in different sections",
                    "Another education bullet to verify consistent formatting"
                ]
            }
        ]
    }
    with open(os.path.join(temp_dir, f"{request_id}_education.json"), 'w') as f:
        json.dump(education_data, f)

    # Skills data
    skills_data = {
        "skills": ["Python", "Testing", "DOCX Generation", "Word Formatting"]
    }
    with open(os.path.join(temp_dir, f"{request_id}_skills.json"), 'w') as f:
        json.dump(skills_data, f)

    # Projects data (no bullets)
    projects_data = {}
    with open(os.path.join(temp_dir, f"{request_id}_projects.json"), 'w') as f:
        json.dump(projects_data, f)

def analyze_docx_for_rogue_formatting(docx_path):
    """o3's DRAMATIC XML ANALYSIS: Look for the specific rogue formatting patterns."""
    print(f"\n🔍 o3's XML ANALYSIS: {docx_path}")
    print("=" * 60)
    
    rogue_paragraphs = []
    
    try:
        with zipfile.ZipFile(docx_path, 'r') as docx_zip:
            # Check document.xml for rogue formatting
            try:
                document_xml = docx_zip.read('word/document.xml').decode('utf-8')
                
                # Parse XML to find bullet paragraphs
                root = ET.fromstring(document_xml)
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                
                bullet_count = 0
                rogue_count = 0
                
                for para_idx, para in enumerate(root.findall('.//w:p', ns)):
                    # Check if it has numbering
                    numPr = para.find('.//w:numPr', ns)
                    has_numbering = numPr is not None
                    
                    # Check for direct indentation
                    pPr = para.find('.//w:pPr', ns)
                    direct_indent = None
                    if pPr is not None:
                        ind = pPr.find('.//w:ind', ns)
                        if ind is not None:
                            left = ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left')
                            hanging = ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hanging')
                            if left or hanging:
                                direct_indent = {"left": left, "hanging": hanging}
                    
                    # Get paragraph text
                    text_runs = para.findall('.//w:t', ns)
                    text = ''.join(t.text or '' for t in text_runs)
                    
                    # Check for bullet paragraphs (either with numbering or containing bullet-like text)
                    is_bullet = has_numbering or any(bullet_char in text for bullet_char in ['•', '–', '-']) and len(text) > 10
                    
                    if is_bullet:
                        bullet_count += 1
                        print(f"\n📋 BULLET PARAGRAPH {bullet_count}:")
                        print(f"   Text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
                        print(f"   Has numbering: {has_numbering}")
                        
                        if direct_indent:
                            rogue_count += 1
                            left_val = direct_indent["left"]
                            hanging_val = direct_indent["hanging"]
                            
                            if left_val:
                                left_twips = int(left_val)
                                left_cm = left_twips / 567
                                left_inches = left_twips / 1440
                                print(f"   🚨 ROGUE LEFT INDENT: {left_twips} twips = {left_cm:.3f} cm = {left_inches:.3f} inches")
                                
                                # Check for the specific 118745 twips value o3 mentioned
                                if abs(left_twips - 118745) < 100:
                                    print(f"   🎯 MATCHES o3's ROGUE VALUE: ~118745 twips!")
                            
                            if hanging_val:
                                hanging_twips = int(hanging_val)
                                hanging_cm = hanging_twips / 567
                                hanging_inches = hanging_twips / 1440
                                print(f"   🚨 ROGUE HANGING INDENT: {hanging_twips} twips = {hanging_cm:.3f} cm = {hanging_inches:.3f} inches")
                            
                            rogue_paragraphs.append({
                                "paragraph": bullet_count,
                                "text": text[:50],
                                "left_twips": int(left_val) if left_val else None,
                                "hanging_twips": int(hanging_val) if hanging_val else None,
                                "has_numbering": has_numbering
                            })
                        else:
                            print(f"   ✅ NO DIRECT INDENT (clean)")
                
                print(f"\n📊 SUMMARY:")
                print(f"   Total bullet paragraphs: {bullet_count}")
                print(f"   Paragraphs with rogue formatting: {rogue_count}")
                
                if rogue_count == 0:
                    print(f"   ✅ NO ROGUE FORMATTING DETECTED")
                else:
                    print(f"   ❌ ROGUE FORMATTING FOUND IN {rogue_count} PARAGRAPHS")
                    
            except KeyError:
                print("❌ document.xml not found")
            except ET.ParseError as e:
                print(f"❌ XML parse error: {e}")
    
    except Exception as e:
        print(f"❌ DOCX analysis failed: {e}")
    
    return rogue_paragraphs

def test_production_route():
    """Test the complete production route and analyze results."""
    print("🧪 o3's DRAMATIC INTEGRATION TEST")
    print("=" * 50)
    
    try:
        # Create temp directory and test data
        temp_dir = tempfile.mkdtemp()
        request_id = "integration_test"
        create_complete_test_data(temp_dir, request_id)
        
        print(f"📁 Created test data in: {temp_dir}")
        
        # Import and run through build_docx (simulates production)
        from utils.docx_builder import build_docx
        
        print(f"\n📄 Generating document through PRODUCTION build_docx...")
        print(f"⚠️  This will show ALL diagnostic logging from our enhanced system")
        
        # Generate document
        docx_buffer = build_docx(request_id, temp_dir, debug=False)
        
        # Save for analysis
        output_path = "integration_test_production.docx"
        with open(output_path, 'wb') as f:
            f.write(docx_buffer.getvalue())
        
        print(f"\n✅ Document generated: {output_path}")
        
        # Analyze for rogue formatting
        rogue_paragraphs = analyze_docx_for_rogue_formatting(output_path)
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        # Final assessment
        print(f"\n🎯 FINAL ASSESSMENT:")
        if len(rogue_paragraphs) == 0:
            print(f"   ✅ SUCCESS: No rogue formatting detected")
            print(f"   ✅ All bullets should show proper 0.13\" indentation in Word")
        else:
            print(f"   ❌ FAILURE: {len(rogue_paragraphs)} paragraphs have rogue formatting")
            print(f"   ❌ This explains why Word shows flush bullets despite correct XML")
            
            # Show which specific paragraphs have issues
            for rogue in rogue_paragraphs:
                print(f"   📋 Paragraph {rogue['paragraph']}: '{rogue['text']}...'")
                if rogue['left_twips']:
                    print(f"      Left: {rogue['left_twips']} twips")
                if rogue['hanging_twips']:
                    print(f"      Hanging: {rogue['hanging_twips']} twips")
        
        return len(rogue_paragraphs) == 0
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_production_route()
    print(f"\n{'🎉 INTEGRATION TEST PASSED' if success else '💥 INTEGRATION TEST FAILED'}") 