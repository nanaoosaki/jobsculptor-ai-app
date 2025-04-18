# Known Issues

## Resume Formatting Issues

### Company Name and Location Separation Issue
**Status**: Unresolved (April 18, 2025)

**Description**:  
The application fails to properly separate company names from city names when they appear without clear separators. For example, "DIRECTV LOS ANGELES" is not being parsed correctly to separate the company name "DIRECTV" from the location "LOS ANGELES".

**Attempted Solutions**:
1. Modified the `format_job_entry` and `format_education_entry` functions to separate city and state from the location text for display
2. Added regex pattern detection in `format_experience_content` to identify common US city names within company strings
3. Updated the LLM resume parsing prompt to explicitly instruct the model to separate company names from locations

**Impact**:  
In the PDF output, city names may appear directly adjacent to company names instead of being properly aligned with the state on the right side of the page.

**Possible Future Solutions**:
1. Implement a dedicated pre-processing step that uses a comprehensive database of company names and city names to identify and separate them
2. Create a more sophisticated NLP-based entity recognition system specifically for company and location entities
3. Add a manual correction option in the UI to allow users to edit the parsed company/location information before generating the final PDF
4. Fine-tune the LLM specifically for resume parsing with a focus on entity separation

**Priority**: Medium

### Bullet Point Duplication in Resume Output
**Status**: Partially Resolved (April 18, 2025)

**Description**:  
Some sections of the tailored resume output show duplicate bullet point symbols. The issue occurs inconsistently, with some bullets correctly formatted while others show duplicated bullet symbols (e.g., "• • Integrated AWS QuickSight..."). The problem appears to be related to the different formatting paths used for different types of content.

**Attempted Solutions**:
1. Added a `clean_bullet_points` function to remove bullet point symbols from parsed content
2. Enhanced bullet point detection logic in `format_section_content` to identify content that should be formatted as bullets based on content characteristics rather than just bullet symbols
3. Added validation to ensure bullet points are properly cleaned during parsing
4. Modified regex patterns to better detect various bullet point formats

**Impact**:  
In the PDF and HTML output, some bullet points appear with duplicate bullet symbols, affecting the visual presentation and professionalism of the resume.

**Possible Future Solutions**:
1. Refactor the content formatting pipeline to use a consistent approach for all bullet points regardless of section type
2. Implement a post-processing step specifically to check for and remove duplicate bullet symbols in the HTML output
3. Create a more comprehensive bullet point detection system that doesn't rely on simple pattern matching
4. Provide configuration options to customize bullet point styles and formats
5. Add special handling for content from PDF source documents which may have different formatting characteristics

**Priority**: Medium

---

## Other Issues 