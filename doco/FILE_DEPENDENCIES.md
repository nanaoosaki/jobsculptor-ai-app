# File Dependencies for Resume Tailoring Application

## Overview
This document outlines the dependencies and interactions between various modules in the resume tailoring application, focusing on the newly implemented `resume_index.py` module.

## resume_index.py

### Purpose
The `resume_index.py` module is responsible for tracking and logging resume processing details. It maintains a simple index of resumes and associated metadata like processing notes and job targeting information.

### Key Functions
- **add_resume**: Adds a resume to the index with metadata.
- **add_note**: Adds a processing note to a resume.
- **add_processing_record**: Adds a processing record to a resume.
- **get_resume_info**: Retrieves information about a resume.

### Interactions
- **tailoring_handler.py**: Utilizes `get_resume_index` to log resumes and processing notes.
- **claude_integration.py**: May interact indirectly by providing data that is logged in the index.

### Dependencies
- **os**: For file path operations.
- **json**: For reading and writing the index file.
- **logging**: For logging operations.
- **datetime**: For timestamping entries.
- **threading**: For ensuring thread safety with locks.

### File Structure
- **resume_index.json**: The default file where the index is stored. It is created in the same directory as `resume_index.py` if not specified otherwise.

## Runtime Reload Caveat
`html_generator.py`, `style_manager.py`, and any other imported Python modules are **only loaded at Flask startup**.  The development reloader detects template changes but *not* deep imports.  After editing these files you must restart the server (`Ctrl-C` then `python app.py`).

## Conclusion
The `resume_index.py` module is a critical component for maintaining a history of resume processing activities, providing valuable insights and traceability for the application. 