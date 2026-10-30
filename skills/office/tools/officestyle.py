"""A clean default look for new Word, PowerPoint and Excel files.

Import with the bundled Python:

    import sys; sys.path.insert(0, "<this skill>/tools")
    import officestyle

Fonts: Arial for Latin text and Microsoft YaHei (微软雅黑) for Chinese, Japanese and Korean text. Both exist on
Windows; on macOS and Linux the engine and Office substitute the metric-compatible or equivalent sans fonts
(Liberation Sans, PingFang SC, Noto Sans CJK), so the files read the same everywhere.
"""
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

LATIN = "Arial"
EAST_ASIAN = "Microsoft YaHei"
TEXT = RGBColor(0x26, 0x26, 0x26)
HEADING = RGBColor(0x11, 0x18, 0x27)
MUTED = RGBColor(0x6B, 0x72, 0x80)
ACCENT = RGBColor(0x25, 0x63, 0xEB)
RULE = "D0D5DD"
HEADER_FILL = "F2F4F7"


# ---------------------------------------------------------------- Word

def set_fonts(target, latin=LATIN, east_asian=EAST_ASIAN):
    """Set Latin and East Asian fonts on a docx run or style (python-docx sets only the Latin one)."""
    target.font.name = latin
    element = target.element if hasattr(target, "element") else target._element
    rpr = element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        fonts.set(qn(attr), latin)
    fonts.set(qn("w:eastAsia"), east_asian)
    for theme in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        fonts.attrib.pop(qn(theme), None)


def _no_border(style):
    ppr = style.element.find(qn("w:pPr"))
    if ppr is not None:
        border = ppr.find(qn("w:pBdr"))
        if border is not None:
            ppr.remove(border)


def new_document(margins_cm=(2.2, 2.4)):
    """An A4 document with sans fonts, readable spacing and plain dark headings."""
    document = Document()
    section = document.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(margins_cm[0])
    section.left_margin = section.right_margin = Cm(margins_cm[1])

    styles = document.styles
    normal = styles["Normal"]
    set_fonts(normal)
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = TEXT
    fmt = normal.paragraph_format
    fmt.space_before, fmt.space_after = Pt(0), Pt(6)
    # 「至少」而不是倍数：中文字体自带的行高比 Arial 大，按倍数算两种字体的行就高低不齐
    fmt.line_spacing_rule = WD_LINE_SPACING.AT_LEAST
    fmt.line_spacing = Pt(17)

    for name, size, before, after in (("Title", 22, 0, 10), ("Heading 1", 16, 18, 8),
                                      ("Heading 2", 13, 14, 6), ("Heading 3", 11.5, 12, 4)):
        style = styles[name]
        set_fonts(style)
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.italic = False
        style.font.color.rgb = HEADING
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.AT_LEAST
        style.paragraph_format.line_spacing = Pt(round(size * 1.35))
        _no_border(style)
    subtitle = styles["Subtitle"]
    set_fonts(subtitle)
    subtitle.font.size, subtitle.font.italic, subtitle.font.color.rgb = Pt(12), False, MUTED
    for name in ("List Bullet", "List Number", "Caption"):
        set_fonts(styles[name])
    return document


def _cell_fill(cell, hex_color):
    tcpr = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:val"), "clear")
    shading.set(qn("w:color"), "auto")
    shading.set(qn("w:fill"), hex_color)
    tcpr.append(shading)


def style_table(table, header=True, widths_cm=None):
    """Light horizontal rules, a shaded bold header row and cell padding."""
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblpr = table._tbl.tblPr
    for old in tblpr.findall(qn("w:tblBorders")) + tblpr.findall(qn("w:tblCellMar")):
        tblpr.remove(old)
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "bottom", "insideH"):
        line = OxmlElement(f"w:{edge}")
        line.set(qn("w:val"), "single")
        line.set(qn("w:sz"), "6")
        line.set(qn("w:color"), RULE)
        borders.append(line)
    for edge in ("left", "right", "insideV"):
        line = OxmlElement(f"w:{edge}")
        line.set(qn("w:val"), "nil")
        borders.append(line)
    tblpr.append(borders)
    margins = OxmlElement("w:tblCellMar")
    for edge, twips in (("top", 70), ("bottom", 70), ("left", 110), ("right", 110)):
        margin = OxmlElement(f"w:{edge}")
        margin.set(qn("w:w"), str(twips))
        margin.set(qn("w:type"), "dxa")
        margins.append(margin)
    tblpr.append(margins)
    for row_index, row in enumerate(table.rows):
        for column, cell in enumerate(row.cells):
            if widths_cm:
                cell.width = Cm(widths_cm[column])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.AT_LEAST
                paragraph.paragraph_format.line_spacing = Pt(15)
                if header and row_index == 0:
                    for run in paragraph.runs:
                        run.font.bold = True
            if header and row_index == 0:
                _cell_fill(cell, HEADER_FILL)
    return table


# ---------------------------------------------------------------- PowerPoint

def set_run_fonts(run, latin=LATIN, east_asian=EAST_ASIAN):
    """Set Latin and East Asian fonts on a pptx run."""
    from pptx.oxml.ns import qn as pqn
    run.font.name = latin
    rpr = run._r.get_or_add_rPr()
    ea = rpr.find(pqn("a:ea"))
    if ea is None:
        ea = rpr.makeelement(pqn("a:ea"), {})
        rpr.find(pqn("a:latin")).addnext(ea)
    ea.set("typeface", east_asian)


def new_presentation():
    """A 16:9 presentation whose theme fonts are Arial and Microsoft YaHei, so every placeholder and text box inherits them."""
    from pptx import Presentation
    from pptx.oxml.ns import qn as pqn
    from pptx.util import Inches
    presentation = Presentation()
    ratio = Inches(13.333) / presentation.slide_width
    presentation.slide_width, presentation.slide_height = Inches(13.333), Inches(7.5)
    master = presentation.slide_masters[0]
    # 默认模板是 4:3 排的：母版、版式里的框照比例横向拉开，不然 16:9 的页上都挤在左边
    for owner in [master, *master.slide_layouts]:
        for shape in owner.shapes:
            if shape.left is not None and shape.width is not None:
                shape.left, shape.width = int(shape.left * ratio), int(shape.width * ratio)
    theme_part = next(rel.target_part for rel in master.part.rels.values() if rel.reltype.endswith("/theme"))
    from lxml import etree
    theme = etree.fromstring(theme_part.blob)
    for group in ("a:majorFont", "a:minorFont"):
        node = theme.find(f".//{pqn(group)}")
        node.find(pqn("a:latin")).set("typeface", LATIN)
        node.find(pqn("a:ea")).set("typeface", EAST_ASIAN)
        for script in node.findall(pqn("a:font")):
            if script.get("script") in ("Hans", "Hant", "Jpan", "Hang"):
                script.set("typeface", EAST_ASIAN)
    theme_part._blob = etree.tostring(theme, xml_declaration=True, encoding="UTF-8", standalone=True)
    return presentation


# ---------------------------------------------------------------- Excel

def new_workbook():
    """A workbook whose default cell font is Arial 10.5 (Excel's default Calibri is missing on many machines)."""
    from openpyxl import Workbook
    from openpyxl.styles import Font
    workbook = Workbook()
    workbook._fonts[0] = Font(name=LATIN, size=10.5)
    return workbook


def style_header(sheet, row=1, widths=None):
    """Bold shaded header row with a bottom rule; optional column widths {"A": 18}."""
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    for cell in sheet[row]:
        if cell.value is None:
            continue
        cell.font = Font(name=LATIN, size=10.5, bold=True, color="111827")
        cell.fill = PatternFill("solid", fgColor=HEADER_FILL)
        cell.border = Border(bottom=Side(style="thin", color=RULE))
        cell.alignment = Alignment(vertical="center")
    for column, width in (widths or {}).items():
        sheet.column_dimensions[column].width = width
    sheet.freeze_panes = sheet.cell(row=row + 1, column=1)
