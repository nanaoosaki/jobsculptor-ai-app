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
- Fixed tab stop positions don't adapt to different page dimensions and margin settings
- Different parts of the code were using different tab stop positions

### Implementation Solution

Building on the successful style-first approach used for left alignment, we implemented a more advanced solution for right alignment:

1. **Dynamic Tab Stop Calculation**
   - Replaced the static tab stop position with dynamic calculation based on document properties
   - Extracted actual page width and margins from the document section
   - Calculated content width as: `page_width - left_margin - right_margin`
   - Positioned the tab stop at this precise width to align with the right margin

2. **Unit Conversion**
   - Properly converted internal EMU measurements (1/914400 of an inch) to centimeters
   - Used formula: `tab_position_cm = content_width_emu / 360000.0`

3. **Error Handling**
   - Added fallback for unusual document dimensions
   - Implemented validation to ensure positive tab stop positions
   - Added detailed logging for debugging

**Results:**
- Dates and locations now align perfectly with the right margin
- Alignment is consistent regardless of content length
- Solution adapts to different page sizes and margin settings

**Lessons Learned:**
- Document properties provide more reliable positioning than fixed measurements
- Direct calculation from page dimensions ensures consistent alignment
- Dynamic approaches are more maintainable than hard-coded values

This implementation established a robust solution for right alignment that complements our left alignment fixes, resulting in a professionally formatted document with consistent alignment throughout.

### Current Status

With this fix, all alignment issues in the DOCX output have been resolved:
1. Left alignment is consistent across all content elements (left edge)
2. Right alignment is consistent for all dates and locations (right edge)
3. The style-first approach ensures reliable and customizable formatting

These improvements create a professional, polished appearance for the DOCX output that matches the quality of the HTML and PDF outputs.

## Unified Margin Control in DOCX Output (2025-07-XX)

### Current Implementation Analysis

We've successfully implemented two different approaches for controlling alignment in DOCX:

1. **Left Alignment Control**:
   - Uses style-based approach through custom styles (`MR_SectionHeader`, `MR_Content`, etc.)
   - All left indentation controlled by design tokens:
     ```json
     "docx-section-header-indent-cm": "0",
     "docx-company-name-indent-cm": "0",
     "docx-role-description-indent-cm": "0",
     "docx-bullet-left-indent-cm": "0"
     ```
   - Applied consistently through StyleEngine to all paragraph styles

2. **Right Alignment Control**:
   - Uses dynamic calculation based on page dimensions
   - Tab stops positioned relative to page width, margins, and content area
   - Implemented in `format_right_aligned_pair` function
   - Calculates position using:
     ```python
     page_width_emu = section.page_width
     left_margin_emu = section.left_margin
     right_margin_emu = section.right_margin
     content_width = page_width_emu - (left_margin_emu + right_margin_emu)
     ```

### Unified Margin Control Strategy

To make future margin adjustments easier, we can implement a unified approach:

1. **Centralized Margin Control**:
   Add new design tokens for global margin control:
   ```json
   {
     "docx-global-left-margin-cm": "2.0",
     "docx-global-right-margin-cm": "2.0"
   }
   ```

2. **Implementation Points**:
   - **Left Alignment**: All left indentation tokens would be calculated relative to `docx-global-left-margin-cm`
   - **Right Alignment**: Tab stop calculation would use `docx-global-right-margin-cm` instead of extracting from section properties
   - **Page Setup**: Section margins would be set using these global values

3. **Adjustment Process**:
   To adjust margins, simply update the global margin tokens and:
   1. Run `python tools/generate_tokens.py` to update style definitions
   2. Restart the Flask server
   3. Generate a new document to verify changes

### Benefits of This Approach

1. **Single Source of Truth**: 
   - All margin-related values controlled by two tokens
   - No need to modify multiple style definitions or code paths

2. **Consistent Behavior**:
   - Left and right margins will always be symmetrical
   - All content elements will respect the same margins

3. **Easy Maintenance**:
   - Simple token updates instead of code changes
   - No need to understand the underlying DOCX structure

4. **Predictable Results**:
   - Changes will affect all document elements consistently
   - No risk of misaligned elements

### Implementation Checklist

When implementing margin changes:

1. **Update Design Tokens**:
   - Modify `docx-global-left-margin-cm` and `docx-global-right-margin-cm` in `design_tokens.json`

2. **Regenerate Styles**:
   ```bash
   python tools/generate_tokens.py
   ```

3. **Restart Services**:
   - Restart Flask server to apply changes

4. **Verify Changes**:
   - Generate test document
   - Check all elements respect new margins:
     - Section headers
     - Company/role information
     - Bullet points
     - Right-aligned dates/locations
     - Professional summary
     - Skills sections

5. **Document Updates**:
   - Record changes in version history
   - Update any relevant documentation

This unified approach makes margin adjustments straightforward and maintainable, without requiring deep knowledge of the DOCX formatting architecture.

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