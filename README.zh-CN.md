<p align="center">
  <a href="README.md">English</a> | 简体中文
</p>

# Office 文档

> <sub>本文档由 Anthropic 的 Claude Fable 5.2 生成。</sub>

这是 Miyu 的一个技能软件包，提供一个技能 `office`，可以让 AI 编写、阅读和修改 Word（.docx）、PowerPoint（.pptx）和 Excel（.xlsx）文件，把页面渲染成图片来检查排版，导出 PDF，以及重新计算表格里的公式。

整个运行环境都打包在软件包里，安装之后就能使用，不需要另外安装 Python 库、Node 或 LibreOffice：

| 自带的组件 | 用途 |
|---|---|
| Python 3.12（python-build-standalone）和 python-docx、python-pptx、openpyxl、XlsxWriter、pandas、numpy、Pillow、lxml | 编写、阅读和修改文件 |
| Node.js 22 和 LibreOffice Kit（`@deepseek-ai/libreoffice-kit`） | 渲染成图片、导出 PDF、重新计算公式 |

LibreOffice 引擎在 Linux 上是 WASM 版，在 macOS 和 Windows 上是原生版。

## 使用方法

安装以后，直接跟 AI 说就可以了，例如「写一份周报 Word」「把这个 Excel 的合计算出来」「这份 PPT 转成 PDF」。AI 平时只看到技能的名字和一句说明，用到这个技能时才会读取 `SKILL.md` 和对应格式的那份参考资料。

新建的文件用 `officestyle` 设定字体、字号、行距和表格样式。不传参数时使用 Arial 配微软雅黑、五号字，适合在屏幕上阅读的文档；字体和字号可以通过参数传入，AI 会按文档的类型选择（正式报告用宋体配 Times，公文用仿宋三号，PPT 用无衬线字体）。常用的搭配、中文字号对照表、本机安装了哪些字体（`tools/fonts.py`），以及缺少的字体由引擎用什么字体代替，都写在 `references/fonts.md` 里。如果不使用 `officestyle`，python-docx 这些库默认使用衬线字体（Times、宋体一类）和蓝色标题，在屏幕上看起来又丑又模糊。如果用户给了模板，或者要修改现成的文件，就保持原来的样式。

技能文件夹在沙盒里是只读的：脚本、中间文件和结果都写在会话的工作区里。给人看文件的时候，先用引擎转换出一份同名的 PDF，再对 PDF 和原文件各调用一次 `show`；网页界面的右栏可以直接显示 PDF，而 Word、PPT、Excel 文件只显示成可以下载的卡片。如果用户要的本来就是 PDF，就只给 PDF。

## 软件包的内容

软件包的目录结构如下：

```text
skills/office/
├── SKILL.md              # 入口：运行环境在哪、什么时候要用引擎、怎么交付
├── references/           # word.md、powerpoint.md、excel.md、engine.md、fonts.md
├── tools/dsoffice.py     # 用自带的 Node 跑 LibreOffice Kit 的命令行
├── tools/officestyle.py  # 新建文件的样式：字体、字号可传，默认 Arial + 微软雅黑
├── tools/fonts.py        # 列出本机装的字体（引擎画得出来的那些）
└── runtime/              # 打包时拼进来（build/runtime.sh），仓库里没有
```

每种系统对应一个软件包文件（`targets`），四种都可以在 Linux 上构建出来。运行：

```sh
build/runtime.sh linux-x86_64     # 或 linux-aarch64、macos-aarch64、windows-x86_64
```

所有版本都是固定的：Python 和 Node 按发布方给出的 SHA-256 核对，Python 库按 `build/requirements.txt` 固定，npm 包按 `build/kit-package-lock.json` 里的完整性哈希核对。构建时会用到一次 npm（下载来的 Node 自带的那个），打包进软件包的是已经解开的文件，用户那边不需要 npm。

## 限制

这个技能有以下限制：

- LibreOffice 排版的结果和 Word、PowerPoint、Excel 会有出入，主要在字体和分页上。如果文档要求的字体本机没有，渲染结果里的 `missingFonts` 会把它们列出来。
- 渲染需要几秒到十几秒（WASM 版慢一些）。
- 老格式（.doc、.xls、.ppt）要先用引擎转换成新格式再修改；加密的文件打不开；带宏的文件，宏不会运行，也不会被修改。

## 许可证

技能的说明改写自 DeepSeek Harness 的 `skill-office`（MIT 许可证）。自带的各个组件各有自己的许可证，详细的见 [NOTICE.md](NOTICE.md)。
