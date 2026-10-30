# Fonts

A document names its fonts; whoever opens or renders it draws them with the fonts installed on that machine. The engine here renders with this machine's fonts, and the user's Word, PowerPoint or Excel uses theirs. A font that is missing is replaced: with an equivalent when one is known (table below), otherwise with a default face, which is how an unstyled document ends up in thin serif type.

## Common choices

| Document | Latin | Chinese | Sizes |
|---|---|---|---|
| Everyday, business, read on screen | Arial | 微软雅黑 Microsoft YaHei | body 五号 10.5 pt (`officestyle` default) |
| Formal printed report, paper | Times New Roman | body 宋体 SimSun, headings 黑体 SimHei | body 小四 12 pt or 五号 10.5 pt |
| Chinese official document (公文, GB/T 9704-2012) | Times New Roman | title 方正小标宋简体 FZXiaoBiaoSong-B05S; body 仿宋_GB2312 FangSong_GB2312; level-1 headings 黑体 SimHei; level-2 楷体_GB2312 KaiTi_GB2312 | title 二号 22 pt; body and headings 三号 16 pt |
| Slides | Arial | 微软雅黑 Microsoft YaHei | titles 28–40 pt, text 16–24 pt |

A font the user names, or the fonts of a template or existing file, are the document's fonts. Windows ships SimSun, SimHei, KaiTi, FangSong and Microsoft YaHei; FangSong_GB2312, KaiTi_GB2312 and the FZ (方正) fonts are installed separately, and where they are missing Windows users often have FangSong and KaiTi instead.

Chinese size names: 初号 42 pt, 小初 36, 一号 26, 小一 24, 二号 22, 小二 18, 三号 16, 小三 15, 四号 14, 小四 12, 五号 10.5, 小五 9.

## Setting them

`officestyle` takes fonts and sizes as arguments; headings default to the body fonts.

```python
officestyle.new_document()                                    # Arial + Microsoft YaHei, 10.5 pt
officestyle.new_document(latin="Times New Roman", east_asian="SimSun", size=12,
                         heading_latin="Arial", heading_east_asian="SimHei")
officestyle.new_document(latin="Times New Roman", east_asian="FangSong_GB2312", size=16,
                         heading_east_asian="SimHei", heading_sizes=(22, 16, 16, 16))
officestyle.new_presentation(latin="Arial", east_asian="Microsoft YaHei")
officestyle.new_workbook(font="Arial", size=10.5)
```

A single run takes its own fonts with `officestyle.set_fonts(run, latin, east_asian)` (Word) or `officestyle.set_run_fonts(run, latin, east_asian)` (PowerPoint), for example a 公文 title in FZXiaoBiaoSong-B05S.

## What this machine has

```text
<python> <this skill>/tools/fonts.py --cjk                  # installed families with Chinese glyphs
<python> <this skill>/tools/fonts.py "SimSun" "FangSong"    # whether these families are installed
```

The engine's `render` and `convert` output lists `missingFonts`: fonts the document names that this machine lacks. Each is drawn with the first installed family of its group:

| Named | Drawn with, in order of preference |
|---|---|
| Arial, Helvetica, sans-serif | Liberation Sans, Helvetica, DejaVu Sans, then a CJK sans |
| Times New Roman, serif | Liberation Serif, Times, DejaVu Serif, then a CJK serif |
| Courier New, monospace | Liberation Mono, DejaVu Sans Mono, Menlo |
| Calibri / Cambria | Carlito / Caladea |
| 微软雅黑 Microsoft YaHei | PingFang SC, Noto Sans CJK SC, Noto Sans SC |
| 黑体 SimHei | Heiti SC, STHeiti, Noto Sans CJK SC, Source Han Sans SC |
| 宋体 SimSun | Songti SC, STSong, Noto Serif CJK SC, Source Han Serif SC |
| 楷体 KaiTi | Kaiti SC, STKaiti, LXGW WenKai |
| 仿宋 FangSong | STFangsong, Songti SC, Noto Serif CJK SC |

Names outside these groups (FangSong_GB2312, FZ fonts, most decorative fonts) have no listed equivalent here; a render shows what replaced them. The preview then differs from what a user with those fonts sees, while the file itself still names the intended fonts.
