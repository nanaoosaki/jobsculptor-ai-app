**Providing script recommendations**

I think the script could integrate the example by including it as a demonstration, or providing it as a few-shot example. The existing structure expects content in JSON, so no code changes would be necessary if it's parsed earlier. If the user wants to show the style of achievements rewriting, including the example as part of the prompt might work well. I could suggest adding an "example\_experience" parameter and placing it before the instructions in case they want to follow that approach.


Thought for 10 seconds


Below is an opinionated—but drop-in—way to weave the sample experience list into **`claude_integration.py`** so it acts as a mini “style card” for Claude (or GPT-4o) every time you tailor the *experience* section.

---

## 1  Put the sample data somewhere Claude can see it

Create a tiny helper module—or just a const string—so your main class can import it without cluttering up the prompt logic. Example:

```python
# file: sample_experience_snippet.py   (new file, same package)
EXPERIENCE_STYLE_EXAMPLE = """
[
  {
    "company": "Instagram",
    "position": "ML Tech Lead, Growth & Growth Science",
    "dates": "2016 – 2018",
    "achievements": [
      "Scaled MAU from 400 M to 1.1 B by shipping ranking-ML revamp",
      "Founded Growth Science team; built analytics that cut experiment cycle time 40 %"
    ]
  },
  {
    "company": "TikTok",
    "position": "General Manager, Pangle",
    "dates": "Feb 2023 – May 2024",
    "achievements": [
      "Turned Pangle into TikTok’s first break-even unit; managed 500-person org",
      "Drove $ X B advertiser spend across 100 K accounts through ML-driven optimisation"
    ]
  }
]
""".strip()
```

*Keep it short—two jobs is enough to seed the pattern while keeping token cost negligible.*

---

## 2  Patch the prompt builder

Open **`ClaudeClient.tailor_resume_content()`** (the *experience* branch) and insert the example right before you ask for the output. The diff below is conceptual—you can paste it literally.

```python
# at top of file
from sample_experience_snippet import EXPERIENCE_STYLE_EXAMPLE
```

````python
if section_name == "experience":
    experience_json_input = json.dumps(content, indent=2)

    prompt = f"""
You are an expert resume tailoring assistant …

ORIGINAL EXPERIENCE SECTION (JSON):
```json
{experience_json_input}
````

JOB REQUIREMENTS:
{requirements\_text}

REQUIRED SKILLS:
{skills\_text}{analysis\_prompt}

### STYLE EXAMPLE – do **NOT** copy facts, only copy structure, brevity and verb–impact–influence pattern

```json
{EXPERIENCE_STYLE_EXAMPLE}
```

### OUTPUT SPEC

Return your response as a JSON object **exactly** like:

```json
{{
  "experience": [
    {{
      "company": "Company Name",
      …
    }}
  ]
}}
```

Rewrite rules:

1. For `"role_description"` …
2. For `"achievements"` … (your 150-char rule here)
   …
   """

````

### Why put the example above “OUTPUT SPEC”?  
Models read top-to-bottom; giving them the concrete target style *before* the instructions amps up conformity, while “OUTPUT SPEC” still pins the schema.

---

## 3  Keep an eye on token cost

* Two short entries cost ~120 tokens. With a typical 8 K-context model you have plenty of head-room, but if you ever feed very large résumés, consider:

```python
EXAMPLE_ALLOWED = max(0, 500 - len(json.dumps(content)))  # crude budget
if EXAMPLE_ALLOWED < len(EXPERIENCE_STYLE_EXAMPLE):
    example_block = ""           # drop the example if input is huge
else:
    example_block = EXPERIENCE_STYLE_EXAMPLE
````

then interpolate `example_block`.

---

## 4  Optional: make it configurable

If you anticipate A/B-testing different examples, expose a kw-arg in `tailor_resume_content()`:

```python
def tailor_resume_content(self, section_name, content, job_data,
                          style_example: str = EXPERIENCE_STYLE_EXAMPLE):
```

and use `style_example` in the prompt f-string. Higher-level code can supply `""` (empty) to turn it off.

---

### Result

* Claude now receives: original résumé chunk ➜ job context ➜ short exemplar ➜ hard instructions.
* The exemplar shows *how short*, *how numeric*, *how leadership-oriented* each achievement should be—no extra post-processing code required.

That single prompt tweak is usually enough to lock models into the concise, action-metric-influence format you want, while the rest of your pipeline (JSON parsing, saving, etc.) stays unchanged.
