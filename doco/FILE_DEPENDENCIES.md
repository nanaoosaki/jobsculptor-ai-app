# File Dependencies for Resume Tailoring Application

## Overview
This document outlines the dependencies and interactions between various modules in the resume tailoring application, focusing on the newly implemented `resume_index.py` module.

## resume_index.py

### Purpose
The `resume_index.py` module is responsible for tracking and logging resume processing details. It maintains a simple index of resumes and associated metadata like processing notes and job targeting information.

### Key Functions
- **add_resume**: Adds a resume to the index with metadata.
- **add_note**: Adds a processing note to a resume.
- **add_processing_record**: Adds a processing record to a resume.
- **get_resume_info**: Retrieves information about a resume.

### Interactions
- **tailoring_handler.py**: Utilizes `get_resume_index` to log resumes and processing notes.
- **claude_integration.py**: May interact indirectly by providing data that is logged in the index.

### Dependencies
- **os**: For file path operations.
- **json**: For reading and writing the index file.
- **logging**: For logging operations.
- **datetime**: For timestamping entries.
- **threading**: For ensuring thread safety with locks.

### File Structure
- **resume_index.json**: The default file where the index is stored. It is created in the same directory as `resume_index.py` if not specified otherwise.

## Runtime Reload Caveat
`html_generator.py`, `style_manager.py`, and any other imported Python modules are **only loaded at Flask startup**.  The development reloader detects template changes but *not* deep imports.  After editing these files you must restart the server (`Ctrl-C` then `python app.py`).

## Updated I/O and Workflow

- **Session-Specific Data Storage**: All cleaned resume data is now stored using UUIDs in `static/uploads/temp_session_data/`, ensuring data isolation and multi-user compatibility.
- **Raw LLM Responses**: Continue to be stored with timestamps in `static/uploads/api_responses/` for logging and debugging.
- **Log Messages**: Updated to accurately reflect file operations and enhance traceability.
- **Data Flow**: LLM -> Structured JSON -> Save Structured JSON with UUID -> Load Structured JSON with UUID -> Format to HTML and PDF.
- **PDF Export Process**: Enhanced with WeasyPrint for consistent and professional output, ensuring alignment with HTML preview and inclusion of role descriptions.

## Conclusion
The `resume_index.py` module is a critical component for maintaining a history of resume processing activities, providing valuable insights and traceability for the application. The recent updates ensure a more robust and consistent data handling process, improving both functionality and user experience.

---

## Learnings from Recent Fixes

### Key Learnings:

1. **Understanding Data Types:**
   - Ensure all functions handling data are aware of potential multiple types (e.g., strings, lists, dictionaries) and can process them correctly.
   - Implement type-aware checks to prevent errors like `AttributeError` when methods assume a specific type.

2. **Modular Code Review:**
   - Review all related functions and modules that interact with the data when fixing an issue. Ensure changes in one part of the codebase don't introduce errors elsewhere.

3. **Testing and Validation:**
   - Thoroughly test the application with various inputs after implementing a fix to ensure the issue is resolved and no new issues are introduced.
   - Use logs to trace the flow of data and identify where errors occur.

4. **Documentation:**
   - Keep documentation up-to-date with changes in the codebase, including updating any dependencies or interactions between modules.
   - Documenting solutions and learnings helps future developers understand the context and reasoning behind changes.

---

## Updated Dependencies and Interactions

### sample_experience_snippet.py

#### Purpose
The `sample_experience_snippet.py` script provides example data for the LLM to follow, ensuring consistency in the output of tailored achievements. It includes examples with '??' placeholders to guide the LLM in generating quantifiable achievements.

#### Interactions
- **claude_integration.py**: Utilizes examples from `sample_experience_snippet.py` to improve the consistency and structure of the tailored achievements.

### Optimizations for Quantifiable Achievements

#### Overview
Recent optimizations have focused on ensuring that every achievement bullet point in the experience section contains a quantifiable metric, either as a number or using the '??' placeholder.

#### Key Changes
- **Guardrail Logic**: Updated to inject '??' when no digit or placeholder is present, without relying on unit words or placement tokens.
- **Prompt Optimization**: Emphasizes the action-impact-influence structure, generating concise and structured achievements with a character limit of 130 characters.
- **Example Inclusion**: Examples with '??' in `sample_experience_snippet.py` provide a pattern for the LLM to follow, improving the consistency of the output.

#### Implications
- **Structured Output**: Future optimizations should focus on clear, structured prompts with explicit rules, maintaining a balance between flexibility and strict guidelines.
- **System Message Reinforcement**: Reinforcing key rules in the system message can further improve compliance with the desired output format.
- **Post-Processing Checks**: Implementing post-processing checks, such as assertions for character limits, can serve as an additional safeguard to catch any deviations from the expected output.

## Token Generation Script

### tools/generate_tokens_css.py

- Purpose: Reads `design_tokens.json` and writes SCSS variable definitions to `static/scss/_tokens.scss`.
- Input: `design_tokens.json` (design tokens for colors, spacing, margins, fonts, etc.).
- Output: `static/scss/_tokens.scss` containing SCSS `$` variables that are imported by other SCSS files.
- Usage: Run `python tools/generate_tokens_css.py` whenever `design_tokens.json` changes to regenerate token variables.

### SCSS Compilation Workflow

1. Regenerate Tokens:
   - Run `python tools/generate_tokens_css.py` to update `_tokens.scss`.
2. Compile SCSS:
   - Use Sass to compile SCSS to CSS:
     ```bash
     sass static/scss/preview.scss static/css/preview.css
     sass static/scss/print.scss static/css/print.css
     ```
3. Restart Server:
   - Restart the Flask dev server (`Ctrl-C` then `python app.py`) to load updated templates and CSS.

This workflow ensures that design token edits (including margin and padding adjustments) propagate through the SCSS build and into both the HTML preview and PDF output.

--- 