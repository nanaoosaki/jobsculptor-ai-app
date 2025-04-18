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

---

## Other Issues 