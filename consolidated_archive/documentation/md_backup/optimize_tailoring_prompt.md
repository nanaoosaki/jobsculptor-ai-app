**Optimizing prompt modifications**

I need to refine the prompt for clearly structured achievements that meet specific criteria. This includes using a strong verb, quantifiable impact, and influence related to the ideal candidate. To keep it concise, I could limit each achievement to one sentence with a character or token limit (say 120 characters). A good approach might be adding a specific template or structure, such as "\[Action] | \[Impact] | \[Influence]"", and asking for concise, bulleted outputs. This would keep each response short and focused.


Thought for 10 seconds


Below is a surgical edit that keeps the overall structure of your current **experience-section** prompt but tightens the "achievements" clause so the model:

* **stays under a character cap** (pick the number that prints cleanly in your layout—I use 130 below);
* always shows an **action → quantifiable impact → influence/strategy** arc;
* never invents facts beyond the original bullet.

---

### 1  Where to patch

Inside `tailor_resume_content()` you already build the long f-string for the experience prompt.  Replace the **achievements** sub-instruction block (and the matching item in the "IMPORTANT" list) with the version below. Nothing else needs to change.

```python
# --- replace ONLY this part of the prompt template ---
2.  For the "achievements":
    • Rewrite EACH achievement as **one sentence ≤ 130 characters**.  
    • Sentence must follow the pattern  
      "**<Strong Verb>** + original core fact → **numbered outcome** → **who/what it influenced**".  
      – strong verb & influence must reference the job's requirements/ideal-candidate traits.  
      – numeric outcome (%, $, #) must be truthful to the underlying résumé fact; do **not** invent data.  
    • If the original bullet lacks a metric, infer a reasonable one **only if** a figure is present elsewhere in the entry; otherwise keep it qualitative but concise.  
    • Do not add new bullets, split bullets, or remove existing bullets.
```

Then update the "IMPORTANT" checklist so the fourth item becomes:

```
4. Each achievement must obey the 130-character limit and the action-impact-influence structure above.
```

Putting the hard rules here (rather than buried lower in the prompt) keeps them inside the model's short-term buffer when it starts generating.

---

### 2  Why this works

1. **Explicit token budget** – The character (or token) ceiling is clear and measurable, so models like GPT-4o and Claude-3 tend to self-truncate before reaching it.

2. **Ordered micro-template** – The *verb → metric → influence* recipe limits wander-off prose while still giving the model flexibility to choose verbs and emphasise relevant skills.

3. **Ground-truth safeguard** – "Do **not** invent data" plus the fallback rule for missing metrics keeps hallucination risk low.

4. **Positioning** – Stating these rules immediately before generation (not at the top of the file) and echoing them in the IMPORTANT list raises their salience in the model's working context.

---

### 3  Optional extra guardrails

* **System message reinforcement**
  Change the existing system prompt to:

  ```
  You are an expert resume tailor. Return ONLY valid JSON in the specified format. 
  Each "achievements" item must be a single sentence ≤ 130 characters.
  ```

  Because the system role has top priority, this doubles the chance the model will comply.

* **Post-filter assertion**
  After you parse the JSON, run a quick Python check:

  ```python
  for job in experience:
      assert all(len(a) <= 130 for a in job["achievements"]), "Over-length bullet detected"
  ```

  If any assertion fails, log it and either trim or ping the LLM for a retry with a harsher temperature/`max_tokens`.

---

Implementing that single prompt swap (and, if you like, the two optional reinforcements) keeps the rest of your pipeline untouched while giving you crisp, size-bounded, criteria-focused achievements.

## Consolidated Optimization Strategies for Quantifiable Achievements

### Overview
This document consolidates the strategies and patches applied to optimize the prompt for quantifiable achievements in the resume tailoring application. The goal is to ensure that every achievement bullet point in the experience section contains a quantifiable metric, either as a number or using the '??' placeholder.

### Guardrail Logic
- **Injection of '??'**: The guardrail logic ensures that every achievement bullet point includes a quantifiable metric. If no digit or placeholder is present, '??' is injected without relying on unit words or placement tokens.
- **Prompt Optimization**: The prompt emphasizes the action-impact-influence structure, generating concise and structured achievements with a character limit of 115-130 characters.
- **Example Inclusion**: Adding an example with '??' in `sample_experience_snippet.py` provides a pattern for the LLM to follow, improving the consistency of the output.

### Patches for Numeric Achievements
- **Real Numbers and Placeholders**: The LLM keeps any real numbers that already appear in the résumé bullet. If no metric is present, a placeholder '??' is used, signaling to the user to replace it with the true figure.
- **Stable JSON**: The use of '??' as plain text ensures that JSON parsing and downstream code remain unaffected.

### What Didn't Work
- **Previous Attempts**: Earlier attempts that relied on detecting unit words or specific placement tokens ('by', 'to', 'of') were not effective, as they missed cases where these tokens were absent.
- **Over-reliance on Model**: Initially, there was an over-reliance on the model to infer metrics, which led to inconsistent results. The explicit guardrail logic was necessary to enforce the presence of a metric.

### Implications for Future Optimization
- **Structured Output**: Future optimizations should focus on clear, structured prompts with explicit rules, maintaining a balance between flexibility and strict guidelines.
- **Prompt Positioning**: Placing critical instructions close to the generation point in the prompt helps maintain their salience in the model's working context.
- **System Message Reinforcement**: Reinforcing key rules in the system message can further improve compliance with the desired output format.
- **Post-Processing Checks**: Implementing post-processing checks, such as assertions for character limits, can serve as an additional safeguard to catch any deviations from the expected output.

#### Additional Improvements from `improvements_quantifiable_achivements.md`
- **Strict Metric Token Rule**: The prompt now strictly enforces exactly one metric token per achievement, either a real number or '??', but never both.
- **Character Limit Adjustment**: The character limit for achievements has been adjusted to 115-130 characters to ensure fuller lines and prevent over-injection of placeholders.
- **Example with Real Numbers**: A third example in the style block demonstrates a bullet with a real number without any '??', providing a clear pattern for the model.
- **Guardrail Enhancements**: The guardrail logic has been enhanced to remove '??' when real digits are present and to inject '??' only when no numeric value is found, ensuring the "exactly one" rule is maintained.

Overall, the combination of prompt optimization and robust guardrail logic has proven effective in achieving structured and quantifiable achievements in the resume tailoring application.

### Addressing the Injection Issue

#### Overview
The fallback logic in `_clean_metric_tokens` was causing an injection of "by ?? %" without checking for existing punctuation. This was resolved by adjusting the logic to inject before any terminal punctuation, ensuring cleaner sentence boundaries.

#### Fix Details
- **Regex Handling**: The fallback logic now uses regex to split off trailing punctuation, allowing the placeholder to be inserted correctly before the punctuation.
- **Example**: Before: "Architected batch-compute systems, preventing outages." After: "Architected batch-compute systems, preventing outages by ?? %."

#### Optional Polishing
- **Bullet Stripping**: Ensure bullets are stripped before calling `_clean_metric_tokens`.
- **Space Normalization**: Normalize double spaces after final truncation.

#### Prompt Update
- **Metric Placement Hint**: Added a hint to prefer placing the metric immediately after the quantified verb phrase, not as a tail clause.

These changes ensure that the injection of "by ?? %" is handled gracefully, maintaining sentence integrity and readability.

---

### 4  Post-Processing Injection Fix

The fallback logic in the bullet normalization function can glue "by ?? %" after existing terminal punctuation. To ensure the placeholder is inserted **before** any final `.`, `!`, or `?`, replace the fallback block in your post-processing guardrail (`_clean_metric_tokens` or `normalize_bullet`) with the snippet below:

```python
# --- fallback: append before trailing punctuation ------------------------
if not injected:
    # Split off a trailing punctuation mark, if any
    m = re.match(r'^(.*?)([.!?])?$', text.strip())
    core, punct = m.group(1), m.group(2) or ''
    # add placeholder, then restore the punctuation
    text = f'{core} by ?? %{punct}'
    logger.info(f"Cleaned metric: injected placeholder before punctuation: {text}")
# ------------------------------------------------------------------------
```

What it does:
1. Captures a terminal punctuation mark (if present) with a simple regex.
2. Inserts the placeholder **before** the punctuation, preserving sentence boundaries.
3. Maintains the final length cap (e.g., `text[:130]`).

**Optional polishing:**
- Ensure bullets are stripped before calling normalization.
- After truncation, normalize multiple spaces:

  ```python
  text = re.sub(r'\s{2,}', ' ', text)[:130]
  ```

**Prompt hint:**
Add the following to your LLM prompt to encourage correct placement:

```
❏ Prefer placing the metric immediately after the quantified verb phrase
  (e.g., "... reducing latency by ?? % across ..."), not as a tail clause.
```

---



