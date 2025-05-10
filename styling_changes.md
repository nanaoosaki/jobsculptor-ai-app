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