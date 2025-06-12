Thought for 5 seconds


Below is a tight patch you can drop into **both** the Claude and OpenAI prompt builders (the *experience* branch) so the LLM:

* keeps any **real numbers** that already appear in the résumé bullet,
* otherwise writes the metric as a **placeholder** using “`??`”, e.g. “increased ARR by ?? %,”
* signals clearly to the user that they should swap the placeholder for the true figure.

I show the replacement block plus the small “IMPORTANT” line you must also edit.
Nothing else in your pipeline needs to change—the JSON schema, parsing, and file-saving all stay the same.

---

### 1  Replace the “achievements” instruction block

```python
# -------------- OLD (condensed) -----------------
# 2.  For the "achievements":
#     • Rewrite EACH achievement as one sentence ≤ 150 characters …
# ------------------------------------------------

# -------------- NEW -----------------------------
2.  For the "achievements":
    • Rewrite **each** bullet as **one sentence ≤ 150 characters**.  
    • Sentence pattern → **<Strong Verb> → quantifiable outcome → influence/strategy**.  
    • **If the original bullet ALREADY contains a number or percent**, preserve it.  
    • **If no metric is present**, insert a placeholder written as **"??"** followed by the
      unit, e.g. **"increased revenue by ?? %"** or **"saved ?? hrs / week"**.
      – Do **not** fabricate specific values.  
      – The user will replace "??" later.  
    • Do not add, delete, or split bullets; keep facts faithful to the original résumé.
```

### 2  Edit the matching “IMPORTANT” checklist line

Change item 4 (or whichever number you now use) to:

```
4. Each achievement must be ≤ 150 characters and follow the verb-metric-influence template,
   using "??" as the metric if no real number exists in the source bullet.
```

*(Keep the other IMPORTANT rules the same.)*

### 3  (Optionally) reinforce in the system prompt

If you want an extra guardrail, append this to the **system** message you already send:

```
Always use "??" as the metric placeholder when the original text has no numeric value.
```

Because the **system** role overrides the user role, the model is less likely to forget.

---

### 4  Why this satisfies your new policy

* **Grounded data** – the LLM never invents numbers; it either re-uses existing ones or writes “??”.
* **User editability** – placeholders make the missing metric obvious and searchable.
* **Stable JSON** – “??” is plain text, so your JSON parsing and downstream code are unaffected.
* **Conciseness** – the 150-character ceiling remains, ensuring bullets print cleanly.

Drop those two text edits into the prompt template inside `tailor_resume_content()` for both clients, redeploy, and you’re done.
