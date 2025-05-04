# Resume Tailoring Application

AI-powered resume tailoring tool that analyzes job postings and optimizes resumes to match job requirements using Claude AI.

## Completed Tasks

- [x] Set up basic Flask application structure
- [x] Create resume upload and parsing functionality
- [x] Implement job listing parser for LinkedIn and generic URLs
- [x] Integrate Claude AI for resume tailoring
- [x] Fix resume section parsing with enhanced regex patterns
- [x] Add fallback mechanism for non-standard resume formats
- [x] Improve error handling in resume parsing
- [x] Add detailed logging for debugging
- [x] Fix JavaScript to correctly display tailored resume
- [x] Implement LLM-based resume parsing with fallback mechanism
- [x] Integrate LLM parsing into initial resume upload process
- [x] Add configurable LLM provider selection (Claude/OpenAI)
- [x] Create JSON caching for parsed resume data
- [x] Improve job parser to extract complete job text for LLM processing
- [x] Update job parser UI to display complete job description
- [x] Implement LLM-based job posting analysis
- [x] Enhance UI to better display tailored sections with AI analysis highlights
- [x] Implement YC-Eddie Style resume format in document generation
- [x] Enhance resume styling with modern box borders and arrow bullet points
- [x] Update resume formatting with dot bullet points instead of arrows
- [x] Add horizontal line under contact information section
- [x] Remove bold font formatting from resume sections
- [x] Reduce line spacing between resume sections for better readability
- [x] Fix empty bullet points in tailored resume output
- [x] Add resume index system for tracking relationships between parsed resumes, LLM responses, and generated PDFs
- [x] Fix Python module import path issue by adding current directory to sys.path in app.py
- [x] Fix missing contact section in tailored resume
- [x] Fix missing professional summary section in tailored resume
- [x] Centralize styling architecture using design tokens and SCSS; removed inline styles and JS width hacks; ensured consistent HTML/PDF output via `preview.css` and `print.css`
- [x] Implemented PDF generation using WeasyPrint, ensuring consistent and professional output.
- [x] Centralized styling using design tokens and SCSS, aligning HTML and PDF appearances.
- [x] Refactored CSS into SCSS files, improving maintainability and separation of concerns.

## In Progress Tasks

- [x] Switch from Word document generation to PDF export for better consistency (Completed)
- [x] Implement HTML-to-PDF conversion with professional styling
- [x] Update download functionality to provide PDF files instead of Word documents
- [x] Optimize PDF layout for ATS compatibility and professional appearance
- [ ] Optimize tailoring prompts for high-quality, achievement-focused content
- [ ] Create resume format validator to help prepare optimal resumes
- [ ] Add visual diff feature to highlight tailoring changes
- [ ] Add confidence scores to LLM parsing results

## Future Tasks

- [ ] Implement alternative LLM providers as fallback options
- [ ] Add job search functionality using search engine tools
- [ ] Create user accounts and save tailoring history
- [ ] Implement resume scoring against job requirements
- [ ] Add bulk processing of multiple job listings
- [ ] Implement few-shot learning with example resumes for improved parsing
- [ ] Add section-specific prompts for more accurate tailoring

## New Tasks

- [x] Add Job Description Below Title
  - Implemented a feature to add a job description or role description right below the title and period if it does not exist in the original resume.
  - Ensured the description is concise and relevant to the job title.
  - **Priority**: Medium
  - **Implementation Plan**:
    - Modified `html_generator.py` to check for the presence of a job description.
    - If missing, generated a brief description using LLM based on the job title and period.
    - Ensured the description is properly formatted and inserted in the resume.

- [ ] Restrict Output Tokens for Tailored Bullet Points
  - Restrict the output tokens for tailored bullet points to be 85-105 characters to ensure they fit in one line.
  - **Priority**: High
  - **Implementation Plan**:
    - Update the LLM prompt to include a character limit for bullet points.
    - Implement validation to ensure bullet points do not exceed the character limit.
    - Test with various resume content to ensure readability and consistency.

- [ ] Enable DOCX download functionality
  - Allow users to download their tailored resume as a DOCX file for further editing.
  - **Branch**: enable-docx-download
  - **Priority**: Medium
  - **Implementation Plan**:
    1. Add a new Flask route `/download/docx/<request_id>` to serve DOCX export.
    2. Implement DOCX generation using python-docx, mirroring the PDF exporter logic.
    3. Add a "Download DOCX" button in the UI next to the PDF download option.
    4. Write tests for DOCX output and update documentation.

## Cleaned Up Tasks

- Removed completed tasks and consolidated ongoing tasks for clarity.
- Updated task descriptions to reflect current priorities and implementation plans.
- Ensured all tasks have clear implementation steps and expected outcomes.

## Implementation Plan

The resume tailoring application uses a Flask backend with a simple frontend interface. The core functionality revolves around:

1. Resume parsing and section extraction:
   - Uses python-docx to extract content from DOCX files
   - Identifies sections through heading styles and text formatting
   - Implements fallback mechanisms for non-standard formats
   
   **Enhanced LLM-based Resume Parsing:**
   - Integrate LLM (Claude/OpenAI) as the primary method for resume parsing
   - Send the entire resume content to LLM with a prompt to identify and categorize sections
   - Store parsed sections in a structured JSON format with section types as keys
   - Implement a fallback mechanism to use the existing regex/heading-based parser if:
     - LLM API call fails (network/authentication issues)
     - LLM response doesn't contain expected section structure
     - Timeout occurs during LLM processing
   - Cache LLM parsing results to avoid repeated API calls for the same resume
   - Add logging for both successful LLM parsing and fallbacks to traditional parsing
   - Create a configurable toggle to enable/disable LLM parsing for testing/development

2. Job listing parsing:
   - Scrapes job listings from LinkedIn and other URLs
   - Extracts requirements, skills, and job details
   - Formats job data for AI processing
   
   **Enhanced LLM-based Job Analysis:**
   - Integrate LLM (Claude/OpenAI) to intelligently analyze job postings
   - Send the complete job text to LLM with a prompt to extract structured insights
   - Have the LLM identify:
     - Candidate profile: What type of candidates the position is targeting
     - Hard skills: Technical and job-specific skills required
     - Soft skills: Personal and interpersonal skills valued
     - Ideal candidate: Comprehensive description of the perfect match
   - Return the analysis in structured JSON format for frontend consumption
   - Cache the LLM analysis results to avoid repeated API calls
   - Implement fallback to regex-based parsing if LLM analysis fails
   - Add logging for the analysis process and results
   - Add a configurable toggle to enable/disable LLM job analysis

3. AI-powered tailoring:
   - Uses Claude AI through Anthropic API or OpenAI API
   - Analyzes resume sections against job requirements
   - Generates tailored content that emphasizes relevant experience

4. Document generation:
   - Creates new DOCX files with tailored content
   - Preserves original formatting and structure
   - Provides downloadable files and HTML preview

## LLM Resume Parsing Implementation Details

1. **Parser Integration:**
   - Created `llm_resume_parser.py` module with the `LLMResumeParser` class
   - Modified `claude_integration.py` to attempt LLM parsing before traditional parsing
   - Modified `upload_handler.py` to use LLM parsing during initial resume upload
   - Used the same section structure to ensure compatibility between all methods

2. **Data Flow:**
   - Resume upload → LLM parsing → Section extraction → Display in UI
   - LLM parsing failures gracefully fall back to traditional parsing
   - Parsed resume data is cached as JSON files to avoid repeated API calls
   - Sections are immediately displayed in UI with proper categorization

3. **Configuration Options:**
   - `USE_LLM_RESUME_PARSING` - Enable/disable LLM parsing (default: true)
   - `LLM_RESUME_PARSER_PROVIDER` - Select LLM provider (auto, claude, openai)
   - Auto-detection of available API keys when provider is set to "auto"

4. **LLM Prompt Design:**
   - Clear instructions for section identification without adding/changing content
   - Specific output format requirements to ensure consistent JSON structure
   - Low temperature (0.1) for deterministic, precise output
   - Explicit handling of each resume section type

## LLM Job Analysis Implementation Details

1. **Analyzer Integration:**
   - Created new `llm_job_analyzer.py` module with job analysis functions
   - Added a prompt template designed to extract structured insights from job postings
   - Integrated analysis into the job parsing workflow through `job_parser.py`
   - Modified `job_parser_handler.py` to include LLM analysis in the response

2. **Data Flow:**
   - Job URL submission → Traditional parsing → Complete text extraction → LLM analysis → UI display
   - LLM analysis failures gracefully fall back to traditional parsing
   - Analyzed job data cached as JSON files to avoid repeated API calls
   - Analysis results displayed in UI alongside other job information

3. **Configuration Options:**
   - `USE_LLM_JOB_ANALYSIS` - Enable/disable LLM job analysis (default: true)
   - `LLM_JOB_ANALYZER_PROVIDER` - Select LLM provider (auto, claude, openai)
   - Auto-detection of available API keys when provider is set to "auto"

4. **LLM Prompt Design:**
   - Clear instructions for extracting specific insights from job postings
   - Structured output format with sections for different aspects of analysis
   - Low temperature (0.1) for deterministic, precise output
   - Consistent JSON output structure for frontend consumption

5. **UI Integration:**
   - Added a dedicated "AI Analysis" section at the top of job requirements
   - Used purple color theme to distinguish AI insights from regular content
   - Created visual components for candidate profile, hard skills, soft skills, and ideal candidate
   - Enhanced the tailoring process to use the AI analysis for better matching

6. **Provider Support:**
   - Added support for both Claude and OpenAI as analysis providers
   - Implemented configuration settings for provider selection
   - Added fallback logic when using "auto" provider selection
   - Prioritized OpenAI for job analysis when both providers are available

## YC-Eddie Style Implementation Details

1. **YC-Eddie Style Resume Format:**
   - Implement a single, high-quality resume format based on YC and Eddie's best practices
   - Create consistent document styling with professional fonts, spacing, and margins
   - Define structured formatting for headers, section titles, and content
   - Apply uniform bullet point styling and paragraph formatting
   - Ensure ATS compatibility while maintaining professional appearance

2. **Document Generation Enhancements:**
   - Create a completely new document instead of using the original as a template
   - Remove dependency on original document formatting that causes duplicate headers
   - Implement dedicated `resume_styler.py` module for consistent document styling
   - Define precise formatting specifications (fonts, sizes, margins, spacing)
   - Create proper heading hierarchies with consistent styling
   - Standardize bullet point formatting for experience and skills sections

3. **Specific Formatting Requirements:**
   - **Document Properties**:
     - Margins: 1.0cm top/bottom, 2.0cm left/right
     - Default font: Calibri, 11pt
     - Page size: Letter (8.5" x 11")
   - **Section Headers**:
     - Font: Calibri, 14pt, bold
     - Color: Dark blue (RGB: 0, 0, 102)
     - Centered alignment with full box border (all four sides)
     - Spacing: 6pt after header
     - Added spacing before each section
   - **Contact Information**:
     - Font: Calibri, 12pt
     - Alignment: Center
     - Include name, email, phone, and optional LinkedIn/website
   - **Bullet Points**:
     - Indentation: 0.25" left indent, -0.25" first line (hanging indent)
     - Arrow character (▸) instead of standard bullet (•)
     - Spacing: 6pt after each bullet point
     - Consistent formatting across all sections

4. **Implementation Components:**
   - Create `YCEddieStyler` class with methods for:
     - Setting document properties (margins, default styling)
     - Creating and applying section styles (headers, content, bullets)
     - Processing each section with appropriate formatting
     - `add_box_border` method for adding borders to section headers
     - `add_bullet_point` method for consistent arrow-style bullets
   - Modify `generate_tailored_resume_document` to:
     - Create a new blank document instead of using original template
     - Apply YC-Eddie styling through the styler class
     - Add tailored content with consistent section formatting
     - Save with appropriate naming convention

5. **Prompt Optimization (Priority):**
   - Research and document effective resume content patterns from YC and Eddie
   - Enhance system prompts with specific guidance for high-quality resume content
   - Implement section-specific prompts with targeted instructions:
     - **Summary**: Concise, impactful summaries positioning the candidate for the role
     - **Experience**: Achievement-focused content with metrics and strong action verbs
     - **Skills**: Prioritized skills aligned with job requirements
     - **Education/Projects**: Consistent formatting with relevant highlights

6. **Implementation Approach:**
   - Create improved base prompts focusing on:
     - Quantifying achievements with specific metrics
     - Using strong action verbs at the beginning of bullet points
     - Focusing on outcomes and impact rather than responsibilities
     - Removing generic or irrelevant information
     - Highlighting experience relevant to the job requirements
     - Maintaining concise, impactful language throughout
   - Add example formats and phrasings for few-shot learning
   - Implement enhanced document styling in the generation process
   - Test outputs against original content to measure improvements

## PDF Export Implementation Details

1. **PDF Generation Approach:**
   - Implemented WeasyPrint library for high-quality HTML-to-PDF conversion
   - Created dedicated PDF exporter module with configurable options
   - Utilized existing HTML preview as the source for PDF generation
   - Added PDF-specific CSS styling and page settings
   - Implemented proper error handling with fallback to DOCX format

2. **PDF Exporter Implementation:**
   - Created `pdf_exporter.py` module with the `PDFExporter` class
   - Implemented `create_pdf_from_html` helper function for easy integration
   - Added metadata support for title, author, and other PDF properties
   - Configured document properties (margins, page size, headers/footers)
   - Implemented font configuration for consistent text rendering
   - Added detailed logging throughout the PDF generation process

3. **PDF Styling:**
   - Created `pdf_styles.css` with print-specific CSS rules
   - Defined page properties using CSS `@page` rules for margins and size
   - Added page headers and footers with pagination
   - Implemented proper page break handling to prevent awkward section splits
   - Applied consistent typography and spacing for professional appearance
   - Configured bullet point styling and list formatting for clarity

4. **Integration with Tailoring Workflow:**
   - Updated `tailoring_handler.py` to use PDF generation instead of DOCX
   - Implemented error handling with automatic fallback to DOCX if PDF fails
   - Added appropriate file type indicators in API responses
   - Maintained the same filename conventions for consistency
   - Preserved HTML preview functionality alongside PDF generation

5. **Cross-Platform Considerations:**
   - Added support for GTK dependencies on Windows systems
   - Ensured Linux compatibility for deployment on hosting platforms
   - Implemented proper file path handling for different operating systems
   - Added clear error messaging for dependency issues
   - Maintained consistent output across different environments

6. **Benefits of PDF Generation:**
   - Consistent appearance across different devices and platforms
   - Professional formatting with precise control over layout
   - Smaller file sizes compared to DOCX for easier sharing
   - Better print quality with properly defined page settings
   - Improved security with read-only document format
   - ATS compatibility with properly structured content

7. **PDF Formatting Issue Resolution:**
   - **Issue**: Content being incorrectly center-aligned in PDF output for PDF input files
   - **Root Cause**: CSS specificity conflict where `.resume-section:first-child { text-align: center; }` (meant for contact section) was affecting all content in PDF-sourced resumes
   - **Analysis**: When processing PDF files, the HTML structure differs from DOCX files since we can't detect formatting details, causing different CSS inheritance behavior
   - **Solution Implemented**:
     - Added explicit content wrapper classes to all sections (`

## Task Breakdown: Adjust Resume Formatting to Utilize Full A4 Page Width

### Issue Analysis
The current resume formatting does not properly utilize the full A4 page width, resulting in a narrow appearance that affects the visual presentation and readability of the resume. After analyzing the code:

1. The HTML/CSS styling in multiple files controls the width of the resume:
   - In `html_generator.py`, the inline CSS defines `.tailored-resume-content` with a width of `8.27in` (A4 width) but includes large padding of `0 1in` (1 inch on each side).
   - In `static/css/styles.css`, there's a similar `.tailored-resume-content` class that sets the same width and padding.
   - In `static/css/pdf_styles.css`, the width for the resume content is set to `max-width: 100%` but inherits other constraints.

2. The actual content width is being constrained by these excessive margins and padding, reducing the effective content area to approximately 6.27 inches instead of the full 8.27 inches of an A4 page.

3. The PDF generation process uses these same CSS constraints when creating the final document, carrying over the narrow formatting.

### Root Cause
The root cause appears to be:
1. Excessive padding/margins in the CSS that leave too much whitespace on the sides
2. Inconsistent width settings across different CSS files
3. A possible misunderstanding of box-sizing and how padding factors into width calculations

### Debug Plan

1. **Inspect and modify CSS properties**:
   - Reduce the horizontal padding in `.tailored-resume-content` from `0 1in` to `0 0.5in` in both `html_generator.py` and `static/css/styles.css`.
   - Ensure the `box-sizing: border-box` property is consistently applied.
   - Review and adjust other margin and padding settings that may be affecting the layout.

2. **Update PDF styling**:
   - Adjust the @page margins in `static/css/pdf_styles.css` to be consistent with the HTML preview.
   - Currently set to `margin: 1cm 2cm;`, consider reducing to `margin: 1cm 1.5cm;` to allow more horizontal space.

3. **Test content flow**:
   - After making these changes, test with resumes containing long bullet points to ensure text flows properly.
   - Verify that line lengths remain readable and don't become too long.
   - Check for any side effects on mobile responsiveness.

4. **Improve parent container constraints**:
   - Examine the `.resume-preview-container` class which may be adding additional constraints.
   - Ensure it allows the resume content to use the full available width.

5. **Address special elements**:
   - Review the formatting of section headers and ensure they span the full width appropriately.
   - Check for any fixed-width elements that may need adjustment.

### Implementation Steps

1. **Update HTML Generator Template**:
   - Modify the inline CSS in `html_generator.py` to reduce padding and ensure proper width calculation.
   ```css
   .tailored-resume-content {
       width: 8.27in; /* A4 width in inches */
       max-width: 100%; /* Ensure responsiveness */
       margin: 0 auto;
       padding: 0 0.5in; /* Reduced from 1in to 0.5in */
       box-sizing: border-box;
       /* other properties remain the same */
   }
   ```

2. **Update Styles.css**:
   - Make the same changes to `.tailored-resume-content` in `static/css/styles.css` for consistency.
   - Review other container classes that might be affecting width.

3. **Update PDF Styles**:
   - Modify the page margins in `static/css/pdf_styles.css`:
   ```css
   @page {
     size: letter portrait;
     margin: 1cm 1.5cm; /* Reduced from 2cm to 1.5cm */
     /* other properties remain the same */
   }
   ```

4. **Test the changes**:
   - Generate previews and PDFs with various resume content.
   - Verify the appearance on different screen sizes.
   - Ensure the text remains readable while utilizing more horizontal space.

### Expected Results
The changes should:
1. Increase the effective content width of the resume
2. Maintain proper formatting and readability
3. Improve the overall visual presentation by using the page space more efficiently
4. Create a more professional appearance to the generated resumes

### Verification Process
1. Compare before/after screenshots of the resume preview
2. Generate PDFs with the new styling and verify proper page width utilization
3. Test with long bullet points to ensure proper text flow
4. Verify that mobile responsiveness is maintained

### Priority
Medium - This issue affects the visual presentation but doesn't prevent core functionality. 

## Styling Architecture Evaluation and Refactoring Plan

### Current Architecture Assessment

The current styling implementation for the resume tailoring application is fragmented across multiple files and technologies, making it challenging to maintain consistency and implement changes efficiently:

1. **Multiple Style Sources**:
   - Inline CSS in `html_generator.py` (defines core resume styling)
   - External CSS in `static/css/styles.css` (web UI styling)
   - External CSS in `static/css/pdf_styles.css` (PDF-specific styling)
   - JavaScript-applied styling in `static/js/main.js` (dynamically applies styles)
   - HTML template in `pdf_exporter.py` (contains additional inline styles)

2. **Coordination Challenges**:
   - Changes need to be synchronized across multiple files
   - No single source of truth for styling constants (widths, colors, spacing)
   - Hard to trace which styles are actually applied and in what order
   - Difficult to maintain consistency between HTML preview and PDF output

3. **Redundancy and Conflicts**:
   - Same classes defined in multiple places with slightly different properties
   - Potential for style conflicts requiring `!important` overrides
   - Duplicate code for similar styling constructs
   - Inconsistent naming conventions

### Proposed Refactoring Strategy

To address these issues, we propose a comprehensive styling architecture refactoring:

1. **Centralized Styling System**:
   - Create a dedicated `resume_styles.py` module to define all styling constants
   - Implement a `StyleManager` class that generates consistent CSS for all outputs
   - Use template variables instead of hardcoded values in all HTML/CSS
   - Define a single source of truth for all measurements, colors, and formatting

2. **Style Separation by Concern**:
   - `base_styles.css`: Core styling shared by all components
   - `preview_styles.css`: Specific to UI preview
   - `print_styles.css`: Specific to PDF generation
   - Eliminate inline styles in Python code where possible

3. **Consistent Styling API**:
   - Create helper functions for generating commonly used style blocks
   - Implement CSS variable system for key values (widths, colors, spacing)
   - Document all style components and their intended usage
   - Add validation to ensure styles meet requirements

4. **Implementation Phases**:

   **Phase 1: Style Extraction and Centralization**
   - Extract all inline styles from Python files into CSS files
   - Create a style constants module with all measurements and colors
   - Document all existing style rules and their purposes
   - Identify and resolve conflicting styles

   **Phase 2: Style Manager Implementation**
   - Create a `StyleManager` class to generate consistent styles
   - Add methods for HTML preview and PDF export styling
   - Implement template system for style application
   - Add validation to ensure consistent rendering

   **Phase 3: HTML/CSS Refactoring**
   - Update all HTML generators to use the style manager
   - Convert hardcoded values to references to style constants
   - Implement responsive design considerations
   - Ensure accessibility compliance

   **Phase 4: PDF Generation Integration**
   - Refactor PDF export to use consistent styling
   - Ensure perfect match between preview and PDF output
   - Optimize PDF styling for printing and ATS compatibility
   - Add configurability for different page sizes and formats

### Expected Benefits

1. **Maintainability**:
   - Single point of control for all styling changes
   - Reduced risk of inconsistencies when implementing changes
   - Better organization of style components

2. **Consistency**:
   - Unified appearance across preview and generated PDFs
   - Consistent spacing, colors, and typography
   - Predictable behavior across different resume content

3. **Extensibility**:
   - Easier to add new style variants or themes
   - Better support for different paper sizes and formats
   - Foundation for future UI/UX improvements

4. **Developer Experience**:
   - Clear documentation of styling components
   - Reduced complexity when making style changes
   - Shorter development cycles for style-related features

### Implementation Considerations

- **Backward Compatibility**: Ensure existing resumes continue to render correctly
- **Testing Strategy**: Compare before/after rendering to verify visual consistency
- **Performance Impact**: Evaluate any performance changes from the new architecture
- **Refactoring Risks**: Plan for incremental changes to minimize disruption

### Priority and Timeline

This is a significant architectural change that should be planned as a medium-priority, high-impact task. The implementation should be phased to allow for ongoing feature development, with each phase taking approximately:

- Phase 1: 3-5 days
- Phase 2: 5-7 days
- Phase 3: 3-5 days
- Phase 4: 3-5 days

Total estimated effort: 2-3 weeks of dedicated development time.

Given the current priorities, this should be scheduled after addressing critical user-facing issues, but before implementing extensive new styling features.

## Learnings

- Centralizing styling improves consistency and maintainability across different outputs.
- Using design tokens as a single source of truth simplifies updates and modifications.

## Solutions Implemented

- Created `design_tokens.json` for visual constants.
- Developed a `StyleManager` class for consistent style application.
- Ensured consistent styling across HTML and PDF outputs.

## New Styling Fixes (May 2025)

### Overview
Address five UI/print styling issues discovered during QA testing.  These changes touch both the HTML preview and PDF output.  We will tackle them in a single sprint because they share the same SCSS sources.

### Issues to Resolve
1. Remove redundant text: **"User Resume Parsed (LLM)"**
2. Reduce **section-header** height and left-align header text
3. Align bullet points flush with company/title lines
4. Standardise page margins to **1 inch** on all sides (preview + PDF)

### Implementation Plan
| Step | File(s) | Action |
|------|---------|--------|
|1| `upload_handler.py`, `templates/index.html` | Delete or hide the header string *User Resume Parsed (LLM)* so it no longer shows in the UI. |
|2| `design_tokens.json` | Change `"paper-padding-vertical"` & `"paper-padding-horizontal"` to `"1in"`.  Add `"sectionHeaderPadding": "4px 8px"` for tight boxes.  Re-generate `_tokens.scss` (or hand-edit if script unavailable). |
|3| `static/scss/_resume.scss` | a) Update `.section-box` `padding` → `$sectionHeaderPadding` and `text-align:left`; b) Update `.resume-section h2` to `text-align:left`. |
|4| `static/scss/_resume.scss` | Adjust bullet styles: `.job-content ul { margin-left:0; padding-left:1.1em; }` and `.job-content li { padding-left:1.1em; }` |
|5| `static/scss/print.scss` | Set `@page { margin: 1in; }` |
|6| **Build** | Re-compile SCSS → `preview.css`, `print.css` (command: `npm run build-scss` or `sass static/scss:static/css`). |
|7| **QA** | Run Flask locally, upload a sample résumé, verify preview & PDF.  Check: no extra label, slim headers left-aligned, bullets aligned, 1-in margins. |
|8| **Docs** | Update `KNOWN_ISSUES.md` – mark items resolved, and add any notes.  Commit & push. |

### Timeline
Estimated effort: **1–2 hours** including QA and commit.

--- 