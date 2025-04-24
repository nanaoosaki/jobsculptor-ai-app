"""
Resume Index Module

This module provides functionality for tracking and logging resume processing details.
It maintains a simple index of resumes and associated metadata like processing notes
and job targeting information.
"""

import os
import json
import logging
import time
from datetime import datetime
from threading import Lock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeIndex:
    """Class for managing a resume index that tracks processing details."""
    
    def __init__(self, index_file=None):
        """Initialize the resume index.
        
        Args:
            index_file (str, optional): Path to the index file. Defaults to 'resume_index.json'
                                       in the current directory.
        """
        self.index_file = index_file or os.path.join(os.path.dirname(__file__), 'resume_index.json')
        self.lock = Lock()  # For thread safety
        self.index = self._load_index()
    
    def _load_index(self):
        """Load the index from the index file."""
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Initialize with empty structure if file doesn't exist
                return {"resumes": {}, "last_updated": datetime.now().isoformat()}
        except Exception as e:
            logger.warning(f"Error loading resume index: {e}")
            # Return a default empty index on error
            return {"resumes": {}, "last_updated": datetime.now().isoformat()}
    
    def _save_index(self):
        """Save the index to the index file."""
        try:
            # Update the last updated timestamp
            self.index["last_updated"] = datetime.now().isoformat()
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
            
            # Save to a temporary file first to avoid corruption
            temp_file = f"{self.index_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
            
            # Rename temporary file to the actual file
            os.replace(temp_file, self.index_file)
            
            logger.debug(f"Resume index saved to {self.index_file}")
        except Exception as e:
            logger.warning(f"Error saving resume index: {e}")
    
    def add_resume(self, resume_id, filename, metadata=None):
        """Add a resume to the index.
        
        Args:
            resume_id (str): Unique identifier for the resume
            filename (str): Name of the resume file
            metadata (dict, optional): Additional metadata for the resume
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.lock:  # Thread safety
                # Initialize resume entry if it doesn't exist
                if resume_id not in self.index["resumes"]:
                    self.index["resumes"][resume_id] = {
                        "filename": filename,
                        "added_date": datetime.now().isoformat(),
                        "processing_history": [],
                        "notes": []
                    }
                else:
                    # Update the filename if resume already exists
                    self.index["resumes"][resume_id]["filename"] = filename
                
                # Add metadata if provided
                if metadata:
                    if "metadata" not in self.index["resumes"][resume_id]:
                        self.index["resumes"][resume_id]["metadata"] = {}
                    self.index["resumes"][resume_id]["metadata"].update(metadata)
                
                self._save_index()
                
                logger.info(f"Added resume to index: {resume_id} - {filename}")
                return True
        except Exception as e:
            logger.warning(f"Error adding resume to index: {e}")
            return False
    
    def add_note(self, resume_id, note):
        """Add a processing note to a resume.
        
        Args:
            resume_id (str): Unique identifier for the resume
            note (str): Processing note to add
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.lock:  # Thread safety
                # Check if resume exists in index
                if resume_id not in self.index["resumes"]:
                    logger.warning(f"Resume not found in index: {resume_id}")
                    return False
                
                # Add note with timestamp
                note_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "note": note
                }
                self.index["resumes"][resume_id]["notes"].append(note_entry)
                
                self._save_index()
                
                logger.info(f"Added note to resume {resume_id}: {note}")
                return True
        except Exception as e:
            logger.warning(f"Error adding note to resume: {e}")
            return False
    
    def add_processing_record(self, resume_id, process_type, details=None):
        """Add a processing record to a resume.
        
        Args:
            resume_id (str): Unique identifier for the resume
            process_type (str): Type of processing (e.g., 'tailoring', 'parsing')
            details (dict, optional): Additional details about the processing
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.lock:  # Thread safety
                # Check if resume exists in index
                if resume_id not in self.index["resumes"]:
                    logger.warning(f"Resume not found in index: {resume_id}")
                    return False
                
                # Add processing record with timestamp
                record = {
                    "timestamp": datetime.now().isoformat(),
                    "process_type": process_type,
                }
                
                if details:
                    record["details"] = details
                
                self.index["resumes"][resume_id]["processing_history"].append(record)
                
                self._save_index()
                
                logger.info(f"Added processing record to resume {resume_id}: {process_type}")
                return True
        except Exception as e:
            logger.warning(f"Error adding processing record to resume: {e}")
            return False
    
    def get_resume_info(self, resume_id):
        """Get information about a resume.
        
        Args:
            resume_id (str): Unique identifier for the resume
        
        Returns:
            dict: Resume information or None if not found
        """
        try:
            with self.lock:  # Thread safety
                if resume_id in self.index["resumes"]:
                    return self.index["resumes"][resume_id]
                else:
                    logger.warning(f"Resume not found in index: {resume_id}")
                    return None
        except Exception as e:
            logger.warning(f"Error getting resume info: {e}")
            return None


# Singleton instance
_resume_index = None
_index_lock = Lock()

def get_resume_index():
    """Get the resume index singleton instance.
    
    Returns:
        ResumeIndex: The resume index instance
    """
    global _resume_index
    
    if _resume_index is None:
        with _index_lock:  # Thread safety for singleton creation
            if _resume_index is None:  # Double-check pattern
                try:
                    _resume_index = ResumeIndex()
                except Exception as e:
                    logger.error(f"Error initializing resume index: {e}")
                    # Return a dummy index that won't crash but also won't persist
                    class DummyIndex:
                        def add_resume(self, *args, **kwargs): return True
                        def add_note(self, *args, **kwargs): return True
                        def add_processing_record(self, *args, **kwargs): return True
                        def get_resume_info(self, *args, **kwargs): return {}
                    
                    return DummyIndex()
    
    return _resume_index 