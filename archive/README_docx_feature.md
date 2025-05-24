# DOCX Download Feature

This document provides instructions on how to test the new DOCX download feature.

## Implementation Summary

The following components have been implemented:

1. **Token Generation**: Updated `style_manager.py` and `tools/generate_tokens.py` to support DOCX style mappings
2. **DOCX Builder**: Created `utils/docx_builder.py` to build DOCX files from resume data
3. **Download Route**: Added `/download/docx/<request_id>` route to `app.py`
4. **UI Integration**: Added DOCX download button to the tailored resume view
5. **Testing**: Created `tests/test_docx_builder.py` for unit testing

## Testing Instructions

### 1. Generate DOCX Style Tokens

First, ensure the DOCX style mappings are generated:

```bash
python tools/generate_tokens.py
```

This will create a `_docx_styles.json` file in `static/styles/`. You can verify the file was created with:

```bash
ls -la static/styles/_docx_styles.json
```

### 2. Unit Testing

Run the DOCX builder unit tests:

```bash
python -m tests.test_docx_builder
```

The test will create a temporary DOCX file that you can inspect. The location will be printed in the console output.

### 3. Full Integration Testing

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Upload a resume and tailor it to a job description
3. When the tailoring is complete and you see the preview, you should see both:
   - "Download PDF" button
   - "Download DOCX" button
4. Click the "Download DOCX" button to download the resume in DOCX format
5. Open the downloaded file in Microsoft Word or another compatible application

### 4. Validation Checklist

- [ ] DOCX file downloads successfully
- [ ] Content matches the HTML preview/PDF download
- [ ] Formatting is consistent with HTML/PDF (headings, bullets, etc.)
- [ ] All resume sections are included (contact, summary, experience, education, skills, projects)
- [ ] File opens in Microsoft Word without errors

## Troubleshooting

If you encounter issues:

1. **Missing Dependencies**: Ensure the required libraries are installed:
   ```bash
   pip install python-docx Pillow
   ```

2. **Style Issues**: If styling doesn't match expectations, check the `_docx_styles.json` file and regenerate it:
   ```bash
   python tools/generate_tokens.py
   ```

3. **Cannot Load DOCX**: Check the application logs for errors during DOCX generation

4. **Missing Sections**: Verify the JSON files in the temp_session_data directory for the request

## Next Steps

Future enhancements:

1. Caching generated DOCX files
2. Adding support for embedded images in DOCX
3. Improving bullet point formatting
4. Adding more style customization options