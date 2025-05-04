**Addressing the injection issue**

I’m analyzing an issue with a string's punctuation. It seems like the fallback logic is causing an injection of "by ?? %" without checking if there's already a punctuation mark, like a period, at the end. This happens when appending to the string without properly accounting for sentence boundaries. To fix this, I’ll include logic to check punctuation before adjusting the string—for example, by using an if statement within the code to ensure the adjustment happens before the period. I'll also use regex for cleaner punctuation handling.


Thought for 19 seconds


The extra *“, by ?? %.”* happens only in the **fallback branch** of `_clean_metric_tokens`:

```python
# current fallback
text = f'{text} by ?? %'   # ← punctuation in the original string is still there,
                           #   so “ by ?? %” is glued on *after* the final period
```

When no pivot word (“ by ”, “ to ”, “ of ”) is present the function simply
concatenates the placeholder to the **very end** of the sentence, ignoring any
existing terminal punctuation.
That is why you see “… hybrid clouds, by ?? %.” – the full stop that was
already there remains, and the new chunk lands in front of it.

---

### Fix — inject **before** the final punctuation

Replace the *fallback* block inside `_clean_metric_tokens` with the snippet
below (do the same in both the Claude- and OpenAI-side helpers):

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

**What it does**

1. Captures a terminal `.`, `!`, or `?` (if present) with a regex.

2. Builds `core + " by ?? %" + punctuation`.
   *Example:*
   • *before*: `"Architected batch-compute systems, preventing outages."`
   • *after*:  `"Architected batch-compute systems, preventing outages by ?? %."`

3. Keeps the total length cap (`return text[:130]`) after the injection.

---

### Optional polishing

* Strip possible “*, –, •*” bullets **before** calling `_clean_metric_tokens`
  (you already do this, just ensure it’s outside the metric test so it always
  runs).
* After the final truncation, normalise double spaces:

  ```python
  text = re.sub(r'\s{2,}', ' ', text)[:130]
  ```

---

### Update the prompt (minor)

Add one more hint so the LLM itself aims to place the metric **inside** the
impact clause instead of at the very end. For instance:

```
❏ Prefer placing the metric immediately after the quantified verb phrase
  (“… reducing latency by ?? % across …”), not as a tail clause.
```

(But the deterministic post-processor above guarantees correctness even when
the model forgets.)

Implementing the small regex tweak removes the dangling *“by ?? %”* problem
without needing additional clean-up passes or higher-temperature retries.
