# PowerPoint presentations (.pptx)

python-pptx creates and edits .pptx files. It is not a renderer: whether text fits, contrast and overall look come from a render (`engine.md`).

## Editing

- Slide layouts, text runs, images, tables and charts are worth inspecting before an edit.
- Changing only the requested content keeps mixed run formatting. Rebuilding slides can drop animations, SmartArt and other extension content.

```python
from pptx import Presentation

presentation = Presentation("report.pptx")
for shape in presentation.slides[0].shapes:
    if shape.has_text_frame and shape.text == "Quarterly report":
        shape.text_frame.paragraphs[0].runs[0].text = "Quarterly results"
presentation.save("report-edited.pptx")
```

## Creating

Editable text boxes, tables and native charts keep the deck editable. Images come from local files. Slide size, font sizes and chart data are set explicitly: `Inches` or `Cm` for positions and sizes, `Pt` for font sizes.

`Presentation()` alone is 4:3 with Calibri theme fonts; changing only `slide_width` to 16:9 leaves the layouts' placeholders crowded on the left. `officestyle.new_presentation()` returns a 16:9 deck with the layouts widened and the theme fonts set to Arial and Microsoft YaHei, so placeholders and new text boxes inherit them.

```python
import sys
sys.path.insert(0, "<this skill>/tools")
import officestyle
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches, Pt

presentation = officestyle.new_presentation()
slide = presentation.slides.add_slide(presentation.slide_layouts[6])  # blank
title = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12), Inches(0.8))
run = title.text_frame.paragraphs[0].add_run()
run.text = "Quarterly report"
run.font.size = Pt(30)
data = CategoryChartData()
data.categories = ["Q1", "Q2"]
data.add_series("Revenue", [12, 18])
slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
                       Inches(0.8), Inches(1.6), Inches(11.5), Inches(4.8), data)
presentation.save("report.pptx")
```

- Paragraph alignment does not move a text box. A title centered on the slide needs both the paragraph centered and the box centered against `presentation.slide_width`.
- A native chart embeds a workbook with its data; that workbook is part of the file.
- East Asian text: `run.font.name` sets the Latin font (`a:latin`); CJK text uses the `a:ea` element, which goes right after `a:latin`:

```python
from pptx.oxml.ns import qn
run.font.name = "Noto Sans CJK SC"            # creates a:latin
rpr = run._r.get_or_add_rPr()
ea = rpr.find(qn("a:ea"))
if ea is None:
    ea = rpr.makeelement(qn("a:ea"), {})
    rpr.find(qn("a:latin")).addnext(ea)
ea.set("typeface", "Noto Sans CJK SC")
```

## Checking

Reopening the saved file confirms slide count, text, chart data and notes, including unchanged content. Text fitting, overlap and contrast are only visible in a render.
