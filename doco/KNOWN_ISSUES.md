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

**Impact**: 
- The visual appearance of the resume was affected, making it look unprofessional.

**Resolution**: 
- The issue has been resolved by refining the cleaning process and ensuring proper encoding.

**Priority**: Medium

### u2022 Character Issue
**Status**: Unresolved

**Description**: 
The 'u2022' character is appearing in the experience section, causing confusion and affecting the visual appearance of the resume.

**Impact**: 
- The presence of the character makes the resume look unprofessional and is difficult to debug.

**Next Steps**: 
1. Investigate the source of the 'u2022' character in the resume content.
2. Ensure proper encoding and character handling in the HTML and PDF generation.

**Priority**: High

### Section Header Box Width
**Status**: Unresolved

**Description**: 
The section header box is too wide, leaving excessive space on either side.

**Impact**: 
- The layout appears unbalanced, with wasted space around section headers.

**Next Steps**: 
1. Adjust the CSS to reduce the width of the section header box.
2. Ensure the layout is visually appealing and space-efficient.

**Priority**: Medium

### Section Header Box Fill
**Status**: Resolved

**Description**: 
The section header box had a blue fill, but it should only have a blue outline with a transparent fill.

**Impact**: 
- The current design did not match the intended visual style.

**Resolution**: 
- The CSS was modified to change the section header box to have a transparent fill and a blue outline.

**Priority**: Medium

### Missing Contact Section in HTML Preview and PDF
**Status**: Unresolved

**Description**: 
The contact section is missing in both the HTML preview and the PDF output.

**Impact**: 
- Important contact information is not displayed, affecting the completeness of the resume.

**Next Steps**: 
1. Investigate the data flow to ensure the contact section is correctly parsed and included.
2. Verify the HTML and PDF generation processes to ensure the contact section is not omitted.

**Priority**: High

### Remove 'User Resume Parsed (LLM)' Text
**Status**: Unresolved

**Description**: 
The text 'User Resume Parsed (LLM)' is displayed in the user resume parsed component, which is unnecessary and should be removed.

**Impact**: 
- The text clutters the user interface and may confuse users.

**Next Steps**: 
1. Identify the component responsible for displaying this text.
2. Modify the component to remove the unnecessary text.

**Priority**: Medium

---

## Other Issues

All known issues have been resolved. If new issues arise, they will be documented here. 