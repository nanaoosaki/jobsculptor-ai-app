# Implementation Plan for Resume Styling Improvements

## Overview

This document outlines the implementation plan for three key styling improvements to the resume tailoring application:

1. Add boxes around section headers (like "PERSONAL SUMMARY", "PROFESSIONAL EXPERIENCE") - **DOCX focus only**
2. Reduce line spacing between section headers and content text - **DOCX focus only**
3. Add boxes around job title/date period elements - **Cross-format implementation**

## Current Status Assessment

Based on the project documentation and image examples:

- **Section Header Boxes (Task 1)**: Already implemented correctly in HTML/PDF but missing in DOCX
- **Section Header Spacing (Task 2)**: Already implemented correctly in HTML/PDF but needs adjustment in DOCX
- **Job Title Boxes (Task 3)**: Needs implementation across all formats (HTML, PDF, DOCX)

## Pre-Implementation Validation

### For Tasks 1-2 (DOCX-only Implementation)

1. **DOCX Border Implementation Testing (Day 1)**
   - Create test files with both paragraph and table-based border approaches
   - Test on Windows (Word), macOS (Word for Mac), and LibreOffice
   - **Make an early decision**: If paragraph borders render acceptably on macOS, choose them as the primary method
   - Document platform-specific behaviors and the chosen approach

2. **Token Structure Validation**
   - Ensure DOCX-specific tokens can be properly consumed by the style engine
   - Verify that existing HTML/PDF styling remains unchanged
   - Create a "freeze test" for HTML/PDF output to prevent regressions

3. **Accessibility Verification**
   - Check how different border approaches affect heading hierarchy in DOCX
   - Ensure document outline and screen reader compatibility
   - Verify table of contents generation with the styled headings

### For Task 3 (Cross-Format Implementation)

1. **Token Pipeline and Naming Cohesion**
   - Design a consistent token structure that works across all formats
   - Ensure proper mapping from design tokens to CSS and DOCX styling

2. **Layout Testing**
   - Test with very long job titles and date periods
   - Verify proper wrapping behavior in all formats
   - Test in multi-column layouts with intentionally long titles

3. **Page Break Handling**
   - Ensure boxes don't break across pages in PDF output
   - Verify consistent appearance of job title boxes in all formats

## Implementation Plan

### 1. Add Boxes Around Section Headers (DOCX Only)

#### Files to Modify:
- `design_tokens.json` - Add DOCX-specific tokens for section header boxes
- `style_manager.py` or `style_engine.py` - Implement DOCX styling for section headers
- `token_validator.py` (new) - Create token validation script focused on DOCX tokens

#### Previously Encountered Issues & Solutions:
- **Flask Server Caching**: Always restart Flask server after making changes to Python files
- **DOCX Styling Precedence**: Style-level formatting is more reliable than direct paragraph formatting
- **Platform Differences**: Word for Mac handles borders differently than Windows versions

#### Early Decision on Border Approach:
Based on initial spike testing, we will commit to **paragraph-border styling** as our primary approach unless testing reveals significant rendering issues on macOS. The table-based approach will be kept as commented fallback code only.

#### Specific Changes:

1. **Update Design Tokens with DOCX-Specific Formatting**:
   ```json
   {
     "sectionHeader": {
       "border": {
         "widthPt": 1,
         "color": "#000000",
         "style": "single"
       },
       "paddingPt": 5,
       "spacingAfterPt": 8
     }
   }
   ```

2. **Create Named Style for Boxed Headers in DOCX**:
   ```python
   def create_boxed_heading_style(doc, tokens):
       """Create a BoxedHeading2 style for section headers with borders"""
       # Create a new style based on Heading 2
       boxed_heading = doc.styles.add_style('BoxedHeading2', WD_STYLE_TYPE.PARAGRAPH)
       boxed_heading.base_style = doc.styles['Heading 2']
       
       # Set outline level for accessibility and TOC inclusion
       boxed_heading.paragraph_format.outline_level = WD_OUTLINE_LEVEL.LEVEL_2
       
       # Get token values or use defaults
       border_width_pt = tokens.get("sectionHeader.border.widthPt", 1)
       border_color = tokens.get("sectionHeader.border.color", "#000000")
       border_style = tokens.get("sectionHeader.border.style", "single")
       padding_pt = tokens.get("sectionHeader.paddingPt", 5)
       
       # Convert hex color to RGB
       rgb = hex_to_rgb(border_color)
       
       # Apply border to the style
       # Primary approach: Direct paragraph borders
       try:
           # Use style._element to access XML representation
           p_pr = boxed_heading._element.get_or_add_pPr()
           p_borders = p_pr.get_or_add_pBdr()
           
           # Apply border to all four sides
           for side in ['top', 'right', 'bottom', 'left']:
               side_border = getattr(p_borders, f"get_or_add_{side}")()
               side_border.val = border_style
               side_border.sz = Pt(border_width_pt * 8)  # Word uses 8ths of a point
               side_border.color = rgb
               side_border.space = Pt(padding_pt)
           
           return 'BoxedHeading2'
       except Exception as e:
           logger.warning(f"Failed to apply paragraph borders: {e}. Using regular heading style.")
           return 'Heading 2'  # Default to regular heading if borders fail
       
       # Note: Table-based approach kept as reference only - not used unless 
       # paragraph borders prove unviable during initial testing
       """
       # Fallback approach: Table-based borders
       # Only use if paragraph borders fail on macOS testing
       def create_table_based_heading(doc, text, tokens):
           table = doc.add_table(rows=1, cols=1)
           cell = table.cell(0, 0)
           cell.text = ""
           
           # Apply paragraph formatting
           p = cell.paragraphs[0]
           p.style = 'Heading 2'
           p.text = text
           
           # Set border properties
           # ...table border code...
           
           return table
       """
   ```

3. **Update DOCX Generation to Use Named Style**:
   ```python
   def apply_section_header_style(doc, paragraph, tokens):
       """Apply the BoxedHeading2 style to a section header paragraph"""
       # Ensure the style exists in the document
       style_name = create_boxed_heading_style(doc, tokens)
       
       # Apply the style to the paragraph
       paragraph.style = style_name
       
       # Set spacing after (reduced spacing)
       spacing_after_pt = tokens.get("sectionHeader.spacingAfterPt", 8)
       paragraph.paragraph_format.space_after = Pt(spacing_after_pt)
       
       return paragraph
   ```

4. **Create Token Accessor with Fallbacks**:
   ```python
   class TokenAccessor:
       """Safely access tokens with fallbacks and warnings"""
       
       def __init__(self, tokens_data):
           self.tokens = tokens_data
           self.warnings = set()  # Track warned keys to avoid repetition
       
       def get(self, key_path, default=None):
           """
           Access a token by dot-notation path with fallback.
           Example: get("sectionHeader.border.widthPt", 1)
           """
           parts = key_path.split('.')
           current = self.tokens
           
           try:
               for part in parts:
                   current = current[part]
               return current
           except (KeyError, TypeError):
               if key_path not in self.warnings:
                   logger.warning(f"Missing token: {key_path}, using default: {default}")
                   self.warnings.add(key_path)
               return default
   ```

5. **Add DOCX vs PDF Assertion Test**:
   ```python
   def test_docx_section_header_border():
       """Test that DOCX section headers have the correct border properties"""
       # Load tokens at the test level to avoid dependency issues
       with open('design_tokens.json', 'r') as f:
           token_data = json.load(f)
       tokens = TokenAccessor(token_data)
       
       # Generate a test document with boxed headers
       doc_path = generate_test_document_with_boxed_headers()
       
       # Open the document with python-docx
       doc = Document(doc_path)
       
       # Find first section header by style
       section_header = None
       for paragraph in doc.paragraphs:
           if paragraph.style.name == 'BoxedHeading2':
               section_header = paragraph
               break
       
       assert section_header is not None, "No BoxedHeading2 style paragraph found"
       
       # Access the paragraph's XML to check border properties
       p_pr = section_header._element.get_or_add_pPr()
       p_borders = p_pr.get_or_add_pBdr()
       
       # Check top border width (in 8ths of a point)
       top_border = p_borders.top
       expected_width = int(8 * float(tokens.get("sectionHeader.border.widthPt", 1)))
       assert top_border.sz == expected_width, f"Border width mismatch. Expected: {expected_width}, Got: {top_border.sz}"
       
       # Check outline level for accessibility
       outline_level = p_pr.outline_lvl.val if p_pr.outline_lvl else None
       assert outline_level == 1, f"Outline level should be 1 (LEVEL_2), got {outline_level}"
       
       # Similar checks for other sides and properties
   ```

6. **Create Improved HTML/PDF Freeze Test**:
   ```python
   def test_html_pdf_freeze():
       """Ensure HTML/PDF styling for section headers remains unchanged"""
       # Parse command-line arguments for baseline update flag
       import argparse
       parser = argparse.ArgumentParser()
       parser.add_argument('--update-baseline', action='store_true', 
                         help='Update the baseline screenshots')
       args, _ = parser.parse_known_args()
       
       baseline_path = "baseline_screenshot.png"
       current_path = "current_screenshot.png"
       
       # Generate current screenshot
       generate_current_screenshot(current_path)
       
       # Update baseline if requested or if it doesn't exist
       if args.update_baseline or not os.path.exists(baseline_path):
           shutil.copy(current_path, baseline_path)
           logging.info(f"Updated baseline screenshot at {baseline_path}")
           return
       
       # Compare screenshots with tolerance for minor rendering differences
       # Use structural similarity index (SSIM) instead of exact comparison
       from skimage.metrics import structural_similarity as ssim
       import numpy as np
       from PIL import Image
       
       baseline_img = np.array(Image.open(baseline_path).convert('L'))
       current_img = np.array(Image.open(current_path).convert('L'))
       
       # Calculate similarity score (1.0 = identical, 0.0 = completely different)
       similarity = ssim(baseline_img, current_img)
       
       # Require high similarity but allow for minor rendering differences
       assert similarity > 0.98, f"HTML/PDF styling differs significantly. SSIM: {similarity}"
       logging.info(f"HTML/PDF styling similarity: {similarity:.4f}")
   ```

### 2. Reduce Line Spacing Between Section Headers and Content (DOCX Only)

This task is integrated with task 1 for DOCX, as the spacing is controlled by the same style definition. The token `sectionHeader.spacingAfterPt` already handles this adjustment.

### 3. Add Boxes Around Job Title/Date Period (Cross-Format Implementation)

#### Files to Modify:
- `design_tokens.json` - Add styling tokens for job title boxes
- `static/scss/_resume.scss` - Create/update job title styling
- `html_generator.py` - Ensure job titles are wrapped in appropriate elements
- `style_manager.py` - Add DOCX styling for job title boxes

#### Specific Changes:

1. **Update Design Tokens with Cross-Format Structure**:
   ```json
   {
     "jobTitleBox": {
       "border": {
         "width": { "px": "1px", "pt": "1" },
         "color": "#000000",
         "style": { "css": "solid", "docx": "single" }
       },
       "padding": { "px": "3px 8px", "pt": "3" },
       "marginBottom": { "px": "5px", "pt": "5" },
       "borderRadius": { "px": "0px", "pt": "0" },
       "maxWidth": "100%"
     }
   }
   ```

2. **Update SCSS Styling**:
   ```scss
   .job-title-box {
     display: inline-block;
     border: $jobTitleBoxBorderWidth $jobTitleBoxBorderStyle $jobTitleBoxBorderColor;
     padding: $jobTitleBoxPadding;
     margin-bottom: $jobTitleBoxMarginBottom;
     border-radius: $jobTitleBoxBorderRadius;
     max-width: $jobTitleBoxMaxWidth;
     white-space: normal; // Allow text to wrap inside the box
     break-inside: avoid; // Prevent breaking across pages
   }
   
   @media print {
     .job-title-box {
       // Print-specific overrides for PDF
       border-width: $jobTitleBoxBorderWidth !important;
       border-style: $jobTitleBoxBorderStyle !important;
       border-color: $jobTitleBoxBorderColor !important;
     }
   }
   ```

3. **Update HTML Generator Helper**:
   ```python
   def render_job_title(title, date_period):
       """Render a job title with consistent box styling"""
       return f'<span class="job-title-box">{title} - {date_period}</span>'
   ```

4. **Update DOCX Styling for Job Titles with Column Width Handling**:
   ```python
   def apply_job_title_box_style(doc, paragraph, tokens):
       """Apply box border styling to a job title in DOCX"""
       # We'll use a table-based approach for consistent rendering
       # This is more compatible than paragraph borders for inline elements
       
       # Extract content from paragraph
       text = paragraph.text
       
       # Get the container width (column width)
       container_width = get_container_width(paragraph)
       
       # Remove the paragraph
       p_index = doc._element.body.index(paragraph._element)
       doc._element.body.remove(paragraph._element)
       
       # Insert a 1-row, 1-column table at the same position
       table = doc._element.body.insert(p_index, CT_Tbl())
       tbl = Table(table, doc)
       
       # Critical: Set table to respect column width
       table.allow_autofit = False
       table.width = container_width
       
       # Set table properties for border
       border_width_pt = tokens.get("jobTitleBox.border.width.pt", 1)
       border_color = tokens.get("jobTitleBox.border.color", "#000000")
       border_style = tokens.get("jobTitleBox.border.style.docx", "single")
       
       # Add a row and cell
       row = tbl.add_row()
       cell = row.cells[0]
       
       # Set cell text
       cell.text = text
       
       # Apply borders to the cell
       cell_borders = cell._tc.get_or_add_tcPr().get_or_add_tcBorders()
       for side in ['top', 'left', 'bottom', 'right']:
           border = getattr(cell_borders, f"get_or_add_{side}")()
           border.val = border_style
           border.sz = Pt(border_width_pt * 8)
           border.color = hex_to_rgb(border_color)
       
       # Set cell padding
       padding_pt = tokens.get("jobTitleBox.padding.pt", 3)
       cell_margins = cell._tc.get_or_add_tcPr().get_or_add_tcMar()
       for side in ['top', 'left', 'bottom', 'right']:
           margin = getattr(cell_margins, f"get_or_add_{side}")()
           margin.w = Pt(padding_pt) * 20  # Word uses twentieth of a point
       
       # Return the table object for further manipulation if needed
       return tbl
   
   def get_container_width(paragraph):
       """Determine the container width (column width) for a paragraph"""
       # Default width (for single column)
       default_width = Inches(6.5)
       
       # Try to determine if we're in a multi-column section
       try:
           # Get section properties
           section = paragraph._element.xpath("./ancestor::w:sectPr")
           if section:
               # Check for columns
               cols = section[0].xpath("./w:cols")
               if cols and cols[0].get(qn("w:num")) > 1:
                   # We're in a multi-column layout
                   num_cols = int(cols[0].get(qn("w:num")))
                   # Account for column spacing
                   col_spacing = Inches(0.25)  # Default spacing
                   if cols[0].get(qn("w:space")):
                       col_spacing = Twips(int(cols[0].get(qn("w:space"))))
                   
                   # Calculate column width
                   page_width = Inches(8.5)  # Default letter size
                   margins = Inches(1)       # Default margins
                   available_width = page_width - (2 * margins)
                   col_width = (available_width - (col_spacing * (num_cols - 1))) / num_cols
                   
                   return col_width
       except Exception as e:
           logger.warning(f"Couldn't determine column width: {e}")
       
       return default_width
   ```

5. **Add Visual Regression Test for Job Title Boxes**:
   ```python
   def test_job_title_box_visual_consistency():
       """Test visual consistency of job title boxes across formats"""
       # Load tokens at the test level to avoid dependency issues
       with open('design_tokens.json', 'r') as f:
           token_data = json.load(f)
       tokens = TokenAccessor(token_data)
       
       # Generate test content with job title boxes
       generate_test_resume_with_job_title_boxes(with_long_titles=True)
       
       # Take screenshots of HTML preview and PDF
       html_screenshot = take_html_preview_screenshot()
       pdf_screenshot = take_pdf_screenshot()
       
       # Capture DOCX image
       docx_screenshot = convert_docx_to_image()
       
       # Compare key regions (job title areas)
       html_job_title = extract_job_title_region(html_screenshot)
       pdf_job_title = extract_job_title_region(pdf_screenshot)
       docx_job_title = extract_job_title_region(docx_screenshot)
       
       # Calculate similarity scores (using structural similarity index)
       html_pdf_similarity = calculate_similarity(html_job_title, pdf_job_title)
       html_docx_similarity = calculate_similarity(html_job_title, docx_job_title)
       pdf_docx_similarity = calculate_similarity(pdf_job_title, docx_job_title)
       
       # Assert reasonable similarity thresholds
       assert html_pdf_similarity > 0.9, f"HTML-PDF similarity too low: {html_pdf_similarity}"
       assert html_docx_similarity > 0.85, f"HTML-DOCX similarity too low: {html_docx_similarity}"
       assert pdf_docx_similarity > 0.85, f"PDF-DOCX similarity too low: {pdf_docx_similarity}"
       
       # Generate a multi-column test case
       generate_test_resume_with_job_title_boxes(multi_column=True, with_long_titles=True)
       
       # Verify DOCX output in multi-column layout
       multi_column_docx = Document("test_multi_column.docx")
       # Verify tables don't exceed column width
       # ... verification code ...
   ```

## Implementation Strategy

### For Tasks 1-2 (DOCX Focus)

1. **Create Branch and Backup Files**:
   ```bash
   git checkout -b add-docx-section-headers
   cp style_manager.py style_manager.py.bak
   cp design_tokens.json design_tokens.json.bak
   ```

2. **DOCX Border Approach Testing** (Critical Decision Point):
   - Create test files with both paragraph and table-based border approaches
   - Test on multiple platforms to determine the most reliable method
   - **Make decisive choice on paragraph vs table borders before proceeding**
   - Document findings and select primary implementation strategy
   - Commit to paragraph borders unless testing reveals major issues

3. **Update Design Tokens**:
   - Add DOCX-specific tokens for section headers
   - Keep structure simple with DOCX-only values
   - Avoid changing any HTML/PDF-related tokens

4. **Implement Named Style in DOCX**:
   - Create the `BoxedHeading2` style based on the standard `Heading 2`
   - Set proper outline level for accessibility and TOC
   - Apply borders and spacing according to design tokens
   - Test style application to ensure proper heading hierarchy

5. **Create DOCX Unit Tests**:
   - Add tests that verify border properties in generated DOCX files
   - Create PDF vs DOCX visual comparison tests
   - Add HTML/PDF freeze test with appropriate tolerance
   - Include `--update-baseline` flag for controlled baseline updates

6. **Document DOCX Implementation**:
   - Create clear documentation on the DOCX styling approach
   - Document platform-specific considerations
   - Add notes indicating that HTML/PDF implementations are already correct

### For Task 3 (Cross-Format)

1. **Create Branch**:
   ```bash
   git checkout -b add-job-title-boxes
   ```

2. **Update Design Tokens**:
   - Add cross-format tokens for job title boxes
   - Structure tokens with format-specific variants (px/pt)

3. **Update Token Generator**:
   - Ensure generator correctly processes the multi-format tokens
   - Add support for extracting the right units for each output format

4. **Implement HTML/CSS Changes**:
   - Update SCSS with job title box styling
   - Add page break control for PDF output
   - Compile updated CSS

5. **Update HTML Generator**:
   - Add helper function for rendering job titles with boxes
   - Update all job title rendering to use the helper

6. **Implement DOCX Style**:
   - Add table-based border styling for job titles in DOCX
   - Add container width detection for multi-column support
   - Ensure tables respect column width limits
   - Ensure consistent visual appearance with HTML/PDF

7. **Add Cross-Format Tests**:
   - Create visual regression tests comparing all three formats
   - Test with various job title lengths and edge cases
   - Test specifically in multi-column layouts with long titles

## Build and Validation Process

### For Tasks 1-2 (DOCX Focus)

```bash
#!/bin/bash
# validate_docx_styles.sh

# Exit immediately if a command exits with a non-zero status
set -e

# Validate tokens
echo "Validating DOCX tokens..."
python tools/validate_docx_tokens.py

# Generate test DOCX
echo "Generating test DOCX..."
python tools/generate_test_docx.py

# Run DOCX tests with proper exit code handling
echo "Running DOCX tests..."
python -m pytest tests/test_docx_styling.py
test_exit_code=$?

# Run freeze test
echo "Running HTML/PDF freeze test..."
python -m pytest tests/test_html_pdf_freeze.py
freeze_exit_code=$?

# Check exit codes
if [ $test_exit_code -ne 0 ] || [ $freeze_exit_code -ne 0 ]; then
  echo "❌ Tests failed. Please check the output above."
  exit 1
fi

echo "✅ DOCX style validation complete."
```

### For Task 3 (Cross-Format)

```bash
#!/bin/bash
# build_cross_format_styles.sh

# Exit immediately if a command exits with a non-zero status
set -e

# Validate tokens
echo "Validating tokens..."
python tools/validate_tokens.py

# Regenerate tokens from JSON
echo "Generating tokens..."
python tools/generate_tokens_css.py

# Compile SCSS to CSS
echo "Compiling SCSS..."
sass static/scss/preview.scss static/css/preview.css
sass static/scss/print.scss static/css/print.css

# Generate test outputs in all formats
echo "Generating test outputs..."
python tools/generate_test_outputs.py

# Run visual regression tests with proper exit code handling
echo "Running visual regression tests..."
python -m pytest tests/test_visual_regression.py
test_exit_code=$?

if [ $test_exit_code -ne 0 ]; then
  echo "❌ Visual regression tests failed. Please check the output above."
  exit 1
fi

echo "✅ Cross-format styling validation complete. Please restart the Flask server."
```

## Documentation Updates

### Style Guide Updates

Add the following to the style documentation:

1. **Section Headers**:
   ```
   Section header styling is canonical in PDF; DOCX must visually match it.
   HTML/PDF edits require a regression review because they're already ship-shape.
   
   The DOCX implementation uses a named style 'BoxedHeading2' which maintains
   the document outline for accessibility while adding visual box borders.
   
   TODO: When theme support is added in the future, refactor to 
   `themes.default.sectionHeader.*` to support multiple theme variations.
   ```

2. **Job Title Boxes**:
   ```
   Job title boxes use a unified token approach across all three formats.
   Any changes to these tokens will affect HTML, PDF, and DOCX outputs.
   
   DOCX implementation uses a table-based approach for consistent rendering
   across all Word versions and platforms.
   
   Multi-column layouts: Job title boxes in DOCX are implemented as tables
   that respect column width to prevent overflow in multi-column layouts.
   ```

3. **Token Structure Documentation**:
   ```
   - Section header tokens are DOCX-specific since HTML/PDF are already implemented
   - Job title tokens use a multi-format structure with format-specific variants
   - All token changes should be validated across relevant formats
   
   Token Schema Evolution:
   - Current: Flat token structure with format-specific paths
   - Future: Consider moving to a theme-based structure (themes.default.*)
     when multiple themes are needed
   ```
4. **Testing Notes**:
   ```
   HTML/PDF Freeze Tests:
   - Run `pytest --update-baseline` to update baseline screenshots when:
     1. Making intentional styling changes that are approved
     2. After browser/rendering engine updates that affect anti-aliasing
     3. After the initial setup to generate the first baseline
   
   - Do NOT update baselines when:
     1. Investigating a regression
     2. When making changes that shouldn't affect HTML/PDF rendering
   ```

## Key Focus Areas

1. **For Tasks 1-2 (DOCX Focus)**:
   - **Early decision on border approach**: Paragraph borders are preferred for heading outline/TOC preservation
   - DOCX styling quality and accessibility (proper outline level)
   - Named style implementation with outline level preserved
   - Maintaining DOCX-PDF visual parity
   - Preventing HTML/PDF regressions with appropriate tolerance

2. **For Task 3 (Cross-Format)**:
   - Consistent appearance across all formats
   - Token structure supporting all output needs
   - Column width handling in multi-column layouts
   - Visual regression testing with specific tests for narrow columns
   - Edge case handling for long titles 
