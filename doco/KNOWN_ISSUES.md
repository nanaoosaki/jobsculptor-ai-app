# Known Issues

## All issues listed below have been resolved as of [current date].

### Company Name and Location Separation Issue
**Status**: Resolved

### Bullet Point Duplication in Resume Output
**Status**: Resolved

### Empty Bullet Points in Tailored Resume
**Status**: Resolved

### Excessive Line Length in Bullet Points
**Status**: Resolved

### Missing Contact Section in Tailored Resume
**Status**: Resolved

### Missing Professional Summary Section
**Status**: Resolved

### Missing Projects Section in Tailored Resume
**Status**: Resolved

### Missing Education Entries in Tailored Resume
**Status**: Resolved

### Narrow Formatting of Resume
**Status**: Resolved

### Frame Lines in PDF Download
**Status**: Resolved

### PDF Generation Delay
**Status**: Resolved

### Styling Discrepancy: Preview vs. PDF & PDF Enlargement
**Status**: Resolved

**Description**: 
Recent attempts to apply styling changes (e.g., adding a test outline) resulted in the change appearing **only** in the downloaded PDF, not in the live HTML preview. Furthermore, the PDF content appeared enlarged or misaligned with standard page dimensions after the change. This indicates a divergence in how styles are applied/loaded between the preview and PDF generation, despite efforts towards single-source styling (`ALIGN_HTML_PDF_STYLING_PLAN.md`). The root cause likely involves browser caching for the preview and potentially unexpected CSS interactions within the PDF renderer.

**Impact**: 
- The preview does not accurately reflect the final PDF output, hindering development and testing.
- The PDF layout is potentially broken or unprofessional.

**Next Steps**: 
1. Investigate browser caching and CSS linking for the HTML preview.
2. Analyze CSS rules applied during PDF generation to find the cause of the enlargement.
3. Re-verify the implementation against `ALIGN_HTML_PDF_STYLING_PLAN.md` and `styling_changes.md`.

**Priority**: High

### Styling Changes Not Reflected
**Status**: Resolved

**Description**: 
Despite implementing various styling changes, there have been no visible changes in the application's appearance. This indicates a fundamental issue in our approach to styling.

**Root Cause Analysis**:
- The root causes listed in `single-source styling.md` and `styling_changes.md` did not resolve the issue. This suggests that either the identified causes are incorrect or there are additional factors we are missing.

**Impact**:
- The lack of visual changes affects the application's user interface and user experience, as the intended styling improvements are not being realized.

**Next Steps**:
1. Conduct a thorough review of the styling implementation to identify any overlooked issues.
2. Re-evaluate the root causes and explore alternative explanations for the lack of visual changes.
3. Consider consulting with a styling expert to gain additional insights.

**Priority**: High

### Bullet Point Overlap Issue
**Status**: Resolved

**Description**: 
A 'u2022' character was appearing in the experience section, overlapping with bullet points in both the HTML preview and PDF download.

**Resolution**:
- Added proper spacing and positioning for bullet points in the SCSS
- Added new design tokens for bullet list padding, item padding, and text indentation
- Applied consistent styling to all bullet points across the resume
- Verified the fix in both HTML preview and PDF output

**Impact**: 
- The bullet points now display correctly with proper spacing and alignment
- The visual appearance of the resume is improved, looking more professional

**Priority**: Medium

### Section Header Box Width
**Status**: Resolved

### Section Header Box Fill
**Status**: Resolved

### Margin Size
**Status**: Resolved

### Section Box Height
**Status**: Resolved

### Bullet Point Length and Symbol
**Status**: Resolved

### Bullet Point Character Issue in CSS
**Status**: Resolved

**Description**: 
The CSS files `print.css` and `preview.css` contained a hard-coded string "u2022" for bullet points, which was displayed literally in the experience section of resumes.

**Resolution**:
- Replaced the hard-coded "u2022" with the properly escaped Unicode character "\2022" in both CSS files.

**Impact**: 
- Bullet points now display correctly in both the HTML preview and PDF outputs, improving the professional appearance of resumes.

**Next Steps**: 
- Monitor for any further styling discrepancies in resume outputs.

**Priority**: Low

### Hard-Coded Bullet Point Issue
**Status**: Resolved

**Description**: 
The recompilation of `_resume.scss` was resulting in the hard-coded "u2022" character being inserted into the CSS files instead of a proper bullet point.

**Resolution**:
- Updated the `bullet-glyph` variable in `design_tokens.json` from `"\"\\u2022\""` to `"\"\\2022\""`, using the proper CSS escape syntax.
- Regenerated tokens with `python tools/generate_tokens_css.py`
- Recompiled SCSS files with `sass static/scss/preview.scss static/css/preview.css` and `sass static/scss/print.scss static/css/print.css`
- Verified the bullet points now correctly display in both the HTML preview and PDF.

**Impact**: 
- Bullet points now display correctly with the proper bullet symbol instead of the literal text "u2022".

**Priority**: Medium

### DOCX Download Missing Sections
**Status**: Resolved

**Description**: 
When downloading a résumé in DOCX format, only the Skills section was visible and it displayed raw JSON data instead of formatted skills. All other sections (contact, experience, education, projects) were missing.

**Root Cause**:
The issue was due to a mismatch between the data structures in the JSON files and what the DOCX builder expected:
- Experience, education, and projects were stored as direct lists, not dictionaries with keys
- Contact and summary sections used a 'content' key structure
- The skills section needed proper formatting for nested dictionaries

**Resolution**:
- Enhanced the DOCX builder to handle different data structures flexibly
- Added special handling for sections with 'content' keys
- Added robust type checking throughout the code
- Improved handling of skills data to properly format categories and items
- Added special case for projects with string content
- Created a test script to verify DOCX generation outside the web app

**Impact**: 
- DOCX downloads now correctly display all résumé sections with proper formatting
- The code is more robust and can handle various data structures without errors

**Priority**: High

### Misunderstanding Regarding DOCX Download Button Implementation

**Issue Description**: 
There was a misunderstanding regarding the implementation of the DOCX download button. Initially, it was thought that the button was located in the `tailored_resume.html` template. However, it has been confirmed that the button is actually implemented in the `index.html` template. Additionally, the handling of download types is managed by the `main.js` file.

**Impact**: 
This misunderstanding may lead to confusion when troubleshooting or enhancing the download functionality, as the relevant code is not where it was initially assumed to be.

**Next Steps**: 
1. Review the `index.html` file to ensure the DOCX download button is correctly implemented.
2. Verify the functionality in `main.js` to ensure it properly handles the download types for both PDF and DOCX formats.
3. Update any related documentation to reflect the correct locations of the button and its handling logic.

**Priority**: Medium

### Redundant Text in Resume Section
**Status**: Resolved

### Section Header Height and Alignment
**Status**: Resolved

### Bullet Point Alignment
**Status**: Resolved

### Page Margin Size
**Status**: Resolved

---

## Other Issues

All known issues have been resolved. If new issues arise, they will be documented here.

### New Known Issues

1. **Redundant Text in Resume Section**
   - **Description**: The text 'User Resume Parsed (LLM)' appears unnecessarily in the resume section.
   - **Impact**: Clutters the UI and may confuse users.
   - **Next Steps**: Remove the redundant text from the UI.
   - **Priority**: Medium

2. **Section Header Height**
   - **Description**: The section headers are too tall, taking up excessive vertical space.
   - **Impact**: Affects the visual balance and readability of the resume.
   - **Next Steps**: Adjust the CSS to reduce the height of section headers.
   - **Priority**: Medium

3. **Section Header Alignment**
   - **Description**: Section header texts are not left-aligned as intended.
   - **Impact**: Misalignment affects the professional appearance of the resume.
   - **Next Steps**: Modify the CSS to ensure section headers are left-aligned.
   - **Priority**: Medium

4. **Bullet Point Alignment**
   - **Description**: Bullet points are not aligned with the company/title.
   - **Impact**: Misalignment affects readability and professionalism.
   - **Next Steps**: Adjust the CSS to align bullet points with the company/title.
   - **Priority**: Medium

5. **Page Margin Size**
   - **Description**: The page margins are larger than desired, currently exceeding 1 inch on each side.
   - **Impact**: Reduces the amount of content visible on each page.
   - **Next Steps**: Reduce the page margins to 1 inch on each side.
   - **Priority**: Medium

### Resolved Issues

1. **Grey Bar in PDF Output**
   - **Status**: Resolved
   - **Description**: A grey horizontal bar appeared in the PDF output but not in the HTML preview.
   - **Resolution**: Updated `print.scss` to hide the contact-divider, resolving the issue.

2. **Bullet Point Formatting**
   - **Status**: Resolved
   - **Description**: Bullet points were not aligned correctly, affecting readability.
   - **Resolution**: Updated SCSS to ensure proper alignment and appearance of bullet points.

3. **Contact Information Preservation**
   - **Status**: Resolved
   - **Description**: Contact information was not being preserved in tailored resumes.
   - **Resolution**: Fixed the issue to ensure contact details are preserved correctly.

### Unresolved Issues

1. **Margin Size Issue**
   - **Status**: Unresolved
   - **Description**: The margin set to 1 inch is larger than expected and needs to be reduced to 1 cm.
   - **Impact**: Reduces the amount of content visible on each page.
   - **Next Steps**: Adjust the margin size in the SCSS files to 1 cm.

2. **Section Box Height Issue**
   - **Status**: Unresolved
   - **Description**: The section box height needs to be reduced further. The width is also incorrectly set to 100% in SCSS, preventing it from fitting the content.
   - **Impact**: The layout appears unbalanced, with excessive vertical space and width in section headers.
   - **Next Steps**: Modify `.section-box` in `_resume.scss` (remove `width: 100%`, change `display: block` to `display: inline-block`), recompile SCSS, restart server, and verify.
   - **Priority**: Medium

3. **Bullet Point Length and Symbol Issue**
   - **Status**: Unresolved
   - **Description**: Bullet points are too long, and the bullet point symbol is missing.
   - **Impact**: The readability and professional appearance of the resume are affected.
   - **Next Steps**: Adjust the bullet point length in the SCSS files and ensure the bullet point symbol is correctly displayed.
   - **Priority**: Medium

4. **Section Header Box Width**
   - **Status**: Reopened / Unresolved
   - **Description**: The section header box was previously thought resolved but is still displaying at full width due to `width: 100%` in `_resume.scss`, overriding the intended fit-content behavior.
   - **Resolution**: Planned fix involves removing `width: 100%` and changing `display: block` to `display: inline-block` in `_resume.scss`.

5. **Bullet Point Formatting**
   - **Status**: Resolved
   - **Description**: Bullet points were not aligned correctly, affecting readability.
   - **Resolution**: Updated SCSS to ensure proper alignment and appearance of bullet points.

6. **Contact Information Preservation**
   - **Status**: Resolved
   - **Description**: Contact information was not being preserved in tailored resumes.
   - **Resolution**: Fixed the issue to ensure contact details are preserved correctly.

7. **Section Header Box Fill**
   - **Status**: Unresolved
   - **Description**: The section header box currently has a blue fill, but it should only have a blue outline with a transparent fill.
   - **Impact**: The current design does not match the intended visual style.
   - **Next Steps**: Modify the CSS to change the section header box to have a transparent fill and a blue outline.
   - **Priority**: Medium

8. **Bullet Point Character Issue in CSS**
   - **Status**: Resolved
   - **Description**: The CSS files `print.css` and `preview.css` contained a hard-coded string "u2022" for bullet points, which was displayed literally in the experience section of resumes.
   - **Resolution**: Replaced the hard-coded "u2022" with the properly escaped Unicode character "\2022" in both CSS files.
   - **Impact**: Bullet points now display correctly in both the HTML preview and PDF outputs, improving the professional appearance of resumes.
   - **Next Steps**: Monitor for any further styling discrepancies in resume outputs.
   - **Priority**: Low

9. **Hard-Coded Bullet Point Issue**
   - **Status**: Resolved
   - **Description**: The recompilation of `_resume.scss` was resulting in the hard-coded "u2022" character being inserted into the CSS files instead of a proper bullet point.
   - **Resolution**: Updated the `bullet-glyph` variable in `design_tokens.json` from `"\"\\u2022\""` to `"\"\\2022\""`, using the proper CSS escape syntax.
   - **Impact**: Bullet points now display correctly with the proper bullet symbol instead of the literal text "u2022".
   - **Priority**: Medium

10. **Margin Size Issue**
    - **Status**: Unresolved
    - **Description**: The margin set to 1 inch is larger than expected and needs to be reduced to 1 cm.
    - **Impact**: Reduces the amount of content visible on each page.
    - **Next Steps**: Adjust the margin size in the SCSS files to 1 cm.
    - **Priority**: Medium

11. **Section Box Height Issue**
    - **Status**: Unresolved
    - **Description**: The section box height needs to be reduced further. The width is also incorrectly set to 100% in SCSS, preventing it from fitting the content.
    - **Impact**: The layout appears unbalanced, with excessive vertical space and width in section headers.
    - **Next Steps**: Modify `.section-box` in `_resume.scss` (remove `width: 100%`, change `display: block` to `display: inline-block`), recompile SCSS, restart server, and verify.
    - **Priority**: Medium

12. **Bullet Point Length and Symbol Issue**
    - **Status**: Unresolved
    - **Description**: Bullet points are too long, and the bullet point symbol is missing.
    - **Impact**: The readability and professional appearance of the resume are affected.
    - **Next Steps**: Adjust the bullet point length in the SCSS files and ensure the bullet point symbol is correctly displayed.
    - **Priority**: Medium

13. **DOCX Contact Section Missing**
    - **Status**: Resolved
    - **Description**: The contact section was missing from the DOCX output, despite being visible in the PDF output and the corresponding JSON file existing in the temporary directory.
    - **Impact**: Users downloading the DOCX version couldn't see their contact information, reducing the professional appearance and usefulness of the resume.
    - **Resolution**: Implemented string parsing logic to extract contact details from different formats and added support for various contact data structures.
    - **Priority**: High

14. **DOCX Styling Inconsistency**
    - **Status**: Resolved
    - **Description**: The DOCX file lacks proper styling compared to the PDF and HTML outputs. The current implementation doesn't fully leverage the design tokens system for consistent styling.
    - **Impact**: DOCX downloads appeared less professional and didn't match the styling users see in the preview or PDF.
    - **Resolution**: Enhanced design token mapping for DOCX, implemented comprehensive paragraph styling, and created predefined document styles for section headers and bullet points.
    - **Priority**: Medium 