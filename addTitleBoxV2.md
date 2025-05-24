# Implementation Plan for Role and Title Box

This document outlines the implementation plan for adding a background box to role and title lines in resumes, similar to section headers but with distinct styling. The implementation will ensure consistency across HTML, PDF, and DOCX outputs.

## Current Implementation Analysis

### HTML/PDF Section Header Box
- Section headers use `<div class="section-box">` wrappers
- Styled through SCSS with design tokens 
- The styling uses `display: block` with `width: auto`
- Box styling includes border, padding, and text formatting
- WeasyPrint converts the HTML to PDF, maintaining styling

### DOCX Section Header Box
- Uses a table-based approach with single-cell tables
- Custom `HeaderBoxH2` style based on Normal (not Heading 2)
- Asymmetric cell margins (less on top) for optimal spacing
- Top vertical alignment to prevent excess space
- Controlled through the `word_styles` package

## Revised Implementation Plan

### 1. What to Keep As-Is

| Component | Decision | Rationale |
|-----------|----------|-----------|
| Existing section-header helpers | ✅ Keep unchanged | Already stable in all three formats |
| Design-token → CSS generator | ✅ Keep unchanged | Works well, we'll only add new tokens |
| HTML structure for company/location/dates | ✅ Keep unchanged | No regression risk |

### 2. Changes Needed

#### 2.1 Design Tokens

Add the following tokens to `design_tokens.json`, ensuring all values are strings:

```json
{
  "roleBox": {
    "borderColor": "#4A6FDC",
    "borderWidthPx": "1",
    "paddingPx": "4",
    "background": "transparent",
    "backgroundColor": "transparent",
    "borderRadiusPx": "0.5",
    "textColor": "#333333",

    "docx": {
      "borderWidthPt": "0.75",
      "borderColor": "#4A6FDC",
      "borderThemeColor": "accent1",
      "paddingTopTwips": "40",
      "paddingSideTwips": "80"
    }
  }
}
```

#### 2.2 Token Generator Update

Verify `generate_tokens_css.py` correctly handles token conversion:

```python
# Add to the token mapping section if needed
token_groups_to_process = [
    "sectionBox", 
    "roleBox"  # Add this line if token groups are explicitly listed
]

# Ensure camelCase to kebab-case conversion happens
# If unsure, output both formats for safety
def generate_css_var_name(key, prefix=""):
    """Generate both camelCase and kebab-case versions of CSS variables"""
    camel = f"--{prefix}{key}"
    kebab = camel.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase()
    return [camel, kebab]  # Return both formats if needed

# Add warning for missing token groups in non-default palettes
def check_token_groups_in_palettes(tokens, palettes):
    for palette_name, palette in palettes.items():
        if palette_name == "default":
            continue
        for group_name in ["roleBox"]:  # List of required groups
            if group_name not in palette:
                logger.warning(f"{group_name} missing in palette {palette_name} – falling back to default")
```

#### 2.3 SCSS Update

Update `_resume.scss` to extend the existing section box with proper specificity:

```scss
// after .section-box rules
.position-bar {
  gap: 0.25rem;  // Add spacing between role box and dates
  break-inside: avoid;  // Prevent page breaks in PDF/print
  
  .role-box {
    @extend .section-box;              // Reuse borders/padding logic
    display: inline-block;             // Allow it to fit content
    border-color: var(--roleBox-borderColor, var(--sectionBox-borderColor, #4A6FDC));
    border-width: calc(var(--roleBox-borderWidthPx, 1) * 1px + 0px);  // Force calc evaluation for WeasyPrint
    padding: calc(var(--roleBox-paddingPx, 4) * 1px + 0px);
    color: var(--roleBox-textColor, #333333);
    border-radius: calc(var(--roleBox-borderRadiusPx, 0.5) * 1px + 0px);
    background-color: var(--roleBox-backgroundColor, transparent);
    
    // Dark mode support
    @media (prefers-color-scheme: dark) {
      background: transparent;
      border-color: currentColor;
    }
    
    // Print-specific adjustments
    @media print {
      line-height: 1.1;  // Match DOCX exact line height
    }
  }
}
```

#### 2.4 HTML Generation Update

Update `html_generator.py` to add a role box span with improved accessibility:

```python
def format_experience_for_html(experience_item):
    """Format experience with role box styling"""
    company = experience_item.get('company', '')
    location = experience_item.get('location', '')
    dates = experience_item.get('dates', '')
    role = experience_item.get('title', '')
    
    # Add ID for accessibility linking
    html = f'<div class="company-location" id="company-location">{company}, {location}</div>'
    html += f'<div class="position-bar" aria-labelledby="company-location">'
    html += f'<span class="role-box" role="presentation" aria-label="Job title: {role}">{role}</span>'
    
    # Add non-breaking space for screen reader pause
    html += f'&nbsp;<span class="dates">{dates}</span>' if dates else ''
    html += '</div>'
    
    # Continue with existing achievements formatting...
```

#### 2.5 DOCX Implementation

Create a robust shim that handles theme colors and uses percentage-based widths:

```python
def add_role_box(doc, role, dates=None):
    """
    Reuse the header-box table helper with proper handling of theme colors and widths.
    """
    # If add_box_table doesn't accept token_group, create a shim
    def add_box_table_with_tokens(doc, cols, token_group):
        tokens = TOKENS[token_group]['docx']
        
        # Handle theme color vs hex color
        border_color = tokens['borderColor']
        theme_color = tokens.get('borderThemeColor', None)
        
        # Call the original function with explicit args from tokens
        table = add_box_table(doc, cols=cols, 
                           border_width_pt=float(tokens['borderWidthPt']),
                           border_color=border_color,
                           border_theme_color=theme_color,  # Pass theme color if supported
                           padding_top_twips=int(tokens['paddingTopTwips']),
                           padding_side_twips=int(tokens['paddingSideTwips']))
        
        # Manual theme color fallback if needed
        if theme_color and not hasattr(add_box_table, 'supports_theme_color'):
            try:
                manually_apply_theme_color(table, theme_color, 
                                         float(tokens['borderWidthPt']))
            except Exception as e:
                logger.warning(f"Failed to apply theme color: {e}")
        
        return table
    
    # Use the shim or the original function depending on implementation
    cols = 2 if dates else 1
    tbl = add_box_table_with_tokens(doc, cols=cols, token_group="roleBox")
    
    # Apply percentage-based column widths instead of fixed inches
    if cols == 2:
        # Use the preferred width percentage helper if available
        if hasattr(doc, 'set_preferred_width_percent'):
            doc.set_preferred_width_percent(tbl.columns[0], 70)
            doc.set_preferred_width_percent(tbl.columns[1], 30)
        else:
            # Fallback to direct width setting
            from docx.shared import Inches
            tbl.columns[0].width = Inches(4.5)  # Role column
            tbl.columns[1].width = Inches(2)    # Dates column
    
    # Check for RTL support
    language_dir = get_document_language_direction(doc)
    if language_dir == 'rtl':
        set_table_rtl(tbl)  # Apply RTL setting if needed
    
    _fill_cell(tbl.cell(0, 0), role, bold=True)
    
    if dates:
        # Add a non-breaking hyphen for screen reader pause
        from docx.oxml.ns import qn
        para = tbl.cell(0, 1).paragraphs[0]
        
        # Add text with proper formatting
        run = para.add_run()
        run.font.italic = True
        
        # Insert non-breaking hyphen before dates for screen reader pause
        no_break = OxmlElement('w:noBreakHyphen')
        run._r.append(no_break)
        
        run.text = dates
        para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    return tbl

def set_table_rtl(table):
    """Set the table to RTL mode for right-to-left languages"""
    for row in table.rows:
        # Add the bidiVisual property to the row properties
        row_pr = row._tr.get_or_add_trPr()
        bidi = OxmlElement('w:bidiVisual')
        row_pr.append(bidi)

def manually_apply_theme_color(table, theme_color, border_width_pt):
    """Manually apply theme color to table borders if the helper doesn't support it"""
    from docx.oxml.ns import qn
    from docx.shared import Pt
    
    # Convert point size to eighth points (Word's unit)
    sz_val = str(int(border_width_pt * 8))
    
    # Get table properties
    tbl_pr = table._tbl.get_or_add_tblPr()
    
    # Get or create border properties
    borders = OxmlElement('w:tblBorders')
    
    # Create border elements for all sides
    for side in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{side}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), sz_val)
        border.set(qn('w:themeColor'), theme_color)
        borders.append(border)
    
    # Replace existing borders
    old_borders = tbl_pr.find(qn('w:tblBorders'))
    if old_borders is not None:
        tbl_pr.remove(old_borders)
    
    tbl_pr.append(borders)
```

### 3. Print Stylesheet Check

Ensure `print.scss` imports the resume styles:

```scss
// In print.scss - add if missing
@use 'resume';
```

### 4. Unit Testing

Add both visual regression and fast Python-only tests:

```python
def test_role_box_styling():
    """Test that role title appears in a box across all output formats"""
    # Create a test resume with a single experience entry
    test_resume = create_test_resume_with_role()
    
    # Generate outputs in all three formats
    html_output = generate_html_preview(test_resume)
    pdf_output = generate_pdf(test_resume)
    docx_output = generate_docx(test_resume)
    
    # Verify role box appears in HTML
    assert '<span class="role-box" role="presentation" aria-label="Job title:' in html_output
    
    # For PDF/DOCX, use visual comparison with previous golden images
    # Set SSIM threshold to 0.96 to allow for minor anti-aliasing variations
    compare_with_golden_image("role_box_pdf", pdf_output, similarity_threshold=0.96)
    compare_with_golden_image("role_box_docx_word", docx_output, similarity_threshold=0.96)
    compare_with_golden_image("role_box_docx_libreoffice", docx_output, similarity_threshold=0.96)
    
    # Store outputs as snapshots for future comparison
    save_snapshot("role_box_html", html_output)
    save_snapshot("role_box_pdf", pdf_output)
    save_snapshot("role_box_docx", docx_output)
```

```python
def test_role_box_helper():
    """Fast Python-only test for the add_role_box helper"""
    # Create a minimal document
    from docx import Document
    doc = Document()
    
    # Test without dates
    tbl1 = add_role_box(doc, "Senior Engineer")
    assert len(tbl1.columns) == 1
    assert tbl1.cell(0, 0).text == "Senior Engineer"
    
    # Test with dates
    tbl2 = add_role_box(doc, "Senior Engineer", "2020-Present")
    assert len(tbl2.columns) == 2
    assert tbl2.cell(0, 0).text == "Senior Engineer"
    assert "2020-Present" in tbl2.cell(0, 1).text
    
    # No need to save/open the document - just checking structure
```

### 5. Integration Plan

1. **Update Design Tokens**
   - Add the `roleBox` token group to `design_tokens.json` with string values
   - Add background and borderRadius tokens
   - Run: `python tools/generate_tokens_css.py`
   - Verify CSS variables are generated correctly with both camelCase and kebab-case if needed
   - Add warning for missing token groups in non-default palettes

2. **Update SCSS**
   - Add the `.role-box` style with proper specificity
   - Add gap to `.position-bar`
   - Add fallback values for all CSS variables
   - Add `+ 0px` to all calc() expressions for WeasyPrint
   - Add `break-inside: avoid` to prevent page breaks
   - Add dark mode media query
   - Add print media query with line-height
   - Add border-radius from tokens
   - Verify that `print.scss` imports `_resume.scss`
   - Run: `sass static/scss/preview.scss static/css/preview.css`
   - Run: `sass static/scss/print.scss static/css/print.css`

3. **Update HTML Generator**
   - Modify `format_experience_for_html()` to add the role box span
   - Replace `role="text"` with `role="presentation"` and `aria-label`
   - Add non-breaking space before dates for screen reader pause
   - Add ID to company-location for accessibility
   - Add aria-labelledby to position-bar

4. **Update DOCX Builder**
   - Add the `add_role_box()` helper with theme color handling
   - Add manual theme color fallback mechanism
   - Add percentage-based column width control
   - Add non-breaking hyphen for screen reader pause
   - Add RTL support
   - Update experience entry generation to use the helper

5. **Update CI Configuration**
   - Add `roleBox` token hash to the Sass-compile cache key
   - Update visual test SSIM threshold to 0.96

6. **Update Documentation**
   - Add to `CHANGELOG.md`: "NEW token group `roleBox`; no breaking change, but custom themes must add it or the role title falls back to section box styles. If `roleBox` is absent we now fall back to `sectionBox` styles."

7. **Restart Flask Server**
   - Run: `python app.py`

8. **Test Across All Formats**
   - Verify HTML preview, PDF, and DOCX outputs

### 6. Risk Mitigation

| Previous Risk | How It's Addressed |
|---------------|-------------------|
| Global `all: unset` nuking styles | No global resets used; extending existing styles instead |
| New wrapper `<div>` disrupting layout | Using inline `<span>` that fits within existing flex layout |
| Missing SCSS variables in print.css | Explicitly checking print.scss imports and adding fallback values |
| DOCX style duplication | Creating a shim with proper type conversion and theme color handling |
| Column width inconsistency | Using percentage-based widths instead of fixed inches |
| Dark mode compatibility | Adding specific dark mode media query |
| PDF rendering issues | Adding calc workaround for WeasyPrint and border-radius |
| RTL support | Adding bidiVisual property for right-to-left languages |
| Accessibility | Improving ARIA attributes and adding pauses for screen readers |
| Missing tokens in custom themes | Adding fallbacks and warnings to handle missing tokens gracefully |
| PDF page breaks | Adding break-inside: avoid to prevent splitting across pages |
| WeasyPrint calc bug | Adding "+ 0px" to force evaluation of calc expressions |
| CI caching issues | Updating cache keys to prevent stale builds |

### 7. Testing and Verification

1. **Visual Comparison**
   - Ensure only the role title line changes
   - Verify spacing and alignment remain consistent
   - Test in both light and dark mode

2. **Cross-Format Testing**
   - Verify HTML preview looks correct
   - Confirm PDF export matches the preview
   - Validate DOCX format looks consistent with other outputs
   - Test with RTL language setting if applicable

3. **Edge Cases**
   - Test with very long role titles
   - Test with missing location or dates
   - Test with multiple experience entries
   - Test with different page sizes (A4/Letter)
   - Test with custom themes that might be missing the roleBox token group

4. **Accessibility Testing**
   - Verify screen reader behavior
   - Check that role presentation and aria-label work correctly
   - Confirm that pauses between elements improve readability

### 8. Deployment Approach

1. Start with a clean branch from the last known good commit
2. Apply the changes in order:
   - Design tokens with string values, including background and borderRadius
   - Token generator update with warnings for missing tokens
   - SCSS extension with fallbacks, calc fixes, and print safeguards
   - HTML generator with accessibility improvements and screen reader pauses
   - DOCX builder with theme color handling, percentage widths, and RTL support
   - CI configuration updates
   - Documentation updates in CHANGELOG.md
3. Run visual regression tests with 0.96 SSIM threshold
4. Run fast Python-only unit tests
5. Deploy when verified

This comprehensive approach addresses all technical edge cases while maintaining the core simplicity of extending existing stable components. It ensures consistent styling across all output formats while considering accessibility, internationalization, and different rendering environments. 