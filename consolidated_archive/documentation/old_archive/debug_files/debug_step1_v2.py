import docx
import re

# Open the latest downloaded DOCX file
doc = docx.Document("downloadedYCinspiredResume_v5.docx")

print("=== STEP 1 DIAGNOSTIC: Analyzing Company/Institution Paragraph Styles ===\n")

# Look for experience and education sections
experience_found = False
education_found = False
current_section = None

for i, p in enumerate(doc.paragraphs):
    text = p.text.strip()
    
    # Track which section we're in
    if re.search(r'EXPERIENCE', text, re.I):
        current_section = "EXPERIENCE"
        experience_found = True
        print(f"📍 Found EXPERIENCE section at paragraph {i}")
        print(f"   Style: {p.style.name}, space_after: {p.paragraph_format.space_after}")
        continue
    elif re.search(r'EDUCATION', text, re.I):
        current_section = "EDUCATION" 
        education_found = True
        print(f"📍 Found EDUCATION section at paragraph {i}")
        print(f"   Style: {p.style.name}, space_after: {p.paragraph_format.space_after}")
        continue
    
    # Look for company/institution entries (they typically have locations with state abbreviations)
    if text and current_section in ["EXPERIENCE", "EDUCATION"]:
        # Pattern for company entries: Company Name followed by location (City, STATE)
        company_pattern = r'([^,]+),\s*([A-Z]{2})\s*$'
        if re.search(company_pattern, text):
            print(f"🏢 Company/Institution: '{text}'")
            print(f"   Paragraph {i}, Section: {current_section}")
            print(f"   Style: {p.style.name}")
            print(f"   space_after: {p.paragraph_format.space_after}")
            print(f"   space_before: {p.paragraph_format.space_before}")
            
            # Check if this is one of our known companies
            if "Global Cloud" in text:
                print("   ⭐ This is Global Cloud Inc.")
            elif "TechCorp" in text:
                print("   ⭐ This is TechCorp LLC (the one that works)")
            elif "HealthData" in text:
                print("   ⭐ This is HealthData Systems")
            elif "Notecnirp" in text:
                print("   ⭐ This is Notecnirp University")
            elif "Jiangning" in text:
                print("   ⭐ This is Jiangning University")
            print()

# Summary
print("=== SUMMARY ===")
if not experience_found:
    print("❌ No EXPERIENCE section found!")
if not education_found:
    print("❌ No EDUCATION section found!")

print("\n=== MR_Company Style Analysis ===")
# Check if MR_Company style exists and what its properties are
try:
    mr_company_style = doc.styles['MR_Company']
    print(f"✅ MR_Company style exists")
    print(f"   space_after: {mr_company_style.paragraph_format.space_after}")
    print(f"   space_before: {mr_company_style.paragraph_format.space_before}")
    print(f"   base_style: {mr_company_style.base_style.name if mr_company_style.base_style else 'None'}")
except KeyError:
    print("❌ MR_Company style not found in document!")

print("\n=== All Available Styles ===")
available_styles = [s.name for s in doc.styles if s.type == 1]  # Type 1 = paragraph styles
print(f"Total paragraph styles: {len(available_styles)}")
print("Custom MR_ styles found:", [s for s in available_styles if s.startswith('MR_')]) 