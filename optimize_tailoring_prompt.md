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

## Progress and Attempts in Optimizing Prompt for Quantifiable Achievements

### Overview
We successfully implemented changes to ensure that every achievement bullet point in the experience section contains a quantifiable metric, either as a number or using the '??' placeholder. This was achieved by refining the prompt and guardrail logic in `claude_integration.py`.

### What Worked
- **Guardrail Logic**: The updated guardrail logic from `improvements_quantifiable_achivements.md` was effective in ensuring that every achievement bullet point includes a quantifiable metric. The logic now injects '??' when no digit or placeholder is present, and it does so without relying on unit words or placement tokens.
- **Prompt Optimization**: The prompt was optimized to emphasize the action-impact-influence structure, which helped in generating concise and structured achievements. The character limit was set to 130 characters, ensuring brevity and focus.
- **Example Inclusion**: Adding an example with '??' in `sample_experience_snippet.py` provided a pattern for the LLM to follow, improving the consistency of the output.

### What Didn't Work
- **Previous Attempts**: Earlier attempts that relied on detecting unit words or specific placement tokens ('by', 'to', 'of') were not effective, as they missed cases where these tokens were absent.
- **Over-reliance on Model**: Initially, there was an over-reliance on the model to infer metrics, which led to inconsistent results. The explicit guardrail logic was necessary to enforce the presence of a metric.

### Implications for Future Optimization
- **Structured Output**: The success of the current approach suggests that future optimizations should continue to focus on clear, structured prompts with explicit rules. This includes maintaining a balance between flexibility and strict guidelines to ensure the model generates the desired output.
- **Prompt Positioning**: Placing critical instructions close to the generation point in the prompt helps maintain their salience in the model's working context.
- **System Message Reinforcement**: Reinforcing key rules in the system message can further improve compliance with the desired output format.
- **Post-Processing Checks**: Implementing post-processing checks, such as assertions for character limits, can serve as an additional safeguard to catch any deviations from the expected output.

Overall, the combination of prompt optimization and robust guardrail logic has proven effective in achieving structured and quantifiable achievements in the resume tailoring application.



