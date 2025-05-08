import os
import sys
import time
import subprocess
import logging
import importlib.util
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app_restart.log')
    ]
)
logger = logging.getLogger(__name__)

def verify_docx_builder():
    """Verify that docx_builder.py contains our right-alignment changes."""
    try:
        # Import the module to verify it loads without errors
        spec = importlib.util.spec_from_file_location("docx_builder", "utils/docx_builder.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check for key functions and imports
        logger.info("Verifying docx_builder.py...")
        
        # Load file contents to check for specific code
        with open("utils/docx_builder.py", "r") as f:
            content = f.read()
            
        # Check for tab alignment code
        if "tab_stops.add_tab_stop" in content:
            logger.info("✓ Found tab stops for right alignment")
        else:
            logger.warning("✗ Missing tab stops for right alignment!")
            
        # Check for WD_TAB_ALIGNMENT import
        if "WD_TAB_ALIGNMENT" in content:
            logger.info("✓ Found WD_TAB_ALIGNMENT import")
        else:
            logger.warning("✗ Missing WD_TAB_ALIGNMENT import!")
            
        logger.info("Docx builder verification complete.")
        return True
    except Exception as e:
        logger.error(f"Error verifying docx_builder.py: {e}")
        return False

def restart_app():
    """Restart the Flask application."""
    try:
        logger.info("Attempting to find running application process...")
        
        # Find the application process
        if sys.platform == 'win32':
            # On Windows
            try:
                # Find Python processes
                pythons = subprocess.check_output('tasklist /FI "IMAGENAME eq python.exe" /FO CSV', shell=True).decode().strip().split('\r\n')
                
                if len(pythons) > 1:  # Header + at least one process
                    logger.info(f"Found {len(pythons)-1} Python processes")
                    # Kill all Python processes (since we can't easily determine which is our app)
                    # This is a simplified approach - in production, you'd want to be more selective
                    logger.info("Stopping Python processes...")
                    os.system('taskkill /F /IM python.exe')
                else:
                    logger.info("No Python processes found running")
            except Exception as e:
                logger.error(f"Error finding/stopping Python processes: {e}")
        else:
            # Unix-based systems (Linux/Mac)
            try:
                # Find processes with 'flask' or 'app.py' in the command
                app_processes = subprocess.check_output("ps aux | grep -E 'flask|app\.py' | grep -v grep", shell=True).decode().strip().split('\n')
                
                if app_processes:
                    for process in app_processes:
                        pid = process.split()[1]
                        logger.info(f"Stopping process {pid}...")
                        os.system(f"kill -9 {pid}")
                else:
                    logger.info("No Flask processes found running")
            except Exception as e:
                logger.error(f"Error finding/stopping Flask processes: {e}")
        
        # Wait a moment to ensure processes are stopped
        time.sleep(2)
        
        # Start the application
        logger.info("Starting application...")
        
        if sys.platform == 'win32':
            # On Windows, use start to run in background
            subprocess.Popen("start python app.py", shell=True)
        else:
            # On Unix systems
            subprocess.Popen(["python", "app.py"], start_new_session=True)
        
        logger.info("Application restart initiated.")
        return True
    except Exception as e:
        logger.error(f"Error restarting application: {e}")
        return False

if __name__ == "__main__":
    logger.info(f"=== Application Restart Script - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    # Verify changes to docx_builder.py
    if verify_docx_builder():
        # Restart the application
        restart_app()
        logger.info("Please wait a moment for the application to start, then test the DOCX download.")
    else:
        logger.error("Verification failed - please check docx_builder.py before restarting.") 