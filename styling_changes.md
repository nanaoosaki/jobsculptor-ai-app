# Implementation Plan for Styling Changes

## Goal
Enhance the resume styling to include:
1. Tighter line spacing
2. Boxed section headers
3. Bold font for positions, titles, locations, and time periods

## Phase 0 – Safety / Prep

A. Create a new branch:
   ```bash
   git checkout -b style/tight-lines-boxed-headers
   ```

B. Run the CSS build to ensure the pipeline is clean:
   ```bash
   python tools/generate_tokens_css.py
   python -m sass static/scss/preview.scss static/css/preview.css
   python -m sass static/scss/print.scss static/css/print.css
   ```

## Phase 1 – Token Upgrades

File: `design_tokens.json`

1. Tighter default line height:
   ```json
   "font.lineHeight.normal": 1.4,
   "font.lineHeight.tight": 1.25,
   ```

2. Section header box colors & border:
   ```json
   "color.sectionBox.border": "#3A3A3A",
   "color.sectionBox.bg": "#FFFFFF",
   ```

3. Bullet / list rhythm:
   ```json
   "space.section.y": "0.55rem",
   "space.bullet.y": "0.15rem"
   ```

4. Bold weight token:
   ```json
   "font.weight.bold": 700
   ```

## Phase 2 – Regenerate SCSS Variables

Execute:
```bash
python tools/generate_tokens_css.py
```

## Phase 3 – Core Resume SCSS Changes

File: `static/scss/_resume.scss`

1. Expose the new line-height token:
   ```scss
   $line-height-tight: $font-lineHeight-tight !default;
   ```

2. Apply tighter line height:
   ```scss
   .tailored-resume-content {
       line-height: $line-height-tight;
   }

   .job-content li,
   .education-content li,
   .project-content li,
   .contact-section p {
       line-height: $line-height-tight;
   }
   ```

3. Section Header "Box" style:
   ```scss
   .section-box {
       margin: $space-section-y 0;
       padding: 0.35rem 0.6rem;
       border: 1px solid $color-sectionBox-border;
       background: $color-sectionBox-bg;
       font-weight: $font-weight-bold;
       text-transform: uppercase;
       letter-spacing: 0.5px;
   }
   ```

4. Bold weight for metadata lines:
   ```scss
   .position-bar {
       .role,
       .company-name,
       .institution,
       .project-title,
       .degree,
       .dates,
       .location {
           font-weight: $font-weight-bold;
       }
   }
   ```

5. Tighten bullet spacing:
   ```scss
   ul.bullets li { margin-bottom: $space-bullet-y; }
   ```

6. Ensure the print stylesheet mirrors these overrides.

## Phase 4 – Re-compile CSS

```bash
python tools/generate_tokens_css.py
python -m sass static/scss/preview.scss static/css/preview.css
python -m sass static/scss/print.scss static/css/print.css
```

## Phase 5 – Template Check

Ensure `templates/resume_pdf.html` emits the correct structure for SCSS rules to take effect.

## Phase 6 – QA Checklist

1. Browser preview – visually inspect:
   - Section headers show boxed style
   - Lines look ~10–15% tighter
   - Position / company / location / dates are bold
   - Margins & page width unchanged

2. PDF export – compare side-by-side with preview.

3. Run unit / visual diff tests if configured.

4. Ensure `design_tokens.json` passes JSON linting.

## Phase 7 – Commit for Review

```bash
git add design_tokens.json static/scss/_resume.scss static/css/*
git commit -m "Tighter leading, boxed section headers, bold meta text (token-based)"
```

Open a pull request and ping reviewers.

## Roll-back Plan

Use `git revert <commit>` or `git reset --hard` to restore the prior look instantly. 