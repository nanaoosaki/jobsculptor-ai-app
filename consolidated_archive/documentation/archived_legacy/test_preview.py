import os
from claude_integration import generate_resume_preview

def test_preview_rendering():
    # Path to an existing tailored resume
    resume_path = "static/uploads/f82fd54d-087b-491e-bf11-614311cf842e_tailored.docx"
    
    # Check if file exists
    if not os.path.exists(resume_path):
        print(f"File not found: {resume_path}")
        
        # Look for any tailored resume file instead
        files = os.listdir("static/uploads")
        tailored_files = [f for f in files if f.endswith("_tailored.docx")]
        
        if tailored_files:
            resume_path = os.path.join("static/uploads", tailored_files[0])
            print(f"Using alternative file: {resume_path}")
        else:
            print("No tailored resume files found")
            return
    
    # Generate the preview HTML
    html = generate_resume_preview(resume_path)
    
    # Save HTML to a file for inspection
    with open("resume_preview.html", "w") as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Resume Preview Test</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                .resume-preview { max-width: 800px; margin: 0 auto; padding: 20px; }
                .resume-heading-1 { color: #2c3e50; margin-top: 20px; }
                .resume-heading-2 { color: #3498db; margin-top: 15px; }
                .resume-paragraph { margin: 8px 0; }
                .resume-bullet-list { margin: 8px 0; padding-left: 20px; }
                .resume-bullet-item { margin: 5px 0; }
            </style>
        </head>
        <body>
            <h1>Resume Preview Test</h1>
            """ + html + """
        </body>
        </html>
        """)
    
    print(f"Preview HTML saved to resume_preview.html")
    print("Open this file in a browser to view the formatted preview")
    
    # Print a small excerpt of the HTML for quick inspection
    html_excerpt = html[:500] + "..." if len(html) > 500 else html
    print("\nHTML Preview Excerpt:")
    print("-" * 50)
    print(html_excerpt)
    print("-" * 50)

if __name__ == "__main__":
    test_preview_rendering() 