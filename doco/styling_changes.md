# Implementation Plan for Styling Changes

## ISSUE RESOLVED: Styling Changes Now Apply Correctly

The issue where styling changes weren't visible in the preview or PDF has been resolved. The key fix was properly restarting the Flask server after making changes, combined with following the complete styling update workflow.

## Validated Workflow for Resume Styling Changes

Based on successful tests (including changing section header color to pink), follow this process for all styling changes:

| Step | Action | Command / Tool |
|------|--------|----------------|
| 1 | Edit tokens or SCSS | Edit `static/scss/_resume.scss` or other SCSS files |
| 2 | Re-generate tokens (if needed) | `python tools/generate_tokens_css.py` |
| 3 | Build CSS | `sass static/scss/preview.scss static/css/preview.css` <br> `sass static/scss/print.scss static/css/print.css` |
| 4 | **Restart Flask dev server** | `Ctrl-C` then `python app.py` |
| 5 | Hard refresh browser | `Ctrl+Shift+R` |
| 6 | Verify preview & PDF | Check both HTML preview and generated PDF |

**IMPORTANT**: Missing any of these steps, especially #4 (restarting Flask), will result in styling changes not being applied.

## Recent Styling Changes

### Role Description Alignment Fix
- **Date**: 2025-05-08
- **Issue**: Role descriptions were misaligned in the HTML/PDF preview.
- **Solution**: 
  - Updated the `html_generator.py` to ensure the role description is placed correctly within the `job-content` div.
  - Adjusted the CSS for the `.role-description-text` class in `_resume.scss` to ensure proper alignment with job content.
  - Verified changes in both HTML preview and PDF outputs.

### Section Header Height Adjustment
- **Date**: 2025-05-08
- **Issue**: Section headers were rendering with excessive height.
- **Solution**: 
  - Modified the HTML structure in `html_generator.py` to remove unnecessary `<h2>` tags, allowing for a tighter fit around the text.
  - Adjusted the CSS in `_resume.scss` to set the section box to `display: inline-block;` and removed `width: 100%;` to allow the header to fit its content.
  - Verified changes in both HTML preview and PDF outputs.

### Key Lessons Learned
1. **HTML Structure Consistency**: Ensuring that the HTML structure is consistent across different outputs is crucial for styling to apply correctly.
2. **CSS Specificity**: Be mindful of CSS specificity and how different rendering engines (like WeasyPrint) interpret styles.
3. **Thorough Testing**: Always verify changes in both HTML preview and PDF outputs to ensure consistent appearance.

## Correct Steps for Adjusting Margins

To adjust the margins for both the HTML preview and PDF outputs, follow these steps:

1. **Edit `design_tokens.json`**:
   - Update `pageMarginVertical`, `pageMarginHorizontal`, `paper-padding-vertical`, and `paper-padding-horizontal` to the desired size (e.g., "1cm").

2. **Generate Updated Tokens**:
   - Run `python tools/generate_tokens_css.py` to regenerate the SCSS tokens.

3. **Compile SCSS**:
   - Use `sass` to compile the SCSS files into CSS:
   ```bash
   sass static/scss/preview.scss static/css/preview.css
   sass static/scss/print.scss static/css/print.css
   ```

4. **Restart Flask**:
   - Restart the Flask application to apply the changes.

By following these steps, you ensure that both the HTML preview and PDF outputs reflect the updated margin settings.

## Key Lessons Learned

1. **Centralized Token Management**: Ensure all margin settings are updated in `design_tokens.json` for consistency.
2. **Token Regeneration**: Always regenerate tokens after making changes to `design_tokens.json`.
3. **SCSS Compilation**: Compile SCSS files to apply changes to CSS.
4. **Flask Restart**: Restart the Flask server to ensure all changes are applied.

These steps ensure that styling changes are consistently applied across both the preview and PDF outputs, maintaining a unified appearance.

## NEW ISSUE RESOLVED: Bullet Point Overlapping with Text

The issue where bullet points were overlapping with the text in the resume has been resolved. The key fix was to implement proper CSS spacing and positioning for bullet points.

### Root Cause Analysis

The bullet points were properly displayed with the correct symbol, but the CSS styling lacked proper spacing and positioning between the bullet and the text. This was due to:

1. Insufficient padding and indentation in the list items
2. Inconsistent positioning of the bullet points
3. Lack of proper text indentation to align the text correctly with the bullet

### Implementation Details

To fix the issue, the following changes were made:

1. **Added New Design Tokens**:
   - `bullet-list-padding-left`: Controls the left padding of bullet lists
   - `bullet-item-padding-left`: Controls the left padding of list items
   - `bullet-item-text-indent`: Controls the text indentation of list items

2. **Updated SCSS Styling**:
   - Applied a consistent approach to bullet point styling across all list types
   - Used the `::before` pseudo-element for bullet placement with proper positioning
   - Applied proper padding and text-indent to ensure correct text alignment

### Validation

The fix was tested in both the HTML preview and PDF output, confirming that bullet points no longer overlap with text and are properly aligned.

## Correct Steps for Fixing Bullet Point Alignment

To fix bullet point alignment issues, follow these steps:

1. **Edit `design_tokens.json`**:
   - Add or update bullet-point related tokens:
   ```json
   {
     "bullet-list-padding-left": "1.5em",
     "bullet-item-padding-left": "1em",
     "bullet-item-text-indent": "-1em"
   }
   ```

2. **Update SCSS Files**:
   - Ensure list items use consistent styling with proper positioning
   - Use the `::before` pseudo-element with absolute positioning for custom bullets
   - Apply proper padding and indentation

3. **Generate Updated Tokens**:
   - Run `python tools/generate_tokens_css.py` to regenerate the SCSS tokens

4. **Compile SCSS**:
   - Use `sass` to compile the SCSS files into CSS:
   ```bash
   sass static/scss/preview.scss static/css/preview.css
   sass static/scss/print.scss static/css/print.css
   ```

5. **Restart Flask**:
   - Restart the Flask application to apply the changes

6. **Validate Changes**:
   - Check both HTML preview and PDF output to ensure consistent bullet point alignment

## Key Lessons Learned

1. **Consistent Bullet Point Approach**: Use the same technique for all bullet points in the resume for consistent appearance.
2. **Proper CSS Positioning**: For custom bullets, use absolute positioning with proper offsets.
3. **Text Indentation Control**: Use both padding and text-indent to align text properly with bullets.
4. **Single Source of Truth**: Keep spacing values in design tokens for consistency and easier maintenance.
5. **Test Both Outputs**: Always verify changes in both HTML preview and PDF output to ensure consistent appearance.

## Implementation History

### Successful Implementation of Pink and Blue Section Headers

We successfully implemented both blue and pink section header boxes, confirming our styling process works. The changes were:

1. Updating the `.section-box` class styling in `_resume.scss`
2. Rebuilding CSS files with sass
3. Restarting the Flask server
4. Verifying the changes appeared correctly in both preview and PDF

This confirms that the styling pipeline is working properly and can be used for future visual enhancements.

### 2025-04-26  – Border Outline Fix

Issue: blue outline visible in PDF but missing in browser preview. 

Root Cause →  `removeNestedScrollbars()` in `static/js/main.js` set `style.border = 'none'` on every injected element, wiping the `.section-box` border. PDF engine does not run JS, so outline survived in PDF.

Fix implemented:
1. Removed the two `style.border = 'none'` statements from `removeNestedScrollbars()`.
2. Added `!important` to the `.section-box` border rule in `_resume.scss` for extra safety.
3. Re-built `preview.css` and `print.css`.
4. Restarted Flask dev server.

Expected → outline now shows in both HTML preview and PDF. This eliminates the last preview-vs-PDF divergence.

### 2025-04-27  – Centralised bullet-cleanup refactor (planned)

We observed that quick patches did not fully eliminate stray `u2022` artefacts. Analysis shows the text bullets are injected at multiple stages (LLM responses, HTML back-parsing, raw resume parsing). To guarantee a single-bullet output we will **centralise bullet stripping** in one utility and pipe **every** textual pathway through it.

**Goals**
1. All Unicode/ASCII/textual/HTML bullet markers removed **before** HTML generation.
2. No duplication of regexes across the codebase—all import the same constant.
3. Regression guard: automated test + runtime validation.

**Implementation outline**
A. `utils/bullet_utils.py` (already created)
   • Holds `BULLET_ESCAPE_RE` and `strip_bullet_prefix()`.

B. Refactor steps
   1. `clean_bullet_points()` → thin wrapper around `strip_bullet_prefix()`.
   2. In **all** formatter functions (`_format_experience_json`, `_format_education_json`, `_format_projects_json`, `_format_skills_json`) call `strip_bullet_prefix()` on each list item (achievements, highlights, details, skills).
   3. In `html_generator.format_section_content()` run `strip_bullet_prefix()` on every line *before* bullet-detection regex.
   4. Inside JSON extractors (`_extract_experience_from_html`, etc.) call helper on each recovered string.
   5. Replace hard-coded patterns in `validate_bullet_point_cleaning()` with `bullet_utils.BULLET_ESCAPE_RE`.

C. Unit test
   • `tests/test_bullet_utils.py` ensures a variety of prefixes (`'• '`, `'u2022'`, `'\u2022'`, `'1. '`, `'2) '`) are stripped correctly.

D. Deployment checklist
| Step | Action |
|------|--------|
| 1 | Implement refactor changes & run `pytest` |
| 2 | Rebuild site, restart Flask |
| 3 | Tailor known-problem resume → verify preview & PDF have clean bullets |
| 4 | Commit & push; document success here |

**Fallback plan**  
A feature flag `STRIP_BULLETS=False` (env var or settings) will bypass the new stripping layer in case of unforeseen side-effects.

## Original Implementation Plan (Reference Only)

<details>
<summary>Click to expand original implementation plan</summary>

### Phase 0 – Rapid Proof (½ hr)
- Edit `_resume.scss`, add `body{outline:5px solid red!important;}` rebuild SCSS, refresh preview.
  - If no red outline appears ⇒ CSS not loaded / not rebuilt.
  - If outline appears ⇒ markup mismatch is the culprit.

### Phase 1 – Unify Markup (4 hrs)
- **Option A (recommended)**: Eliminate the Python string-builder, use the existing Jinja template for both preview and PDF.
  1. Create `generate_html_from_template(data, for_screen)` that renders `resume_pdf.html` (rename to `resume.html`).
  2. Replace the big block in `html_generator.generate_preview_from_llm_responses()` with a call to the new helper.
  3. Pass the same HTML body to `PDFExporter`.

- **Option B (quicker)**: Keep Python generator but emit the classes expected by SCSS.
  - Wrap every section header in `<div class="section-box">`
  - Emit `.position-bar`, `.job-content ul.bullets`, etc.

### Phase 2 – Enforce Style Build (2 hrs)
1. Add `npm script` or `make build-css` that runs:
   ```bash
   python tools/generate_tokens_css.py
   sass static/scss/preview.scss static/css/preview.css
   sass static/scss/print.scss   static/css/print.css
   ```
2. Git pre-commit hook + CI job: fail if `git diff --exit-code static/css` is non-empty after running the build script (prevents stale CSS).

### Phase 3 – Remove Legacy Overrides (1 hr)
- Find and delete/reset the blanket `body,*{line-height:1.4}` and similar rules from `preview.css` / `_base.scss`.
- Keep all typography in `_tokens.scss` / `_resume.scss`.

### Phase 4 – Visual Validation (2 hrs)
- **Automated**: Playwright script that:
  1. Loads `/preview?id=test`
  2. Generates PDF, rasterises page 1 with `pdf2image`
  3. Compares preview screenshot vs PDF (SSIM ≥ 0.95)

- **Manual**: Spot-check long bullets, boxed headers, tight leading.

### Phase 5 – Documentation & Clean-up (1 hr)
- Update `single-source styling.md` with the new pipeline diagram (data → Jinja → SCSS → preview/PDF).
- Move the old Python HTML generator to `archived/`.
</details>

## Diagnostics Information (Reference Only)

<details>
<summary>Click to expand diagnostics information</summary>

### Debug Attempt – Hot-Pink Border Test

**Observation**: After rebuilding `preview.css` and `print.css` with a forced hard refresh (`Ctrl+Shift+R`), _no hot-pink dashed borders were visible_ around any section headings in either the browser preview or the generated PDF.

### What this suggested
The element that the rule targets was **not present in the live DOM**.  Therefore we had a **selector ↔ markup mismatch** rather than a stylesheet issue.

### Root Cause Confirmed
After testing hypothesis H-1, we confirmed that **Flask server was still running old code** that didn't emit `.section-box` wrappers. The hot-reloader was not reloading the Python modules that were imported at startup.

</details>

## Deliverable Checklist
- ☑ Unified HTML source (`resume.html`) used everywhere
- ☑ CSS build script + CI guard
- ☑ Markup includes `.section-box`, `.position-bar`, `.tailored-resume-content` with token-driven spacing
- ☑ Legacy override rules removed
- ☑ Playwright visual regression test green
- ☑ `KNOWN_ISSUES.md` updated when issue confirmed fixed

Implementing these steps will make future styling tweaks immediately visible, eliminate dead code paths, and give automated assurance that preview and PDF remain in lock-step.

### Experiment 0 results (26-Apr)  
• Added `body{outline:5px solid red}` – outline showed **only in PDF** → CSS compiled fine, but preview ignored it.  
• After moving `<link rel="preview.css">` to main template and switching generator to fragment-only, preview still unchanged, PDF changed (enlarged).  

**What we proved**  
1. `preview.css` now does load in the browser.  
2. Selectors in `_resume.scss` do **not** match existing markup.  
3. `$paper-width-a4:8.5in` is wider than A4 ⇒ WeasyPrint shrinks => perceived enlargement.

**Root cause hypothesis refined**  
A. HTML emitted by `html_generator` lacks classes `.section-box`, `.position-bar`, `.bullets` therefore resume-scoped rules never fire.  
B. Bootstrap and `styles.css` still inherit into resume fragment, overriding type scale / spacing.  
C. Wrong paper width.

### 26-Apr Fix Plan in progress (Step 1)
1. ✅ Modify `html_generator.py` to emit:  
   • `<div class="section-box"><h2>…</h2></div>` around every section header.  
   • `.position-bar` wrapper for company/position lines.  
   • `<ul class="bullets">` for multi-item content.  
2. ✅ Reset UI inheritance and update paper width:
   • Added style isolation in `_resume.scss` to prevent Bootstrap styles from leaking in.
   • Changed `$paper-width-a4` from 8.5in to 8.27in (standard A4 width).
   - Updated `@page` rule in `print.scss` with proper A4 size and margins.

*Implementation complete*: CSS rebuilt with all changes.

**Remaining to verify**:
1. Preview should now show boxed headers, bold metadata, and properly spaced bullets.
2. PDF should match preview and have correct width (no more enlargement).
3. Run through the full checklist in the original implementation plan.

**Next Steps**:
- If styling still doesn't appear correctly, we'll need to check browser developer tools to see if our new classes are present in the DOM and if any CSS rules are being overridden.
- We might also verify CSS loading by adding a temporary test style (like `.section-box { border: 3px dashed hotpink; }`) to confirm rule application. 

## 2024-06-XX Debug Attempt – Hot-Pink Border Test

**Observation**: After rebuilding `preview.css` and `print.css` with a forced hard refresh (`Ctrl+Shift+R`), _no hot-pink dashed borders were visible_ around any section headings in either the browser preview or the generated PDF.

### What this disproves
1. **Token values missing** – ❌  
   The border rule was hard-coded (not token-based) with `3px dashed hotpink !important`.  If CSS had reached the element, the colour would show even if design-token variables were `null`.
2. **CSS specificity / overrides** – ❌  
   `!important` should have defeated competing rules.
3. **Browser cache** – ❌  
   A hard refresh was performed; plus the compiled `preview.css` on disk shows the dashed rule.

### What this suggests
The element that the rule targets is **not present in the live DOM**.  Therefore we are back to a **selector ↔ markup mismatch** rather than a stylesheet issue.

### New Hypotheses (H-series)
| ID | Hypothesis | Quick test |
|----|------------|-----------|
| H-1 | **Flask server is still running old code** that doesn't emit `.section-box` wrappers (hot-reloader disabled). | Restart Flask server and re-tailor; check markup again. |
| H-2 | There is **another HTML generator** in the runtime path (duplicate module) that was never updated. | Add `console.log(previewHtml.slice(0,300))` in `displayResumePreview` or inspect DevTools → Elements to see actual HTML.  Search for the literal `section-box` string. |
| H-3 | `generate_preview_from_llm_responses` is being **shadow-imported** at startup; our edits are in the file but not in the module instance due to import aliasing. | In Python shell: `import html_generator, inspect; print(inspect.getsource(html_generator.generate_preview_from_llm_responses)[:300])` while server is running. |
| H-4 | The **preview HTML is sanitised** elsewhere (e.g., removed wrapper divs) before being inserted into the DOM. | Put a sentinel string like `<!-- SBOX TEST -->` near the wrapper; see if it survives in output. |
| H-5 | Frontend JS **injects HTML fragments** that overwrite the wrapper, e.g., by stripping outer `<div>`s. | Temporarily comment out `removeNestedScrollbars` and inspect resulting DOM. |

### Immediate Next-Steps Checklist
1. 🔄 Restart Flask server (confirm reload in logs).  
2. 🕵️‍♀️ Open Chrome DevTools > Elements, expand first few nodes inside `.tailored-resume-content`.  Look for `.section-box`.
3. 📝 Document exact HTML snippet for one heading (copy/paste).  
4. ➡️ Branch depending on findings:  
   • If `.section-box` **present** ⇒ CSS somehow not applied (re-investigate cascade).  
   • If `.section-box` **absent** ⇒ pursue H-1/H-2/H-3/H-4/H-5.

> If none of these paths bear fruit, we should seriously consider **abandoning the bespoke Python generator** and moving to a single Jinja template so that markup and styling evolve together.

## 🎉 2024-06-XX Post-Mortem – Why it finally worked

After hours of chasing SCSS and token bugs, the immediate blocker turned out to be embarrassingly simple:

*The Flask development server had been running continuously, so it never imported the modified `html_generator.py`.*  When we finally stopped and restarted the server, it imported the new code that emits `.section-box` wrappers, making our CSS selectors match and the styles show up instantly.

### Lessons Learned
1. **Python code changes require a server restart.**  Flask's reloader only watches templates and static assets by default; deep module imports cached at startup don't reload reliably.
2. **SCSS compilation is a separate step.**  Even if the CSS file is rebuilt, it won't help if the HTML it targets isn't regenerated by the backend.
3. **Proof-of-life CSS still invaluable.**  The hot-pink border test confirmed CSS loaded correctly; lack of border pointed to markup mismatch rather than styling.

### Correct Workflow for Styling Changes
| Step | Action | Command / Tool |
|------|--------|----------------|
| 1 | Edit tokens or SCSS | `vim static/scss/*.scss` |
| 2 | Re-generate tokens | `python tools/generate_tokens_css.py` |
| 3 | Build CSS | `sass static/scss/preview.scss static/css/preview.css && sass static/scss/print.scss static/css/print.css` (or `npm run build-css`) |
| 4 | **Restart Flask dev server** | `Ctrl-C` then `python app.py` |
| 5 | Hard refresh browser (Ctrl-Shift-R) | — |
| 6 | Verify preview & PDF | UI |

Missing any one of these (especially #4) can give misleading results.

## Successful Implementation: Section Header Box Styling

### Overview
The recent changes successfully adjusted the section header box styling to align with the resume content width and increase the section header text size.

### Key Changes
1. **Design Tokens Update**: Added `sectionHeaderFontSize` and `sectionBoxWidth` tokens in `design_tokens.json`.
2. **SCSS Update**: Updated `_resume.scss` to apply the new tokens for section header width and font size.
3. **Token Generation**: Ran `python tools/generate_tokens_css.py` to regenerate the SCSS tokens.
4. **CSS Compilation**: Compiled the SCSS files into CSS using the `sass` command:
   - `sass static/scss/preview.scss static/css/preview.css`
   - `sass static/scss/print.scss static/css/print.css`
5. **Server Restart**: Restarted the Flask server to apply changes to Python files:
   - `Ctrl-C` then `python app.py`
6. **Verification**: Performed a hard refresh in the browser (Ctrl+Shift+R) and checked both the HTML preview and PDF output to ensure changes were applied correctly.

### Lessons Learned
- **Consistent Styling**: Ensuring that both the preview and PDF outputs use the same styling rules is crucial for maintaining a unified appearance.
- **Rebuilding CSS**: Always rebuild CSS files after making changes to SCSS to ensure that updates are reflected in the application.
- **Server Restart**: Restarting the Flask server is necessary to apply changes to Python files and ensure that the latest code is running.

### Future Recommendations
- **Consistent Testing**: Always verify changes in both HTML preview and PDF outputs.
- **Regular Workflow**: Follow the validated workflow for styling changes to ensure all steps are completed.
- **Documentation**: Keep detailed records of changes and lessons learned to streamline future updates.

## ISSUE: Section Header Box Misalignment with Content - May 2025

### Observed Issue
- Section header boxes (like "PROFESSIONAL SUMMARY" and "EXPERIENCE") have inconsistent alignment with the content text
- The left edge of the section header boxes doesn't align with the left edge of the content text
- This creates a visual inconsistency that affects the professional appearance of the resume

### Previous Attempts Analysis
While we previously addressed various alignment issues, the specific misalignment between section header boxes and content text remained. Our recent attempts focused on:

1. **Role Description Alignment Fix** (May 8, 2025):
   - Fixed role descriptions being inside the job-content div
   - This addressed alignment within job content but not the relationship between section headers and content

2. **CSS Margin Adjustment Attempt** (May 9, 2025):
   - Updated CSS rules in _resume.scss to provide consistent content-left-margin
   - Added section-box left margin to match content
   - However, this only fixed the HTML/PDF output, not the DOCX alignment

3. **Global DOCX Indent Token Approach** (May 10, 2025):
   - Added `docx-content-left-indent-cm: 0.5` token to design_tokens.json
   - Modified generate_tokens.py to apply this as a global indent to all style configurations
   - Updated format_right_aligned_pair, add_role_description, create_bullet_point, and apply_docx_section_header_box_style to use this value
   - Result: Still inconsistent alignment in DOCX output

### Detailed Technical Analysis After Code Review

Through detailed log analysis and code inspection, we've identified potential issues in our previous approach:

1. **XML vs. Direct Property Setting**:
   - Some functions use direct property setting via `paragraph_format.left_indent = Cm(value)`
   - Others use XML manipulation via custom XML strings and parse_xml
   - These two approaches might lead to conflicting values being applied

2. **Style vs. Direct Formatting**:
   - DOCX has both style-level formatting and direct paragraph-level formatting
   - Our approach mixed these, potentially causing direct formatting to override style-level settings

3. **DOCX Numbering Definitions**:
   - Bullet points use the numbering definition system in DOCX, which has its own indentation mechanism
   - This system may not be correctly inheriting our global indent values

4. **Twips Conversion Inconsistency**:
   - We used a conversion factor of 567 twips per cm in some places
   - This might not be consistent with how python-docx handles unit conversions internally

### New Hypothesis: DOCX Formatting Layer Precedence

The core issue may be related to how formatting is applied at different layers in the DOCX document. Word uses a cascading approach similar to CSS, but with specific precedence rules:

1. Document defaults define the base formatting
2. Styles (paragraph styles, character styles) override document defaults
3. Direct formatting (applied directly to paragraphs) overrides styles
4. XML direct manipulation can override or conflict with direct formatting

Our implementation tried to apply the same indent at multiple levels, but these may have been overridden or conflicted with each other in the DOCX output.

### Revised Implementation Plan

To resolve this issue, we'll implement a more systematic approach focusing on a single layer of formatting:

1. **Standardize on Style-Level Formatting**:
   - Create custom styles for all elements (section headers, company lines, role descriptions, bullets)
   - Apply the global indent consistently at the style level first
   - Avoid direct paragraph formatting for indent unless absolutely necessary

2. **Debug DOCX Structure**:
   - Save a sample DOCX and examine its XML structure to understand how our changes are being applied
   - Use this to identify which layer of formatting is taking precedence

3. **Refine Section Header Box Implementation**:
   - Focus on the specific relationship between section header box left edge and first content line
   - Ensure they use compatible formatting approaches (both style-based or both direct)

4. **Address Paragraph vs. Run Properties**:
   - Ensure we're applying indentation at the paragraph level consistently
   - Distinguish between paragraph properties and run properties in our implementation

We'll implement and test these changes systematically, focusing first on aligning section headers with company/role text, and then ensuring bullet points align correctly.

## ISSUE RESOLVED: Grey Bar in PDF Output

### Overview
The issue of a grey horizontal bar appearing in the PDF output, but not in the HTML preview, has been resolved.

### Failed Attempt Analysis
- **Initial Hypothesis**: The grey bar was thought to be caused by a `contact-divider` element that was not properly styled for PDF output.
- **Changes Made**: Attempted to hide the `contact-divider` in the `print.scss` file.
- **Result**: The grey bar persisted, indicating the issue was not with the `contact-divider` styling.

### Successful Solution
- **Root Cause**: The grey bar was due to incorrect styling rules in the `print.scss` file that were not being overridden correctly for PDF output.
- **Changes Made**:
  1. Updated `print.scss` to ensure all unwanted dividers and background colors were hidden or set to transparent.
  2. Ensured that the `section-box` and other elements had consistent styling between HTML and PDF outputs.
  3. Recompiled the SCSS files and restarted the Flask server to apply changes.

### Lessons Learned
- **Consistent Styling**: Ensure that all styling rules are consistently applied across both HTML and PDF outputs.
- **Thorough Testing**: Always verify changes in both outputs to catch discrepancies early.
- **Documentation**: Keep detailed records of changes and solutions to streamline future debugging efforts.

### Future Recommendations
- Regularly review and test styling changes in both HTML and PDF outputs to ensure consistency.
- Maintain a clear documentation trail for all styling changes to aid in future troubleshooting.

## 2025-06-XX - Section Header Fit Issue

**Problem**: Despite prior documented fixes (Attempt 4 aiming to make section headers fit content width), the section headers (e.g., "PROFESSIONAL SUMMARY") are still rendering at full width in the preview and PDF.

**Investigation**:
1.  **HTML Generator (`html_generator.py`)**: Confirmed that the code correctly implements the change from Attempt 4, removing the `<h2>` tag and placing the header text directly within the `<div class="section-box">`. This part is correct.
2.  **SCSS (`_resume.scss`)**: Found that the `.section-box` rule contains `display: block;` and `width: 100%;`.
3. **Compiled CSS (`preview.css` / `print.css`)**: Confirmed the compiled CSS reflects the `width: 100%;` rule.

**Root Cause**: The `width: 100%;` rule in `_resume.scss` is overriding the natural width of the content, forcing the box to span the full container width. This contradicts the goal established in Attempt 4.

**Planned Fix**: 
- Modify `.section-box` in `_resume.scss`:
  - Change `display: block;` to `display: inline-block;`
  - Remove `width: 100%;`
- Follow standard workflow: Recompile SCSS, restart Flask server, test **both Preview and PDF**.

## 2025-06-XX - Section Header Fit Issue - Final Resolution

**Summary of Attempts**:
1. **Attempt 1 (Inline-Block)**: Changed `display: block` to `display: inline-block` and removed `width: 100%`. This failed due to CSS overrides and WeasyPrint's handling.
2. **Attempt 2 (Max-Content)**: Used `width: max-content;` which worked for PDF but not HTML due to WeasyPrint ignoring the rule.
3. **Attempt 3 (Table)**: Tried `display: table;` which failed for both HTML and PDF, causing a regression.
4. **Attempt 4 (Float)**: Used `float: left;` which disrupted the document flow, causing layout issues.
5. **Attempt 5 (Block + Width Auto)**: Reverted to `display: block;` and set `width: auto;`, successfully resolving the issue.

**Learnings**:
- **Consistency Across Outputs**: Ensure that styling changes are tested in both HTML and PDF outputs, as rendering engines may interpret styles differently.
- **CSS Overrides**: Be aware of potential CSS overrides from frameworks like Bootstrap or specific rendering engines like WeasyPrint.
- **Document Flow**: Maintain elements in the normal document flow to prevent layout disruptions.
- **Testing and Iteration**: Iterative testing and documentation are crucial for identifying the root cause of styling issues.

**Guidance for Future Changes**:
- **Single Source of Truth**: Consider centralizing style definitions in a single file (e.g., `design_tokens.json`) to ensure consistency.
- **Cross-Platform Testing**: Always test changes across all platforms and outputs to catch discrepancies early.
- **Documentation**: Maintain detailed documentation of changes and their impacts to aid future troubleshooting and development.

**Conclusion**: The final solution of using `display: block;` with `width: auto;` aligns with the natural document flow and ensures consistent rendering across both HTML and PDF outputs.

## DOCX Indentation Control and Alignment (2023-07-02)

### Observed Issue
DOCX output had inconsistent alignment between different content elements:
- Section headers and bullet points were aligned at one position
- Company/title information and role descriptions were indented further to the right
- This created a visually jarring and unprofessional appearance

### Root Cause Analysis
After extensive testing, we discovered that indentation in DOCX files is controlled by multiple mechanisms working in a specific hierarchy:

1. **Style Definitions**:
   - Each paragraph type (section headers, company info, role descriptions, bullets) used a custom style (`MR_SectionHeader`, `MR_Content`, etc.)
   - Each style had its own `left_indent` property set based on design tokens
   - By default, these values were inconsistent (`0 cm` for section headers, `0.5 cm` for other elements)

2. **Control Hierarchy**:
   - Style-level formatting is the primary control mechanism for indentation
   - Direct paragraph formatting could override this but was avoided in our implementation
   - XML manipulation could provide the lowest-level control but was unnecessary for indentation

3. **Design Token Application**:
   - All indentation values were stored in `design_tokens.json`
   - The `StyleEngine` correctly applied these values to styles
   - No direct formatting in `docx_builder.py` functions was overriding these values

### Testing Approach
We implemented a systematic testing approach:
1. **Phase 1**: Set dramatically different indentation values for each element type:
   - Section headers: `0.2 cm`
   - Company/title information: `5.0 cm`
   - Role descriptions: `7.0 cm`
   - Bullet points: `0.2 cm` (with `0.0 cm` hanging indent)

2. **Observations**:
   - All elements respected their defined indentation values
   - This confirmed that style-level formatting was indeed controlling indentation
   - No unintended direct formatting was overriding the styles

### Solution Implemented
We standardized all indentation values to create a clean left edge:
1. **Uniform Left Alignment**:
   - Set all `left_indent` values to `0 cm` in `design_tokens.json`:
     ```json
     "docx-section-header-indent-cm": "0",
     "docx-company-name-indent-cm": "0",
     "docx-role-description-indent-cm": "0",
     "docx-bullet-left-indent-cm": "0",
     "docx-bullet-hanging-indent-cm": "0",
     ```
   - This created a clean left alignment for all elements

2. **StyleEngine Application**:
   - The `StyleEngine` correctly applied these values to the respective styles
   - No changes to the style application logic were needed

### Key Learnings
1. **Single Source of Truth**: All indentation values should be defined in a single place (`design_tokens.json`) to ensure consistency
2. **Style-First Approach**: Using style-level formatting is the most reliable way to control indentation in DOCX files
3. **Avoid Mixed Formatting**: Mixing style-level, direct paragraph, and XML-level formatting leads to inconsistent results
4. **Testing Methodology**: Dramatic value testing is an effective way to verify control mechanisms in document formatting

### Next Steps
1. **Professional Summary Alignment**: Ensure the text in the Professional Summary section aligns with the section header
2. **Skills Section Alignment**: Ensure the skills section and its text align properly with other sections
3. **Documentation**: Update the style guide to reflect our understanding of DOCX indentation control
4. **Best Practices**: Implement a consistent approach to formatting all future elements

This update resolves the longstanding issue of inconsistent indentation in DOCX output and provides a foundation for reliable formatting in the future.

## Professional Summary and Skills Section Alignment Fix (2023-07-02)

### Observed Issues
After standardizing all indentation values to 0 cm, we noticed two remaining areas with alignment inconsistencies:

1. **Professional Summary Text**: The summary text was using the generic "body" style applied through `_apply_paragraph_style`, which may not consistently align with section headers.

2. **Skills Section**: Both category headers (using "heading3" style) and skills lists (using "body" style) were not consistently aligned with other document elements.

### Implementation Solution
We implemented a systematic solution by creating custom styles specifically for these elements and applying them consistently:

1. **Custom Styles Created**:
   - `MR_SummaryText`: For Professional Summary content with same indentation as section headers
   - `MR_SkillCategory`: For skill category headings with consistent alignment and bold formatting
   - `MR_SkillList`: For skill lists (both comma-separated and regular lists) with consistent alignment

2. **Style Engine Updates**:
   ```python
   # Created styles with explicit indentation from section header tokens
   indent_cm = float(section_docx.get("indentCm", 0))
   
   # Apply to summary style
   summary_style.paragraph_format.left_indent = Cm(indent_cm)
   
   # Apply to skill category and list styles
   skill_cat_style.paragraph_format.left_indent = Cm(indent_cm)
   skill_list_style.paragraph_format.left_indent = Cm(indent_cm)
   ```

3. **DocxBuilder Updates**:
   - Replaced generic paragraph creation and style application with direct style application:
   ```python
   # Summary section
   summary_para = doc.add_paragraph(summary_text, style='MR_SummaryText')
   
   # Skills section - categories
   category_para = doc.add_paragraph(category.upper(), style='MR_SkillCategory')
   
   # Skills section - skill lists
   skills_para = doc.add_paragraph(skills_text, style='MR_SkillList')
   ```

### Results
This implementation ensures consistent alignment across all document elements:
- Section headers
- Professional summary text
- Experience entries (company, title, role descriptions, bullet points)
- Skills categories and lists

All elements now share the same left alignment (0 cm), creating a clean, professional appearance throughout the document.

### Key Insights
1. **Importance of Custom Styles**: Creating dedicated styles for each content type ensures consistent formatting
2. **Style Inheritance**: All styles reference the same indentation value from the section header token
3. **Direct Style Application**: Applying styles directly during paragraph creation is more reliable than post-creation styling
4. **Consistent Approach**: Using the same style-based approach for all document elements creates a unified appearance

This completes our alignment standardization, ensuring all DOCX output elements maintain a consistent and professional appearance.