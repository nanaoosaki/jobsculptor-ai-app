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
- [x] Switch from Word document generation to PDF export for better consistency
- [x] Implement HTML-to-PDF conversion with professional styling
- [x] Update download functionality to provide PDF files instead of Word documents
- [x] Optimize PDF layout for ATS compatibility and professional appearance
- [x] Fix nested scrollbars in User Resume Parsed component
- [x] Implement A4 paper format for HTML resume preview
- [x] Fix contact information preservation in tailored resume output
- [x] Fix LLM response handling and error recovery in resume tailoring process

## In Progress Tasks

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
     - Added explicit content wrapper classes to all sections (`experience-content`, `education-content`, etc.)
     - Applied inline styles with `!important` directly to content elements to override any inheritance issues
     - Added explicit text-align properties to all HTML elements during generation
     - Modified CSS selectors to be more specific about which elements should be centered vs. left-aligned
     - Added inline styles in the HTML head to enforce alignment rules regardless of source document type
   - **Impact**: This ensures consistent formatting across both DOCX and PDF input files, maintaining centered headers while keeping all content properly left-aligned

8. **Resume Format Structure Issue:**
   - **Issue**: In the tailored resume output, job details (company name, position, dates, location) are placed on separate lines instead of being properly aligned as in the original resume
   - **Root Cause**: 
     - The LLM is not preserving the exact format structure when tailoring the content
     - The format_experience_content function is not properly identifying and structuring company/position/date information
     - PDF parsing doesn't maintain the structured layout of flex containers and positioning
   - **Analysis**:
     - When the LLM tailors the resume content, it may not maintain the exact same line structure
     - The parsing logic in format_experience_content has limitations in detecting formatting patterns
     - The detection of company/location and position/date pairs needs to be more robust
   - **Solution Plan**:
     1. **Enhance LLM Prompting**:
        - Update the system and user prompts to emphasize maintaining exact formatting
        - Add specific examples showing the expected output format with proper alignment
        - Include explicit instructions to preserve the line-by-line structure
     2. **Improve Format Detection**:
        - Enhance company/location detection patterns to better identify when they appear on the same line
        - Add more sophisticated regex patterns to detect position/date pairs
        - Recognize common formatting patterns in different resume styles
     3. **Strengthen HTML Structure**:
        - Ensure flex layouts are consistently applied to company/location and position/date pairs
        - Add explicit wrapper divs with proper flex styling
        - Apply consistent CSS properties to maintain alignment
     4. **Add Format Validation**:
        - Implement a post-processing step to verify the formatted output matches expected patterns
        - Add structure validation to ensure company/location and position/date are paired properly
        - Provide fallback formatting when the structure is unclear
   - **Expected Impact**:
     - Consistent formatting between original and tailored resumes
     - Proper alignment of job details with company/location and position/date on respective single lines
     - Improved visual consistency across different resume formats and sources

## LLM Response Handling Improvements

1. **Error Recovery Enhancements:**
   - **Issue**: Application failures due to LLM API response parsing errors and syntax issues
   - **Root Cause Analysis**:
     - Invalid escape sequences in regex patterns causing SyntaxWarnings
     - Indentation errors in certain functions leading to application crashes
     - Incorrect variable references ('llm_client' vs 'self') in OpenAIClient methods
     - Missing 're' module imports in certain function scopes
   - **Solutions Implemented**:
     - Fixed regex patterns by using raw string syntax (fr'pattern') to prevent escape sequence errors
     - Corrected indentation issues in extract_resume_sections function
     - Fixed variable scope references to use appropriate object references
     - Added explicit module imports in functions that need them
     - Enhanced error handling to recover gracefully from JSON parsing failures
   
2. **JSON Response Processing Improvements:**
   - **Issue**: LLM responses sometimes returned malformed JSON leading to parsing failures
   - **Solutions Implemented**:
     - Added multi-stage fallback mechanisms for JSON parsing
     - Implemented regex-based extraction for cases where JSON is malformed
     - Added comprehensive logging of parsing attempts and failures
     - Created consistent internal data structures regardless of parsing method
     - Ensured final output quality even when intermediate parsing has issues

3. **Module Structure Optimizations:**
   - Ensured proper scoping of variables across function boundaries
   - Made error handling more robust with specific exception types
   - Implemented consistent logging patterns throughout the codebase
   - Added more debug information for troubleshooting
   - Ensured deterministic behavior even with inconsistent API responses

4. **Testing and Validation:**
   - Performed extensive testing with various resume formats
   - Verified handling of different API response patterns
   - Confirmed error recovery paths work correctly
   - Validated consistent output quality with all parsing scenarios
   - Added regression tests for previously identified issues

## Results

The LLM-based resume parsing significantly improves the accuracy of section extraction compared to traditional methods:

1. **Accuracy Improvements:**
   - Properly identifies and categorizes resume sections regardless of formatting
   - Maintains the exact content structure from the original resume
   - Works with a wide variety of resume formats and styles

2. **Processing Flow:**
   - Initial upload parsing shows "User Resume Parsed (LLM)" when successful
   - Tailoring process uses the same LLM parser for consistent section extraction
   - Logs show detailed information about parsing process and results
   - Fallbacks ensure the application continues working even if LLM is unavailable

3. **Performance:**
   - OpenAI gpt-4o parses a resume in ~3-5 seconds
   - Claude parsing has similar performance characteristics
   - Both providers extract sections with high accuracy 

The LLM-based job analysis provides deeper insights compared to regex-based extraction:

1. **Enhanced Analysis Benefits:**
   - More nuanced understanding of the job requirements
   - Better identification of implicit skills and qualifications
   - Improved matching between resume content and job requirements
   - Enhanced tailoring quality through better job understanding
   - More targeted suggestions for resume improvements

2. **Analysis Results:**
   - Comprehensive candidate profile describing experience level and role focus
   - Structured lists of both hard technical skills and soft interpersonal skills
   - Detailed ideal candidate description for more effective resume targeting
   - AI insights help users better understand what employers are looking for

3. **User Experience:**
   - Visual distinction of AI-generated insights in the UI
   - Clear organization of analysis results by category
   - Seamless integration with the existing tailoring workflow
   - Improved resume tailoring through more detailed job understanding

The YC-Eddie Style implementation produces consistently high-quality resume outputs:

1. **Style Improvements:**
   - Professional, polished document appearance with clean, modern styling
   - Centered section headers with full box borders for better visual separation
   - Arrow bullet points (▸) instead of standard bullets for improved readability 
   - Consistent spacing and alignment throughout the document
   - Matching styling in both Word documents and HTML previews
   - Clean document generation without reliance on templates

2. **Content Quality:**
   - Achievement-focused content with metrics and results
   - Clear, concise language that highlights candidate value
   - Consistent formatting across all resume sections
   - Better alignment with recruiter expectations and ATS requirements
   - Higher-quality tailored content through optimized prompting

3. **Technical Implementation:**
   - Complete rewrite of document generation for better control
   - Dedicated styling methods for each document element
   - Proper XML manipulation for advanced formatting features
   - Consistent HTML/CSS styling for preview generation
   - Graceful fallbacks for error conditions 

The LLM-based resume parsing significantly improves the accuracy of section extraction compared to traditional methods: 

# Task Breakdown: HTML Preview A4 Paper Format Implementation

## Problem Description
The HTML preview of the tailored resume did not match the dimensions and appearance of the PDF output, leading to inconsistent user experience. The preview needed to be styled to match an A4 paper format with 1-inch margins on both sides.

## Solution Implemented
We have implemented a comprehensive solution to make the HTML preview appear like a standard A4 paper document:

1. **CSS Updates**:
   - Set the width of the preview content to match A4 paper (8.27 inches)
   - Added 1-inch margins on both left and right sides using padding
   - Applied proper box-sizing to ensure correct width calculations
   - Used the same font family and size as the PDF output (Calibri, 11pt)
   - Applied appropriate line height and text color for readability
   - Added a subtle shadow effect to create a "paper" appearance

2. **JavaScript Improvements**:
   - Updated the `displayResumePreview()` function to create a paper-like container
   - Added a centered container to properly position the A4 paper representation
   - Applied consistent styling between the HTML preview and PDF output
   - Ensured proper removal of nested scrollbars in the preview content
   - Added text alignment for the header to match the PDF output

## Testing
The changes have been tested to ensure:
- The HTML preview dimensions match standard A4 paper size
- The content has 1-inch margins on both sides
- The appearance is consistent with the downloaded PDF
- The preview remains responsive and properly scrollable
- All formatting from the original tailored content is preserved

## Impact
This enhancement improves the user experience by providing a consistent view between what users see in the preview and what they get in the downloaded PDF. The WYSIWYG (What You See Is What You Get) approach helps users better evaluate their tailored resume before downloading it. 

# Task Breakdown: Preserve Contact Information in Tailored Resume Output

## Problem Description
The contact information from the original resume was not being included in the tailored resume output. This critical section was missing entirely, making the tailored resume incomplete and unusable for job applications.

## Root Cause Analysis
1. The contact information was being correctly parsed from the original resume
2. However, it was not being consistently included in the final HTML preview generation
3. The `generate_preview_from_llm_responses` function only included contact information if it was explicitly present in the LLM tailored content
4. Since contact information doesn't need tailoring (it should be preserved as-is), it wasn't always being included in the LLM response

## Solution Implemented
We've implemented a comprehensive solution to ensure contact information always appears in the tailored resume:

1. **LLM Resume Parser Enhancements**:
   - Added a global caching mechanism to store the most recently parsed resume data
   - Implemented a `get_cached_parsed_resume()` function to retrieve contact information without re-parsing
   - Enhanced the caching system to make it more robust and accessible across modules

2. **Preview Generation Improvements**:
   - Modified the `generate_preview_from_llm_responses` function to check multiple sources for contact information
   - Added a fallback system that tries first the LLM tailored content, then cached resume data
   - Added proper error handling to ensure the process continues even if contact retrieval fails
   - Ensured contact information appears at the top of the resume with appropriate formatting

3. **Code Integration**:
   - Updated imports to access cached resume data when needed
   - Added logging to track the source of contact information
   - Maintained backward compatibility with existing code

## Testing
The changes have been tested to ensure:
- Contact information consistently appears in tailored resumes
- The original format and content of contact details are preserved
- The system works with both PDF and DOCX resume formats
- Fallback mechanisms work properly when primary sources are unavailable

## Impact
This enhancement significantly improves the usability of tailored resumes by ensuring they always include the essential contact information needed for job applications. Users no longer need to manually add this information after tailoring. 

# Task Breakdown: LLM Response Handling and Error Recovery Improvements

## Problem Description
The application was failing during the resume tailoring process due to various issues with LLM API responses and code syntax errors. These failures prevented users from completing the tailoring process and resulted in error messages instead of properly tailored resumes.

## Root Cause Analysis
1. Several syntax errors in the claude_integration.py file:
   - Invalid escape sequences in regex patterns causing SyntaxWarnings
   - Indentation errors in certain functions
   - Variable scope issues with 're' module imports
   - References to undefined variables

2. LLM response processing challenges:
   - API responses sometimes returned malformed JSON
   - JSON parsing failures not being properly handled
   - Inconsistent variable references between modules

## Solution Implemented
We've implemented a series of improvements to make the application more resilient:

1. **Syntax and Code Fixes**:
   - Fixed regex patterns by using raw string syntax (fr'pattern')
   - Corrected indentation issues in extract_resume_sections function
   - Added explicit 're' module imports where needed
   - Fixed variable scope references to use correct object attributes

2. **Error Handling Enhancements**:
   - Implemented multi-stage fallback mechanisms for JSON parsing
   - Added regex-based extraction for malformed JSON responses
   - Enhanced exception handling with specific error types
   - Ensured proper error logging with detailed contextual information

3. **JSON Response Processing**:
   - Added more robust validation of response structures
   - Implemented fallback content extraction when JSON parsing fails
   - Created consistent internal data structures regardless of parsing method
   - Ensured original content is preserved when tailoring fails

## Testing
The changes have been thoroughly tested to ensure:
- The application handles malformed LLM responses gracefully
- Error recovery paths work correctly and maintain application flow
- The tailoring process completes even with non-ideal API responses
- Error logging provides sufficient detail for troubleshooting
- No syntax errors or warnings appear during normal operation

## Impact
These improvements significantly enhance the reliability of the resume tailoring process, ensuring users can consistently get properly tailored resumes without application failures. The more robust error handling allows the application to recover from unexpected conditions and continue providing value to users. 