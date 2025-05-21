# File Dependencies for Resume Tailoring Application

## Overview
This document outlines the dependencies and interactions between various modules in the resume tailoring application, focusing on the newly implemented features and scripts.

## Core Application Modules

### app.py

#### Purpose
The `app.py` module serves as the main Flask application, handling all web routes, user interactions, and orchestrating the entire resume tailoring process.

#### Key Functions
- **index**: Main route for displaying the UI
- **upload_resume**: Handles resume file uploads
- **parse_job**: Processes job listing URLs/text
- **tailor_resume**: Coordinates the tailoring process
- **preview_resume**: Serves HTML previews of tailored resumes
- **download_resume**: Generates and serves PDF downloads
- **download_docx_resume**: Generates and serves DOCX downloads

#### Dependencies
- **Flask**: For web server and routing
- **tailoring_handler.py**: For resume tailoring coordination
- **upload_handler.py**: For file upload processing
- **job_parser_handler.py**: For job analysis
- **resume_index.py**: For tracking processed resumes
- **pdf_exporter.py**: For PDF generation
- **html_generator.py**: For HTML preview generation
- **docx_builder.py**: For DOCX generation

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
- **word_styles**: Package for advanced DOCX styling

### html_generator.py

#### Purpose
Generates HTML previews of tailored resumes for browser display and PDF generation, ensuring consistent styling across formats.

#### Key Functions
- **generate_preview_from_llm_responses**: Creates HTML from tailored resume sections
- **format_section_for_html**: Formats specific resume sections into HTML
- **format_skill_for_html**: Formats skill entries into HTML
- **create_full_html_document**: Wraps HTML fragment in complete HTML document for PDF export

#### Dependencies
- **os**: For file path operations
- **json**: For reading section data
- **logging**: For error tracking
- **style_manager.py**: For accessing styling information
- **metric_utils.py**: For handling quantifiable metrics

#### I/O
- **Input**: JSON files from `static/uploads/temp_session_data/{request_id}_{section}.json`
- **Output**: HTML fragments for browser preview or complete HTML documents for PDF generation

### config.py

#### Purpose
Central configuration management for the entire application, handling environment variables, API keys, and application settings.

#### Key Functions
- **load_config**: Loads configuration from environment variables
- **get_api_key**: Retrieves API keys safely
- **is_development**: Detects if running in development mode

#### Dependencies
- **os**: For environment variable access
- **dotenv**: For loading .env files in development

#### I/O
- **Input**: Environment variables, .env files
- **Output**: Configuration settings used throughout the application

### claude_integration.py

#### Purpose
Handles all interactions with Claude API, providing tailored resume content based on job requirements.

#### Key Functions
- **tailor_resume_with_claude**: Main function for resume tailoring via Claude
- **tailor_section**: Tailors individual resume sections
- **prepare_prompt**: Creates specialized prompts for different sections
- **process_achievements**: Ensures achievements contain quantifiable metrics

#### Dependencies
- **anthropic**: For Claude API access
- **claude_api_logger.py**: For logging API requests and responses
- **sample_experience_snippet.py**: For example achievement structures
- **metric_utils.py**: For handling quantifiable metrics

#### I/O
- **Input**: Resume sections, job details
- **Output**: Tailored content, saved API responses to `static/uploads/api_responses/`

### resume_processor.py

#### Purpose
Processes uploaded resume files, extracting text and structuring sections for tailoring.

#### Key Functions
- **process_resume**: Main function for resume processing
- **extract_text**: Extracts plain text from DOCX or PDF files
- **detect_sections**: Identifies standard resume sections

#### Dependencies
- **docx2txt**: For DOCX text extraction
- **pdf_parser.py**: For PDF text extraction
- **llm_resume_parser.py**: For advanced section parsing

#### I/O
- **Input**: Uploaded resume files (DOCX/PDF)
- **Output**: Structured resume sections for tailoring

### job_parser.py

#### Purpose
Extracts job details from various sources, including LinkedIn URLs and plain text.

#### Key Functions
- **parse_job_url**: Extracts job details from URLs
- **parse_job_text**: Processes plain text job descriptions
- **extract_linkedin_job**: Special handling for LinkedIn job posts

#### Dependencies
- **requests**: For URL fetching
- **BeautifulSoup**: For HTML parsing
- **llm_job_analyzer.py**: For deep job requirement analysis

#### I/O
- **Input**: Job URLs or text
- **Output**: Structured job details, requirements, and key skills

### llm_job_analyzer.py

#### Purpose
Uses LLMs to analyze job postings for requirements, skills, and candidate profiles.

#### Key Functions
- **analyze_job**: Main function for job analysis
- **extract_requirements**: Identifies key job requirements
- **create_candidate_profile**: Builds ideal candidate profile

#### Dependencies
- **anthropic/openai**: For LLM access
- **claude_api_logger.py**: For logging API interactions

#### I/O
- **Input**: Raw job posting text
- **Output**: Structured job analysis JSON

### llm_resume_parser.py

#### Purpose
Uses LLMs to intelligently parse resume content into structured sections.

#### Key Functions
- **parse_resume_with_llm**: Main parsing function
- **identify_sections**: Detects standard resume sections
- **structure_sections**: Organizes content into structured format

#### Dependencies
- **anthropic/openai**: For LLM access
- **claude_api_logger.py**: For logging API interactions

#### I/O
- **Input**: Raw resume text
- **Output**: Structured resume sections JSON

## Utility Modules

### claude_api_logger.py

#### Purpose
Provides logging functionality for Claude API interactions, helpful for debugging and auditing.

#### Key Functions
- **log_request**: Logs API requests with timestamps
- **log_response**: Logs API responses with tracking information
- **get_log_path**: Generates standardized log file paths

#### Dependencies
- **logging**: For log management
- **os**: For file operations
- **json**: For structured data logging

#### I/O
- **Input**: API requests and responses
- **Output**: Log files in the logs directory

### format_handler.py

#### Purpose
Handles different document formats and conversions between formats.

#### Key Functions
- **detect_format**: Identifies file formats
- **convert_to_text**: Converts various formats to plain text
- **is_supported_format**: Checks if a format is supported

#### Dependencies
- **docx2txt**: For DOCX handling
- **pdf_parser.py**: For PDF handling

#### I/O
- **Input**: Files in various formats
- **Output**: Normalized text content

### job_parser_handler.py

#### Purpose
Orchestrates the job parsing process, coordinating between different parsers.

#### Key Functions
- **handle_job_url**: Processes job URLs
- **handle_job_text**: Processes job description text
- **save_job_data**: Stores parsed job information

#### Dependencies
- **job_parser.py**: For basic job parsing
- **llm_job_analyzer.py**: For advanced job analysis

#### I/O
- **Input**: Job URLs or text from web interface
- **Output**: Structured job data in JSON format

### metric_utils.py

#### Purpose
Handles quantifiable metrics in achievements, ensuring all bullets have measurable impact.

#### Key Functions
- **normalize_metrics**: Ensures consistent metric format
- **inject_placeholder**: Adds placeholder metrics when needed
- **clean_achievement**: Formats achievement bullets

#### Dependencies
- **re**: For regex pattern matching

#### I/O
- **Input**: Achievement text with varying metric formats
- **Output**: Standardized achievement text with proper metrics

### pdf_exporter.py

#### Purpose
Converts HTML resume previews into downloadable PDF documents.

#### Key Functions
- **create_pdf_from_html**: Main function for PDF generation
- **apply_pdf_styles**: Applies print-specific styles to the HTML

#### Dependencies
- **weasyprint**: For HTML to PDF conversion
- **style_manager.py**: For accessing styling information

#### I/O
- **Input**: HTML document from html_generator.py
- **Output**: PDF file saved to static/uploads/

### pdf_parser.py

#### Purpose
Extracts text and structure from PDF resume files.

#### Key Functions
- **extract_text_from_pdf**: Main function for text extraction
- **analyze_pdf_structure**: Identifies document structure

#### Dependencies
- **pypdf**: For PDF processing
- **pdfminer**: For advanced text extraction

#### I/O
- **Input**: PDF resume files
- **Output**: Extracted text content

### restart_app.py

#### Purpose
Utility script for restarting the application after changes, particularly useful in development.

#### Key Functions
- **restart_flask_app**: Restarts the Flask development server
- **check_file_changes**: Monitors file changes to trigger restarts

#### Dependencies
- **os**: For process management
- **subprocess**: For executing commands

#### I/O
- **Input**: File system changes
- **Output**: Application restart actions

### resume_formatter.py

#### Purpose
Formats parsed resume content into standardized structure for processing.

#### Key Functions
- **format_resume**: Main formatting function
- **standardize_sections**: Converts various section formats to standard
- **clean_bullet_points**: Ensures consistent bullet point format

#### Dependencies
- **re**: For pattern matching

#### I/O
- **Input**: Raw parsed resume sections
- **Output**: Standardized resume structure

### resume_styler.py

#### Purpose
Applies YC-Eddie styling to resume content for consistent formatting.

#### Key Functions
- **style_resume**: Main styling function
- **apply_header_style**: Formats section headers
- **style_bullet_points**: Formats achievement bullets

#### Dependencies
- **docx**: For document styling
- **style_engine.py**: For accessing design tokens

#### I/O
- **Input**: Resume content
- **Output**: Styled resume structure

### style_engine.py

#### Purpose
Manages styling rules and token application across different output formats.

#### Key Functions
- **load_design_tokens**: Loads styling variables from design_tokens.json
- **apply_style**: Applies styles to different elements
- **get_docx_style**: Retrieves DOCX-specific styling values

#### Dependencies
- **json**: For reading design tokens
- **os**: For file operations

#### I/O
- **Input**: design_tokens.json configuration
- **Output**: Applied styling rules

### style_manager.py

#### Purpose
High-level style management interface for the application, ensuring consistent styling.

#### Key Functions
- **get_style**: Retrieves style values for different formats
- **get_tokens**: Gets raw design tokens
- **apply_html_style**: Applies styles to HTML elements
- **apply_docx_style**: Applies styles to DOCX elements

#### Dependencies
- **style_engine.py**: For low-level styling operations
- **design_tokens.json**: For style definitions

#### I/O
- **Input**: Style requests from various output generators
- **Output**: Consistent style application across formats

### tailoring_handler.py

#### Purpose
Orchestrates the overall resume tailoring process.

#### Key Functions
- **handle_tailoring**: Main function for tailoring coordination
- **prepare_resume_data**: Gets resume data ready for LLM processing
- **process_llm_responses**: Handles returned tailored content

#### Dependencies
- **claude_integration.py**: For LLM interactions
- **resume_processor.py**: For resume data
- **job_parser.py**: For job requirement data
- **html_generator.py**: For preview generation

#### I/O
- **Input**: Resume and job data
- **Output**: Tailored resume sections saved as JSON files

### token_counts.py

#### Purpose
Utility for counting tokens in various text inputs, important for LLM interactions.

#### Key Functions
- **count_tokens**: Estimates token count for text
- **check_token_limits**: Verifies text is within token limits

#### Dependencies
- **tiktoken**: For OpenAI-compatible tokenization

#### I/O
- **Input**: Text content
- **Output**: Token count estimates

### upload_handler.py

#### Purpose
Handles file uploads and session management.

#### Key Functions
- **handle_resume_upload**: Processes resume file uploads
- **save_uploaded_file**: Saves files with proper naming
- **manage_session**: Handles user session data

#### Dependencies
- **flask**: For session management
- **resume_processor.py**: For processing uploaded resumes

#### I/O
- **Input**: Uploaded files from web interface
- **Output**: Saved files and session information

### yc_eddie_styler.py

#### Purpose
Applies YC-Eddie specific styling guidelines to resume documents.

#### Key Functions
- **style_resume_yc**: Main function for YC-specific styling
- **format_headers**: Applies box styling to headers
- **apply_yc_typography**: Sets font styles per YC guidelines

#### Dependencies
- **docx**: For document manipulation
- **style_engine.py**: For style configuration

#### I/O
- **Input**: Resume document
- **Output**: YC-Eddie styled document

### yc_resume_generator.py

#### Purpose
Generates resumes specifically formatted according to YC-Eddie guidelines.

#### Key Functions
- **generate_resume**: Main generation function
- **build_sections**: Creates properly formatted sections
- **apply_yc_guidelines**: Ensures adherence to YC standards

#### Dependencies
- **docx**: For document creation
- **yc_eddie_styler.py**: For styling application

#### I/O
- **Input**: Tailored resume content
- **Output**: Complete YC-formatted resume document

## word_styles Package

The `word_styles` package was implemented to provide a more reliable and maintainable approach to styling DOCX documents, particularly focused on solving issues with section header spacing and box height.

### word_styles/registry.py

- **Purpose**: Central registry for paragraph and box styles in DOCX documents.
- **Key Classes**: 
  - `ParagraphBoxStyle`: Dataclass representing styling attributes for paragraphs and boxes.
  - `StyleRegistry`: Manages a collection of styles and applies them to documents.
- **Key Functions**:
  - `get_or_create_style()`: Retrieves or creates a style in a document based on a registered style.
  - `apply_direct_paragraph_formatting()`: Applies formatting directly to paragraphs.
  - `apply_compatibility_settings()`: Applies Word compatibility settings for cross-platform consistency.
- **Dependencies**:
  - `docx`: For creating and manipulating DOCX files.
  - `xml_utils.py`: For XML node creation and manipulation.
- **Used by**: `docx_builder.py`, `section_builder.py`

### word_styles/section_builder.py

- **Purpose**: Creates section headers with table-based wrappers and manages content spacing.
- **Key Functions**:
  - `add_section_header()`: Adds a section header with proper styling and spacing.
  - `_add_table_section_header()`: Implements table-based headers with controlled margins.
  - `_set_cell_margins()`: Sets custom margins for table cells.
  - `_set_cell_vertical_alignment()`: Controls vertical alignment within cells.
  - `add_content_paragraph()`: Adds content with consistent styling.
  - `remove_empty_paragraphs()`: Cleans up unwanted paragraphs.
- **Dependencies**:
  - `docx`: For DOCX document manipulation.
  - `registry.py`: For style retrieval and application.
- **Used by**: `docx_builder.py`

### word_styles/xml_utils.py

- **Purpose**: Utilities for direct XML manipulation in DOCX files.
- **Key Functions**:
  - `make_spacing_node()`: Creates XML nodes for paragraph spacing.
  - `make_border_node()`: Creates XML nodes for borders.
  - `make_outline_level_node()`: Creates XML nodes for document structure.
  - `make_compatibility_node()`: Creates XML nodes for Word compatibility settings.
  - `twips_from_pt()`: Converts points to twips (1/20th of a point).
- **Dependencies**:
  - `docx.oxml`: For XML manipulation within DOCX.
- **Used by**: `registry.py`, `section_builder.py`

## Updated Workflows

### Resume Upload and Parsing Workflow

1. **User Uploads Resume**:
   - User submits resume through web interface
   - `app.py` receives request and passes to `upload_handler.py`
   - `upload_handler.py` saves file and initiates processing

2. **Resume Processing**:
   - `resume_processor.py` extracts text using `format_handler.py` (which selects appropriate parser)
   - For DOCX: Uses `docx2txt`
   - For PDF: Uses `pdf_parser.py` 
   - `llm_resume_parser.py` analyzes text using Claude/OpenAI to identify sections
   - `resume_formatter.py` standardizes the sections

3. **Data Storage**:
   - Structured sections saved to `static/uploads/temp_session_data/`
   - Session information updated with resume data
   - `resume_index.py` logs the processed resume

### Job Analysis Workflow

1. **User Provides Job Details**:
   - User enters URL or text through web interface
   - `app.py` passes to `job_parser_handler.py`

2. **Job Analysis**:
   - `job_parser.py` extracts job content (URL or text)
   - `llm_job_analyzer.py` analyzes content with Claude/OpenAI
   - Analysis extracts requirements, skills, and candidate profile

3. **Data Storage**:
   - Job analysis saved to `static/uploads/temp_session_data/`
   - `job_parser_handler.py` coordinates saving job data
   - Session information updated with job details

### Resume Tailoring Workflow

1. **User Requests Tailoring**:
   - User clicks "Tailor Resume" in web interface
   - `app.py` passes request to `tailoring_handler.py`

2. **Data Preparation**:
   - `tailoring_handler.py` retrieves resume and job data
   - Sections prepared for LLM processing

3. **LLM Processing**:
   - `claude_integration.py` tailors each section individually:
     - Uses specialized prompts for each section
     - Incorporates job requirements into prompts
     - Applies `sample_experience_snippet.py` for achievement formatting
     - Enforces quantifiable metrics with `metric_utils.py`
   - API interactions logged by `claude_api_logger.py`

4. **Response Processing**:
   - Tailored content validated and structured
   - `metric_utils.py` ensures all achievements have metrics
   - Sections saved as JSON to `static/uploads/temp_session_data/{request_id}_{section}.json`
   - Raw LLM responses saved to `static/uploads/api_responses/`

### Preview Generation Workflow

1. **User Views Preview**:
   - Preview automatically shown after tailoring
   - `app.py` routes to `/preview/{request_id}`

2. **HTML Generation**:
   - `html_generator.py` loads section JSON files
   - `generate_preview_from_llm_responses()` creates HTML fragment
   - `style_manager.py` ensures consistent styling
   - HTML fragment returned to browser

### PDF Export Workflow

1. **User Requests PDF**:
   - User clicks "Download PDF" button
   - `app.py` routes to `/download/{request_id}`

2. **PDF Generation**:
   - `html_generator.py` creates complete HTML document (not just fragment)
   - `pdf_exporter.py` converts HTML to PDF using WeasyPrint
   - Applies styling from `static/css/print.css` and `static/css/preview.css`
   - PDF saved to `static/uploads/tailored_resume_{request_id}.pdf`
   - PDF served to user via `send_from_directory`

### DOCX Export Workflow

1. **User Requests DOCX**:
   - User clicks "Download DOCX" button
   - `app.py` routes to `/download/docx/{request_id}`

2. **DOCX Generation**:
   - `docx_builder.py` coordinates DOCX creation
   - Loads section JSON files from temp_session_data
   - Creates document with proper styles

3. **Style Application**:
   - `StyleRegistry` from `word_styles.registry` defines styles
   - Section headers created via `section_builder.py` using table-based approach
   - `style_engine.py` and `style_manager.py` provide styling values

4. **Post-Processing**:
   - Empty paragraphs removed via `remove_empty_paragraphs()`
   - Spacing adjusted via `tighten_before_headers()`
   - DOCX file served directly to user's browser

### Configuration and Styling Workflow

1. **Configuration Loading**:
   - `config.py` loads environment variables and settings
   - Application adapts based on environment (development/production)

2. **Style Definition**:
   - `design_tokens.json` contains all styling values
   - `tools/generate_tokens.py` converts to SCSS and DOCX mappings

3. **Style Application**:
   - `style_engine.py` provides low-level styling operations
   - `style_manager.py` coordinates consistent style application
   - Styles applied to HTML via CSS and DOCX via `word_styles`

This architecture provides a clean separation of concerns and ensures consistent styling across all document formats, with a specific focus on resolving styling issues and maintaining consistent user experience.

--- 