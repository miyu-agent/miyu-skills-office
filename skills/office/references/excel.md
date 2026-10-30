# Excel workbooks (.xlsx)

openpyxl reads and edits workbooks, including styles and formulas. pandas analyses data. XlsxWriter writes new workbooks only and cannot open existing ones.

## Reading and editing

- `openpyxl.load_workbook(path, data_only=False)` keeps formulas; `data_only=True` returns the values cached at the last save, which can be missing or stale.
- Sheet names, cell types, formulas, styles, merged ranges and the ranges formulas refer to are worth inspecting before an edit.
- A pandas DataFrame is not the workbook. Writing one over an existing file drops other sheets, formulas, charts and formatting. Results go back into the intended ranges through openpyxl.
- Numbers, dates, booleans and identifiers keep their cell types; a number format is not a type conversion.
- `.xls`, `.xlsb`, encrypted and macro-enabled files are not .xlsx; renaming them does not convert them. The engine converts `.xls` to `.xlsx`. `keep_vba=True` preserves VBA in an .xlsm without running or editing it.

## Creating

```python
import sys
sys.path.insert(0, "<this skill>/tools")
import officestyle

workbook = officestyle.new_workbook()            # default font Arial instead of Calibri
sheet = workbook.active
sheet.title = "Revenue"
for row in [("Quarter", "Revenue"), ("Q1", 12), ("Q2", 18), ("Total", "=SUM(B2:B3)")]:
    sheet.append(row)
officestyle.style_header(sheet, widths={"A": 18, "B": 14})   # bold shaded header, frozen below it
workbook.save("report.xlsx")
```

## Formulas

openpyxl and XlsxWriter write formulas without calculating them. A newly written formula has no cached result until the workbook is recalculated, by the engine (`engine.md`, `recalculate`) or by a spreadsheet application. Constants in place of requested formulas, or stale caches reported as fresh results, misrepresent the workbook.

## Checking

Reopening the saved workbook confirms sheet names, values, types, formulas, styles and totals against the source data, including unchanged content. That check calculates nothing and says nothing about appearance. Fill colors, alignment, spacing and sizing are confirmed with a render of the affected range.
