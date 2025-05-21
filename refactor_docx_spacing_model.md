# DOCX Spacing & Header Refactor (`refactor/docx-spacing-model`)

> **Objective**
> Eliminate persistent layout bugs in Word output by *re-architecting* how the generator
> builds section-header styles and manages inter-paragraph spacing.

---

## 0 — Background ↦ Why the rewrite?

| Symptom                                       | Root-cause category                          | Notes                                                                   |
| --------------------------------------------- | -------------------------------------------- | ----------------------------------------------------------------------- |
| Header boxes randomly taller/shorter than PDF | **Line-height mishandling**                  | Conflicting `w:line`, `line_rule`, `paragraph_format.line_spacing`.     |
| Large gaps before headers                     | **Hidden empty `<w:p>`** & style inheritance | Blank paragraphs inherit default `spaceAfter`, escaping our "fix" loop. |
| Fixes don't "stick" in Word for Mac           | **Namespace / compatibility settings**       | Some `<w:*>` attributes dropped unless `{compat}` flags are set.        |

---

## 1 — High-level design shifts

| Old approach                                                                | New approach                                                               |
| --------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Patch spacing **after** building the doc (`_fix_spacing_between_sections`)  | Build **spacing-neutral** paragraphs from the start; no post-hoc pass.     |
| Two helpers (`create_boxed_heading_style`, `apply_*`) that double-set props | **Single source of truth** in a *style registry* object; one writer.       |
| Hard-coded XML fragments sprinkled in python-docx calls                     | A tiny DSL to emit XML nodes ⇒ easier A/B testing of `<w:spacing>` combos. |

---

## 2 — Refactor work-breakdown

### 2.1  Style-Registry

```text
/word_styles/
    __init__.py
    registry.py          # ↤ new – central dict of ParagraphStyle → attrs
    xml_utils.py         # tiny helpers (twips, nsdecls, make_spacing_node, …)
```

* [ ] **Define** `ParagraphBoxStyle` dataclass
  (`name, outline_level, border, padding_twips, line_rule, min_line_twips, keep_with_next`)
* [ ] **Pre-register** `BoxedHeading2` and any variants in `registry.py`.
* [ ] Expose `get_or_create(style_name, doc)` that *idempotently* inserts the style once.

### 2.2  Builder rewrite

*Target files*: `docx_builder.py`, `section_builder.py`

| Step | Action                                                                                                                                                                                                                       |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | Delete legacy `_fix_spacing_between_sections`.                                                                                                                                                                               |
| 2    | New `add_section(doc, text)` →<br>• fetch style from registry<br>• create one **and only one** empty paragraph *before* header with `spaceAfter=0` (guard against double gaps)<br>• header paragraph: `keep_with_next=True`. |
| 3    | Ensure every **content** paragraph sets both `spaceBefore=0` and **token-driven** `spaceAfter` (6 pt).                                                                                                                       |

### 2.3  Test harness

```
/tests/docx_spacing/
    test_line_height_matrix.py   # generates a grid of lineRule/line values
    test_no_blank_paras.py       # asserts no para between text→header
```

* [ ] Fixtures create **scratch** DOCX with 3 headers × 2 paragraphs each.
* [ ] Parse resulting XML, assert:

  ```python
  for p in header_paras:
      assert p.xpath("./w:pPr/w:spacing/@w:before") == ['0']
      assert p.xpath("./w:pPr/w:pBdr")[0].get("w:space") == '20'  # 1pt
  ```
* [ ] Visual diff vs baseline screenshot for smoke CI.

### 2.4  Compatibility flags

* [ ] Inject `<w:compat>` with `<w:compatSetting w:name="ptoNoSpaceBefore" w:val="1"/>`
  to force Word to honor zero-spacing.

---

## 3 — Migration plan

| Day | Task                                                         | Owner | Done-when                                               |
| --- | ------------------------------------------------------------ | ----- | ------------------------------------------------------- |
| D0  | Branch **`refactor/docx-spacing-model`** from latest `main`. | —     | branch pushed                                           |
| D1  | Build Style-Registry skeleton + unit tests.                  | A     | `pytest -q` green                                       |
| D2  | Rewrite section builder; nuke old spacing-fix pass.          | B     | Generated doc shows zero blank paras (manual)           |
| D3  | Integrate DSL XML helpers; tune lineRule matrix.             | A     | Select value with smallest header box in Win & Mac Word |
| D4  | CI: add tests & GitHub action for scratch visual diff.       | C     | PR checks green                                         |
| D5  | Docs: update `STYLE_GUIDE.md` & migration notes.             | D     | Review approved                                         |
| D6  | QA sign-off → merge **squash** → tag `vX.Y.0`.               | Lead  | tag pushed                                              |

---

## 4 — Acceptance criteria

* **Header box height**: *max* 2 pt over text ascender/descender (single-line).
  Verified on Word Win (16) & Word Mac (16).
* **Inter-section gap**: ≤ 6 pt (one CSS‐baseline) between last content line and next header outer border.
* **No hidden paragraphs** between sections (`grep -c "<w:p></w:p>"` == 0).
* All regression tests pass on Linux CI (LibreOffice XML parse) **and** visual diff ≈ 1 px tolerance.

---

## 5 — Risks & mitigations

| Risk                                            | Mitigation                                                                         |
| ----------------------------------------------- | ---------------------------------------------------------------------------------- |
| Word's "auto" line math varies across versions. | Matrix test + pin min-line twips per version; final value chosen by runtime sniff. |
| Registry complicates future theme work.         | Expose `.clone(for_theme)` helper; keeps API stable.                               |
| DSL overkill?                                   | It's \~50 LOC; if abandoned, plain XML strings still work.                         |

---

## 6 — Post-merge clean-ups (backlog)

* Migrate **JobTitleBox** styles into same registry.
* Collapse token look-ups into a `TokenAccessor` wrapper that feeds the registry.
* Add CLI `tools/docx_style_dump.py` to inspect live documents for easier debugging.

---

## 7 — Implementation progress and observations

### 7.1 — What's working

* ✅ **Spacing between sections** is now fixed - logs confirm `tighten_before_headers` is properly handling 17+ section transitions
* ✅ **Empty paragraph removal** is successful - logs show "Removed 5 unwanted empty paragraphs"
* ✅ **Style registry architecture** is functioning as designed with style application and direct formatting working
* ✅ **EmptyParagraph control** is correctly inserted before section headers
* ✅ **BoxedHeading2 style** is being correctly applied to all section headers

### 7.2 — Remaining issues

* ❌ **Section header box styling** - boxes still have incorrect visual appearance (too tall, disproportionate)
* ❌ **Box height not respecting settings** - despite proper XML settings, Word may be interpreting them differently

### 7.3 — Log analysis

```
INFO:word_styles.registry:Style 'BoxedHeading2' already exists in document
INFO:word_styles.registry:Style 'EmptyParagraph' already exists in document
INFO:word_styles.registry:Applied direct formatting from style 'EmptyParagraph' to paragraph
INFO:word_styles.section_builder:Added empty control paragraph before section header
INFO:word_styles.registry:Applied direct formatting from style 'BoxedHeading2' to paragraph
INFO:word_styles.section_builder:Added section header: SKILLS with style BoxedHeading2
INFO:utils.docx_builder:Applied BoxedHeading2 style to section header: SKILLS
...
INFO:word_styles.section_builder:Removed 5 empty paragraphs
INFO:utils.docx_builder:Found 18 section headers
INFO:utils.docx_builder:Fixed spacing: Set space_after=0 on paragraph before section header at index 3
...
INFO:utils.docx_builder:Fixed spacing: Set space_after=0 on paragraph before section header at index 58
```

The logs clearly show that the implementation is applying styles correctly, but the visual output doesn't match expectations.

### 7.4 — Next steps

1. **Deeper issue investigation**:
   - Examine Word's XML interpretation by creating a perfect example in Word directly and saving as DOCX
   - Compare its XML structure with our generated XML
   - Test additional combinations of line rule + line height beyond our initial matrix

2. **More extensive testing**:
   - Isolate the box styling issue with a minimal test document containing only section headers
   - Test with different border options (other than single 1pt)
   - Try alternative approach using shading instead of borders

3. **Platform compatibility**:
   - Verify behavior across Word for Windows, Word for Mac, and Word Online to identify potential platform-specific issues

4. **Fallback options**:
   - Prepare alternative styling approach (table-based headers) as fallback if XML approach can't be made consistent
   - Consider conditional styling based on detected Word version

---

## 8 — Expert Analysis & Box Height Fix

### 8.1 — Current Observations

* **Inter-section gap ✅** – The spacing between content and section headers is fixed 
* **Header-box height ❌** – Section header boxes are still much taller than needed (~10-12pt extra space above and below)

The current implementation successfully fixed external spacing but did not correctly handle the paragraph's internal line box (the height Word allocates for text inside the border).

### 8.2 — Root Cause Analysis

| Attribute                     | What we set               | What Word does                                                    | Visible effect                                                                          |
| ----------------------------- | ------------------------- | ----------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `w:spacing@lineRule`          | **auto**                  | Treats `@line` as ***minimum*** line height                       | Word keeps at least the min value but adds extra leading → too tall                      |
| `w:spacing@line`              | **276 twips** (≈ 13.8 pt) | Same as default 11pt paragraph plus built-in leading              | For a 14pt bold heading, Word still adds its own leading ⇒ ~22-24pt total               |
| Border padding `w:pBdr@space` | 20 twips (1 pt)           | Added **outside** the line box                                    | +1pt top, +1pt bottom                                                                   |

Result: Even with 1pt padding, we end up with ~26pt total height for the boxes.

### 8.3 — Solution Options

| Option                                                                                           | Pros                                                             | Cons                                                                                    | Recommended When                                                 |
| ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| **A. Exact line height**<br>`w:lineRule="exact"` <br>`w:line="fontSize*20"` (or `fontSize+2 pt`) | • Preserves outline level<br>• Minimal code changes<br>• Simpler | • Multi-line headings could get clipped<br>• Must clear paragraph_format.line_spacing   | For our current implementation with paragraph-based borders       |
| **B. Single-row table wrapper** (1×1 table, borders on the cell)                                 | • Perfect auto-sizing<br>• Handles multi-line headings           | • More complex implementation<br>• Requires explicit heading outline level preservation | For bullet-proof pixel-perfect boxes with potential wrapped text  |

### 8.4 — Implementation Plan

For our current paragraph-based approach, the exact line height solution is recommended:

1. **Stop fighting Word with the API line_spacing**
   - Remove any direct manipulation of paragraph_format.line_spacing

2. **Update XML spacing to use EXACT line rule**
   - Change lineRule from "auto" to "exact"
   - Set line height based on font size plus minimal padding (fontSize+1pt)
   - Keep space_before=0 and explicit space_after values
   
3. **Update registry.py**
   - Modify ParagraphBoxStyle defaults for BoxedHeading2 to use "exact" line rule
   - Calculate line height based on font size (font_size_pt + 1.0) * 20

4. **Add acceptance test**
   - Generate a test DOCX with single-line headers
   - Export to PDF and measure rectangle height (should be ≤16pt)

### 8.5 — Updated Acceptance Criteria

* **Header box height**: Total height should be approximately "font size + 2pt border padding" (≈16pt for 14pt font)
* **Inter-section gap**: Maintain current success (≤6pt between content and next header)
* **Multi-line compatibility**: Document behavior with multi-line headings if using exact line height

---

## 9 — Implementation Attempt & Results

### 9.1 — Changes Made

Following o3's analysis and recommendations, we implemented the "exact line height" approach:

1. **Updated `registry.py`**:
   ```python
   # BoxedHeading2 style - Changed from "auto" to "exact" line rule
   self.register(ParagraphBoxStyle(
       name="BoxedHeading2",
       # ...other properties unchanged...
       line_rule="exact",  # Changed from "auto"
       line_height_pt=15.0,  # Changed from 13.8pt to 14pt+1pt
       # ...
   ))
   ```

2. **Modified `xml_utils.py`**:
   ```python
   def make_spacing_node(before=0, after=0, line=None, line_rule="auto", 
                      before_auto=False, after_auto=False):
       # ...
       # Always explicitly set autospacing flags to prevent Word's default behavior
       # For boxed headers we want these OFF to ensure precise control
       if before_auto:
           attrs.append('w:beforeAutospacing="1"')
       else:
           attrs.append('w:beforeAutospacing="0"')
       # ...
   ```

3. **Removed direct `line_spacing` manipulation**:
   ```python
   # Important: Do NOT set line_spacing at the API level to avoid conflicts
   # with the XML spacing node we'll add below
   
   # para_format.line_spacing = 1.0  # <-- This line was removed/commented out
   ```

4. **Created test script**:
   Added `tests/docx_spacing/test_exact_line_height.py` to verify functionality

### 9.2 — Test Results

The test script successfully generated a DOCX file with the following configuration:
```
INFO:__main__:BoxedHeading2 line rule: exact
INFO:__main__:BoxedHeading2 line height: 15.0pt (300 twips)
```

The logs from actual resume generation also showed successful application of styles and proper spacing between sections:
```
INFO:word_styles.registry:Applied direct formatting from style 'BoxedHeading2' to paragraph
INFO:word_styles.section_builder:Added section header: EDUCATION with style BoxedHeading2
INFO:utils.docx_builder:Applied BoxedHeading2 style to section header: EDUCATION
...
INFO:word_styles.section_builder:Removed 5 empty paragraphs
INFO:utils.docx_builder:Fixed spacing: Set space_after=0 on paragraph before section header at index 3
```

However, **visual inspection shows that section header boxes remain too tall**, despite all the XML properties being correctly set according to our logs.

### 9.3 — Observations & Next Steps

Several possible explanations for the persistence of the issue:

1. **Word overriding our settings**: Word may be applying its own internal rules that override our explicit XML settings
2. **XML namespace issues**: Some XML attributes may not be properly recognized due to namespace conflicts
3. **Multiple style definitions**: There might be conflicting style definitions in the document
4. **Inter-platform differences**: Behavior may vary across different versions of Word (Windows vs. Mac)

We recommend two paths forward:

1. **Minimal DOCX generation test** - Create a test that only generates a simple document with one section header using minimal code to eliminate potential interference from other code
2. **Table-based approach** - Implement o3's alternative solution using a single-row table wrapper for section headers which should completely bypass Word's paragraph spacing model

---

## 10 — Why the "exact line-height" experiment failed

### 10.1 — Analysis from o3

| Suspect                       | What we changed                         | What Word actually did                                                                                                                                                     | Evidence                                                                                                                                                                                                                   |
| ----------------------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **XML `<w:spacing>`**         | `lineRule="exact"` `line="300"`         | Word *kept* \~25 pt line box                                                                                                                                               | The physical height didn't shrink even though the XML was correct in the ­.docx we unzipped.                                                                                                                               |
| **Paragraph‐format cache**    | Removed `paragraph_format.line_spacing` | Word sometimes *persists* a cached `lineSpacing` attribute on `<w:pPr>` the **first** time the paragraph object is created; subsequent XML injection doesn't overwrite it. | In the produced XML there is both `<w:spacing … line="300" lineRule="exact">` **and** a latent `<w:lineSpacing w:line="276" w:lineRule="auto"/>` node placed higher by python-docx. Word honours the *first* one it meets. |
| **Default style inheritance** | Tried idempotent style registry         | The base "Heading 2" or "Normal" style still has `spacing lineRule="auto" line="276"`; if you *link* rather than *override* Word merges the two.                           | Header paragraphs show *two* `<w:spacing>` nodes after unpacking.                                                                                                                                                          |
| **Compatibility settings**    | Injected only `ptoNoSpaceBefore`        | Older Word compatibility switches (esp. `overrideTableStyleHps`) are *unset*. Word 16 (Mac) therefore falls back to pre-2003 line-height math.                             | Opening the doc in Win Word 2016 → *slightly* shorter but still too tall; in LibreOffice → perfect.                                                                                                                        |

### 10.2 — Minimal repro that proves the clash

```python
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml

doc = Document()
p = doc.add_paragraph("PROFESSIONAL SUMMARY")
p.style = doc.styles['Heading 2']
p.paragraph_format.line_spacing = None            # ❌ python-docx writes its own node
# Inject our exact line rule
p_pr = p._element.get_or_add_pPr()
p_pr.append(parse_xml(
    f'<w:spacing {nsdecls("w")} w:before="0" w:after="0" w:line="300" w:lineRule="exact"/>'
))
doc.save("min_bug.docx")
```

Unzip → `word/document.xml` shows **two** spacing blocks. Word uses the first one (the one written by python-docx), ignoring ours.

### 10.3 — New hypothesis

> \*\*The border-paragraph approach fails because python-docx **always emits its own `<w:spacing>` when `line_spacing` is *unset*, and Word resolves the first node it sees.**
>
> Unless we dive into python-docx internals to strip that earlier node, any XML we append later will keep being ignored on some Word builds.

---

## 11 — Table-based solution

### 11.1 — Two ways forward

| Path                                                                                                                                                     | What changes                                                        | Risk                                                           | Effort                                |
| -------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------- |
| **A. Monkey-patch python-docx**<br>intercept `_Paragraph._pPr.get_or_add_spacing()` to *remove* existing spacing before we write ours.                   | Keeps single-paragraph-with-borders design.                         | Ties us to a private API; future python-docx update may break. | medium                                |
| **B. Switch to 1 × 1 table wrapper** (the fallback we parked). Word uses table row height = exact content + cell margins, no hidden `<w:spacing>` nodes. | Abandons the buggy line-height code path entirely; no monkey-patch. | Slightly larger XML; need to preserve heading outline level.   | medium-high (write once, then stable) |

Given the hours sunk already, **Path B is safer**.

### 11.2 — Implementation plan

1. **Add `BoxedHeading2Table` to the style registry**

```python
ParagraphBoxStyle(
    name="BoxedHeading2Table",
    wrapper="table",          # new field → builder chooses table route
    border_twips=20,
    padding_twips=20,
    outline_level=1,
)
```

2. **section\_builder.py**

```python
def add_section_header(doc, text):
    style = registry.get("BoxedHeading2Table", doc)
    tbl = doc.add_table(rows=1, cols=1)
    tbl.autofit = False
    cell = tbl.rows[0].cells[0]
    _apply_cell_border(cell, style.border_twips)
    _set_cell_margins(cell, style.padding_twips)
    para = cell.paragraphs[0]
    para.style = doc.styles['Heading 2']          # inherit font etc.
    para.text = text
    _promote_outline_level(para, style.outline_level)
    return tbl
```

3. **Utilities**

```python
def _promote_outline_level(para, level):
    from docx.oxml.ns import qn
    p_pr = para._element.get_or_add_pPr()
    lvl = p_pr.get_or_add_outlineLvl()
    lvl.set(qn('w:val'), str(level))
```

4. **Remove** all paragraph-spacing fiddling for headers; keep it only for *content* paragraphs.

### 11.3 — Updated testing approach

* **Box height test** now checks the `<w:tr>` row height rather than paragraph spacing.
* Visual baseline: header box top/bottom = 1 pt padding ± 1 px.

### 11.4 — Why this will work

* Word's table layout engine **never inserts hidden leading** the way paragraph spacing does; the row shrinks to ascent+descent exactly.
* Cell margin is the only vertical padding and we control it in twips.
* Works identically on Win, Mac, Word Online, and LibreOffice (already validated in quick manual tests by generating a table-wrapped sample).

### 11.5 — Branch name and commit message

We've already renamed the branch to `refactor/docx-header-table-wrapper` to indicate the intention:

> *"Move section headers to 1×1 table wrapper to eliminate Word paragraph-spacing artifacts."*

---

*Updated: May 21, 2025*

---

### Quick-start for devs 👩‍💻

```bash
git switch -c refactor/docx-spacing-model
pip install -r requirements-dev.txt
pytest -q tests/docx_spacing          # fast deterministic suite
python examples/generate_demo.py      # manual Word eyeball
```

---

*Ready for Sonnet 3.7 to sprint on!*
