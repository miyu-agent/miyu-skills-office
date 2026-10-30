# Third-party notices

This package redistributes the following components unmodified. Their license texts ship inside `skills/office/runtime/` next to each component.

| Component | License | Where its license is |
|---|---|---|
| DeepSeek Harness `skill-office` (skill text adapted) | MIT, Copyright (c) 2026 DeepSeek | below |
| CPython 3.12 (python-build-standalone) | PSF License and bundled third-party licenses | `runtime/python/lib/python3.12/LICENSE.txt` (Windows: `runtime/python/LICENSE.txt`) |
| python-docx, python-pptx, openpyxl, XlsxWriter, pandas, numpy, Pillow, lxml and their dependencies | MIT / BSD / HPND (each package's own) | `*.dist-info/` in the Python `site-packages` |
| Node.js | MIT and bundled third-party licenses | `runtime/node/LICENSE` |
| `@deepseek-ai/libreoffice-kit` and its engines | MPL-2.0; LibreOffice is MPL-2.0 with third-party components | `runtime/kit/node_modules/@deepseek-ai/*/` (`LICENSE`, `licenses/`, and `sources/` with the source changes) |
| fontkit, saxes, fflate, koffi and other npm dependencies | MIT / BSD / Apache-2.0 (each package's own) | `runtime/kit/node_modules/*/LICENSE*` |

## DeepSeek Harness skill-office

MIT License

Copyright (c) 2026 DeepSeek

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
