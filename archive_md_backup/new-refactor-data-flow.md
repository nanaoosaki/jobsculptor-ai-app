# Refactoring Plan: Session-Based Data Storage for Resume Tailoring

**1. Objective:**

Eliminate the use of fixed filenames (e.g., `contact.json`, `experience.json`) for storing *cleaned* resume data during the tailoring process. Implement session-specific storage using unique request IDs (UUIDs) to ensure multi-user compatibility and prevent data overwrites. Raw LLM responses will continue to be stored with timestamps for logging and debugging purposes.

**2. Key Changes Overview:**

*   Generate a unique request ID (UUID) for each tailoring operation.
*   Define a dedicated temporary directory for session data (e.g., `static/uploads/temp_session_data/`).
*   Store cleaned, processed resume sections in temporary files named `[UUID]_[section_name].json` within this directory.
*   Modify data saving logic (`claude_integration.py`) to use session-specific filenames for *cleaned* data, while keeping timestamped raw responses in `api_responses`.
*   Modify data loading logic (`html_generator.py`) to read from session-specific filenames using the request UUID.
*   Adapt relevant route handlers (`app.py`, `tailoring_handler.py`) and frontend JavaScript (`main.js`) to manage and pass the request UUID.
*   Implement or outline a strategy for cleaning up temporary session files.

**3. Detailed Implementation Steps:**

*   **Step 3.1: Introduce Request ID (UUID)**
    *   **File:** `tailoring_handler.py` (within the main function handling the tailoring request).
    *   **Action:** Import the `uuid` module: `import uuid`.
    *   **Action:** Generate a unique `request_id = str(uuid.uuid4())` at the beginning of the tailoring process.
    *   **Action:** Pass this `request_id` as an argument to downstream functions, specifically `claude_integration.py.tailor_resume_content` (or equivalent).
    *   **Logging:** Add `logging.info(f"Starting tailoring process with request_id: {request_id}")`.
    *   **Return Value:** Ensure the `request_id` is returned by the handler function so the calling route (`app.py`) can use it (e.g., for generating preview/download links or storing in session).

*   **Step 3.2: Create Temporary Storage Directory**
    *   **File:** `app.py` (or an initialization module like `config.py`).
    *   **Action:** Define the path, potentially using Flask app config: `TEMP_SESSION_DATA_PATH = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_session_data')`. Make sure `UPLOAD_FOLDER` is correctly configured.
    *   **Action:** Add code during application startup (`if __name__ == '__main__':` block or factory function) to check if `TEMP_SESSION_DATA_PATH` exists and create it if not: `os.makedirs(TEMP_SESSION_DATA_PATH, exist_ok=True)`.
    *   **(Optional):** Consider adding `static/uploads/temp_session_data/` to `.gitignore`.

*   **Step 3.3: Modify Saving Logic for Cleaned Data**
    *   **File:** `claude_integration.py` (within `tailor_resume_content` and/or helper functions responsible for saving processed sections).
    *   **Action:** Modify the function(s) responsible for saving the *final, cleaned* section data (after LLM response parsing and cleaning). These functions must now accept the `request_id` as an argument.
    *   **Action:** Define the base path: `temp_data_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp_session_data')` (use `current_app` if inside request context, or pass path from config).
    *   **Action:** Determine the filename: `cleaned_filepath = os.path.join(temp_data_dir, f"{request_id}_{section_name}.json")`.
    *   **Action:** Save the cleaned data (Python dictionary/list) as JSON to `cleaned_filepath`.
    *   **Action:** **Remove** the existing code that saves cleaned data to fixed filenames like `os.path.join(api_responses_dir, f"{section_name}.json")`.
    *   **Action:** **Confirm** that the existing logic for saving *raw*, timestamped LLM responses (e.g., `experience_response_TIMESTAMP.json`) to the `api_responses` directory remains unchanged.
    *   **Logging:** Update log messages: `logging.info(f"Saved cleaned {section_name} content for request {request_id} to {cleaned_filepath}")`.

*   **Step 3.4: Modify Loading Logic for HTML/PDF Generation**
    *   **File:** `html_generator.py` (within functions like `generate_preview_from_llm_responses`, `generate_pdf_html`, or helper `load_section_data`).
    *   **Action:** Modify the function(s) responsible for loading section data to accept the `request_id` as an argument.
    *   **Action:** Define the base path: `temp_data_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp_session_data')`.
    *   **Action:** Construct the expected filepath: `section_filepath = os.path.join(temp_data_dir, f"{request_id}_{section_name}.json")`.
    *   **Action:** Load the JSON data from `section_filepath`. Handle potential `FileNotFoundError` gracefully.
    *   **Action:** Remove any fallback logic that attempts to load from the old fixed filenames (`contact.json`, etc.).
    *   **Logging:** Update log messages: `logging.info(f"Loading cleaned {section_name} data for request {request_id} from {section_filepath}")`.

*   **Step 3.5: Adapt Route Handlers and Function Calls**
    *   **File:** `app.py` (routes like `/tailor-resume`, and potentially new routes for preview/download based on ID) and `tailoring_handler.py`.
    *   **Action:** In the `/tailor-resume` route (POST), after calling the `tailoring_handler` function and receiving the `request_id`:
        *   Decide how to make the `request_id` available for subsequent preview/download requests:
            *   **Option A (Return to Frontend):** Include `request_id` in the JSON response to the frontend.
            *   **Option B (Flask Session):** Store `request_id` in `session['current_request_id'] = request_id`. Requires Flask session setup (secret key).
    *   **Action:** If using Option A, modify frontend JavaScript (`static/js/main.js`) to receive the `request_id` and use it to construct URLs for subsequent GET requests (e.g., `/preview/<request_id>`, `/download/<request_id>`).
    *   **Action:** Create or modify routes (e.g., `/preview/<request_id>`, `/download/<request_id>`) in `app.py`:
        *   These routes will extract the `request_id` from the URL (or retrieve from Flask `session` if using Option B).
        *   Pass the `request_id` to `html_generator.generate_preview_from_llm_responses` or similar functions.
    *   **Action:** Review and update function signatures throughout the call chain (`app.py` -> `tailoring_handler.py` -> `claude_integration.py` -> `html_generator.py`) to ensure `request_id` is passed where needed.

*   **Step 3.6: Temporary File Cleanup Strategy**
    *   **Action:** Define and document the chosen cleanup strategy.
    *   **Recommendation (for later implementation):** Implement a scheduled task (e.g., using Flask-APScheduler or a separate cron job/scheduled task) that runs periodically (e.g., daily) and deletes files in `TEMP_SESSION_DATA_PATH` older than a configured duration (e.g., 24 hours).
    *   **Initial Step:** Document that cleanup is needed and perhaps add a placeholder function or a manual cleanup note in the README.

*   **Step 3.7: Testing**
    *   **Action:** Perform thorough testing:
        *   Single user tailoring workflow.
        *   Simulate concurrent users (e.g., multiple browser tabs making requests simultaneously).
        *   Verify correct data isolation – each user should see their own tailored content.
        *   Verify file creation: Check `temp_session_data` for `[UUID]_[section].json` files.
        *   Verify file absence: Check `api_responses` to ensure fixed files (`contact.json`, etc.) for *cleaned* data are no longer created/updated.
        *   Verify raw responses: Ensure `*_response_TIMESTAMP.json` files are still created in `api_responses`.
        *   Verify HTML preview and PDF download functionality using the `request_id`.
        *   Review application logs for correct `request_id` usage and file path logging.

**4. Documentation:**

This plan is documented in `new-refactor-data-flow.md`. Update project README or other relevant documentation to reflect the new workflow and the temporary data storage location.

**Fixes and Changes Implemented:**

- Corrected misleading log messages in `html_generator.py` to accurately reflect the use of UUID-based filenames for loading cleaned data.
- Ensured that all cleaned data is saved and loaded using session-specific UUIDs in `static/uploads/temp_session_data/`.
- Verified that raw LLM responses continue to be saved with timestamps in `static/uploads/api_responses/` for debugging purposes.
- Updated the logging to provide clear and accurate information about file operations, enhancing traceability and debugging.
- Confirmed that the application workflow aligns with the refactor plan, ensuring data isolation and multi-user compatibility. 