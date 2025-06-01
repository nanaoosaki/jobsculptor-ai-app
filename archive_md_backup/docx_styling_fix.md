**Providing debugging guidance**

The user’s described issue seems to involve misalignment and missing styling elements, especially a section header box. To assist, I'll suggest a debugging approach. First, I'd recommend analyzing the underlying XML of the docx files, as python-docx has limitations with styling directly. I’ll guide them step by step, explaining methods like adjusting "style" elements and manually fixing XML nodes. Given the technical nature, I can provide specific instructions and a plan to resolve the formatting and alignment issues effectively.


Thought for 10 seconds


A good way to think about the problem is that Word really doesn’t “render” a paragraph until three separate layers of instructions all agree:

1. the style definition in **styles.xml**
2. any *direct* paragraph properties (pPr) you hang on the paragraph
3. the run-level properties inside each run (rPr)

Whenever the same attribute shows up in more than one of those layers, Word will use the *last* one it sees in the XML tree – which is almost never the order you expect when you mix the python-docx API with manual XML injections.  The visual symptoms you’re seeing (headers losing their borders / backgrounds and content drifting to the left) are classic “style overwritten by later direct formatting” problems.

Below is a debugging drill that surfaces where the overrides are happening, followed by the smallest set of changes that usually fixes the layout.

---

### ❶  Prove to yourself which layer is winning

1. **Generate two one-page DOCX files** from the same JSON:

   * *A* – your normal pipeline, with *all* style, direct and XML tweaks.
   * *B* – a stripped build in which you **only** attach a named style to every paragraph and do *nothing* else (no `paragraph_format`, no XML pBdr, no run-level tweaks).  Ten lines of conditional logic in `docx_builder` can toggle this.
2. Unzip both files (`unzip A.docx -d A/` etc.) and open the two **document.xml** files side-by-side.  Search for your “PROFESSIONAL EXPERIENCE” text – the paragraph tag will be obvious.
3. Compare the `<w:pPr>` blocks.  If the stripped build shows your border/shading XML but the full build doesn’t, the extra formatting is clobbering the pPr you need.  If *both* show the XML yet Word still hides the box, the style definition in **styles.xml** is absorbing a later override.

Nine times out of ten you’ll discover that the pPr in the full build is missing your `<w:pBdr>` or `<w:shd>` elements.

---

### ❷  Lock the style in one place – then stop touching it

A reproducible pattern is:

* create *one* paragraph style called, say, **MR\_SectionHeader**
* give it **all** the decoration you want – border, shading, 0 cm indent, spacing, run properties – directly in `create_docx_custom_styles()`
* mark the style as *basedOn="Normal"* and *qFormat="1"*; don’t set `basedOn` to Heading 1 or anything that already has its own border
* **turn off** every bit of direct formatting later:

```python
para = doc.add_paragraph(style='MR_SectionHeader')
para.alignment = WD_ALIGN_PARAGRAPH.LEFT   # OK – alignment is paragraph-only
# DO NOT call para.paragraph_format.* for indent/spacing
# DO NOT inject XML here – it will overwrite the style’s pPr
run = para.add_run(header.upper())         # run-level bold if you need it
run.bold = True
```

Word now sees a single `w:pPr` coming from the style and leaves it alone.

---

### ❸  Indent the rest of the resume relative to that fixed zero point

* In **design\_tokens.json** define only *one* left indent (e.g. `contentIndentCm: 0.63`).
* Give **MR\_Content**, **MR\_Bullet**, **MR\_RoleDescription** that same left indent in the *style definition* – *not* via `para.paragraph_format.left_indent`.
* For bullets: set `w:ind w:left="X" w:hanging="360"` in the bullet paragraph style and remove all list-level tweaks from code; python-docx respects style list properties when you specify `style="List Bullet"`.

With every paragraph referencing a style that already holds the correct indent, nothing in the code needs to know numbers – and nothing will fight the header.

---

### ❹  Border/shading still not showing?  Three things to test in isolation

1. **Color value** – Word ignores the tag if it can’t parse the color.  Use uppercase hex and no leading “#”.
2. **Size units** – border size (w\:sz) is in eighths of a point; for a 0.5-pt rule use `w:sz="4"`.
3. **Element order** – inside `<w:pPr>` the *entire* border block must precede `<w:shd>` or Word sometimes drops the shade.  Easiest: build a sample file in Word with the exact border you want, unzip, copy the ordering.

---

### ❺  A quick validation script

Add this to `utils/docx_debug.py`:

```python
def dump_pprops(docx_path, text_snippet, context=30):
    from zipfile import ZipFile
    from lxml import etree
    with ZipFile(docx_path) as z:
        xml = z.read('word/document.xml')
    root = etree.fromstring(xml)
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    for p in root.xpath('.//w:p', namespaces=ns):
        if text_snippet in ''.join(p.itertext()):
            print(etree.tostring(p.find('w:pPr', ns), pretty_print=True).decode())
            print('-' * 60)
```

Run it on both A and B; you’ll see immediately which properties disappear.

---

### ❻  If you need the box to stretch *edge-to-edge*

Paragraph borders stop at the paragraph margin.  If the left margin of content is 0.63 cm and the header margin is 0, your rule will always be shorter.  Two ways around it:

* **table trick** – put the header in a one-row, one-cell, borderless table; apply the rule to the **table**; set `tblInd` to negative half-margin to overhang.
* **text box** – Word’s drawingML shapes can span full width; python-docx can’t build them, but `python-docx-template` can merge them from a .dotx.

Most people accept the header being flush with content rather than page edge, so start by aligning everything to the same left indent.

---

### ❼  When nothing else works

Export a “good” sample from Word, paste the XML into `styles.xml` at runtime, and point your paragraphs at that style – no API, no guessing.  It’s heavy-handed but bullet-proof.

---

### Suggested next experiment

1. Comment-out *all* `paragraph.paragraph_format` calls in `docx_builder`.
2. Generate file B (style-only).  If the box shows up and everything aligns, you’ve proved the override theory.
3. Re-enable direct formatting one attribute at a time until the box disappears – that’s your offender.

Keep that failing file for diffing; after two or three passes you’ll know exactly which call or XML helper sabotages the pPr.

Once you have a minimally-styled, correctly-rendered document, you can layer back only the direct tweaks that are genuinely impossible in style definitions (e.g., mixed inline emphasis).

Feel free to paste a small failing XML snippet here if the border still vanishes after the clean-style test—we can diagnose the specific OOXML element ordering next.
