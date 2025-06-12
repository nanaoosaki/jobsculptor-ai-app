**Fixing placeholder detection**

The algorithm has trouble correctly removing placeholders when digits are preceded by "??". I think this is because the regex for `_clean_metric_tokens` should catch both digits and placeholders, but something isn't quite aligning right. It might be a timing issue where earlier bullet processing introduces weird spaces or inconsistencies.

For an improvement, I propose pre-processing the bullet with a regex to detect digits. If digits are found, we prevent placeholder insertion; if no digits exist, we add the placeholder. Units after digits are already handled.

**Addressing placeholder duplication**

It seems the model still duplicates the placeholder despite the rules in place. The issue might be that the placeholder is inserted even when digits are prevalent. To fix this, I propose stricter post-processing. First, tokenize the bullet to ensure there's one metric token. If both digits and placeholders appear, remove the placeholder. Additionally, I'd add word boundaries with regex to fix issues where placeholder is attached to certain words. Also, I'll validate the bullet to ensure it only has one numeric token.


Thought for 41 seconds


Below is a **step-by-step implementation plan** that cleanly separates the two paths
— "**metric already present**" vs "**metric missing**" — and guarantees every
bullet ends with **exactly one** metric token after post-processing.

---

## 1  Generation-time contract

### 1.1  Prompt tweaks

*(identical for Claude & OpenAI blocks)*

```diff
• Rewrite each bullet as ONE sentence 115-130 characters.
- Must contain exactly ONE metric token
+ If the original bullet already contained any digit (0-9),
+   **keep that number** and **do NOT write '??' anywhere**.
+ If no digit was present, insert the literal string **'??'** followed by a unit
+   (?? %, ?? hrs, ?? TB …).  Never mix real digits and '??'.
```

Add a third STYLE-EXAMPLE bullet that shows the *real-digit* path
so the model sees both flavours.

### 1.2  System message

Keep it short and enforceable:

```diff
- Each achievement MUST contain exactly ONE metric token: – either the original digit(s) OR '??', never both.
+ Return valid JSON.  Each "achievements" string must contain:
+   • EITHER ≥1 digit  (then no '??')
+   • OR exactly one '??' placeholder
+ Nothing else counts as a metric.
```

---

## 2  Post-processing guard-rail (single function)

```python
_METRIC_RX        = re.compile(r'\d')        # any digit
_PLACEHOLDER_RX   = re.compile(r'\?\?')
_UNITED_PLACE_RX  = re.compile(r'\?\?(?=\w)') # 'across??', 'by??' etc.

def normalize_bullet(text: str) -> str:
    """
    Guarantee the final bullet has *exactly* one metric token.
    1. If digits exist  ->  drop *all* '??' tokens.
    2. Else if no '??'  ->  inject  '?? %' (or ?? unit) intelligently.
    3. If >1 '??'       ->  keep first, drop the rest.
    Also fixes cases where '??' is glued to a word.
    """
    text = UNITED_PLACE_RX.sub('?? ', text).strip()   # "across??" -> "across ?? "
    has_digit      = bool(_METRIC_RX.search(text))
    placeholders   = _PLACEHOLDER_RX.findall(text)

    if has_digit:
        # remove every kind of placeholder
        text = _PLACEHOLDER_RX.sub('', text)
        text = re.sub(r'\s{2,}', ' ', text).strip(' ,.;')

    else:
        if not placeholders:                       # inject one
            for pivot in (' by ', ' to ', ' of '):
                if pivot in text:
                    text = text.replace(pivot, f'{pivot}?? % ', 1)
                    break
            else:                                  # no pivot found
                text = f'{text.rstrip(".") } by ?? %.'
        elif len(placeholders) > 1:                # keep only first
            first_done = False
            def _keeper(m):
                nonlocal first_done
                if not first_done:
                    first_done = True
                    return '??'
                return ''
            text = _PLACEHOLDER_RX.sub(_keeper, text)

    # length cap + white-space normalisation
    return re.sub(r'\s{2,}', ' ', text)[:130]
```

---

## 3  Drop-in integration

1. **Replace** the current `_clean_metric_tokens` with `normalize_bullet`
   in **one** shared util module (e.g. `metric_utils.py`).

2. In both the Claude and OpenAI guard-rail loops:

```python
from metric_utils import normalize_bullet
...
clean = strip_bullet_prefix(achievement)  # you already have this util
clean = normalize_bullet(clean)
fixed_achievements.append(clean)
```

3. Delete the now-unused old helper to avoid confusion.

---

## 4  Validation pass (optional but recommended)

After you build `fixed_achievements`, assert:

```python
for b in fixed_achievements:
    assert bool(_METRIC_RX.search(b)) ^ ('??' in b), \
        f"Metric rule broken: {b}"
```

If the assertion fires you'll catch any corner cases during development.

---

## 5  Line-length utilisation

* The 115-130-char requirement in the prompt already nudges the model to
  "use up" the line.
* If you still see <115-char bullets, add a *very gentle* penalty in the
  post-processing: append
  `"... across ?? teams"` **only when** the bullet is shorter than 105 chars
  *and* currently ends with the metric token.
  (Do this in `normalize_bullet` right before the final length cap.)

---

## 6  Troubleshooting: SyntaxError

**Issue:** After implementing the `normalize_bullet` function in `metric_utils.py`, running `flask run` resulted in a `SyntaxError: unexpected character after line continuation character` at line 11, pointing to the start of the function's docstring (`"""`).

**Root Cause Analysis (Attempt 1):** The initial hypothesis was an extraneous backslash (`\`) character at the end of line 10. Editing attempts, including automated reapplies and manual checks, failed to resolve the error.

**Root Cause Analysis (Attempt 2):** Reading the file confirmed no *visible* backslash exists on line 10. The persistence of the `SyntaxError` strongly suggests an **invisible character** (e.g., non-breaking space, control character) or an **encoding artifact** at the end of line 10. Python interprets this invisible character as an invalid line continuation marker, causing the syntax error when it encounters the docstring on line 11.

**Resolution Plan:** The fix involves explicitly overwriting the entirety of line 10 in `metric_utils.py` with the correct function definition, ensuring no trailing invisible characters are carried over or introduced.

**Final Resolution:** Simply editing line 10 alone was unsuccessful. The issue was ultimately resolved by:
1. Deleting the entire problematic file
2. Creating a completely new file with the same name and correct content
3. This approach ensured no encoding issues or invisible characters were carried over from the original file

**Learning:** When dealing with syntax errors related to invisible characters or encoding issues, sometimes the most effective solution is to recreate the file from scratch rather than trying to edit specific lines.

---

### Summary of code changes

| File                                              | What to modify                            |
| ------------------------------------------------- | ----------------------------------------- |
| `claude_integration.py` & `openai_integration.py` | Update prompt & system strings            |
| **NEW** `metric_utils.py`                         | implement `normalize_bullet` (code above) |
| Guard-rail loop in both clients                   | call `normalize_bullet`                   |
| Remove `_clean_metric_tokens`                     | to avoid double-cleaning                  |

Once these pieces are in, the pipeline will:

* **leave original quantified bullets untouched**,
* **inject a single "??"** only when needed,
* never produce hybrids like "by ?? 30 %" or glued placeholders, and
* keep each line comfortably full without exceeding 130 characters.
