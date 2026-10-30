---
name: office
description: "Create, read, edit and check Word (.docx), PowerPoint (.pptx) and Excel (.xlsx) files; render pages to images, export to PDF, recalculate formulas. Bundles its own Python and LibreOffice engine. 写 Word、做 PPT、Excel 表格、转 PDF."
metadata:
  display_name: Office documents
  summary: Word, PowerPoint and Excel files, with rendering and PDF export
  display_name_zh: Office 文档
  summary_zh: 写、读、改 Word、PPT、Excel，渲染成图、导出 PDF
---

# Office documents

This folder carries a complete runtime. Nothing needs to be installed, and the system Python is not involved.

## Runtime

Paths below are relative to this folder (the folder holding this `SKILL.md`).

| What | Linux, macOS | Windows |
|---|---|---|
| Python 3.12 with python-docx, python-pptx, openpyxl, XlsxWriter, pandas, numpy, Pillow, lxml | `runtime/python/bin/python3` | `runtime\python\python.exe` |
| LibreOffice engine (render, PDF, recalculate) | `<python> tools/dsoffice.py <command> …` | same |
| Default look for new files | `tools/officestyle.py` (import after `sys.path.insert(0, "<this folder>/tools")`) | same |

Run scripts with the bundled Python by its absolute path. The folder is read-only: scripts, intermediate files and outputs go in the workspace. Script names such as `docx.py`, `pptx.py`, `openpyxl.py` or `inspect.py` shadow the libraries.

## New files

A document made with the libraries' bare defaults uses serif fonts (Times-like Latin, Song-style CJK), blue template headings and cramped tables, and reads poorly on screen. `officestyle` gives new files a plain sans look: Arial with Microsoft YaHei (微软雅黑), readable sizes and spacing, light tables. Both fonts are standard on Windows; elsewhere the engine and Office substitute equivalents (Liberation Sans, PingFang SC, Noto Sans CJK).

- Word: `officestyle.new_document()`, `officestyle.style_table(table)`, `officestyle.set_fonts(run)`
- PowerPoint: `officestyle.new_presentation()` (16:9, theme fonts set), `officestyle.set_run_fonts(run)`
- Excel: `officestyle.new_workbook()`, `officestyle.style_header(sheet, widths={"A": 18})`

A user's own template or an existing file keeps its own design.

## References

Each format has its own notes; read the one the task needs.

- `references/word.md`: .docx with python-docx
- `references/powerpoint.md`: .pptx with python-pptx
- `references/excel.md`: .xlsx with openpyxl and pandas
- `references/engine.md`: rendering pages to images, PDF export, formula recalculation

## What needs the engine

Creating files and changing content, data or formulas, including incidental formatting such as bold headers or number formats, need only Python. Reopening the saved file with the same library checks content and structure.

The engine is for:
- images of pages or slides, for the user or for a visual check;
- changes whose point is appearance (spacing, sizes, alignment, colors), which a visual check confirms;
- PDF output, including the PDF made for showing a document (see Delivering);
- refreshed formula results.

A rendering pass takes several seconds. A user's request to skip rendering stands.

## Delivering

Save to a new file unless the user asks for an in-place edit.

Showing a document to the user takes two `show` calls:
1. A PDF of the final file, made with `convert` (`references/engine.md`) and saved next to it under the same name (`report.docx` → `report.pdf`). The user's interface displays PDFs; it shows .docx, .pptx and .xlsx only as a download card.
2. The final file itself, so the user can download the editable original.

When the user asked for a PDF, that PDF is the deliverable and one `show` is enough. Intermediate scripts, previews and reports stay out of the delivery unless asked for.

Notes adapted from DeepSeek Harness `skill-office` (MIT).
