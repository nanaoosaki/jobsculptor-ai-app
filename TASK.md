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

## In Progress Tasks

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