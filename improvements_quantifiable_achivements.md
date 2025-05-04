### Why the **experience** bullets still slip through

Your new guard-rail *is* running, but its “inject the `??`” block fires **only when three conditions are true simultaneously**:

1. no digit is present,
2. `"??"` isn’t already present, **and**
3. *no* “unit word” is detected **and** one of the *placement* tokens (`" by "`, `" to "`, `" of "`) *is* found.

The problem bullets (`“… reducing query time and improving cost efficiency.”`) meet #1 & #2,
but they **fail #3** – there is no `by / to / of`, so the placeholder never gets injected.

---

## Targeted fixes

| #                               | what to change                                                              | why / details                                                                                                                                                 |
| ------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1**                           | **Remove the placement-token requirement** when you fall back to appending. | If no `by / to / of` is found just append `" by ?? %"`.                                                                                                       |
| **2**                           | Broaden / drop the `unit word` whitelist.                                   | “time”, “latency”, “speed”, “accuracy” are not in your list, so they block the injection test. Safest: if there is **no digit and no ‘??’**, inject — period. |
| **3**                           | Strip bullets **before** metric checks, not inside them.                    | The leading “•” stopped the regex `^\d` in some variants. You did that, but only inside the loop for strings; move it to the very top of the loop.            |
| **4**                           | Move the 130-char truncation **after** injection *and* strip-bullet.        | Otherwise the newly-added “ by ?? %” can be chopped off.                                                                                                      |
| **5**                           | Add an assert at the end of the guard-rail.                                 | \`\`\`python                                                                                                                                                  |
| for ach in fixed\_achievements: |                                                                             |                                                                                                                                                               |

```
assert re.search(r'(?:\d|\\?\\?)', ach), f"metric missing: {ach}"
```

````
  In dev you can raise; in prod you can log-warning and append `" by ?? %"`. |
| **6** | Put a working `??` example in `EXPERIENCE_STYLE_EXAMPLE`. | LLMs copy patterns they see. |

---

## Minimal code patch (inside the guard-rail loop)

```python
clean = re.sub(r'^[•\-\u2022\*]\s*', '', achievement).strip()

has_digit       = bool(re.search(r'\d', clean))
has_placeholder = "??" in clean

if not has_digit and not has_placeholder:
    # <-- we don’t care about unit words any more
    if " by " in clean:
        clean = clean.replace(" by ", " by ?? ", 1)
    elif " to " in clean:
        clean = clean.replace(" to ", " to ?? ", 1)
    elif " of " in clean:
        clean = clean.replace(" of ", " of ?? ", 1)
    else:
        clean = f"{clean} by ?? %"

# final safety: guarantee one metric token
if not re.search(r'(?:\d|\\?\\?)', clean):
    clean = f"{clean} by ?? %"

clean = clean[:130]                              # truncate last
fixed_achievements.append(clean)
````

*(Apply the same block in both the Claude and OpenAI branches.)*

---

### No prompt / temperature tweak needed

The model is already instructed correctly; this change simply **guarantees** every bullet meets the rule even when the model forgets. After the patch you should see, e.g.:

```
• Optimized ETL processes with Spark, reducing query time by ?? % and improving cost efficiency.
```

If you still spot bullets without a metric, the end-of-loop `assert` will flag them immediately, making further debugging trivial.
