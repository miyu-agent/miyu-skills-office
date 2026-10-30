# The engine: render, PDF, recalculate

The engine is LibreOffice Kit, run through `tools/dsoffice.py` with the bundled Python:

```text
<python> <this skill>/tools/dsoffice.py render --input <file> --output-dir <new dir> [--pages "1,3"]
<python> <this skill>/tools/dsoffice.py render --input <book.xlsx> --output-dir <new dir> --sheet <exact name> [--range A1:F30]
<python> <this skill>/tools/dsoffice.py convert --input <file> --output <new file.pdf>
<python> <this skill>/tools/dsoffice.py recalculate --input <book.xlsx> --output <new book.xlsx>
<python> <this skill>/tools/dsoffice.py capabilities
```

- Paths are absolute or relative to the working directory; each is quoted. Outputs are new paths: an existing output file is never overwritten, and `--output-dir` must not exist yet (the engine creates it).
- Each command prints one JSON object. `render` lists every image (`path`, `width`, `height`, page) and `missingFonts`; `convert` gives `pageCount` and `missingFonts`.
- `capabilities` lists formats, limits and options.
- LibreOffice output can differ from Word, PowerPoint or Excel, mainly in fonts and pagination. `missingFonts` names fonts the document asks for that this machine lacks.

## Render

Accepts .docx, .doc, .odt, .pptx, .ppt, .odp, .xlsx, .xls, .ods and .pdf; writes PNG pages plus `manifest.json`. Pages and slides are numbered from 1, at most 100 per call; several go in one `--pages` value (`"1,3,4"`). For workbooks, `--sheet` takes the exact sheet name and `--range` an A1 range; sheet numbers are not page numbers.

`read` on a PNG shows it. Images for the user are kept and delivered. Images only for checking go in a fresh directory in the workspace, for example `.office-preview-<random>/render`, and that directory is removed after looking.

A render of a file with content that comes out fully blank or transparent is an engine failure, not the document's look. Another render of the same thing gives the same result. The work then rests on the content checks; the reply says the visual check was not completed.

## PDF

`convert` with a `.pdf` output exports the document; the output suffix picks the format (`pdf`, `docx`, `odt`, `xlsx`, `ods`, `csv`, `pptx`, `odp`, `txt`), so `.doc` → `.docx` and `.xls` → `.xlsx` work too. A finished PDF starts with `%PDF-`. Spreadsheet PDFs follow the workbook's print settings.

## Recalculate

`recalculate` refreshes every formula's cached result and saves a new workbook, formulas kept. Reading it with openpyxl `data_only=True` gives the new values, `data_only=False` the formulas. It does not judge whether the formulas are right.
