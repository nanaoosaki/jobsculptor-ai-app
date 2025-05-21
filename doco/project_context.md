# Resume Tailor Project Context

## Project Overview
The Resume Tailor is an AI-powered application that helps users customize their resumes for specific job postings. It uses Claude or OpenAI to analyze job listings and tailor resumes to highlight relevant skills and experience. The application provides a professional PDF output with consistent formatting based on YC-Eddie style guidelines.

## Repository Details
- **GitHub Repository**: https://github.com/nanaoosaki/manus_resume_site
- **Current Branch**: main
- **Local Development Path**: D:\AI\manus_resumeTailor

## Deployment Status
- **Deployed At**: PythonAnywhere (free tier)
- **Domain**: jobsculptor.ai
- **Deployment Date**: April 17, 2025
- **Special Notes**: Using system Python (no virtualenv) due to disk quota limitations

## Key Features Implemented
1. **Resume Parsing**: LLM-based resume parsing with traditional fallback
2. **Job Analysis**: Extracts requirements, skills, and candidate profiles from job listings
3. **Resume Tailoring**: Customizes each resume section based on job requirements
4. **YC-Eddie Style Formatting**: Creates clean, professional resume documents with modern styling (centered headers with box borders and dot bullet points)
5. **Preview Generation**: Shows HTML preview of tailored resumes with consistent styling
6. **Multi-Provider Support**: Works with both OpenAI and Claude APIs
7. **PDF Export**: Generates professionally formatted PDF documents instead of Word documents
8. **A4 Paper Format**: Implemented A4 paper format for HTML preview matching PDF output

## Technologies and APIs
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Document Processing**: python-docx, docx2txt, WeasyPrint (for PDF generation)
- **LLM Providers**: 
  - Claude (Anthropic) - Primary
  - OpenAI (GPT-4o) - Fallback
- **Job Source Support**: LinkedIn and generic job listings

## Recent Changes and Fixes
1. **Template Dependency Removed**: Eliminated reliance on template_resume.docx
2. **Resume Preview Fixed**: Separated user resume and tailored resume previews
3. **LLM Resume Parsing**: Added sophisticated document parsing with LLMs
4. **Deployment Optimized**: Modified for PythonAnywhere free tier constraints
5. **Job Analysis Enhanced**: Added comprehensive job requirement extraction
6. **Modern Resume Styling**: Updated document formatting with centered box headers and dot bullet points
7. **HTML Preview Alignment**: Ensured consistent styling between documents and HTML previews
8. **PDF Export**: Switched from Word document generation to PDF export for better consistency
9. **A4 Paper Format**: Implemented proper A4 paper dimensions with 1-inch margins for HTML preview
10. **Contact Information Fix**: Attempted to ensure contact information is preserved in tailored resumes
11. **Styling Architecture Refactor**: Centralized styling using design tokens and SCSS; removed inline styles and JS width hacks; HTML and PDF outputs now consistent via `preview.css` and `print.css`
12. **Single-Source Styling Implementation**: Centralized styling using design tokens and SCSS, ensuring consistent styling across HTML and PDF outputs.
13. **Resume Section Parsing Improvements**: Enhanced section detection with expanded regex patterns and better default section handling, implemented a fallback mechanism, and improved error handling.
14. **Align HTML & PDF Styling**: Achieved alignment between HTML preview and PDF output by centralizing styling using design tokens and SCSS, improving maintainability and consistency.
15. **Role Description Integration**: Successfully integrated role descriptions into both HTML and PDF outputs, ensuring they are generated when missing and styled consistently.

## Recent Improvements

1. **Session-Specific UUID Data Storage**: Implemented UUID-based filenames for storing cleaned resume data, ensuring data isolation and multi-user compatibility.
2. **Enhanced Logging**: Updated log messages to accurately reflect file operations, improving traceability and debugging.
3. **Consistent Data Flow**: Ensured a consistent data flow from LLM responses to structured JSON, saved and loaded using UUIDs, and formatted to HTML for previews and PDFs.

## Current Limitations and Known Issues
1. **PythonAnywhere Constraints**: 
   - 512MB disk quota on free tier
   - CPU time limitations (100 seconds/day)
2. **Large Resume Handling**: Very large resumes (>20 pages) may exceed token limits
3. **Custom Formatting**: Limited support for highly customized resume formats
4. **Contact Information Missing**: Contact information may not be preserved in tailored resume output
5. **Company/Location Separation**: Difficulty separating company names from locations in some formats
6. **Bullet Point Duplication**: Some bullet points appear duplicated in the final output

## File Structure and I/O Details

### Core Application Files
- **app.py**: 
  - Main Flask application
  - **Input**: HTTP requests, form submissions
  - **Output**: HTML responses, redirects, file downloads
  - **Dependencies**: All other modules

- **config.py**: 
  - Configuration settings
  - **Input**: Environment variables
  - **Output**: Configuration constants and settings
  - **Used by**: All other modules

### Resume Processing
- **resume_processor.py**: 
  - Handles resume file upload and basic parsing
  - **Input**: DOCX files, PDF files
  - **Output**: Parsed resume content, JSON cache files
  - **Used by**: app.py, upload_handler.py

- **llm_resume_parser.py**: 
  - LLM-based resume parsing
  - **Input**: Resume text content, LLM provider selection
  - **Output**: Structured resume sections, cached parsing data
  - **Used by**: claude_integration.py, resume_processor.py

- **resume_formatter.py**:
  - Formats parsed resume content into standardized structure
  - **Input**: Raw parsed resume sections
  - **Output**: Standardized resume structure with consistent formatting
  - **Used by**: resume_processor.py, upload_handler.py

### Job Analysis
- **job_parser.py**: 
  - Job listing extraction
  - **Input**: LinkedIn URLs, general job URLs
  - **Output**: Structured job details, requirements
  - **Used by**: app.py, job_parser_handler.py

- **llm_job_analyzer.py**: 
  - LLM-based job posting analysis
  - **Input**: Job posting text, LLM provider selection
  - **Output**: Structured job analysis, candidate profile, skills
  - **Used by**: job_parser.py

- **job_parser_handler.py**:
  - Orchestrates job parsing process
  - **Input**: Job URLs or text from web interface
  - **Output**: Structured job data in JSON format
  - **Used by**: app.py

### Resume Tailoring
- **claude_integration.py**: 
  - LLM integration for tailoring
  - **Input**: Resume sections, job details, API keys
  - **Output**: Tailored resume content
  - **Used by**: tailoring_handler.py, app.py

- **tailoring_handler.py**: 
  - Orchestrates the tailoring process
  - **Input**: Resume path, job data, API provider
  - **Output**: Tailored document, preview HTML
  - **Used by**: app.py

### Document Generation
- **resume_styler.py**: 
  - YC-Eddie style resume formatter
  - **Input**: Tailored section content
  - **Output**: Formatted Word document
  - **Used by**: claude_integration.py, tailoring_handler.py

- **pdf_exporter.py**: 
  - Converts HTML to PDF
  - **Input**: HTML resume content
  - **Output**: PDF document
  - **Used by**: tailoring_handler.py

- **docx_builder.py**:
  - Generates Microsoft Word (.docx) files with consistent styling
  - **Input**: Tailored resume JSON sections
  - **Output**: Formatted DOCX document
  - **Used by**: app.py

- **html_generator.py**:
  - Generates HTML previews for browser display and PDF generation
  - **Input**: Tailored resume JSON sections
  - **Output**: HTML fragments or complete documents
  - **Used by**: tailoring_handler.py, app.py

### Frontend
- **templates/index.html**: 
  - Main application interface
  - Handles user interactions
  - **Input**: User actions
  - **Output**: Visual interface

- **static/css/styles.css**: 
  - Main stylesheet for UI
  - **Used by**: index.html

- **static/css/pdf_styles.css**: 
  - Styles specific to PDF output
  - **Used by**: pdf_exporter.py

- **static/js/main.js**: 
  - Frontend JavaScript
  - Handles AJAX requests, UI updates
  - **Input**: User actions, server responses
  - **Output**: DOM updates
  - **Used by**: index.html

### Utility Modules
- **claude_api_logger.py**:
  - Logs Claude API interactions
  - **Input**: API requests and responses
  - **Output**: Log files with timestamps
  - **Used by**: claude_integration.py

- **format_handler.py**:
  - Handles document format detection and conversion
  - **Input**: Various file formats
  - **Output**: Normalized text content
  - **Used by**: resume_processor.py

- **metric_utils.py**:
  - Manages quantifiable metrics in achievements
  - **Input**: Achievement text
  - **Output**: Standardized metrics format
  - **Used by**: claude_integration.py, html_generator.py

- **pdf_parser.py**:
  - Extracts text from PDF files
  - **Input**: PDF documents
  - **Output**: Extracted text content
  - **Used by**: resume_processor.py

- **restart_app.py**:
  - Development utility for restarting the application
  - **Input**: File system changes
  - **Output**: Application restart actions
  - **Used by**: Developers during development

- **style_engine.py**:
  - Low-level style management and token application
  - **Input**: design_tokens.json
  - **Output**: Applied styling rules
  - **Used by**: style_manager.py, resume_styler.py

- **style_manager.py**:
  - High-level style management interface
  - **Input**: Style requests from generators
  - **Output**: Consistent style application
  - **Used by**: html_generator.py, docx_builder.py, pdf_exporter.py

- **token_counts.py**:
  - Utility for counting tokens in text
  - **Input**: Text content
  - **Output**: Token count estimates
  - **Used by**: claude_integration.py

- **upload_handler.py**:
  - Manages file uploads and sessions
  - **Input**: Uploaded files from web interface
  - **Output**: Saved files and session data
  - **Used by**: app.py

- **yc_eddie_styler.py**:
  - Applies YC-Eddie styling guidelines
  - **Input**: Resume document
  - **Output**: YC-styled document
  - **Used by**: resume_styler.py

- **yc_resume_generator.py**:
  - Generates YC-formatted resumes
  - **Input**: Tailored content
  - **Output**: Complete YC-formatted document
  - **Used by**: resume_styler.py

### word_styles Package
- **registry.py**:
  - Central registry for DOCX styles
  - **Input**: Style definitions
  - **Output**: DOCX style registry
  - **Used by**: docx_builder.py, section_builder.py

- **section_builder.py**:
  - Creates properly styled section headers
  - **Input**: Document, header text
  - **Output**: Formatted headers with tables
  - **Used by**: docx_builder.py

- **xml_utils.py**:
  - XML manipulation utilities for DOCX
  - **Input**: Style specifications
  - **Output**: XML nodes for DOCX
  - **Used by**: registry.py, section_builder.py

## Application Workflow

### 1. Resume Upload Process
1. User uploads resume (DOCX/PDF) via web interface
2. `app.py` receives the file and passes it to `resume_processor.py`
3. `resume_processor.py` saves the file and initiates parsing
4. `llm_resume_parser.py` attempts to parse the resume with LLM:
   - If successful, returns structured sections
   - If fails, falls back to traditional parsing
5. Parsed resume sections are displayed in the UI
6. Resume data is cached for future use

### 2. Job Parsing Process
1. User enters a job URL via web interface
2. `app.py` passes the URL to `job_parser.py`
3. `job_parser.py` extracts job listing content:
   - For LinkedIn, uses specific scraping techniques
   - For other sites, uses generic extraction
4. `llm_job_analyzer.py` analyzes the job content to extract:
   - Candidate profile
   - Hard skills required
   - Soft skills valued
   - Ideal candidate description
5. Job requirements and analysis are displayed in the UI
6. Job data is cached for future use

### 3. Resume Tailoring Process
1. User requests tailoring via web interface
2. `app.py` triggers `tailoring_handler.py`
3. `tailoring_handler.py` coordinates:
   - Getting resume sections from cache or re-parsing
   - Getting job details from cache or re-parsing
   - Calling LLM integration
4. `claude_integration.py` performs section-by-section tailoring:
   - Each section sent to Claude/OpenAI with specific prompts
   - Content optimized for job requirements
   - Contact information preserved without changes
5. `generate_preview_from_llm_responses` creates HTML preview
6. HTML preview displayed to user in the UI
7. When download requested, `pdf_exporter.py` converts HTML to PDF

### 4. PDF Export Process
1. User clicks "Download Tailored Resume"
2. `app.py` triggers PDF generation
3. `pdf_exporter.py`:
   - Takes HTML content from preview
   - Applies PDF-specific styles
   - Uses WeasyPrint to convert HTML to PDF
4. PDF file is sent to user's browser for download

## Current Development Focus
1. **Contact Information Preservation**: Fixing issues with contact details in tailored resumes
2. **HTML Preview Enhancement**: Ensuring HTML preview precisely matches PDF output
3. **Bullet Point Formatting**: Resolving inconsistencies in bullet point display
4. **Company/Location Separation**: Improving the accuracy of entity recognition
5. **PDF Format Optimization**: Fine-tuning A4 paper layout and margins

## Future Roadmap
1. **Visual Diff Feature**: Highlight changes between original and tailored resume
2. **Resume Format Validator**: Help prepare optimal resumes before tailoring
3. **Confidence Scores**: Add confidence metrics to LLM parsing results
4. **Alternative LLM Providers**: Implement backup providers for resilience
5. **User Accounts**: Save tailoring history and multiple resumes
6. **Resume Scoring**: Analyze resume against job requirements
7. **Bulk Processing**: Support tailoring for multiple job listings at once

## To Include in Future Conversations
When starting new conversations with Claude about this project, include this file and mention:
1. You're working on the Resume Tailor application
2. Reference recent changes you've made
3. Specify which part of the application you're focusing on
4. Indicate if you're working on local development or deployment

## Project Context

This project focuses on creating an AI-powered resume tailoring tool that optimizes resumes to match job requirements using LLM technology. The application helps job seekers create targeted resumes for specific job listings.

## Learnings

- Centralizing styling using design tokens and SCSS improves consistency and maintainability across different outputs.
- Using a single-source styling approach simplifies updates and modifications.

## Solutions Implemented

- Implemented PDF generation using WeasyPrint for consistent and professional output.
- Centralized styling using `design_tokens.json` and SCSS, aligning HTML and PDF appearances.
- Refactored CSS into SCSS files, improving maintainability and separation of concerns.
- Ensured consistent application of styles across HTML preview and PDF generation, resulting in a unified appearance.
- Enhanced resume parsing with expanded regex patterns and better default section handling.
- Implemented a robust fallback mechanism for resume parsing to ensure downstream processes have the required data structure.
- Improved error handling in the resume section extraction process.
- Achieved alignment between HTML preview and PDF output by centralizing styling using design tokens and SCSS.
- Removed inline styles and JavaScript width hacks, leading to a cleaner and more maintainable codebase.
- Implemented a single-source styling architecture that allows for easy updates and modifications.

- Created `design_tokens.json` to store all visual constants, ensuring a single source of truth for styling.
- Developed a `StyleManager` class to manage and apply styles consistently across different outputs.
- Refactored CSS into SCSS files, separating concerns and improving maintainability.
- Ensured consistent application of styles across HTML preview and PDF generation, resulting in a unified appearance.
- Enhanced resume parsing with expanded regex patterns and better default section handling.
- Implemented a robust fallback mechanism for resume parsing to ensure downstream processes have the required data structure.
- Improved error handling in the resume section extraction process.
- Achieved alignment between HTML preview and PDF output by centralizing styling using design tokens and SCSS.
- Removed inline styles and JavaScript width hacks, leading to a cleaner and more maintainable codebase.
- Implemented a single-source styling architecture that allows for easy updates and modifications.

## Recent Major Changes

1. **Section Header Box Width Adjustment**: Updated the section header box width to match the resume width, ensuring a consistent and professional appearance.
2. **Grey Bar Issue in PDF Output**: Resolved the issue of a grey horizontal bar appearing in the PDF output by updating the `print.scss` styling rules.
3. **Styling Architecture Refactor**: Centralized styling using design tokens and SCSS, ensuring consistent styling across HTML and PDF outputs.
4. **PDF Export Enhancements**: Improved PDF generation with WeasyPrint, ensuring consistent and professional output.
5. **Resume Formatting Improvements**: Adjusted resume formatting to utilize full A4 page width, improving visual presentation and readability.
6. **Bullet Point Formatting**: Resolved inconsistencies in bullet point display, ensuring proper alignment and appearance.
7. **Contact Information Preservation**: Fixed issues with contact details in tailored resumes, ensuring they are preserved correctly.
8. **HTML Preview Enhancement**: Ensured HTML preview precisely matches PDF output, improving consistency and user experience.
9. **DOCX Header Box Spacing Fix**: Implemented a table-based approach with custom HeaderBoxH2 style for section headers, resolving issues with excessive spacing in DOCX output.

## New Package: word_styles

### Purpose
The `word_styles` package was implemented to solve persistent issues with DOCX styling, particularly related to section header spacing and box height. It provides a more reliable and maintainable approach to styling DOCX documents compared to direct paragraph styling.

### Components
- **registry.py**: 
  - Defines the style registry and paragraph box styles
  - Creates and manages styles within DOCX documents
  - Provides centralized style definitions for consistent application
  - Includes the new `HeaderBoxH2` style based on Normal for table cell content

- **section_builder.py**: 
  - Implements section header creation with table-based wrappers
  - Sets asymmetric cell margins and vertical alignment
  - Manages spacing between sections
  - Controls paragraph formatting and outline levels

- **xml_utils.py**: 
  - Provides utilities for direct XML manipulation in DOCX files
  - Creates properly formatted XML nodes for borders, spacing, etc.
  - Handles unit conversions (points to twips, etc.)
  - Ensures cross-platform compatibility with XML namespaces

### Updated DOCX Generation Workflow

1. **Initiation**:
   - User requests a DOCX download via the web interface
   - Flask route handler calls `utils.docx_builder.build_docx()`

2. **Document Preparation**:
   - `build_docx()` creates a new DOCX document
   - The style registry (`word_styles.registry`) is initialized
   - Custom styles are registered, including `HeaderBoxH2` for table cell content

3. **Section Header Generation**:
   - For each section (experience, education, etc.), `add_section_header()` is called
   - Instead of using paragraph-based borders, a single-cell table is created
   - The table has controlled borders matching the design specifications
   - A custom `HeaderBoxH2` style (based on Normal, not Heading 2) is applied to the paragraph inside the cell
   - Asymmetric cell margins are applied (less on top) for optimal spacing
   - Vertical alignment is set to "top" to eliminate excess space
   - Outline level is preserved for proper document structure

4. **Content Generation**:
   - Content paragraphs are added with appropriate styles
   - Bullet points and other formatting are applied
   - Spacing between content and the next section header is controlled

5. **Post-Processing**:
   - Empty paragraphs are removed
   - Spacing between content and section headers is tightened
   - Final document structure is optimized for consistent rendering

6. **File Delivery**:
   - The DOCX file is created in memory
   - The file is returned to the user for download

### Control Hierarchy for DOCX Styling

The styling in DOCX documents is controlled through multiple layers, with each component having specific responsibilities:

1. **design_tokens.json**:
   - Defines base styling values for colors, sizes, etc.
   - Contains specific values for DOCX styling

2. **word_styles.registry.StyleRegistry**:
   - Central registry for all paragraph and box styles
   - Creates and manages style definitions
   - Ensures styles are consistent and properly applied

3. **word_styles.section_builder**:
   - Controls the creation of section headers using table wrappers
   - Manages section spacing and formatting
   - Applies styles from the registry to document elements

4. **docx_builder.py**:
   - Orchestrates the overall document creation process
   - Loads content from JSON files
   - Calls into the word_styles package to apply styles
   - Handles final document assembly

This layered approach provides a clean separation of concerns and makes the styling process more maintainable and consistent.

## Updated File Structure and I/O Details

### New Styling Components for DOCX
- **word_styles/registry.py**: 
  - **Purpose**: Central registry for paragraph and box styles in DOCX documents
  - **Key Classes**: `ParagraphBoxStyle`, `StyleRegistry`
  - **Input**: Style definitions from design tokens
  - **Output**: DOCX styles applied to documents
  - **Used by**: docx_builder.py, section_builder.py

- **word_styles/section_builder.py**: 
  - **Purpose**: Creates section headers with table-based wrappers
  - **Key Functions**: `add_section_header()`, `_add_table_section_header()`, `_set_cell_margins()`
  - **Input**: Document object, header text, style definition
  - **Output**: Formatted section headers in DOCX documents
  - **Used by**: docx_builder.py

- **word_styles/xml_utils.py**: 
  - **Purpose**: Utilities for direct XML manipulation in DOCX files
  - **Key Functions**: `make_spacing_node()`, `make_border_node()`, `twips_from_pt()`
  - **Input**: Style specifications (points, colors, etc.)
  - **Output**: XML nodes for DOCX documents
  - **Used by**: registry.py, section_builder.py

### Testing Components
- **tests/docx_spacing/test_table_section_headers.py**:
  - **Purpose**: Tests table-based section headers in DOCX
  - **Input**: None
  - **Output**: Test DOCX files in tests/docx_spacing/output/
  - **Used by**: Developers for validation

- **tests/docx_spacing/test_header_fix_simple.py**:
  - **Purpose**: Simple test for header box styling
  - **Input**: None
  - **Output**: Test DOCX files in tests/docx_spacing/output/
  - **Used by**: Developers for validation

## Recent Implementation: DOCX Header Box Styling

### Overview
We implemented a comprehensive solution to address persistent issues with section header spacing in DOCX output. This was achieved through a complete refactoring of the approach to DOCX styling.

### Key Changes
1. **Table-Based Approach**: Replaced paragraph borders with single-cell tables for section headers
2. **Custom HeaderBoxH2 Style**: Created a purpose-built style based on Normal (not Heading 2) to avoid inheriting unwanted spacing
3. **Asymmetric Cell Margins**: Implemented less padding on top (10 twips) than sides/bottom (20 twips)
4. **Top Vertical Alignment**: Forced text to align to the top of the cell
5. **Outline Level Preservation**: Maintained document structure for navigation and accessibility

### Results
- **Compact Header Boxes**: Eliminated excess space above and below header text
- **Consistent Spacing**: Ensured proper spacing between content and the next section header
- **Cross-Platform Compatibility**: Works consistently across all Word versions and platforms

### Implementation Components
- **word_styles Package**: New package with StyleRegistry and section header components
- **Table-Based Headers**: Single-cell tables with controlled borders and margins
- **Custom Paragraph Style**: Purpose-built HeaderBoxH2 style with zero spacing
- **XML Manipulation**: Direct XML control for reliable styling across platforms

### Key Technical Insights
- **Style Inheritance Matters**: Basing styles on Heading 2 automatically inherited unwanted spacing attributes
- **Multiple Spacing Nodes Cause Issues**: Word honors the first spacing node it encounters
- **Table Cells Provide Better Control**: More reliable layout than paragraph-based approaches
- **Vertical Alignment Is Critical**: Default center alignment created the appearance of excess space
- **Asymmetric Padding Works Well**: Different margins for different sides allow precise control

### Documented in
- **refactor_docx_spacing_model.md**: Detailed analysis and implementation plan
- **add_improvements_styling.md**: Summary of changes for styling improvements

## Starting the Application

To start the Resume Tailor application, follow these steps:

1. Ensure you have Python installed on your system.
2. Navigate to the project directory in your terminal.
3. Run the following command to start the Flask application:
   ```
   python app.py
   ```
4. The application will start and be accessible at `http://127.0.0.1:5000` in your web browser.

**Note:** This is a development server. For production deployment, use a production WSGI server.

## Detailed Application Workflow

### Resume Tailoring Process: From Upload to PDF Download

#### 1. Initialization and Data Collection
1. User uploads resume (DOCX/PDF) and provides job description
2. Application generates a unique `request_id` (UUID format, e.g., `29fbc315-fa41-4c7b-b520-755f39b7060a`)
3. Resume is parsed into structured sections (contact, summary, experience, education, skills, projects)
4. Job requirements are extracted and analyzed

#### 2. LLM Tailoring Process
1. Each resume section is tailored individually using the selected LLM (Claude or OpenAI):
   - Contact information is preserved without changes
   - Summary is rewritten to match job requirements
   - Experience bullets are tailored to highlight relevant achievements
   - Education is adjusted to emphasize relevant coursework
   - Skills are reorganized to prioritize job-relevant skills
   - Projects (if present) are tailored to showcase relevant work
2. LLM responses are saved as raw API responses:
   ```
   static/uploads/api_responses/{section}_response_{timestamp}.json
   ```
3. Quantifiable metrics in achievement bullets are normalized:
   - If digits exist → all placeholder tokens ("??") are removed
   - If no "??" exists → "?? %" or appropriate unit is injected
   - If multiple "??" tokens → keep first, drop others
   - Placeholders attached to words are separated (e.g., "across??" → "across ?? ")
   - Placeholders are inserted before terminal punctuation
   - Example transformations:
     ```
     "Designed a data placement service for S3-like storage, ensuring 99.9999% data durability for data lakes by ?? %."
     "Built a garbage collector to ?? reclaim space via compaction, handling deleted, orphaned, and corrupted data."
     ```

#### 3. Section Data Storage
1. Each tailored section is cleaned and structured as JSON
2. Files are saved with request_id-based naming:
   ```
   static/uploads/temp_session_data/{request_id}_{section}.json
   ```
3. Example paths:
   ```
   29fbc315-fa41-4c7b-b520-755f39b7060a_contact.json
   29fbc315-fa41-4c7b-b520-755f39b7060a_summary.json
   29fbc315-fa41-4c7b-b520-755f39b7060a_experience.json
   29fbc315-fa41-4c7b-b520-755f39b7060a_education.json
   29fbc315-fa41-4c7b-b520-755f39b7060a_skills.json
   29fbc315-fa41-4c7b-b520-755f39b7060a_projects.json
   ```

#### 4. HTML Preview Generation
1. `html_generator.py` loads all section JSON files for the specific request_id
2. For screen preview:
   - Function: `generate_preview_from_llm_responses(request_id, upload_folder, for_screen=True)`
   - Output: HTML fragment (~6649 chars) optimized for browser display
   - Route: `/preview/{request_id}`
3. For PDF generation:
   - Function: `generate_preview_from_llm_responses(request_id, upload_folder, for_screen=False)`
   - Output: Complete HTML document (~6939 chars) optimized for PDF generation
   - Includes proper DOCTYPE, charset, and complete HTML structure

#### 5. PDF Generation Process
1. User requests PDF download via frontend
2. Request is sent to `/download/{request_id}` route
3. Backend generates full HTML document (not just fragment)
4. PDF generation via `pdf_exporter.py`:
   - Function: `create_pdf_from_html(html_content, output_path, metadata)`
   - Uses WeasyPrint to convert HTML to PDF
   - Applies CSS from both `static/css/print.css` and `static/css/preview.css`
   - Handles web-specific CSS properties (ignores unsupported properties like box-shadow)
5. PDF is saved to disk:
   ```
   static/uploads/tailored_resume_{request_id}.pdf
   ```
6. PDF is served to user via `send_from_directory` with proper MIME type

#### 6. Styling Application
1. Design tokens in `design_tokens.json` define all styling variables:
   - Page margins (currently 0.8cm vertical and horizontal)
   - Colors (primary: #4A6FDC, secondary: #2A4494, text: #333333)
   - Font sizes and families
   - Spacing and layout measurements
2. Tokens are converted to SCSS variables:
   - Tool: `tools/generate_tokens_css.py`
   - Output: `static/scss/_tokens.scss`
3. SCSS is compiled to CSS:
   - Command: `sass static/scss/preview.scss static/css/preview.css`
   - Command: `sass static/scss/print.scss static/css/print.css`
4. CSS is applied to:
   - Browser preview (primarily preview.css)
   - PDF generation (both print.css and preview.css)

#### 7. Output File Management
1. Temporary files are stored in patterns:
   - API responses: `static/uploads/api_responses/{section}_response_{timestamp}.json`
   - Section JSON: `static/uploads/temp_session_data/{request_id}_{section}.json`
2. Final output files:
   - PDF: `static/uploads/tailored_resume_{request_id}.pdf`
3. Resume indexing:
   - Each tailored resume is added to `resume_index.json`
   - Includes metadata like job title and processing timestamp

### Exact Processing Sequence (from logs)

1. **Tailoring Request**:
   - POST request to `/tailor-resume`
   - Request_id generated (e.g., `29fbc315-fa41-4c7b-b520-755f39b7060a`)

2. **LLM Processing**:
   - Each section processed sequentially
   - Achievement bullets normalized
   - Example transformation: "Designed a data placement service for S3-like storage, ensuring 99.9999% data durability for data lakes by ?? %."

3. **Data Storage**:
   - Six JSON section files saved to temp_session_data folder
   - All reference the same request_id

4. **Preview Generation**:
   - HTML fragment (6649 chars) generated for browser preview
   - Full HTML document (6939 chars) generated for PDF export

5. **PDF Generation**:
   - WeasyPrint converts HTML to PDF
   - CSS applied (with browser-specific properties ignored)
   - PDF saved to uploads folder

6. **Download Delivery**:
   - GET request to `/download/29fbc315-fa41-4c7b-b520-755f39b7060a`
   - PDF served to user's browser

The entire process from tailoring request to PDF download takes approximately 6-10 seconds, depending on the size of the resume and complexity of the job description. 

## Detailed I/O Relationships

### Data Flow in Resume Tailoring

1. **Resume Upload → Structured Data**
   - File uploaded → `upload_handler.py` → stored in `static/uploads/`
   - Text extracted → `resume_processor.py` (using appropriate parser)
   - Sections identified → `llm_resume_parser.py` or fallback parser
   - Structured data → stored in session and temporary JSON files

2. **Job Input → Requirement Analysis**
   - URL/text input → `job_parser_handler.py` → `job_parser.py`
   - Content analysis → `llm_job_analyzer.py`
   - Requirements extracted → stored in session and temporary JSON files

3. **Tailoring Request → Tailored Content**
   - Request initiated → `tailoring_handler.py`
   - Data prepared → sent to `claude_integration.py`
   - LLM processing → raw responses stored in `static/uploads/api_responses/`
   - Structured results → JSON stored in `static/uploads/temp_session_data/`

4. **Preview Request → HTML Display**
   - Request received → `app.py` routes to preview function
   - JSON loaded → `html_generator.py` renders HTML fragment
   - Styling applied → `style_manager.py` ensures consistency
   - Fragment returned → displayed in browser

5. **Download Request → File Generation**
   - PDF request → HTML generated → `pdf_exporter.py` → WeasyPrint → PDF file
   - DOCX request → JSON loaded → `docx_builder.py` → `word_styles` package → DOCX file
   - File served → downloaded by user's browser

### Configuration Flow

1. **Styling Definition**
   - `design_tokens.json` → central repository of styling values
   - `tools/generate_tokens.py` → generates SCSS variables and DOCX mappings
   - SCSS compilation → CSS files for HTML/PDF rendering
   - Style application → `style_manager.py` → consistent styling across formats

2. **Environment Configuration**
   - Environment variables → `config.py` → application settings
   - API keys → secured access to LLM providers
   - Development/production mode → appropriate behavior

### Logging and Debugging Flow

1. **API Interactions**
   - API calls → `claude_api_logger.py` → detailed logs with timestamps
   - Success/failure tracking → improves debugging
   - Token usage monitoring → optimization opportunities

2. **Application Logs**
   - Key operations logged → standard Python logging
   - File operations → clear traceability
   - Error handling → proper fallbacks

3. **Debugging Tools**
   - Raw API responses saved → detailed analysis possible
   - Structured data preserved → step-by-step workflow examination
   - Log files → chronological operation tracking

## Utility Scripts and Their Roles

### Document Processing Utilities

- **format_handler.py**: Serves as a bridge between different document formats, detecting file types and selecting the appropriate parser. It abstracts away format-specific details from the main processing flow, allowing for easy addition of new supported formats.

- **pdf_parser.py**: Specialized in extracting text and structure from PDF files, which are more complex than DOCX files. It uses PyPDF and PDFMiner libraries to handle various PDF structures and formatting.

### LLM Integration Utilities

- **claude_api_logger.py**: Provides comprehensive logging of all LLM API interactions, including request parameters, response content, tokens used, and timing information. This is crucial for debugging, optimization, and usage tracking.

- **token_counts.py**: Estimates token usage for text being sent to LLMs, helping prevent errors from exceeding context limits and optimizing API usage costs.

- **metric_utils.py**: Ensures that achievement statements contain quantifiable metrics, either as actual numbers or placeholders. It standardizes the format of these metrics across the application.

### Styling and Formatting Utilities

- **style_engine.py**: Provides low-level style manipulation, directly interfacing with design tokens and applying them to different elements. It handles the technical details of styling application.

- **style_manager.py**: Offers a higher-level interface for style application, abstracting away format-specific styling details. It ensures consistent styling across HTML, PDF, and DOCX outputs.

- **yc_eddie_styler.py**: Implements specific styling guidelines from the YC-Eddie resume format, including box headers, spacing, and typography rules.

### Development Utilities

- **restart_app.py**: Monitors file changes and automatically restarts the Flask development server when changes are detected, improving developer productivity.

## Integration Patterns

### Observer Pattern
Used in monitoring file changes and event logging:
- **restart_app.py**: Watches for file changes and triggers actions
- **claude_api_logger.py**: Observes API interactions without affecting core functionality

### Strategy Pattern
Used for format-specific handling and styling:
- **format_handler.py**: Selects appropriate parsing strategy based on file format
- **style_manager.py**: Applies different styling strategies based on output format

### Factory Pattern
Used in document generation:
- **pdf_exporter.py**: Creates PDF documents from HTML content
- **docx_builder.py**: Builds DOCX documents from structured data

### Repository Pattern
Used for data storage and retrieval:
- **resume_index.py**: Maintains a central index of processed resumes
- **job_parser_handler.py**: Manages job data storage and retrieval

### Decorator Pattern
Used in style application:
- **word_styles/registry.py**: Decorates DOCX elements with styling
- **metric_utils.py**: Decorates achievement text with standardized metrics

## Future Integration Considerations

When adding new features or modifying existing ones, consider:

1. **Styling Consistency**: All new visual elements should use the design token system via `style_manager.py`

2. **Logging Integration**: New LLM interactions should use `claude_api_logger.py` for consistent tracking

3. **Error Handling**: All components should include appropriate error handling and fallback mechanisms

4. **File Dependencies**: Update this documentation when adding new files or changing dependencies

5. **Data Flow**: Maintain the established patterns for data passing between components

This comprehensive documentation provides a clear understanding of all components in the resume tailoring application, their interactions, and the overall system architecture. Keeping it updated will facilitate maintenance, debugging, and further development. 