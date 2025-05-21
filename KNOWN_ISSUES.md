# Known Issues

## All issues listed below have been resolved as of [current date].

### DOCX Styling Inconsistencies
**Status**: Resolved

**Description**: 
The DOCX output format had several styling inconsistencies compared to the HTML and PDF outputs:
1. Skills were displayed as bullet points on separate lines rather than as inline text with comma separation
2. Section headers had different spacing and alignment than in HTML/PDF
3. Box styling around section headers was inconsistent with other output formats
4. Job titles and dates were not formatted consistently with HTML/PDF output - titles and dates appeared on separate lines
5. Company and location were not properly right-aligned as in the HTML/PDF output
6. Bullet points had incorrect indentation and styling

**Resolution**:
1. Modified the skills section handling in `utils/docx_builder.py` to format skills as comma-separated text on a single line
2. Enhanced the section header styling in `style_engine.py` to improve alignment and spacing
3. Added paragraph formatting properties in DOCX to better match HTML/PDF appearance
4. Implemented tab-based right-alignment for experience, education, and project sections:
   - Used Word's tab stops feature with right alignment to position elements
   - Created paragraphs with left-aligned content (company/position) and right-aligned content (location/dates)
   - Replaced the previous pipe ("|") separator approach with a cleaner tab-based layout
5. Fixed bullet point formatting with proper indentation and styling

**Impact**: 
- The DOCX output now more closely resembles the HTML and PDF outputs
- Company name appears on the left with location right-aligned on the same line
- Position/title appears on the left with dates right-aligned on the same line
- The unified styling approach maintains a single source of truth while allowing format-specific adaptations

**Technical Details**:
- Used `paragraph.paragraph_format.tab_stops.add_tab_stop(Cm(15), WD_TAB_ALIGNMENT.RIGHT)` for right alignment
- Applied direct styling to individual runs within paragraphs for consistent appearance
- Created separate approaches for HTML/PDF (using CSS flexbox) and DOCX (using tab stops) to achieve the same visual effect

**Priority**: Medium

---

## Other Issues

### New Known Issues

### DOCX Section Header Box Styling Missing
**Status**: Unresolved

**Description**: 
After the DOCX styling refactoring, section header boxes in DOCX output have proper alignment with content, but the box styling (border and/or background color) is not rendering in the output document. This is despite logs indicating successful application of the box styling:
```
INFO:style_engine:Successfully applied DOCX section header box styling
```

**Impact**: 
- The DOCX output lacks the visual distinction of boxed section headers that are present in the HTML/PDF outputs
- This reduces the consistency across different output formats of the resume
- The professional appearance of the document is affected with less visual hierarchy

**Root Cause Analysis**:
The issue appears to be related to how paragraph border and background styling is applied at the XML level in the DOCX document. Several possible causes include:
1. Incompatible XML formatting approach for Word rendering
2. Style conflicts or overrides occurring during document generation
3. Incorrect specification of border/background color values for Word

**Next Steps**: 
1. Generate test documents with various section header styling approaches to identify working methods
2. Inspect the XML structure of the generated DOCX to pinpoint why the styling isn't rendering
3. Test alternative approaches including:
   - Table-based section headers (single-cell tables with borders/background)
   - Shape-based styling (inserting shapes behind text)
   - Different XML formatting approaches more compatible with Word

**Resolution Strategy**:
Work will be tracked in the continuation of the DOCX styling refactoring project (Phase 5 and 6) with an emphasis on fixing the section header box styling while maintaining the alignment improvements already achieved.

**Priority**: Medium 

## DOCX Section Header Styling and Spacing

### Key Insights for Section Header Box Styling

1. **Line Rule and Line Height Matter**: 
   - For optimal section header box height, use `lineRule="auto"` with `line="276"` (13.8pt)
   - Using `exact` line rule with low values can cause text to wrap unexpectedly
   - Using `auto` without a line value doesn't give consistent results

2. **Border Padding Control**:
   - Always use exact twip values for border padding: `w:space="20"` equals 1pt
   - Apply borders to all four sides consistently for a clean box

3. **Spacing Between Sections**:
   - The main cause of unwanted spacing is empty paragraphs between sections
   - Use the `tighten_before_headers` function to find and set `space_after=0` on all paragraphs preceding section headers
   - Apply both API-level changes (`paragraph_format.space_after = Pt(0)`) and XML-level changes for maximum compatibility

4. **Style vs. Direct Formatting**:
   - Create a named style like `BoxedHeading2` based on `Heading 2` for best accessibility
   - Direct paragraph borders offer better copy-paste behavior than table-based approaches
   - Set outline level explicitly for proper TOC generation and screen reader accessibility

5. **Validation Best Practices**:
   - Always validate both the box height and inter-section spacing aspects
   - Test with single-line headers and multi-line headers to ensure consistent appearance
   - Check border padding and spacing values directly in the XML for verification 