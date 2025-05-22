# Implementation Plan: Job Title Boxes (Task 3)

## Critical Implementation Issues Encountered

### Styling Regression Problems

After implementing PR-1 (HTML/CSS + token changes), several critical styling issues were observed:

1. **HTML Preview Regressions**:
   - Margins completely removed from HTML preview
   - Section header boxes no longer displaying
   - Overall spacing and layout compromised

2. **PDF Download Regressions**:
   - Contact section no longer centered
   - Section header boxes missing entirely
   - Font styling and colors lost
   - Bullet points misaligned
   - Significant visual degradation compared to original styling

3. **Root Causes**:
   - CSS variable implementation approach broke existing styling
   - Converting _tokens.scss to use CSS variables (var(--name)) instead of direct SCSS variables
   - Insufficient testing of the cascading effects across different output formats
   - Potential build process issues with CSS generation for both preview and print stylesheets

4. **Working Components**:
   - DOCX implementation remains intact (as it wasn't modified in PR-1)
   - New job title box styling applied correctly, but at the expense of all other styling

### Immediate Rollback Plan

1. Revert changes to _tokens.scss file to restore direct variable definitions instead of CSS variables
2. Keep the job title box styling in _resume.scss but modify it to use direct SCSS variables
3. Restore the original CSS generation process that produced working stylesheets
4. Test thoroughly across all formats before proceeding with any further changes

### Revised Approach for PR-1

Instead of completely converting to CSS variables, a phased approach should be used:

1. Add job title box styling using the existing variable structure without changing the core variable system
2. Create jobTitleBox SCSS variables mirroring the token structure but using existing SCSS approach
3. Implement progressive enhancement by adding job title box styles without modifying the core styling architecture
4. Only proceed with CSS variable conversion as a separate, dedicated refactoring task after thorough testing

### Lessons Learned

1. **Testing**: Changes to core styling architecture require extensive testing across all output formats
2. **Incremental Changes**: Styling system changes should be made incrementally rather than all at once
3. **Fallbacks**: Always implement fallback mechanisms when changing foundational styling approaches
4. **Separation of Concerns**: Keep feature additions (job title box) separate from architecture changes (CSS variables)

## Overview

This document outlines the implementation plan for Task 3 from the styling improvements roadmap: **Job Title Boxes across all formats (HTML, PDF, DOCX)**.

The goal is to apply consistent box styling to job titles in the position bar, creating visual emphasis similar to section headers but with different styling to maintain hierarchy. This styling must be consistent across all export formats.

## Current State Analysis

### Existing Components

1. **Design Tokens**: The `design_tokens.json` file already includes a `jobTitleBox` section with styling parameters for both web and DOCX formats.

2. **Position Bar Implementation**:
   - HTML/CSS: Currently implemented as a div with class "position-bar" in `_resume.scss` 
   - DOCX: Implemented through formatting in `docx_builder.py` with no special styling

3. **Related Styling**:
   - Section header boxes already implemented across all formats
   - Section header DOCX implementation uses table-based approach for reliable spacing

### Gaps

1. The job title (position) within the position bar does not have box styling in any format
2. No implementation exists to apply the jobTitleBox tokens to the position element
3. DOCX implementation needs special handling similar to section headers
4. **Missing Tokens**: `backgroundColor` is missing from design tokens but required for implementation
5. **Missing Utilities**: `_set_cell_background` helper function needed for DOCX implementation
6. **Unit Handling**: Need consistent unit handling between CSS and DOCX formats
7. **Edge Case Support**: Need handling for special cases like missing dates, very long titles, and emoji characters
8. **Accessibility**: Need proper ARIA attributes for screen readers
9. **Internationalization**: Need RTL language support for date fields
10. **Token Deprecation**: Need mechanism for gracefully retiring tokens in the future
11. **Cross-Platform Testing**: Need broader validation for Word rendering across platforms

## Implementation Approach

We'll implement job title boxes using a multi-stage approach:

### 1. Design Token Updates

1. **Add Missing Token Properties**:
   - Add `backgroundColor` to the `jobTitleBox` section in design_tokens.json
   - Consider format-specific font properties using sub-objects
   - Add optional `fontSizePt` override for DOCX format
   - Add `fontFamily` token for consistent typography across formats
   - **Add Token Version**: Include `"tokensVersion": "2025-05-xx"` for validation
   - **Add Deprecation Field**: Include `"deprecated": false` for each top-level token object

2. **Add Default Fallbacks**:
   - Ensure backward compatibility with sensible defaults for all required properties
   - Add fallbacks for borderRadius and padding to prevent issues with legacy JSONs

3. **Add Unit Conversion Utility**:
   - Create a `twip(width_str, base_px=16)` utility to handle unit conversions between CSS and DOCX
   - Raise proper `ValueError` exceptions for invalid units instead of returning zero
   - Strip units correctly when feeding values to DOCX implementation

### 2. HTML/CSS Implementation

1. **Update SCSS**:
   - Modify `_resume.scss` to apply box styling to the position element inside position-bar
   - Use the jobTitleBox tokens for consistent styling
   - Apply `break-inside: avoid` to the entire position-bar (not just the title)
   - Add media query for responsive handling of very long titles
   - **Completely reset any existing position styles** using `all: unset` before applying box styling
   - Add `flex: 1 1 auto` to title span to improve wrapping behavior with long titles
   - Add `overflow-wrap: anywhere;` to prevent horizontal scrolling with long single words
   - Add `prefers-color-scheme: dark` media query for high-contrast/dark mode support
   - Set `font-family` using token variable for consistent typography

2. **Update HTML Generation**:
   - Modify `html_generator.py` to wrap the position text in a specific span with a class for styling
   - Update `format_job_entry()` function to add the necessary HTML structure
   - **Handle Missing Dates**: Omit the dates span if no date is provided
   - **Add Accessibility Attributes**: `role="group"` on position-bar and `aria-label="Job title"` on title span
   - **Add RTL Support**: Add `dir="ltr"` to date span for right-to-left language compatibility
   - Add `loading="lazy"` to any company logo images for performance optimization
   - **Add ID Hooks**: Add `id="job-{index}"` to position-bar elements for E2E testing

3. **Ensure Print Stylesheet**:
   - Verify that CSS variables are properly included in both preview.css and print.css
   - **Fix recursive variable generation** to prevent duplication in print.css
   - Add `--job-title-box-line-height` variable for print CSS to match DOCX leading

### 3. DOCX Implementation

1. **Create Table-Based Job Title Boxes**:
   - Add `_set_cell_background` utility function for applying cell shading
   - **Add Theme Fill Support**: Set `w:themeFill="accent1"` when color matches primary palette
   - Implement 1×2 table approach to keep date inside the box
   - **Implement 1×1 table fallback** when no date is provided
   - **Fix table width calculation** to use proper Length objects for columns
   - Use preferred width instead of fixed width to allow better automatic sizing
   - **Center-align tables** for consistent appearance across page templates
   - Add new functions in `word_styles/section_builder.py` for job title boxes
   - **Explicitly clear outline levels** on paragraphs inside tables to prevent TOC pollution
   - Set fallback font attributes using theme fonts (`asciiTheme`/`hAnsiTheme` set to "minorHAnsi")
   - Add RTL support by setting `bidi="0"` on date text runs

2. **Update DOCX Builder**:
   - Modify `docx_builder.py` to use the new job title box functions
   - Apply proper paragraph and text styling within the boxes
   - Ensure JobTitleBox style is registered before it's used (lazy registration)
   - Check for and eliminate extra empty paragraphs after table insertion
   - **Add thread safety** with lock context manager for future async support

### 4. Token → CSS Generator Enhancements

1. **Add Missing Keys Check**:
   - Implement assertions to validate all required token keys are present
   - Ensure CI fails early if tokens are missing
   - Make validation consistent between CSS and DOCX implementations
   - Validate token version to prevent merging old token files
   - **Create custom TokenValidationError** class for clearer error messages
   - **Handle Deprecation Field**: Support deprecated tokens with warnings

2. **Print Stylesheet Integration**:
   - Fix the current recursive approach to prevent double-appending blocks
   - Use file copying or flags to avoid recursion issues
   - Include line-height variable in print CSS for consistency with DOCX

### 5. Documentation and CI Updates

1. **Update Style Guide**:
   - Add a "Theme authoring quick-start" section to STYLE_GUIDE.md
   - Provide examples of adding palette token sets without modifying code
   - Add note about table semantics: "Tables used as visual boxes are semantically *layout* only—avoid placing real data tables inside them."

2. **Update CI Configuration**:
   - Pin LibreOffice version in CI to avoid anti-aliasing differences affecting tests
   - Add `resume-tokens-hash` job that SHA-1s flattened tokens JSON to invalidate baselines only when tokens change
   - **Add Word-Web Testing**: Create weekly cron job using `woffice2pdf` or Word-online API to diff against baselines
   - Set up non-blocking test to catch Word rendering inconsistencies early

## Updated Files to Modify

### Design Tokens and Utilities
1. `design_tokens.json`
   - Add missing `backgroundColor` property
   - Add optional `fontSizePt` override for DOCX
   - Add `fontFamily` token for consistent typography
   - Add `tokensVersion` field
   - Add `deprecated` field to each top-level token object
   - Add default fallbacks for backward compatibility (especially borderRadius and padding)

2. `utils/unit_conversion.py` (new)
   - Add utility functions for unit conversion between CSS and DOCX
   - Include base_px parameter for rem conversions
   - Add proper error handling for invalid units

### HTML/CSS Implementation
1. `static/scss/_resume.scss`
   - Add styling for job title boxes with proper reset (`all: unset`)
   - Apply jobTitleBox tokens for consistent styling
   - Add media queries for responsive handling
   - Add `flex: 1 1 auto` to improve title shrinking behavior
   - Add `overflow-wrap: anywhere;` for long single-word titles
   - Add dark mode media query for high-contrast support

2. `html_generator.py`
   - Update `format_job_entry()` function
   - Add conditional rendering for date span
   - Add accessibility attributes for screen readers
   - Add RTL support for dates
   - Add unique ID hooks for each job entry

3. `tools/generate_tokens_css.py`
   - Add custom TokenValidationError class for better error reporting
   - Add assertions for required token keys
   - Add token version validation
   - Add support for deprecated field
   - Fix recursive variable generation to prevent duplication
   - Include line-height variable for print CSS
   - Share validation logic with DOCX implementation

### DOCX Implementation
1. `word_styles/registry.py`
   - Add new style definition for job title boxes
   - Ensure eager registration of styles
   - Add font family configuration with theme fallbacks

2. `word_styles/section_builder.py`
   - Add `_set_cell_background` utility function with theme-fill support
   - Add `twip(width_str, base_px)` unit conversion utility
   - Add `add_job_title_box_with_date()` function with fixed width calculation
   - Add 1×1 table fallback for missing dates
   - Add table center alignment
   - Add outline level clearing to prevent TOC pollution
   - Add RTL support for date text

3. `docx_builder.py`
   - Update experience section formatting to use job title box functions
   - Check for and remove extra paragraphs after table insertion
   - Add thread safety context manager for future async support

### Testing
1. Add unit tests for both HTML and DOCX implementations
2. Fix DOCX XPath tests to directly test borders/shading
3. Add visual regression testing baseline using LibreOffice for DOCX
4. Add Word-Web API testing for cross-platform validation
5. Add edge case tests for:
   - Missing dates
   - Very long single-word titles
   - Emoji characters in titles
   - Different border width tokens (parametrized tests)

### Documentation
1. `STYLE_GUIDE.md`
   - Add "Theme authoring quick-start" section
   - Include examples for adding palette token sets
   - Add note about semantic use of tables

## Detailed Implementation Steps

### 1. Design Token Updates

```json
// Update design_tokens.json

"tokensVersion": "2025-05-xx",  // Add version field for validation

"jobTitleBox": {
  "deprecated": false,  // Add deprecation field
  "backgroundColor": "#f0f8ff",  // Add this missing property
  "borderColor": "#4a6fdc",
  "borderWidth": "1px",
  "borderStyle": "solid",
  "borderRadius": "3px",  // Will have fallback if missing
  "paddingVertical": "0.2rem",  // Will have fallback if missing
  "paddingHorizontal": "0.4rem",  // Will have fallback if missing
  "marginTop": "0.1rem",
  "marginBottom": "0.1rem",
  "fontWeight": "600",
  "color": "#333333",
  "lineHeight": "1.2",  // For print CSS to match DOCX
  "fontFamily": "Calibri, system-ui, sans-serif",  // For consistent typography
  
  // Format-specific overrides
  "docx": {
    "backgroundColor": "#f0f8ff",
    "borderColor": "#4a6fdc",
    "borderWidth": "0.75pt",
    "borderStyle": "single",
    "fontWeight": "bold",  // DOCX-specific font weight
    "fontSizePt": 11,  // Optional override for DOCX font size
    "fontFamily": "Calibri"  // DOCX font family (will use theme fonts as fallback)
  }
}
```

### 2. HTML/CSS Implementation

```python
# In html_generator.py - Update format_job_entry() with accessibility, RTL support, and ID hooks

def format_job_entry(company: str, location: str, position: str, dates: str = None, content: List[str] = None, 
                    role_description: Optional[str] = None, job_index: int = 0) -> str:
    """Format a job entry into HTML."""
    html_parts = []
    content = content or []
    
    # Company name and location on the first line
    html_parts.append(f'<div class="job">')
    html_parts.append(f'<div class="job-title-line">')
    
    # Add lazy loading to company logo if present
    if 'logo' in locals():
        html_parts.append(f'<img src="{logo}" alt="{company} logo" loading="lazy" class="company-logo">')
    
    html_parts.append(f'<span class="company">{company}</span>')
    html_parts.append(f'<span class="location">{location}</span>')
    html_parts.append(f'</div>')
    
    # Position and dates on the second line with accessibility attributes and ID hook
    html_parts.append(f'<div id="job-{job_index}" class="position-bar position-line" role="group">')
    
    # Add job-title-box class and aria-label to position span
    html_parts.append(f'<span class="position job-title-box" aria-label="Job title">{position}</span>')
    
    # Only add dates span if there are dates (for internships still in progress, etc.)
    if dates:
        # Add dir="ltr" for RTL language compatibility
        html_parts.append(f'<span class="dates" dir="ltr">{dates}</span>')
    
    html_parts.append(f'</div>')
    
    # Rest of the function remains unchanged
    # ...
```

### 3. DOCX Implementation

```python
# In word_styles/section_builder.py - Add cell background with theme fill support

def _set_cell_background(cell, color, palette_info=None):
    """Set the background shading of a table cell.
    
    Args:
        cell: The table cell to apply shading to
        color: The background color as a hex string (e.g. '#f0f8ff')
        palette_info: Optional dict with primary color info for theme-fill detection
    """
    if not color or not color.startswith('#'):
        return
    
    # Remove # from hex color
    hex_color = color[1:] if color.startswith('#') else color
    
    # Get the cell properties element
    tc_pr = cell._tc.get_or_add_tcPr()
    
    # Create shading element
    shading = OxmlElement('w:shd')
    
    # Check if color matches primary palette color for theme-fill support
    is_primary_color = False
    if palette_info and 'primary' in palette_info:
        primary_color = palette_info['primary'].lower()
        if primary_color == color.lower():
            is_primary_color = True
    
    if is_primary_color:
        # Use theme fill for primary color (survives theme changes)
        shading.set(qn('w:fill'), hex_color)
        shading.set(qn('w:val'), 'clear')
        shading.set(qn('w:color'), 'auto')
        shading.set(qn('w:themeFill'), 'accent1')  # Use accent1 theme color
    else:
        # Standard fill for other colors
        shading.set(qn('w:fill'), hex_color)
        shading.set(qn('w:val'), 'clear')
        shading.set(qn('w:color'), 'auto')
    
    # Add shading element to cell properties
    tc_pr.append(shading)
    
    logger.debug(f"Applied background color {color} to cell" + 
                 (" with theme fill" if is_primary_color else ""))
```

### 4. Token Validation Updates

```python
# In tools/generate_tokens_css.py - Add support for deprecated field

def validate_tokens_version(tokens):
    """Validate the token version to prevent using outdated tokens."""
    version = tokens.get('tokensVersion')
    if not version:
        raise TokenValidationError("Missing tokensVersion in design tokens")
    
    # Could add additional version checks here if needed
    # e.g., comparing against a minimum required version

def validate_token_object(token_name, token_obj):
    """Validate a token object including the deprecation field."""
    # Check for deprecated flag
    if token_obj.get('deprecated', False):
        logger.warning(f"Token '{token_name}' is marked as deprecated and will be removed in a future version")
    
    # Add deprecation field with default if missing
    if 'deprecated' not in token_obj:
        token_obj['deprecated'] = False
    
    return token_obj

def generate_job_title_box_variables(tokens, output_file, is_print=False):
    """Generate CSS variables from jobTitleBox tokens with validation."""
    # Validate token version
    validate_tokens_version(tokens)
    
    # Get job title box tokens and validate
    job_title_box = tokens.get('jobTitleBox', {})
    job_title_box = validate_token_object('jobTitleBox', job_title_box)
    
    # Rest of the function remains the same...
```

### 5. CI Configuration for Word-Web Testing

```yaml
# Add to .github/workflows/test.yml or create new word-web-test.yml

name: Word-Web Rendering Test

on:
  schedule:
    # Run weekly on Monday mornings
    - cron: '0 5 * * 1'
  workflow_dispatch: # Allow manual triggering

jobs:
  word-web-test:
    name: Test Word-Web Rendering
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-github-actions-annotate-failures
          
      - name: Generate test DOCX file
        run: python tests/generate_test_docx.py
          
      - name: Convert DOCX to PDF using Word-Online API
        id: word_online
        continue-on-error: true  # Non-blocking
        run: |
          python tests/convert_docx_word_online.py
          
      - name: Compare rendering with baseline
        if: steps.word_online.outcome == 'success'
        run: python tests/compare_word_online_rendering.py
        
      - name: Upload comparison results
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: word-web-test-results
          path: tests/word_web_results/
```

## Acceptance Criteria (Updated)

1. **Styling Consistency**:
   - Job title boxes have consistent appearance across HTML, PDF, DOCX
   - Styling matches design tokens specified in `jobTitleBox`
   - DOCX implementation uses table approach with proper shading
   - Dark mode and high-contrast support for accessibility
   - Theme-fill support for primary colors in DOCX

2. **Layout and Alignment**:
   - Job title boxes align properly with other elements in the resume
   - Position bar layout remains clean with dates properly aligned
   - Responsive design handles long titles appropriately
   - Very long single words wrap properly with `overflow-wrap: anywhere`

3. **DOCX Specific**:
   - No excess spacing above or below job title boxes
   - Two-cell table approach keeps date aligned with the title
   - One-cell table fallback used when dates are missing
   - Tables are center-aligned for consistent appearance across templates
   - Row height is set to prevent border rendering issues
   - No TOC pollution from paragraphs inside tables
   - Theme font fallbacks for consistent typography
   - Theme-fill support for preserving colors during theme changes

4. **PDF Specific**:
   - Job title boxes don't break across pages
   - Print styles properly applied from CSS variables without duplication
   - Line height matches DOCX leading for consistent appearance

5. **Build and Tokens**:
   - All required token properties validated during build with clear error messages
   - Token version validated to prevent using outdated tokens
   - Deprecation field supported for graceful token retirement
   - Default fallbacks ensure backward compatibility
   - CSS variables properly included in both preview and print stylesheets
   - Unit conversion between CSS and DOCX formats is consistent
   - CI hash-based cache busting for tokens

6. **Edge Cases**:
   - Missing dates handled gracefully in both HTML and DOCX
   - Very long single-word titles wrap properly
   - Emoji characters in titles render correctly
   - RTL language support for dates
   - Various border widths handled correctly

7. **Accessibility**:
   - Proper ARIA attributes for screen readers
   - High-contrast/dark mode support
   - Semantic structure with proper roles
   - ID hooks for E2E testing

8. **Cross-Platform Compatibility**:
   - Weekly Word-Web testing ensures consistent rendering
   - Early detection of platform-specific rendering issues

## Deployment Strategy

We'll follow O3's recommended phased approach:

1. **PR-1: HTML/CSS + tokens**
   - Ship design token updates with version and deprecation fields
   - Add unit conversion utility (will only be used in PR-2)
   - Ship variables, SCSS, and generator changes
   - Add accessibility attributes and ID hooks to HTML
   - Update baseline PNG for web & PDF
   - Validate that variables are properly included in both preview and print CSS

2. **PR-2: DOCX (table wrapper)**
   - Add utility functions, registry style, and builder call
   - Add theme-fill support for primary colors
   - Implement 1×2 table with proper width handling
   - Add 1×1 table fallback for missing dates
   - Add table center alignment
   - Add outline level clearing to prevent TOC pollution
   - Add theme font fallbacks and RTL support
   - Add unit tests and LibreOffice screenshot tests
   - Verify old docs still open with fallback tokens

3. **PR-3: Clean-ups / Edge Cases**
   - Pin LibreOffice version in CI
   - Add token hash-based cache busting
   - Set up Word-Web weekly testing job
   - Refine long title wrapping rules
   - Add edge case tests (emoji, long titles, missing dates, border widths)
   - Address any cross-platform rendering issues
   - Add theme authoring documentation

This incremental approach ensures we can isolate and fix issues at each stage before proceeding to the next.