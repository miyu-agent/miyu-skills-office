# Office 文档

Miyu 的技能包，带一个技能 `office`：让 AI 写、读、改 Word（.docx）、PowerPoint（.pptx）、Excel（.xlsx），把页面渲染成图检查排版，导出 PDF，重算表格公式。

运行环境整个带在包里，装上就能用，不用装 Python 库、Node、LibreOffice：

| 带的 | 做什么 |
|---|---|
| Python 3.12（python-build-standalone）和 python-docx、python-pptx、openpyxl、XlsxWriter、pandas、numpy、Pillow、lxml | 写、读、改文件 |
| Node.js 22 和 LibreOffice Kit（`@deepseek-ai/libreoffice-kit`） | 渲染成图、导出 PDF、重算公式 |

LibreOffice 引擎在 Linux 上是 WASM 版，在 macOS、Windows 上是原生版。

## 怎么用

装上以后直接跟 AI 说：「写一份周报 Word」「把这个 Excel 的合计算出来」「这份 PPT 转成 PDF」。AI 平时只看到技能的名字和一句说明，用到时才读 `SKILL.md` 和对应格式的那份参考。

技能文件夹在沙盒里是只读的：脚本、中间文件、结果都写在会话的工作区。给人看的时候先用引擎转一份同名的 PDF，PDF 和原文件各 `show` 一次：网页右栏能直接看 PDF，Word、PPT、Excel 只显示成能下载的卡片。人要的本来就是 PDF 的，只给 PDF。

## 包里有什么

```text
skills/office/
├── SKILL.md              # 入口：运行环境在哪、什么时候要用引擎、怎么交付
├── references/           # word.md、powerpoint.md、excel.md、engine.md
├── tools/dsoffice.py     # 用自带的 Node 跑 LibreOffice Kit 的命令行
└── runtime/              # 打包时拼进来（build/runtime.sh），仓库里没有
```

一种系统一个包文件（`targets`），在 Linux 上拼好四种：

```sh
build/runtime.sh linux-x86_64     # 或 linux-aarch64、macos-aarch64、windows-x86_64
```

版本都钉死：Python、Node 照发布方的 SHA-256 核对，Python 库照 `build/requirements.txt`，npm 包照 `build/kit-package-lock.json` 的完整性哈希。拼的时候用一次 npm（下载来的 Node 自带的），装进包里的是解好的文件，用户那边没有 npm。

## 限制

- LibreOffice 排出来的和 Word、PowerPoint、Excel 会有出入，主要在字体和分页。文档要的字体本机没有时，渲染结果里的 `missingFonts` 会列出来。
- 渲染要几秒到十几秒（WASM 版慢一些）。
- 老格式（.doc、.xls、.ppt）先用引擎转成新格式再改；加密的文件打不开，带宏的宏不跑、不改。

## 许可

技能说明改写自 DeepSeek Harness 的 `skill-office`（MIT）。带的各个组件各有许可，见 [NOTICE.md](NOTICE.md)。
