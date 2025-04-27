# File Dependencies for Resume Tailoring Application

## Overview
This document outlines the dependencies and interactions between various modules in the resume tailoring application, focusing on the key components and their roles.

## Key Modules and Their Dependencies

### resume_index.py

#### Purpose
The `resume_index.py` module is responsible for tracking and logging resume processing details. It maintains a simple index of resumes and associated metadata like processing notes and job targeting information.

#### Key Functions
- **add_resume**: Adds a resume to the index with metadata.
- **add_note**: Adds a processing note to a resume.
- **add_processing_record**: Adds a processing record to a resume.
- **get_resume_info**: Retrieves information about a resume.

#### Interactions
- **tailoring_handler.py**: Utilizes `get_resume_index` to log resumes and processing notes.
- **claude_integration.py**: May interact indirectly by providing data that is logged in the index.

#### Dependencies
- **os**: For file path operations.
- **json**: For reading and writing the index file.
- **logging**: For logging operations.
- **datetime**: For timestamping entries.
- **threading**: For ensuring thread safety with locks.

#### File Structure
- **resume_index.json**: The default file where the index is stored. It is created in the same directory as `resume_index.py` if not specified otherwise.

### Styling Workflow

#### SCSS and CSS
- **static/scss/_resume.scss**: Core styling for resumes.
- **static/scss/preview.scss**: Screen-specific styles.
- **static/scss/print.scss**: Print-specific styles.
- **static/css/preview.css**: Compiled CSS for screen preview.
- **static/css/print.css**: Compiled CSS for print output.

#### Build Process
- **sass**: Used to compile SCSS into CSS.
- **generate_tokens_css.py**: Generates SCSS tokens from `design_tokens.json`.

### Runtime Reload Caveat
`html_generator.py`, `style_manager.py`, and any other imported Python modules are **only loaded at Flask startup**. The development reloader detects template changes but *not* deep imports. After editing these files you must restart the server (`Ctrl-C` then `python app.py`).

## Updated Data Workflow and File Handling

### LLM Interaction
- **Structured JSON Output:** Modify LLM prompts to request structured JSON output only, avoiding bullet characters.
- **Raw Response Logging:** Save raw, timestamped JSON responses as ground truth in `uploads/api_responses/`.

### Parsing and Cleaning
- **Single Cleaning Step:** Apply `strip_bullet_prefix` immediately after parsing to relevant fields in `claude_integration.py`.
- **Session-Specific Storage:** Store cleaned data in session-specific temporary files in `uploads/temp_session_data/`.

### HTML/PDF Generation
- **Clean Data Usage:** Retrieve cleaned data for HTML/PDF generation in `html_generator.py`, ensuring no additional cleaning is performed.
- **CSS Styling:** Rely on CSS for visual bullet points, using `preview.css` and `print.css`.

### Logging and Debugging
- **Enhanced Logging:** Implement detailed logging for data state transitions and storage locations.

## Conclusion
The `resume_index.py` module is a critical component for maintaining a history of resume processing activities, providing valuable insights and traceability for the application. The styling workflow ensures consistent appearance across HTML and PDF outputs, with a clear build process for maintaining styles. 