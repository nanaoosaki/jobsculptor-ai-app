# Refactoring Data Workflow for Resume Tailoring

**Goal:** Redesign the data workflow for handling LLM responses and generating resume previews/PDFs to improve robustness, traceability, debuggability, and ensure consistent formatting (specifically addressing bullet point issues).

## Current Issues Recap

*   **Inconsistent LLM Output:** LLM responses vary, sometimes including textual bullet markers (`u2022`, `*`, `-`, etc.) or partial HTML.
*   **Fragile Cleaning:** Cleaning attempts at different stages led to artifacts slipping through or affecting intended CSS formatting.
*   **Overly Complex Transformations:** Previous HTML parsing/regeneration steps were error-prone.
*   **Debugging Difficulty:** Hard to pinpoint where errors (like `u2022` or missing data) are introduced.
*   **Storage Conflicts:** Using fixed filenames (`experience.json`) in `api_responses` is not multi-user safe and mixes raw/processed data.

## Proposed New Data Workflow

This workflow emphasizes clear responsibilities, single-point cleaning, session-specific data handling, and CSS-driven visual formatting.

**1. LLM Interaction (Prompt for Structure, Log Raw)**

*   **Action:** Modify LLM prompts to explicitly request **structured JSON output only**. Discourage inclusion of bullet characters (`u2022`, `*`, `-`) within JSON string values.
*   **Storage/Logging:** Save the **raw, timestamped JSON response** exactly as received from the LLM (e.g., `uploads/api_responses/experience_response_TIMESTAMP.json`). This serves as the ground truth.
*   **Log Message:** `INFO: Received raw LLM response for section [section_name], saved to [raw_file_path].`

**2. Parse & Single Clean (Isolate Responsibility)**

*   **File:** `claude_integration.py` (method: `tailor_resume_content`)
*   **Action:** Parse the raw JSON string from the LLM into a Python dictionary/list.
*   **Action:** Immediately after parsing, apply `utils.bullet_utils.strip_bullet_prefix` **only once** to the relevant string fields (e.g., `achievement` strings, `highlight` strings, `skill` strings, `project detail` strings). This is the sole bullet *cleaning* step.
*   **Log Message:** `DEBUG: Parsed LLM response for [section_name] before cleaning: [parsed_data_structure_preview]`
*   **Log Message:** `DEBUG: Parsed LLM response for [section_name] after cleaning: [cleaned_data_structure_preview]`

**3. Store Cleaned Data (Session-Specific)**

*   **Action:** **Stop** saving cleaned data to fixed files (`experience.json`, `education.json`, etc.) in `api_responses`.
*   **Action:** Store the **cleaned Python data structures** in a way tied to the specific user request/session.
    *   **Chosen Method (Subject to confirmation):** Use temporary session files. Generate a unique ID (e.g., UUID) for the tailoring request. Save cleaned data to `uploads/temp_session_data/[UUID]_[section_name].json`.
    *   *(Alternative: Flask `g` object if generation and rendering are in the same request)*
    *   *(Alternative: Flask session, check size limits)*
*   **Action:** Implement cleanup logic for these temporary files (e.g., on session end, or a periodic task).
*   **Log Message:** `INFO: Stored cleaned, structured data for request [request_id] for section [section_name]. Method: temp_file, Location: [temp_file_path]`

**4. HTML/PDF Generation (Consume Clean Data)**

*   **File:** `html_generator.py` (method: `generate_preview_from_llm_responses`)
*   **Action:** Retrieve the cleaned, structured Python data from its temporary location (using the request/session ID).
*   **Action:** Pass these clean Python structures directly to formatting functions (`format_job_entry`, `format_education_entry`, etc.).
*   **Action:** Ensure formatting functions **do not perform any cleaning**. Their sole role is to wrap clean data in HTML tags and add CSS classes (e.g., `class="bullets"` on `<ul>`).
*   **Action:** Rely **entirely** on CSS (`ul.bullets li::before { content: '• '; }`) for visual bullet points.
*   **Log Message:** `INFO: Generating HTML preview for request [request_id]. Retrieved cleaned data for sections: [list_of_sections].`
*   **Log Message:** `DEBUG: Passing cleaned data to format_job_entry: [job_data_preview]`

## Implementation Steps (Branch: `refactor-data-workflow`)

*(To be filled in as work progresses)*

1.  Modify LLM Prompts (If necessary to discourage bullets).
2.  Implement session-specific temporary file storage for cleaned data in `claude_integration.py`.
    *   Generate UUID for request.
    *   Modify `save_tailored_content_to_json` (or replace) to save cleaned structures to `uploads/temp_session_data/[UUID]_[section].json`.
    *   Remove saving to fixed files (`experience.json`, etc.).
3.  Update `html_generator.py` (`generate_preview_from_llm_responses`) to:
    *   Accept the request UUID.
    *   Load data from `uploads/temp_session_data/[UUID]_[section].json`.
    *   Ensure formatting functions (`format_job_entry`, etc.) only format, no cleaning.
4.  Verify CSS (`_resume.scss`) correctly applies visual bullets via `::before` pseudo-element on `ul.bullets li`.
5.  Add/update logging messages as specified above.
6.  Test thoroughly.
7.  Implement cleanup mechanism for temporary files.

## Observations & Learnings Log

### 2025-04-28: Resolution of 'u2022' Issue in HTML and PDF

**Observation:** The literal text `u2022` appeared in both the HTML preview and PDF output of the experience section.

**Initial Hypothesis:** The issue was suspected to originate from the LLM response or data cleaning process.

**Investigation:**
- Verified that the JSON data was clean and free of `u2022` text.
- Confirmed that the cleaning process in `claude_integration.py` was correctly applied.

**Root Cause:**
- The issue was traced to a CSS rule in both `preview.css` and `print.css` that hard-coded `content: "u2022";` in the `::before` pseudo-element for list items.

**Fixes Implemented:**
- Removed the problematic CSS rule from both `preview.css` and `print.css`.
- Restarted the Flask application to apply changes.

**Learnings:**
- The issue was not with the LLM response or JSON data, but with CSS styling.
- It highlights the importance of considering all layers (data, HTML, CSS) when debugging.
- The hard-coded CSS rule was overlooked initially, emphasizing the need for thorough inspection of all potential sources of an issue.

**Conclusion:**
- The HTML preview and PDF output now correctly display bullet points without the `u2022` text.
- This experience underscores the value of a systematic approach to debugging, ensuring all aspects of the rendering process are considered.

## Success Criteria

*   No textual bullet artifacts (`u2022`, `*`, `-`) appear in the final HTML preview or PDF output.
*   Visually correct bullet points (e.g., `•`) are displayed via CSS for lists in Experience, Projects, etc.
*   The system functions correctly with multiple concurrent users.
*   Logs clearly show the data state transitions.
*   The `api_responses` directory only contains raw, timestamped LLM responses. 