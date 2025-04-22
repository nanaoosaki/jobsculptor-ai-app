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

### Empty Bullet Points in Tailored Resume
**Status**: Unresolved (April 21, 2025)

**Description**:  
The tailored resume output contains empty bullet points that appear as lone bullet symbols with no text content. These empty bullets affect the professional appearance of the document and create confusing spacing in the layout.

**Impact**:  
Visual inconsistency in the resume presentation, with empty spaces that may appear as formatting errors to potential employers.

**Possible Solutions**:
1. Add filtering logic to remove any empty bullet points before generating HTML
2. Update the LLM prompt to explicitly instruct not to generate empty bullet points
3. Implement a post-processing check to identify and remove list items with no meaningful content
4. Improve regex patterns to better identify and handle content-less bullet points

**Priority**: High

### Excessive Line Length in Bullet Points
**Status**: Unresolved (April 21, 2025)

**Description**:  
The LLM-generated bullet points often extend too far horizontally, causing poor formatting in the PDF output. The prompt needs to be improved to encourage shorter, more concise bullet points that fit appropriately within the resume layout.

**Impact**:  
Poor visual presentation with text that may extend beyond margins or cause uneven spacing between bullet points.

**Possible Solutions**:
1. Update the LLM prompt to specify a maximum character length for each bullet point
2. Implement a post-processing step to break up long bullet points into multiple points
3. Add a truncation mechanism for bullets that exceed certain length thresholds
4. Provide guidance to the LLM about optimal resume formatting standards

**Priority**: Medium

### Missing Contact Section in Tailored Resume
**Status**: Unresolved (April 21, 2025)

**Description**:  
The contact section from the original resume is not being preserved in the tailored output. The logs show a warning "No contact information found in cached resume or LLM responses", indicating a failure in the contact information preservation process.

**Impact**:  
Tailored resumes lack essential contact information, making them incomplete for job applications.

**Possible Solutions**:
1. Modify the `tailor_resume_with_llm` function to always preserve and transfer contact information
2. Improve caching mechanisms for parsed resume data to ensure contact information is available
3. Add a fallback mechanism to extract contact information directly from the original document if not available in the cached data
4. Update the LLM prompt to explicitly extract and preserve contact information

**Priority**: Critical

### Missing Projects Section in Tailored Resume
**Status**: Unresolved (April 21, 2025)

**Description**:  
The projects section appears to be missing entirely from the tailored resume output despite being present in the original resume. The logs indicate that project data is being processed, but the content is not appearing in the final document.

**Impact**:  
Loss of valuable project information that could demonstrate relevant skills to potential employers.

**Possible Solutions**:
1. Debug the project data flow from parsing to final HTML generation
2. Verify the JSON formatting of project data from the LLM responses
3. Check for conditional logic that might be incorrectly filtering out project sections
4. Ensure project section HTML is properly included in the template generation process

**Priority**: High

### Missing Education Entries in Tailored Resume
**Status**: Unresolved (April 21, 2025)

**Description**:  
The tailored resume shows only one education entry when multiple entries exist in the original resume. The second (or subsequent) education entries are being lost during the tailoring process.

**Impact**:  
Incomplete representation of the candidate's educational background, potentially hiding relevant qualifications.

**Possible Solutions**:
1. Debug the `_format_education_json` method to ensure it properly handles multiple education entries
2. Investigate how the LLM is processing multiple education entries in its response
3. Update the education section prompt to explicitly instruct the LLM to preserve all education entries
4. Add validation to check if the number of education entries in the output matches the input

**Priority**: High

---

## Other Issues 