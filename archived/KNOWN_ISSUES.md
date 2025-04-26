# Known Issues

## Styling Changes Not Reflected

### Issue
The styling changes made to the resume application, including boxed section headers, tighter line spacing, and bold positions, are not reflected in the browser preview or PDF output.

### Root Causes
1. **Token Variable Name Mismatch**: The `generate_tokens_css.py` script initially wrote SCSS variables directly from JSON keys with dots, causing undefined variables in SCSS.
2. **SCSS Compilation Issue**: The SCSS compilation pipeline used `python-libsass`, which does not support the modern `@use` syntax.
3. **Missing Token**: The `color.positionBar.bg` token was missing, causing compilation errors.

### Attempted Fixes
1. **Fixed Token Generation**: Modified `generate_tokens_css.py` to convert dots to hyphens in variable names and regenerated `_tokens.scss`.
2. **Installed Dart Sass**: Installed Dart Sass globally to properly handle the `@use` directives in SCSS files.
3. **Added Missing Token**: Added the `color.positionBar.bg` token to `design_tokens.json`.
4. **Recompiled SCSS**: Successfully compiled both the preview and print SCSS files.

### Outcome
Despite these fixes, the styling changes are still not visible in the application. Further investigation is needed to identify any additional underlying issues. 