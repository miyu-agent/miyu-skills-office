# Word documents (.docx)

python-docx creates and edits .docx files. It does not paginate or render; pages and layout come from the engine (`engine.md`).

## Editing

- A target is found by its text or position; only its runs and formatting need inspecting. A title can be an ordinary paragraph with no Title style.
- Assigning `paragraph.text` replaces all runs and drops their formatting. Changing the text of the relevant runs keeps it.
- Rebuilding a document loses features python-docx does not model (tracked changes, comments, content controls, some fields). Untouched parts survive when the original file is loaded and saved, not recreated.
- Ordinary replacements, colored text and comments are different things from tracked changes.
- Writing package parts directly: a new ZIP with each unchanged member copied once. Appending a replacement member to an existing ZIP duplicates the name and corrupts the file.

## Creating

Paragraph styles carry headings and body text. Tables are sized for the section that holds them; merged cells and nested tables change cell counts.

Chinese, Japanese and Korean text: `run.font.name` sets only the Latin font. The East Asian font is a separate attribute; `officestyle.set_fonts(run_or_style)` sets both, or by hand:

```python
from docx.oxml.ns import qn
run.font.name = "Noto Sans CJK SC"
run._element.rPr.rFonts.set(qn("w:eastAsia"), "Noto Sans CJK SC")
```

Line spacing given as a multiple makes CJK lines taller than Latin ones (their fonts have taller line metrics); an "at least" spacing in points keeps lines even, which is what `officestyle` uses.

```python
import sys
sys.path.insert(0, "<this skill>/tools")
import officestyle
from docx.shared import Pt

document = officestyle.new_document()          # A4, Arial + 微软雅黑, plain headings
document.add_paragraph("Project report", style="Title")
document.add_heading("Summary", level=1)
document.add_paragraph("The findings go here.")
table = document.add_table(rows=3, cols=2)
for r, (item, value) in enumerate([("Item", "Value"), ("Revenue", "18"), ("Cost", "7")]):
    table.cell(r, 0).text, table.cell(r, 1).text = item, value
officestyle.style_table(table)                 # light rules, shaded header, padding
document.add_paragraph("After the table.").paragraph_format.space_before = Pt(8)
document.save("report.docx")
```

A paragraph right after a table has no gap above it unless `space_before` is set.

## Checking

Reopening the saved file with python-docx confirms the requested content and formatting, and that content meant to stay unchanged did. Styling, spacing, sizing or alignment edits are confirmed visually with a render.
