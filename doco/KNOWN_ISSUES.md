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
**Status**: Unresolved

**Description**: 
The section header box currently has a blue fill, but it should only have a blue outline with a transparent fill.

**Impact**: 
- The current design does not match the intended visual style.

**Next Steps**: 
1. Modify the CSS to change the section header box to have a transparent fill and a blue outline.
2. Verify the changes in both the HTML preview and PDF output.

**Priority**: Medium

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

### Margin Size Issue
**Status**: Unresolved

**Description**: 
The margin set to 1 inch is equivalent to approximately 2.54 cm, which is larger than expected. It needs to be reduced to 1 cm.

**Impact**: 
- The large margin reduces the amount of content visible on each page.

**Next Steps**: 
1. Adjust the margin size in the SCSS files to 1 cm.
2. Verify the changes in both the HTML preview and PDF output.

**Priority**: Medium

### Section Box Height Issue
**Status**: Unresolved

**Description**: 
The section box height needs to be reduced further, as previous adjustments did not achieve the desired effect.

**Impact**: 
- The layout appears unbalanced, with excessive vertical space in section headers.

**Next Steps**: 
1. Further reduce the section box height in the SCSS files.
2. Verify the changes in both the HTML preview and PDF output.

**Priority**: Medium

### Bullet Point Length and Symbol Issue
**Status**: Unresolved

**Description**: 
Bullet points are too long, and the bullet point symbol is missing.

**Impact**: 
- The readability and professional appearance of the resume are affected.

**Next Steps**: 
1. Adjust the bullet point length in the SCSS files.
2. Ensure the bullet point symbol is correctly displayed.
3. Verify the changes in both the HTML preview and PDF output.

**Priority**: Medium

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