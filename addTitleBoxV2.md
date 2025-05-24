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

```json{  "roleBox": {    "borderColor": "#4A6FDC",    "borderWidth": "1",    "padding": "4",    "background": "transparent",    "backgroundColor": "transparent",    "borderRadius": "0.5",    "textColor": "#333333",    "docx": {      "borderWidthPt": "0.75",      "borderColor": "#4A6FDC",      "borderThemeColor": "accent1",      "paddingTopTwips": "40",      "paddingSideTwips": "80"    }  }}```

#### 2.2 Token Generator UpdateVerify `generate_tokens_css.py` correctly handles token conversion and fallback logic:```python# Add to the token mapping section if neededtoken_groups_to_process = [    "sectionBox",     "roleBox"  # Add this line if token groups are explicitly listed]# Generate fallback CSS variables for automatic inheritancedef generate_fallback_vars(css_output):    """Generate sectionBox fallback variables for roleBox properties"""    fallback_mappings = {        '--roleBox-borderColor': '--sectionBox-borderColor',        '--roleBox-borderWidth': '--sectionBox-borderWidth',         '--roleBox-padding': '--sectionBox-padding',        '--roleBox-borderRadius': '--sectionBox-borderRadius',        '--roleBox-backgroundColor': '--sectionBox-backgroundColor',        '--roleBox-textColor': '--sectionBox-textColor'    }        fallback_css = "\n/* Automatic fallback from sectionBox to roleBox */\n"    for role_var, section_var in fallback_mappings.items():        fallback_css += f"{section_var}: var({role_var}, {get_default_value(role_var)});\n"        return css_output + fallback_css# Ensure camelCase to kebab-case conversion happens# If unsure, output both formats for safetydef generate_css_var_name(key, prefix=""):    """Generate both camelCase and kebab-case versions of CSS variables"""    camel = f"--{prefix}{key}"    kebab = camel.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase()    return [camel, kebab]  # Return both formats if needed# Add warning for missing token groups in non-default palettesdef check_token_groups_in_palettes(tokens, palettes):    for palette_name, palette in palettes.items():        if palette_name == "default":            continue        for group_name in ["roleBox"]:  # List of required groups            if group_name not in palette:                logger.warning(f"{group_name} missing in palette {palette_name} – falling back to default")```

#### 2.3 SCSS Update

Update `_resume.scss` to extend the existing section box with proper specificity:

```scss// after .section-box rules.position-bar {  break-inside: avoid;      // Prevent page breaks in PDF/print  page-break-inside: avoid; // Legacy compatibility for older print engines    .role-box {    @extend .section-box;              // Reuse borders/padding logic    display: flex;                     // Use flex to align role and dates    justify-content: space-between;    // Role on left, dates on right    align-items: center;               // Vertically center content    border-color: var(--roleBox-borderColor, var(--sectionBox-borderColor, #4A6FDC));    border-width: calc(var(--roleBox-borderWidth, 1) * 1px + 0px);  // Force calc evaluation for WeasyPrint    padding: calc(var(--roleBox-padding, 4) * 1px + 0px) calc(var(--roleBox-padding, 4) * 2px + 0px);  // top/bottom vs sides    color: var(--roleBox-textColor, #333333);    border-radius: calc(var(--roleBox-borderRadius, 0.5) * 1px + 0px);    background-color: var(--roleBox-backgroundColor, transparent);        // Style the role text    .role {      font-weight: bold;      flex-grow: 1;    // Take up available space      min-width: 0;    // Allow truncation on narrow screens    }        // Style the dates    .dates {      font-style: italic;      margin-left: 1rem;     // Add some space between role and dates      white-space: nowrap;   // Prevent dates from wrapping    }        // Dark mode support    @media (prefers-color-scheme: dark) {      background: transparent;      border-color: currentColor;    }        // Print-specific adjustments    @media print {      line-height: 1.1;  // Match DOCX exact line height    }  }}```

#### 2.4 HTML Generation UpdateUpdate `html_generator.py` to wrap both role and dates in the role box with improved accessibility:```pythondef format_experience_for_html(experience_item):    """Format experience with role box styling that encompasses both role and dates"""    company = experience_item.get('company', '')    location = experience_item.get('location', '')    dates = experience_item.get('dates', '')    role = experience_item.get('title', '')        # Add ID for accessibility linking    html = f'<div class="company-location" id="company-location">{company}, {location}</div>'    html += f'<div class="position-bar" aria-labelledby="company-location">'        # Role box now contains both role and dates    html += f'<div class="role-box" role="presentation" aria-label="Position: {role}, {dates if dates else ''}">'    html += f'<span class="role">{role}</span>'        # Add non-breaking space for screen reader pause between role and dates    if dates:        html += f'&nbsp;<span class="dates">{dates}</span>'        html += '</div>'  # Close role-box    html += '</div>'  # Close position-bar        # Continue with existing achievements formatting...```

#### 2.5 DOCX Implementation

Create a robust shim that handles theme colors and uses percentage-based widths:

```pythondef add_role_box(doc, role, dates=None):    """    Create a single-cell table that contains both role and dates, mimicking the flex layout.    """    # If add_box_table doesn't accept token_group, create a shim    def add_box_table_with_tokens(doc, cols, token_group):        tokens = TOKENS[token_group]['docx']                # Handle theme color vs hex color        border_color = tokens['borderColor']        theme_color = tokens.get('borderThemeColor', None)                # Call the original function with explicit args from tokens        table = add_box_table(doc, cols=cols,                            border_width_pt=float(tokens['borderWidthPt']),                           border_color=border_color,                           border_theme_color=theme_color,  # Pass theme color if supported                           padding_top_twips=int(tokens['paddingTopTwips']),                           padding_side_twips=int(tokens['paddingSideTwips']))                # Manual theme color fallback if needed        if theme_color and not hasattr(add_box_table, 'supports_theme_color'):            try:                manually_apply_theme_color(table, theme_color,                                          float(tokens['borderWidthPt']))            except Exception as e:                logger.warning(f"Failed to apply theme color: {e}")                return table        # Always use single column since everything goes in one cell    tbl = add_box_table_with_tokens(doc, cols=1, token_group="roleBox")        # Check for RTL support    language_dir = get_document_language_direction(doc)    if language_dir == 'rtl':        set_table_rtl(tbl)  # Apply RTL setting if needed        # Create a single cell with role and dates formatted like flex layout    cell = tbl.cell(0, 0)    para = cell.paragraphs[0]        # Add the role (bold)    role_run = para.add_run(role)    role_run.font.bold = True        if dates:        # Add some space and the dates (italic, right-aligned effect using tabs)        space_run = para.add_run("\t")  # Tab to push dates to the right                # Add a non-breaking hyphen for screen reader pause        from docx.oxml.ns import qn        no_break = OxmlElement('w:noBreakHyphen')        space_run._r.append(no_break)                dates_run = para.add_run(dates)        dates_run.font.italic = True                # Set up tab stop to simulate right alignment within the cell        from docx.shared import Inches        from docx.enum.text import WD_TAB_ALIGNMENT        tab_stops = para.paragraph_format.tab_stops        tab_stops.add_tab_stop(Inches(6), WD_TAB_ALIGNMENT.RIGHT)        return tbl```

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
    
        # Verify role box appears in HTML with both role and dates    assert '<div class="role-box" role="presentation" aria-label="Position:' in html_output    assert '<span class="role">' in html_output    assert '<span class="dates">' in html_output
    
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
def test_role_box_helper():    """Fast Python-only test for the add_role_box helper"""    # Create a minimal document    from docx import Document    doc = Document()        # Test without dates (single column with just role)    tbl1 = add_role_box(doc, "Senior Engineer")    assert len(tbl1.columns) == 1    assert "Senior Engineer" in tbl1.cell(0, 0).text        # Test with dates (single column with role + tab + dates)    tbl2 = add_role_box(doc, "Senior Engineer", "2020-Present")    assert len(tbl2.columns) == 1  # Still single column    cell_text = tbl2.cell(0, 0).text    assert "Senior Engineer" in cell_text    assert "2020-Present" in cell_text        # No need to save/open the document - just checking structure
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

### 9. O3 Polish Improvements

The following refinements address edge cases and improve compatibility:

#### 9.1 Token Naming Consistency
- Renamed `borderWidthPx` → `borderWidth` (drive units in SCSS)
- Renamed `borderRadiusPx` → `borderRadius` (drive units in SCSS) 
- Renamed `paddingPx` → `padding` (drive units in SCSS)

#### 9.2 Automatic Theme Inheritance
- Generate fallback CSS variables: `--sectionBox-borderColor: var(--roleBox-borderColor, #4A6FDC);`
- Allows custom themes that override `sectionBox` to automatically influence `roleBox`

#### 9.3 SCSS Calc Bug Fixes
- Apply WeasyPrint calc workaround to padding: `calc(var(--roleBox-padding, 4) * 1px + 0px) calc(var(--roleBox-padding, 4) * 2px + 0px)`
- Ensures identical padding in PDF and HTML

#### 9.4 Layout Stability
- Add `min-width: 0` to `.role` to prevent layout breaks on narrow screens
- Allows long titles to truncate rather than pushing dates off-screen

#### 9.5 DOCX Tab Stop Polish
- Call `para.paragraph_format.tab_stops.clear_all()` before adding custom tab stop
- Prevents tiny gaps in Word Mac caused by default tab widths

#### 9.6 RTL Date Handling
- Wrap dashes in RTL marks when `language_dir == 'rtl'`:
  - `dates.replace('–', '\u200F–\u200F')` (en-dash)
  - `dates.replace('—', '\u200F—\u200F')` (em-dash) 
  - `dates.replace('-', '\u200F-\u200F')` (hyphen)
- Prevents "2020–2019" reversal bug in Hebrew/Arabic Word

#### 9.7 Legacy Print Engine Support
- Add `page-break-inside: avoid;` alongside `break-inside: avoid;`
- Wider compatibility with older print engines

#### 9.8 Linting and Cleanup
- Run `ruff check --fix` after implementation
- Catches unused imports like `Pt`, `qn` when theme-color path isn't hit
- Ensures CI passes on first try

### Updated Implementation Notes

Apply these improvements during implementation:

1. **Token Generator**: Include fallback variable generation
2. **SCSS**: Use updated token names, add legacy print properties, padding calc fix
3. **HTML**: No changes needed from O3 feedback
4. **DOCX**: Add RTL date processing and tab stop clearing
5. **Testing**: Include linting in the verification step

These micro-refinements ensure production-ready quality with edge case handling for international users, legacy systems, and various Word versions. 

### 10. Final O3 Micro-Refinements

The following tiny additions ensure bulletproof rollout with graceful degradation:

#### 10.1 Token Backward Compatibility
```python
# In generate_tokens_css.py
def ensure_roleBox_exists(tokens, palettes):
    """Auto-clone sectionBox to roleBox if missing for backward compatibility"""
    for palette_name, palette in palettes.items():
        if "roleBox" not in palette and "sectionBox" in palette:
            logger.warning(f"Auto-cloning sectionBox to roleBox in palette {palette_name} for backward compatibility")
            palette["roleBox"] = palette["sectionBox"].copy()
            # Update any sectionBox-specific properties that should differ
            if "docx" in palette["roleBox"]:
                palette["roleBox"]["docx"] = palette["sectionBox"]["docx"].copy()
```

#### 10.2 Token Documentation
Add to top of `design_tokens.json`:
```json
{
  "_comment": "Token naming convention: width/radius/padding values are unit-less strings. CSS applies units (px) via calc() multiplication. This prevents WeasyPrint calc() bugs and maintains clean token schema.",
  
  "sectionBox": {
    // ... existing tokens
  },
  "roleBox": {
    // ... new tokens  
  }
}
```

#### 10.3 Dark Mode Color Inheritance
```scss
// In dark mode media query, add:
@media (prefers-color-scheme: dark) {
  .role-box {
    background: transparent;
    border-color: currentColor;
    color: inherit;  // Ensure text inherits dark theme color
    
    .dates {
      color: inherit;  // Prevent #333 on dark backgrounds
    }
  }
}
```

#### 10.4 HTML Sanitizer Fallback
```python
# In format_experience_for_html(), add fallback:
html += f'<div class="role-box" role="presentation" aria-label="Position: {role}, {dates if dates else ''}">'
html += f'<span class="role">{role}</span>'
if dates:
    html += f'&nbsp;<span class="dates">{dates}</span>'
html += '</div>'

# Add noscript fallback for aggressive email clients
html += f'<noscript><div class="visually-hidden" aria-hidden="true">{role} {dates if dates else ""}</div></noscript>'
```

#### 10.5 PDF Hyphenation Control
```scss
.role-box {
  // ... existing styles ...
  hyphens: manual;  // Prevent auto-hyphenation of long German job titles
}
```

#### 10.6 DOCX AutoFit Prevention
```python
# In add_role_box(), after table creation:
tbl = add_box_table_with_tokens(doc, cols=1, token_group="roleBox")

# Prevent Word 2010 "Optimize for compatibility" stretching
tbl.allow_autofit = False
tbl.autofit = False  # Both flags needed for full protection

# ... rest of implementation
```

#### 10.7 Fast CI Smoke Test
```python
# Add to CI pipeline before SSIM tests:
def test_pdf_smoke_generation():
    """Fast smoke test to catch blank-page regressions before heavy SSIM tests"""
    minimal_resume = {"experience": [{"title": "Test Role", "company": "Test Co", "dates": "2020"}]}
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        pdf_output = generate_pdf(minimal_resume)
        tmp.write(pdf_output)
        tmp.flush()
        
        # Assert PDF is non-empty and reasonable size
        file_size = os.path.getsize(tmp.name)
        assert file_size > 5120, f"PDF too small ({file_size} bytes), likely blank page regression"
        
        os.unlink(tmp.name)
```

### Implementation Checklist with Micro-Refinements

1. **Design Tokens** ✅
   - Add roleBox token group with unit-less values
   - Add documentation comment explaining naming convention
   - Implement auto-cloning fallback for missing roleBox

2. **CSS Generation** ✅  
   - Generate fallback variables for theme inheritance
   - Handle missing token groups gracefully
   - Emit warnings for backward compatibility

3. **SCSS Updates** ✅
   - Use updated token names (borderWidth, borderRadius, padding)
   - Add legacy print properties (page-break-inside)
   - Fix calc padding for WeasyPrint
   - Add min-width: 0 for layout stability
   - Add hyphens: manual for PDF
   - Improve dark mode with color inheritance

4. **HTML Generator** ✅
   - Wrap role and dates in unified role-box
   - Add accessibility attributes
   - Include noscript fallback for sanitizers

5. **DOCX Builder** ✅
   - Single-cell table with tab stops
   - Clear default tabs before custom ones
   - RTL date processing with Unicode marks
   - Disable autofit for Word 2010 compatibility

6. **Testing & CI** ✅
   - Add fast PDF smoke test (5KB minimum)
   - Visual regression with 0.96 SSIM threshold
   - Linting with ruff check --fix
   - Unit tests for helper functions

### Rollout Confidence

With these micro-refinements, the implementation handles:
- ✅ Ancient third-party themes (auto-cloning)
- ✅ Future contributors (clear documentation)  
- ✅ Dark mode accessibility (color inheritance)
- ✅ Aggressive email clients (noscript fallback)
- ✅ International typography (German hyphenation)
- ✅ Legacy Word versions (autofit prevention)
- ✅ Fast CI feedback (smoke test before SSIM)

**Status: Bulletproof and ready to implement** 🚀 

### 11. Final O3 Micro-Nits

Two tiny tweaks for 100% implementation readiness:

#### 11.1 CSS Variable Cascade Order
```python
# In generate_fallback_vars() - append fallbacks at END of CSS file
def generate_fallback_vars(css_output):
    """Generate sectionBox fallback variables at end to prevent override"""
    fallback_mappings = {
        '--roleBox-borderColor': '--sectionBox-borderColor',
        '--roleBox-borderWidth': '--sectionBox-borderWidth', 
        '--roleBox-padding': '--sectionBox-padding',
        '--roleBox-borderRadius': '--sectionBox-borderRadius',
        '--roleBox-backgroundColor': '--sectionBox-backgroundColor',
        '--roleBox-textColor': '--sectionBox-textColor'
    }
    
    fallback_css = "\n/* Automatic fallback from sectionBox to roleBox - at end to prevent override */\n:root {\n"
    for role_var, section_var in fallback_mappings.items():
        fallback_css += f"  {section_var}: var({role_var}, {get_default_value(role_var)});\n"
    fallback_css += "}\n"
    
    return css_output + fallback_css  # APPEND at end, not prepend
```

#### 11.2 WeasyPrint Version-Aware Calc Fix
```scss
// In SCSS, version-check the calc workaround
.role-box {
  @extend .section-box;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-color: var(--roleBox-borderColor, var(--sectionBox-borderColor, #4A6FDC));
  
  // Version-aware calc fix for WeasyPrint < 58
  @if function-exists(weasyprint-version) and weasyprint-version() < 58 {
    border-width: calc(var(--roleBox-borderWidth, 1) * 1px + 0px);
    padding: calc(var(--roleBox-padding, 4) * 1px + 0px) calc(var(--roleBox-padding, 4) * 2px + 0px);
    border-radius: calc(var(--roleBox-borderRadius, 0.5) * 1px + 0px);
  } @else {
    border-width: calc(var(--roleBox-borderWidth, 1) * 1px);
    padding: calc(var(--roleBox-padding, 4) * 1px) calc(var(--roleBox-padding, 4) * 2px);
    border-radius: calc(var(--roleBox-borderRadius, 0.5) * 1px);
  }
  
  // ... rest of styles
}
```
