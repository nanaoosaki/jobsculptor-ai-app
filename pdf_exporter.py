import os
import logging
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import tempfile
from pathlib import Path
from style_manager import StyleManager
from flask import render_template
from io import BytesIO
import io
import re # Added for debug dumping

# Set up logging
logger = logging.getLogger(__name__)

class PDFExporter:
    """
    PDF Exporter for Resume Tailoring Application
    
    Converts HTML resume content to professionally formatted PDF documents.
    Uses WeasyPrint for high-quality PDF generation with proper styling.
    """
    
    def __init__(self):
        """Initialize the PDF exporter with default configuration"""
        logger.info("Initializing PDF Exporter")
        self.font_config = FontConfiguration()
        # Use StyleManager to get the CSS paths
        self.print_css_path = StyleManager.print_css_path()
        self.preview_css_path = StyleManager.preview_css_path()
        
        # Validate paths
        if not os.path.exists(self.print_css_path):
            logger.error(f"Print CSS file not found at {self.print_css_path}. PDF styling may be incorrect.")
            self.print_css_path = None
        if not os.path.exists(self.preview_css_path):
            logger.warning(f"Preview CSS file not found at {self.preview_css_path}. Some base styles might be missing in PDF.")
            # We might still proceed as print.css should contain most necessary styles
            # self.preview_css_path = None # Optional: uncomment if preview CSS is critical
    
    def html_to_pdf(self, html_content, output_path=None):
        """
        Convert HTML content to PDF using both print and preview stylesheets.
        
        Args:
            html_content (str): HTML content to convert (should NOT contain <link> tags).
            output_path (str, optional): Path where to save the PDF file.
            
        Returns:
            str: Path to the generated PDF file.
        """
        try:
            logger.info(f"Converting HTML to PDF")
            
            # Create a temporary path if none provided
            if not output_path:
                temp_dir = tempfile.gettempdir()
                output_path = os.path.join(temp_dir, f"resume_{os.urandom(4).hex()}.pdf")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # --- BEGIN DEBUG DUMP ---
            # Create a debug directory in the project root
            # Assuming current working directory is the project root (D:\AI\manusResume6)
            project_root = os.getcwd() 
            debug_dir = os.path.join(project_root, "debug_output")
            os.makedirs(debug_dir, exist_ok=True)

            # Dump HTML input (which is full_html from generate_resume_pdf)
            html_debug_path = os.path.join(debug_dir, "debug_weasyprint_input.html")
            try:
                with open(html_debug_path, "w", encoding="utf-8") as f_html:
                    f_html.write(html_content)
                logger.info(f"DEBUG: Dumped HTML input to {html_debug_path}")
            except Exception as e_html_dump:
                logger.error(f"DEBUG: Failed to dump HTML input: {e_html_dump}")

            # Dump CSS content
            css_debug_path = os.path.join(debug_dir, "debug_weasyprint_combined_styles.css")
            combined_css_content_parts = []

            # 1. Inline styles from html_content (which is full_html)
            try:
                style_pattern = re.compile(r"<style>(.*?)</style>", re.DOTALL | re.IGNORECASE)
                inline_styles_match = style_pattern.search(html_content)
                if inline_styles_match:
                    inline_css = inline_styles_match.group(1).strip()
                    combined_css_content_parts.append("/* --- INLINE STYLES (from input HTML <head>) --- */")
                    combined_css_content_parts.append(inline_css)
                    combined_css_content_parts.append("\n") # Explicit newline marker for clarity
            except Exception as e_inline_css:
                logger.error(f"DEBUG: Failed to extract inline CSS: {e_inline_css}")

            # 2. External stylesheets (based on paths used to create CSS objects)
            # Re-read file contents for an accurate dump of what was fed to CSS()
            try:
                if self.print_css_path and os.path.exists(self.print_css_path):
                    combined_css_content_parts.append(f"/* --- PRINT CSS (from {self.print_css_path}) --- */")
                    with open(self.print_css_path, "r", encoding="utf-8") as f_css:
                        combined_css_content_parts.append(f_css.read())
                    combined_css_content_parts.append("\n")
                else:
                    logger.warning(f"DEBUG: Print CSS path not found or not set: {self.print_css_path}")
            except Exception as e_print_css:
                logger.error(f"DEBUG: Failed to read print CSS for dumping: {e_print_css}")
            
            try:
                if self.preview_css_path and os.path.exists(self.preview_css_path):
                    combined_css_content_parts.append(f"/* --- PREVIEW CSS (from {self.preview_css_path}) --- */")
                    with open(self.preview_css_path, "r", encoding="utf-8") as f_css:
                        combined_css_content_parts.append(f_css.read())
                    combined_css_content_parts.append("\n")
                else:
                    logger.warning(f"DEBUG: Preview CSS path not found or not set: {self.preview_css_path}")
            except Exception as e_preview_css:
                logger.error(f"DEBUG: Failed to read preview CSS for dumping: {e_preview_css}")

            try:
                with open(css_debug_path, "w", encoding="utf-8") as f_css_out:
                    f_css_out.write("\n".join(combined_css_content_parts))
                logger.info(f"DEBUG: Dumped CSS content to {css_debug_path}")
            except Exception as e_css_dump:
                logger.error(f"DEBUG: Failed to write combined CSS dump: {e_css_dump}")
            # --- END DEBUG DUMP ---

            # Load CSS stylesheets using paths from StyleManager
            stylesheets = []
            if self.print_css_path:
                try:
                    stylesheets.append(CSS(filename=self.print_css_path, font_config=self.font_config))
                    logger.info(f"Using Print CSS from {self.print_css_path}")
                except Exception as css_err:
                    logger.error(f"Error loading print CSS from {self.print_css_path}: {css_err}")
            
            if self.preview_css_path:
                 try:
                    # Load preview CSS as well to ensure all base styles are present
                    stylesheets.append(CSS(filename=self.preview_css_path, font_config=self.font_config))
                    logger.info(f"Using Preview CSS from {self.preview_css_path}")
                 except Exception as css_err:
                     logger.error(f"Error loading preview CSS from {self.preview_css_path}: {css_err}")

            if not stylesheets:
                 logger.warning("No valid CSS files found. Generating PDF without custom styles.")
            
            # Convert HTML to PDF
            # Ensure the input HTML doesn't contain problematic <link> tags
            # We assume the calling function provides clean HTML (for_screen=False)
            html = HTML(string=html_content)
            html.write_pdf(output_path, stylesheets=stylesheets, font_config=self.font_config)
            
            logger.info(f"PDF generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            # Log the HTML content that caused the error for debugging
            # Be cautious with logging potentially large HTML content
            log_html = html_content[:500] + "..." if len(html_content) > 500 else html_content
            logger.error(f"Error generating PDF: {str(e)}\n--- Failing HTML Start ---\n{log_html}\n--- Failing HTML End ---")
            raise
    
    def generate_resume_pdf(self, resume_html_body, metadata=None, output_path=None):
        """
        Generate a professionally formatted resume PDF.
        
        Args:
            resume_html_body (str): The core HTML content of the resume (inside the <body>).
                                    Should be generated with for_screen=False.
            metadata (dict, optional): Metadata for the PDF (title, author, etc.).
            output_path (str, optional): Path where to save the PDF file.
            
        Returns:
            str: Path to the generated PDF file.
        """
        try:
            # Construct the full HTML document structure needed by WeasyPrint
            # Important: No <link> tags here, as stylesheets are passed directly.
            # o3 CRITICAL FIX: Inline @page rule FIRST to ensure WeasyPrint processes it before any other CSS
            full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.get('title', 'Tailored Resume') if metadata else 'Tailored Resume'}</title>
    <!-- o3 Option B: Inline @page rule for immediate processing -->
    <style>
    @page {{ 
        margin: 0 !important; 
        size: A4; 
    }}
    html, body {{
        box-sizing: border-box !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        outline: none !important;
        background: none !important;
    }}
    </style>
    <!-- External stylesheets are applied programmatically by WeasyPrint AFTER inline styles -->
</head>
<body class="resume-document">
    <!-- The main resume content generated with for_screen=False -->
    {resume_html_body}
</body>
</html>
"""
            # Pass the clean, full HTML to the core conversion method
            return self.html_to_pdf(full_html, output_path)
            
        except Exception as e:
            logger.error(f"Error in generate_resume_pdf wrapper: {str(e)}")
            raise

# Updated helper function signature
def create_pdf_from_html(html_body_content, output_path=None, metadata=None):
    """
    Create a PDF file from the body HTML content.
    
    Args:
        html_body_content (str): HTML content for the body (generated with for_screen=False).
        output_path (str, optional): Path where to save the PDF file.
        metadata (dict, optional): Metadata for the PDF.
        
    Returns:
        str: Path to the generated PDF file.
    """
    exporter = PDFExporter()
    return exporter.generate_resume_pdf(html_body_content, metadata, output_path)

def generate_pdf_from_html(resume_data, output_path=None):
    """
    Generate a PDF from the resume data using WeasyPrint.
    
    Args:
        resume_data (dict): Dictionary containing the tailored resume data
        output_path (str, optional): Path to save the PDF. If None, returns BytesIO.
        
    Returns:
        BytesIO or None: If output_path is None, returns BytesIO containing the PDF.
    """
    # Render the HTML template with the resume data
    html_content = render_template('resume_pdf.html', resume=resume_data)
    
    # Define the CSS files to use
    css_files = [
        'static/css/print.css'  # The print-specific CSS
    ]
    
    # Create CSS objects from the files
    css_list = [CSS(filename=css_file) for css_file in css_files]
    
    # Create the HTML object
    html = HTML(string=html_content)
    
    # Generate the PDF
    if output_path:
        # Save to file
        html.write_pdf(output_path, stylesheets=css_list)
        return None
    else:
        # Return as BytesIO
        pdf_buffer = BytesIO()
        html.write_pdf(pdf_buffer, stylesheets=css_list)
        pdf_buffer.seek(0)
        return pdf_buffer 