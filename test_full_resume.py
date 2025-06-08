import os
import sys
import logging
import shutil
import tempfile
import json
from pathlib import Path

# Add project root to sys.path to allow imports
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'utils'))
sys.path.insert(0, str(project_root / 'word_styles'))

from utils.docx_builder import build_docx

REQUEST_ID = "full_resume_test"

def setup_logging():
    """Setup logging to see all diagnostic messages"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s - %(name)s - %(message)s'
    )

def main():
    """Main function to run the full resume generation test"""
    print("🚀 FULL RESUME DIAGNOSTIC TEST (EXPERIENCE + EDUCATION)")
    print("=============================================================")
    
    setup_logging()
    
    # Create a temporary directory for this test run
    temp_dir = tempfile.mkdtemp(prefix="res_test_")
    logging.info(f"Created temp directory: {temp_dir}")

    try:
        # --- Copy Experience Data ---
        experience_source_path = project_root / '994ef54e-cca8-4406-96ab-298109d84436_experience.json'
        experience_dest_path = Path(temp_dir) / f"{REQUEST_ID}_experience.json"
        shutil.copy(experience_source_path, experience_dest_path)
        logging.info(f"Copied experience data to: {experience_dest_path}")

        # --- Copy Education Data ---
        education_source_path = project_root / 'full_resume_test_education.json'
        education_dest_path = Path(temp_dir) / f"{REQUEST_ID}_education.json"
        shutil.copy(education_source_path, education_dest_path)
        logging.info(f"Copied education data to: {education_dest_path}")

        # --- Run the DOCX Builder ---
        logging.info("Starting docx_builder with both sections...")
        docx_buffer = build_docx(REQUEST_ID, temp_dir, debug=True)
        
        # --- Save the Final Output ---
        output_filename = "final_full_resume_output.docx"
        with open(output_filename, "wb") as f:
            f.write(docx_buffer.getvalue())
        logging.info(f"✅ FINAL DOCUMENT SAVED: {output_filename}")
        logging.info(f"💾 PRE-RECONCILIATION FILE SAVED: resume_before_reconciliation.docx")

    finally:
        # --- Cleanup ---
        logging.info(f"Cleaning up temp directory: {temp_dir}")
        shutil.rmtree(temp_dir)

    print("\n=============================================================")
    print("🎉 FULL RESUME DIAGNOSTIC TEST COMPLETE")
    print("Please provide 'resume_before_reconciliation.docx' and the full log to O3.")

if __name__ == "__main__":
    main() 