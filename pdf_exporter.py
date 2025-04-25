import os
import logging
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import tempfile
from pathlib import Path
from style_manager import StyleManager

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
        # Use StyleManager to get the CSS path
        self.css_path = StyleManager.print_css_path()
        
        # Check if the CSS file exists
        if not os.path.exists(self.css_path):
            logger.error(f"Print CSS file not found at {self.css_path}. PDF styling may be incorrect.")
            self.css_path = None # Fallback or handle error
    
    def html_to_pdf(self, html_content, output_path=None):
        """
        Convert HTML content to PDF
        
        Args:
            html_content (str): HTML content to convert
            output_path (str, optional): Path where to save the PDF file
            
        Returns:
            str: Path to the generated PDF file
        """
        try:
            logger.info(f"Converting HTML to PDF")
            
            # Create a temporary path if none provided
            if not output_path:
                temp_dir = tempfile.gettempdir()
                output_path = os.path.join(temp_dir, f"resume_{os.urandom(4).hex()}.pdf")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Load CSS using the path from StyleManager
            css = None
            if self.css_path and os.path.exists(self.css_path):
                css = CSS(filename=self.css_path, font_config=self.font_config)
                logger.info(f"Using CSS from {self.css_path}")
            else:
                logger.warning("No valid CSS file found. Generating PDF without custom print styles.")
            
            # Convert HTML to PDF
            html = HTML(string=html_content)
            stylesheets = [css] if css else []
            html.write_pdf(output_path, stylesheets=stylesheets, font_config=self.font_config)
            
            logger.info(f"PDF generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
    
    def generate_resume_pdf(self, resume_html, metadata=None, output_path=None):
        """
        Generate a professionally formatted resume PDF
        
        Args:
            resume_html (str): Resume HTML content
            metadata (dict, optional): Metadata for the PDF (title, author, etc.)
            output_path (str, optional): Path where to save the PDF file
            
        Returns:
            str: Path to the generated PDF file
        """
        try:
            # Add HTML wrapper with proper doctype and meta tags, remove inline style block
            full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.get('title', 'Tailored Resume') if metadata else 'Tailored Resume'}</title>
    <!-- Styles are now linked via print.css -->
</head>
<body class="resume-document">
    <main class="resume-content">
        {resume_html}
    </main>
</body>
</html>
"""
            return self.html_to_pdf(full_html, output_path)
            
        except Exception as e:
            logger.error(f"Error generating resume PDF: {str(e)}")
            raise

def create_pdf_from_html(html_content, output_path=None, metadata=None):
    """
    Create a PDF file from HTML content
    
    Args:
        html_content (str): HTML content to convert
        output_path (str, optional): Path where to save the PDF file
        metadata (dict, optional): Metadata for the PDF (title, author, etc.)
        
    Returns:
        str: Path to the generated PDF file
    """
    exporter = PDFExporter()
    return exporter.generate_resume_pdf(html_content, metadata, output_path) 