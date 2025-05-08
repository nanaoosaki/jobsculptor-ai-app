# File Dependencies for Resume Tailoring Application

## Overview
This document outlines the dependencies and interactions between various modules in the resume tailoring application, focusing on the newly implemented features and scripts.

## New and Renamed Scripts

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

### docx_builder.py

#### Purpose
The `docx_builder.py` module generates Microsoft Word (.docx) files with consistent styling based on design tokens. It formats resume data into a structured DOCX format.

#### Key Functions
- **load_section_json**: Loads JSON data for a specific section of the resume.
- **_apply_paragraph_style**: Applies styles to paragraphs based on DOCX style definitions.
- **build_docx**: Constructs the DOCX file from the resume data.

#### Dependencies
- **os**: For file path operations.
- **json**: For reading and writing JSON data.
- **logging**: For logging operations.
- **BytesIO**: For handling in-memory byte streams.
- **docx**: For creating and manipulating DOCX files.

### Updated Workflow for DOCX Download Button Process

1. **User Interaction**: The user clicks the DOCX download button in the `index.html` template.
2. **Route Handling**: The request is sent to the `/download/docx/<request_id>` route in `app.py`.
3. **DOCX Generation**:
   - The `download_docx_resume` function in `app.py` calls the `build_docx` function from `docx_builder.py`.
   - The `build_docx` function retrieves the necessary resume data from temporary session files and applies styles based on the design tokens.
4. **File Creation**: The generated DOCX file is created in memory and returned as a response to the user.
5. **File Download**: The user receives the DOCX file as a downloadable attachment.

### Conclusion
The recent updates and additions to the resume tailoring application enhance its functionality and maintainability. The `resume_index.py` and `docx_builder.py` modules play critical roles in managing resume processing and generating downloadable documents, respectively. Keeping this documentation up-to-date ensures clarity and understanding of the application's structure and workflow.

## Updated I/O and Workflow

- **Session-Specific Data Storage**: All cleaned resume data is now stored using UUIDs in `static/uploads/temp_session_data/`, ensuring data isolation and multi-user compatibility.
- **Raw LLM Responses**: Continue to be stored with timestamps in `static/uploads/api_responses/` for logging and debugging.
- **Log Messages**: Updated to accurately reflect file operations and enhance traceability.
- **Data Flow**: LLM -> Structured JSON -> Save Structured JSON with UUID -> Load Structured JSON with UUID -> Format to HTML and PDF.
- **PDF Export Process**: Enhanced with WeasyPrint for consistent and professional output, ensuring alignment with HTML preview and inclusion of role descriptions.

## Conclusion
The `resume_index.py` module is a critical component for maintaining a history of resume processing activities, providing valuable insights and traceability for the application. The recent updates ensure a more robust and consistent data handling process, improving both functionality and user experience.

---

## Learnings from Recent Fixes

### Key Learnings:

1. **Understanding Data Types:**
   - Ensure all functions handling data are aware of potential multiple types (e.g., strings, lists, dictionaries) and can process them correctly.
   - Implement type-aware checks to prevent errors like `AttributeError` when methods assume a specific type.

2. **Modular Code Review:**
   - Review all related functions and modules that interact with the data when fixing an issue. Ensure changes in one part of the codebase don't introduce errors elsewhere.

3. **Testing and Validation:**
   - Thoroughly test the application with various inputs after implementing a fix to ensure the issue is resolved and no new issues are introduced.
   - Use logs to trace the flow of data and identify where errors occur.

4. **Documentation:**
   - Keep documentation up-to-date with changes in the codebase, including updating any dependencies or interactions between modules.
   - Documenting solutions and learnings helps future developers understand the context and reasoning behind changes.

---

## Updated Dependencies and Interactions

### sample_experience_snippet.py

#### Purpose
The `sample_experience_snippet.py` script provides example data for the LLM to follow, ensuring consistency in the output of tailored achievements. It includes examples with '??' placeholders to guide the LLM in generating quantifiable achievements.

#### Interactions
- **claude_integration.py**: Utilizes examples from `sample_experience_snippet.py` to improve the consistency and structure of the tailored achievements.

### Optimizations for Quantifiable Achievements

#### Overview
Recent optimizations have focused on ensuring that every achievement bullet point in the experience section contains a quantifiable metric, either as a number or using the '??' placeholder.

#### Key Changes
- **Guardrail Logic**: Updated to inject '??' when no digit or placeholder is present, without relying on unit words or placement tokens.
- **Prompt Optimization**: Emphasizes the action-impact-influence structure, generating concise and structured achievements with a character limit of 130 characters.
- **Example Inclusion**: Examples with '??' in `sample_experience_snippet.py` provide a pattern for the LLM to follow, improving the consistency of the output.

#### Implications
- **Structured Output**: Future optimizations should focus on clear, structured prompts with explicit rules, maintaining a balance between flexibility and strict guidelines.
- **System Message Reinforcement**: Reinforcing key rules in the system message can further improve compliance with the desired output format.
- **Post-Processing Checks**: Implementing post-processing checks, such as assertions for character limits, can serve as an additional safeguard to catch any deviations from the expected output.

## Token Generation Script

### tools/generate_tokens_css.py (Renamed to generate_tokens.py)

- **Original Purpose**: Reads `design_tokens.json` and writes SCSS variable definitions to `static/scss/_tokens.scss`.
- **New Purpose**: Expanded to also generate DOCX style mappings in addition to SCSS variables. The script has been renamed to reflect its broader functionality.
- **Input**: `design_tokens.json` (design tokens for colors, spacing, margins, fonts, etc.).
- **Outputs**:
  - `static/scss/_tokens.scss` containing SCSS `$` variables
  - `static/styles/_docx_styles.json` containing DOCX style mappings
- **Usage**: Run `python tools/generate_tokens.py` whenever `design_tokens.json` changes to regenerate both SCSS and DOCX tokens.
- **Functions**:
  - `generate_scss_variables()`: Generates SCSS variables from design tokens
  - `generate_docx_style_mappings()`: Generates DOCX style mappings from design tokens
  - `hex_to_rgb()`: Helper function to convert hex colors to RGB for DOCX styles

### SCSS and DOCX Style Generation Workflow

1. **Regenerate Tokens**:
   - Run `python tools/generate_tokens.py` to update both `_tokens.scss` and `_docx_styles.json`.
2. **Compile SCSS**:
   - Use Sass to compile SCSS to CSS:
     ```bash
     sass static/scss/preview.scss static/css/preview.css
     sass static/scss/print.scss static/css/print.css
     ```
3. **Restart Server**:
   - Restart the Flask dev server (`Ctrl-C` then `python app.py`) to load updated templates, CSS, and DOCX styles.

This workflow ensures that design token edits propagate through to HTML preview, PDF output, and DOCX downloads, maintaining consistent styling across all formats.

### DOCX Format Workflow

1. **User Requests DOCX**:
   - User clicks the DOCX download button in web UI
   - Request is sent to `/download/docx/<request_id>` endpoint

2. **Server Processing**:
   - Flask route handler calls `utils.docx_builder.build_docx()`
   - `build_docx()` loads section data from JSON files in temp session directory
   - Section data is formatted according to DOCX styling rules
   - Document is assembled with proper styles and formatting

3. **File Delivery**:
   - DOCX file is built in memory using python-docx
   - File is sent as attachment with proper MIME type
   - Browser triggers download for the user

4. **Current Limitations**:
   - Skills section formatting needs improvement to properly handle nested structures
   - Section loading may have path or naming convention issues
   - Some sections may not be properly loaded or formatted

### utils/docx_builder.py

- **Purpose**: Generates Microsoft Word (.docx) files with styling based on the project's design tokens.
- **Key Functions**:
  - `load_section_json()`: Loads resume section data from JSON files
  - `_apply_paragraph_style()`: Applies styling to document paragraphs 
  - `build_docx()`: Main function that builds the complete DOCX document
- **Dependencies**:
  - `python-docx`: For creating and styling Word documents
  - `style_manager.py`: To access design token mappings
- **Inputs**: Session data JSON files from `static/uploads/temp_session_data/`
- **Output**: In-memory DOCX file as BytesIO object

--- 