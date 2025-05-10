#!/usr/bin/env python3
"""
DOCX Testing with Real Resume Data

This script tests the DOCX generation with real resume data from the application.
It allows you to test the new styling approach without running the full application.
"""

import os
import sys
import json
import argparse
from pathlib import Path
import logging

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from utils.docx_builder import build_docx
from utils.docx_debug import generate_debug_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_request_ids(temp_dir):
    """Find all request IDs in the temp directory."""
    request_ids = set()
    
    try:
        for filename in os.listdir(temp_dir):
            parts = filename.split('_')
            if len(parts) >= 3 and parts[0] == 'request':
                request_ids.add(parts[1])
    except Exception as e:
        logger.error(f"Error finding request IDs: {e}")
    
    return list(request_ids)

def main():
    """Main function to test DOCX generation with real resume data."""
    parser = argparse.ArgumentParser(description='Test DOCX generation with real resume data')
    parser.add_argument('--request-id', help='Specific request ID to process')
    parser.add_argument('--list', action='store_true', help='List available request IDs')
    parser.add_argument('--temp-dir', default=None, help='Path to temp directory')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--output-dir', default=None, help='Directory to save output files')
    
    args = parser.parse_args()
    
    # Determine temp directory
    if args.temp_dir:
        temp_dir = args.temp_dir
    else:
        # Default to the standard temp directory in the application
        temp_dir = Path(parent_dir) / 'uploads' / 'temp_session_data'
    
    # Ensure temp directory exists
    if not os.path.exists(temp_dir):
        logger.error(f"Temp directory not found: {temp_dir}")
        return 1
    
    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path(parent_dir) / 'docx_test_output'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Using temp directory: {temp_dir}")
    logger.info(f"Using output directory: {output_dir}")
    
    # List available request IDs
    request_ids = find_request_ids(temp_dir)
    
    if args.list:
        logger.info(f"Available request IDs: {', '.join(request_ids)}")
        return 0
    
    # Process specific request ID
    request_id = args.request_id
    
    if not request_id:
        if not request_ids:
            logger.error("No request IDs found in temp directory")
            return 1
        
        # Use the most recent request ID
        request_id = request_ids[-1]
        logger.info(f"No request ID specified, using most recent: {request_id}")
    
    # Generate DOCX file
    try:
        logger.info(f"Generating DOCX for request ID: {request_id}")
        docx_bytes = build_docx(request_id, temp_dir, debug=args.debug)
        
        # Save the DOCX file
        output_path = output_dir / f"test_resume_{request_id}.docx"
        with open(output_path, 'wb') as f:
            f.write(docx_bytes.getvalue())
        
        logger.info(f"DOCX file saved to: {output_path}")
        
        # Check for debug report
        debug_report_path = Path(parent_dir) / f'debug_{request_id}.json'
        if os.path.exists(debug_report_path):
            logger.info(f"Debug report found at: {debug_report_path}")
        
        return 0
    except Exception as e:
        logger.error(f"Error generating DOCX: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main()) 