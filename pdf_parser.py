import os
import logging
import PyPDF2
from pdfminer.high_level import extract_text
import traceback

# Configure logging
logger = logging.getLogger(__name__)

def read_pdf_file(filepath):
    """
    Read and extract content from a PDF file
    
    Args:
        filepath (str): Path to the PDF file
        
    Returns:
        dict: Dictionary with extracted content
    """
    content = {
        'paragraphs': [],
        'tables': []  # PDFs don't have easy table extraction, will be empty
    }
    
    try:
        logger.info(f"Extracting content from PDF file: {filepath}")
        
        # Try using pdfminer first (better text extraction with layout preservation)
        try:
            text = extract_text(filepath)
            paragraphs = [p for p in text.split('\n\n') if p.strip()]
            
            # Process paragraphs
            for para in paragraphs:
                if para.strip():
                    # We can't easily determine formatting from PDF, so use defaults
                    content['paragraphs'].append({
                        'text': para.strip(),
                        'style': 'Normal',
                        'alignment': None,  # Can't reliably determine alignment
                        'bold': False,      # Can't reliably determine bold
                        'italic': False,    # Can't reliably determine italic
                        'font_size': None   # Can't reliably determine font size
                    })
            
            logger.info(f"Successfully extracted {len(paragraphs)} paragraphs from PDF using pdfminer")
            
        except Exception as e:
            logger.warning(f"pdfminer extraction failed, falling back to PyPDF2: {str(e)}")
            
            # Fallback to PyPDF2
            with open(filepath, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                
                # Extract text from each page
                for page_num in range(len(reader.pages)):
                    text += reader.pages[page_num].extract_text() + "\n\n"
                
                # Split text into paragraphs based on double newlines
                paragraphs = [p for p in text.split('\n\n') if p.strip()]
                
                # Process paragraphs
                for para in paragraphs:
                    if para.strip():
                        content['paragraphs'].append({
                            'text': para.strip(),
                            'style': 'Normal',
                            'alignment': None,
                            'bold': False,
                            'italic': False,
                            'font_size': None
                        })
                
                logger.info(f"Successfully extracted {len(paragraphs)} paragraphs from PDF using PyPDF2")
        
        # Attempt to identify headers and sections based on text characteristics
        # This is more heuristic-based than the DOCX parser
        _identify_potential_headers(content['paragraphs'])
        
        return content
        
    except Exception as e:
        logger.error(f"Error extracting content from PDF: {str(e)}")
        logger.error(traceback.format_exc())
        return content

def _identify_potential_headers(paragraphs):
    """
    Attempt to identify headers in the PDF content based on text characteristics
    
    Args:
        paragraphs (list): List of paragraph dictionaries
    """
    for i, para in enumerate(paragraphs):
        text = para['text'].strip()
        
        # Check for potential headers based on text characteristics
        is_potential_header = False
        
        # Short paragraphs that might be headers
        if len(text) < 60 and text.strip():
            # Check if text ends with a colon, which is common for section headers
            if text.endswith(':'):
                is_potential_header = True
            
            # Check if text is in ALL CAPS
            elif text.isupper():
                is_potential_header = True
                
            # Check if the text matches common resume section names
            elif any(section in text.lower() for section in [
                'summary', 'objective', 'experience', 'education', 
                'skills', 'projects', 'work', 'employment', 'qualification',
                'certification', 'contact', 'reference', 'professional',
                'achievement', 'publication', 'language', 'volunteer'
            ]):
                is_potential_header = True
        
        # Update paragraph with potential header status
        if is_potential_header:
            paragraphs[i]['style'] = 'Heading 1'
            paragraphs[i]['bold'] = True 