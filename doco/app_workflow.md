# Resume Tailoring Application Workflow

## Quick Reference Diagram

```
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  User Upload  │    │  Job Analysis │    │   Tailoring   │
│   (Resume)    │───▶│  (Job Post)   │───▶│   Process     │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│resume_processor│    │ job_parser.py │    │claude_integrat│
│  → parsed JSON │    │  → job JSON   │    │  → tailored   │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
                     ┌───────────────┐
                     │HTML Generation│     ┌───────────────┐
                     │Preview Display│────▶│ PDF Export    │
                     └───────┬───────┘     └───────────────┘
                             │
                             │             ┌───────────────┐
                             └────────────▶│ DOCX Export   │
                                           └───────────────┘
```

## Key Process Flows

### 1. Resume Upload & Parsing

```
User → app.py → upload_handler.py → resume_processor.py → [DOCX/PDF] → llm_resume_parser.py → JSON
```

### 2. Job Analysis

```
User → app.py → job_parser_handler.py → job_parser.py → llm_job_analyzer.py → JSON
```

### 3. Tailoring Process

```
User → app.py → tailoring_handler.py → claude_integration.py → [Section JSONs]
                                    → html_generator.py → Preview HTML
```

### 4. Export Options

```
PDF: HTML → pdf_exporter.py → WeasyPrint → PDF File
DOCX: Section JSONs → docx_builder.py → word_styles → DOCX File
```

## File Relationships

### Core Files
- **app.py** → Central controller
- **tailoring_handler.py** → Tailoring orchestration
- **claude_integration.py** → LLM integration
- **html_generator.py** → HTML preview generation

### Input Processing
- **upload_handler.py** → File management
- **resume_processor.py** → Resume parsing
- **job_parser_handler.py** → Job parsing

### Output Generation
- **pdf_exporter.py** → PDF creation
- **docx_builder.py** → DOCX creation

### Styling System
- **design_tokens.json** → Style definitions
- **style_manager.py** → Style application
- **word_styles/** → DOCX-specific styling

### Utility System
- **claude_api_logger.py** → API logging
- **metric_utils.py** → Achievement metrics
- **token_counts.py** → Token usage 