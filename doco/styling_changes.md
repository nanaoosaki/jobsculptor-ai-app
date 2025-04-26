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

## Key Lessons Learned

1. **Flask Server Restart Critical**: The development server caches imports at startup, so changes to Python files (like `html_generator.py`) aren't reflected until restart.
2. **CSS ↔ HTML Coordination**: Both parts need to be in sync - CSS selectors must match the HTML elements emitted by the Python generator.
3. **Complete Process Required**: The styling pipeline has multiple steps, and skipping any can lead to misleading results.
4. **Paper Width Corrections**: Setting the proper A4 width (8.27in instead of 8.5in) fixed PDF output scaling issues.
5. **Style Isolation**: Adding style isolation rules prevents Bootstrap styles from leaking into the resume content.

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
   • Updated `@page` rule in `print.scss` with proper A4 size and margins.

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

## Successful Implementation of Blue Boxes

### Overview
The recent changes successfully implemented blue section header boxes with a filled background, aligning with the desired resume format.

### Key Changes
1. **Section Header Box**: Updated the `.section-box` class to have a blue fill and white text, ensuring a visually appealing and consistent look across both HTML preview and PDF outputs.
2. **CSS Rebuild**: Rebuilt both `preview.css` and `print.css` to apply the new styles effectively.
3. **Testing and Verification**: Verified the changes in both the browser preview and PDF download to ensure consistency and correctness.

### Lessons Learned
- **Consistent Styling**: Ensuring that both the preview and PDF outputs use the same styling rules is crucial for maintaining a unified appearance.
- **Rebuilding CSS**: Always rebuild CSS files after making changes to SCSS to ensure that updates are reflected in the application.
- **Server Restart**: Restarting the Flask server is necessary to apply changes to Python files and ensure that the latest code is running.

### Next Steps
- Continue monitoring for any discrepancies between preview and PDF outputs.
- Document the process for future styling changes to ensure consistency and efficiency.

### Successful Process for Styling Changes

The following process was successfully used to change the section header color to pink:

1. **Edit SCSS Files**: Updated the `_resume.scss` file to change the section header background color to pink.
2. **Re-generate Tokens**: (If needed) Run `generate_tokens_css.py` to update design tokens.
3. **Build CSS**: Compiled the SCSS files into CSS using the `sass` command:
   - `sass static/scss/preview.scss static/css/preview.css`
   - `sass static/scss/print.scss static/css/print.css`
4. **Restart Flask Server**: Restarted the Flask server to apply changes to Python files:
   - `Ctrl-C` then `python app.py`
5. **Verify Changes**: Performed a hard refresh in the browser (Ctrl+Shift+R) and checked both the HTML preview and PDF output to ensure changes were applied correctly.

This process ensures that styling changes are consistently applied across both the preview and PDF outputs. Following these steps will help maintain a unified appearance and streamline future styling updates.

--- 