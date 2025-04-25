# Single-Source Styling Implementation Plan

## Objective
To centralize and streamline the styling of the resume tailoring application, ensuring consistent and maintainable design across both HTML preview and PDF outputs.

## Baseline Inventory (1 dev-hour)
- Enumerate every file that outputs or mutates CSS:
  - `static/css/styles.css`, `static/css/pdf_styles.css`
  - Inline blocks in `html_generator.py`, `pdf_exporter.py`
  - Width tweaks in `static/js/main.js`
- List all class names used by the resume HTML (`resume-section`, `contact-section`, etc.).
- Confirm which filenames are imported by WeasyPrint (log `self.css_path`).

Outcome → inventory doc so nothing is accidentally orphaned.

## 1. Introduce Design Tokens (4 hrs)
1.1 Create `design_tokens.json` (or `.yaml`) at repo root:
```json
{
  "contentWidth": "95%",
  "contentPadding": "0.5in",
  "pageMargin": "1.5cm",
  "primaryColor": "#4a6fdc",
  ...
}
```

1.2 Add a tiny build helper `tools/generate_tokens_css.py`:
```python
import json, pathlib, sys
TOKENS = json.load(open('design_tokens.json'))
with open('static/css/_tokens.scss', 'w') as f:
    for k, v in TOKENS.items():
        f.write(f"${k}: {v};\n")
```
- This script runs pre-commit or via `npm/Makefile`.

## 2. SCSS Refactor (5 hrs)
2.1 Break CSS into three compilable SCSS files:
```
static/scss/
  _tokens.scss       (generated)
  _base.scss         (typography, layout vars, shared classes)
  preview.scss       (imports _tokens.scss, _base.scss, adds UI chrome)
  print.scss         (imports _tokens.scss, _base.scss, adds @page + PDF tweaks)
```

2.2 Compile to:
```
static/css/preview.css   ← replaces styles.css
static/css/print.css     ← replaces pdf_styles.css
```
(Use dart-sass via `npm` or `libsass-python`; choose whichever is CI-friendly.)
- Keep **existing class names** → no HTML changes needed, avoiding any risk to resume job/LLM I/O.

## 3. Centralised StyleManager (Python) (4 hrs)
`app/style_manager.py`
```python
from pathlib import Path
import json

class StyleManager:
    _TOKENS = json.load(open(Path(__file__).with_name('../design_tokens.json')))
    @classmethod
    def token(cls, key): return cls._TOKENS[key]

    @classmethod
    def preview_css_path(cls):
        return str(Path(__file__).with_name('../static/css/preview.css').resolve())

    @classmethod
    def print_css_path(cls):
        return str(Path(__file__).with_name('../static/css/print.css').resolve())
```
Used by both `html_generator.py` and `pdf_exporter.py`.

## 4. Update Python Emitters (3 hrs)
4.1 `html_generator.py`
- Remove the huge inline `<style>` block.
- Inject only:
```html
<link rel="stylesheet" href="/static/css/preview.css">
```
(Flask will serve the static file.)

4.2 `pdf_exporter.py`
- Replace custom inline CSS with:
```python
css = CSS(filename=StyleManager.print_css_path(), font_config=self.font_config)
```
- Keep a **minimal** inline stub only if WeasyPrint cannot load externals in some environments (rare).

## 5. Remove JS Width Hacks (30 min)
- Delete the lines in `static/js/main.js` that set `style.width|maxWidth = '95%'`.
- Confirm preview still renders correctly (it will, because CSS handles width).

## 6. Build / CI Integration (2 hrs)
- Add an NPM script or Makefile target:
```
npm run build-css   # sass static/scss/preview.scss static/css/preview.css
                    # sass static/scss/print.scss   static/css/print.css
python tools/generate_tokens_css.py
```
- GitHub Actions: on push → run build script, fail if compiled CSS differs (guards devs from editing compiled output directly).

## 7. Regression Test Suite (3 hrs)
- Use Playwright (Python) headless:
  1. Post a dummy resume + job → generate preview HTML.
  2. Snapshot `.tailored-resume-content` bounding-box width → assert ≥ 90 % of A4.
  3. Trigger PDF export → open PDF with `pdfplumber` or compare file size checksum.

- Add unit test that every token in `design_tokens.json` is referenced in at least one SCSS file (prevents dead vars).

## 8. Migration & Backward Compatibility (2 hrs)
- Keep old `styles.css` / `pdf_styles.css` for one release cycle but de-reference them.
- Emit console warning if legacy CSS path is requested.

## 9. Documentation & Onboarding (1 hr)
- `STYLING_OVERVIEW.md`
  - Diagram of token flow JSON → SCSS → preview/PDF.
  - "How to change padding in one place."
  - Build command cheatsheet.

## 10. Timeline & Resourcing
Total dev effort ≈ 22 hrs → 3 working days for one engineer, or 2 days with CSS+Python paired.

## Risk & Mitigation
- **CSS cache busting**: add query-string `?v=${hash}` on `<link>` tag.
- **WeasyPrint external stylesheet**: Works fine when provided absolute path; fallback to inline if environment blocks filesystem reads.
- **Token drift**: locked by CI diff test.
- **Parsing/tailoring I/O**: untouched—HTML class names stable, JSON flows unchanged.

## Value Delivered
- One true set of measurements & colours → tweak once, propagate everywhere.
- Zero inline CSS duplication.
- Clean separation of preview vs print.
- No JavaScript styling hacks.
- Safer, faster future styling changes with visual test coverage.

Implementing this plan converts the hard-coded-everywhere width fix into a maintainable, token-driven architecture—ensuring future format tweaks are literally "change one JSON value, re-build CSS, done."

## Results
- HTML preview successfully loads `preview.css` and applies centralized styling tokens.
- Inline styles and JavaScript width hacks removed; full content width now controlled by SCSS.
- PDF generation uses `print.css` via StyleManager; PDF layout matches the HTML preview in A4 format.
- Verified consistent appearance in browser preview and exported PDF output.

## Learnings and Progress

- Successfully centralized styling using design tokens and SCSS, ensuring consistent styling across HTML and PDF outputs.
- Removed inline styles and JavaScript width hacks, leading to a cleaner and more maintainable codebase.
- Implemented a single-source styling architecture that allows for easy updates and modifications.

## Solutions Implemented

- Created `design_tokens.json` to store all visual constants, ensuring a single source of truth for styling.
- Developed a `StyleManager` class to manage and apply styles consistently across different outputs.
- Refactored CSS into SCSS files, separating concerns and improving maintainability.
- Ensured consistent application of styles across HTML preview and PDF generation, resulting in a unified appearance. 