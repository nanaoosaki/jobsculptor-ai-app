# Script Dependencies Reference

## Core Dependencies (Key Modules)

```
app.py
  ├── tailoring_handler.py
  │     ├── claude_integration.py
  │     ├── html_generator.py
  │     └── resume_index.py
  ├── upload_handler.py
  │     └── resume_processor.py
  │           ├── llm_resume_parser.py
  │           ├── pdf_parser.py
  │           └── format_handler.py
  ├── job_parser_handler.py
  │     ├── job_parser.py
  │     └── llm_job_analyzer.py
  ├── pdf_exporter.py
  │     └── style_manager.py
  └── docx_builder.py
        ├── word_styles/registry.py
        ├── word_styles/section_builder.py
        └── word_styles/xml_utils.py
```

## Styling System Dependencies

```
design_tokens.json
  ├── style_engine.py
  │     └── style_manager.py
  │           ├── html_generator.py
  │           ├── pdf_exporter.py
  │           └── docx_builder.py
  └── tools/generate_tokens.py
        ├── static/scss/_tokens.scss
        └── static/styles/_docx_styles.json
```

## LLM Integration Dependencies

```
claude_integration.py
  ├── claude_api_logger.py
  ├── token_counts.py 
  ├── metric_utils.py
  └── sample_experience_snippet.py

llm_resume_parser.py
  └── claude_api_logger.py

llm_job_analyzer.py
  └── claude_api_logger.py
```

## Output Format Dependencies

```
HTML Output
  └── html_generator.py
       ├── style_manager.py
       └── metric_utils.py

PDF Output
  └── pdf_exporter.py
       ├── html_generator.py
       └── style_manager.py

DOCX Output
  └── docx_builder.py
       ├── style_manager.py
       ├── style_engine.py
       └── word_styles/
            ├── registry.py
            ├── section_builder.py
            └── xml_utils.py
```

## Processing Dependencies

```
Resume Upload → resume_processor.py → llm_resume_parser.py → JSON
Job Analysis → job_parser.py → llm_job_analyzer.py → JSON
Tailoring → tailoring_handler.py → claude_integration.py → Tailored Resume
```

## File I/O Dependencies

```
Session Data
  ├── static/uploads/temp_session_data/{request_id}_{section}.json
  │     ├── Used by: html_generator.py
  │     └── Used by: docx_builder.py
  ├── static/uploads/api_responses/{section}_response_{timestamp}.json
  │     └── Used by: troubleshooting/debugging
  └── static/uploads/tailored_resume_{request_id}.pdf
        └── Used by: app.py for downloads
```

## Change Impact Analysis

When modifying these modules, consider their dependencies:

1. **High Impact (Many Dependents)**
   - `style_manager.py` (used by multiple output generators)
   - `app.py` (central controller)
   - `design_tokens.json` (styling source of truth)

2. **Medium Impact**
   - `html_generator.py` (affects preview and PDF)
   - `claude_integration.py` (affects all tailoring)
   - `tailoring_handler.py` (orchestrates process)

3. **Isolated Impact**
   - `word_styles/` package (DOCX-specific)
   - `metric_utils.py` (achievement-specific)
   - Utility scripts (limited scope) 