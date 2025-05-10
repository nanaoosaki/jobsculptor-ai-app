# Implementation Plan for Styling Changes

## DOCX Styling Refactoring - 2025-05-09

### Comprehensive Alignment System Implementation

A comprehensive refactoring of the DOCX styling system was implemented to address the misalignment between section headers, content text, and bullet points. The approach focused on creating a consistent alignment system with a single source of truth for all indent values.

**Key Components**:
1. **Design Token System**: Added DOCX-specific tokens in `design_tokens.json`:
   - `docx-section-header-indent-cm`: 0 (aligns with left margin)
   - `docx-company-name-indent-cm`: 0.5 (consistent indent for company information)
   - `docx-role-description-indent-cm`: 0.5 (matches company indent)
   - `docx-bullet-left-indent-cm`: 0.5 (aligns with content)
   - `docx-bullet-hanging-indent-cm`: 0.5 (creates proper bullet indent)

2. **Enhanced Style Engine**: 
   - Created a unified `StyleEngine` with structured token management
   - Implemented custom style generation with XML-level formatting
   - Added style cleanup mechanisms to prevent conflicts

3. **DOCX Builder Updates**:
   - Rewritten paragraph creation functions to apply consistent formatting
   - Implemented proper tab-based alignment for right-aligned elements
   - Applied direct formatting after style application to ensure consistency
   - Added XML-level formatting to lock in formatting values

### Current Status

The refactoring successfully achieved consistent alignment between section headers, content text, and bullet points by:
1. Using a consistent left indent value (0.5cm) for all content
2. Aligning section headers with the left margin (0cm indent)
3. Ensuring bullet points use a consistent indentation and hanging indent system
4. Applying formatting at multiple levels to ensure reliable rendering

**However, a new issue emerged**: Despite the improved alignment, the section header box styling (border and/or background color) is not visible in the generated DOCX output. The logs indicate successful application:
```
INFO:style_engine:Successfully applied DOCX section header box styling
```

This suggests the XML-level border and background styling may be incompatible with how Word renders these properties, or the styles are being overridden during document generation.

### Next Steps

To complete the DOCX styling refactoring, we need to:

1. **Investigate Box Styling Issue**: 
   - Generate test documents with various section header styling approaches
   - Inspect the XML structure of generated documents to identify why the styling isn't rendering
   - Test alternative approaches like table-based headers or different XML formatting

2. **Verify Full Solution**:
   - Once box styling is fixed, verify it maintains the alignment improvements
   - Test with real resume data across various content types
   - Document the final approach for consistency across all output formats

## DOCX Right Alignment Fix - 2025-05-10

### Right-Aligned Text Inconsistency

After implementing the left alignment fixes, an issue with right-aligned content (dates and locations) was observed. These elements showed inconsistent positioning, with some appearing at different positions than others, creating an unprofessional appearance.

**Root Cause:**
- Right-aligned elements in DOCX files are implemented using tab stops
- The tab stop position was not consistently defined through a dedicated design token
- Different parts of the code were using different tab stop positions

### Implementation Solution

Building on the successful style-first approach used for left alignment, we implemented a consistent solution for right alignment:

1. **New Design Token:**
   - Added `docx-right-tab-stop-position-cm`: `13` to `design_tokens.json`
   - This centralizes the control of right-aligned tab stops in a single place

2. **Updated Tab Stop Handling:**
   - Modified `format_right_aligned_pair` function to use the new design token directly:
   ```python
   # Get the tab stop position from the new dedicated design token
   tokens = StyleEngine.load_tokens()
   tab_position = float(tokens.get("docx-right-tab-stop-position-cm", "13"))
   
   # Remove any existing tab stops to prevent conflicts
   para.paragraph_format.tab_stops.clear_all()
   
   # Add the new tab stop
   para.paragraph_format.tab_stops.add_tab_stop(Cm(tab_position), WD_TAB_ALIGNMENT.RIGHT)
   ```

3. **Eliminated Legacy Tab Stop Handling:**
   - Removed the old code that used the `tabStopPosition` from `docx_styles["global"]`
   - Updated `generate_tokens.py` to use our new token in `docx_styles`

4. **Verified Results:**
   - Created a test script `test_right_alignment.py` to generate sample content
   - Verified that dates and locations consistently align at the same position

This implementation maintains the same style-first methodology used throughout the DOCX styling refactoring, ensuring that all formatting values are driven by centralized design tokens for consistency and easy customization.

### Current Status

With this fix, all alignment issues in the DOCX output have been resolved:
1. Left alignment is consistent across all content elements (left edge)
2. Right alignment is consistent for all dates and locations (right edge)
3. The style-first approach ensures reliable and customizable formatting

These improvements create a professional, polished appearance for the DOCX output that matches the quality of the HTML and PDF outputs.

## Revised Workflow for Styling Changes

| Step | Action | Command / Tool |
|------|--------|----------------|
| 1 | Edit tokens or SCSS | Edit `static/scss/_resume.scss` or `design_tokens.json` |
| 2 | Re-generate tokens | `python tools/generate_tokens.py` |
| 3 | Build CSS | `sass static/scss/preview.scss static/css/preview.css` <br> `sass static/scss/print.scss static/css/print.css` |
| 4 | **Restart Flask dev server** | `Ctrl-C` then `python app.py` |
| 5 | Hard refresh browser | `Ctrl+Shift+R` |
| 6 | Verify all output formats | Check HTML preview, PDF, and DOCX outputs |

**IMPORTANT**: All output formats (HTML, PDF, DOCX) should be checked after making styling changes, as they may behave differently despite using the same source tokens. 