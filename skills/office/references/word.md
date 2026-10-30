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

Chinese, Japanese and Korean text: `run.font.name` sets only the Latin font. The East Asian font is a separate attribute:

```python
from docx.oxml.ns import qn
run.font.name = "Noto Sans CJK SC"
run._element.rPr.rFonts.set(qn("w:eastAsia"), "Noto Sans CJK SC")
```

A font name does not guarantee the font is installed; the engine reports missing fonts when rendering.

```python
from docx import Document

document = Document()
document.add_heading("Project report", level=0)
document.add_paragraph("Summary", style="Heading 1")
document.add_paragraph("The findings go here.")
table = document.add_table(rows=1, cols=2)
table.style = "Table Grid"
table.rows[0].cells[0].text = "Item"
table.rows[0].cells[1].text = "Value"
document.save("report.docx")
```

## Checking

Reopening the saved file with python-docx confirms the requested content and formatting, and that content meant to stay unchanged did. Styling, spacing, sizing or alignment edits are confirmed visually with a render.
