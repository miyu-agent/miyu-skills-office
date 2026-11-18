# skills/office/tools 的测试（审计 2026-11-18 #181）。
#
# 跑法（在仓库根）：
#   python3 -I -B -m unittest discover -s .github/tests
# （不加 -t .：.github 不是合法的包名，加了 unittest 会报 Start directory is not importable。）
# officestyle 那条要 python-pptx 和 python-docx：用 build/runtime.sh 拼好的包内解释器跑，
#   skills/office/runtime/python/bin/python3 -I -B -m unittest discover -s .github/tests
# 当前解释器没有这两个库时那条会跳过（并说明原因），dsoffice 那条只要标准库。
#
# 不联网、不起 Node：dsoffice.py 拷进临时目录，旁边放一个什么都不做的假 node 和假 cli.js。
# 放在 .github/tests/ 而不是 tests/：打包会跳过 .github，测试不会进包。

import importlib.util
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOLS = pathlib.Path(__file__).resolve().parents[2] / "skills" / "office" / "tools"


def have(*names):
    return all(importlib.util.find_spec(n) is not None for n in names)


class DsofficeOutputEquals(unittest.TestCase):
    # 审计 #181-2：引擎不建 --output 的父目录，dsoffice.py 替它建；但只认单独的
    # `--output PATH`，不认 Node util.parseArgs 同样接受的 `--output=PATH`，
    # 新目录 + 等号写法时父目录没建，引擎写文件失败。
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = pathlib.Path(self.tmp.name)
        tools = root / "office" / "tools"
        tools.mkdir(parents=True)
        shutil.copy2(TOOLS / "dsoffice.py", tools / "dsoffice.py")
        runtime = root / "office" / "runtime"
        node = runtime / "node" / "node"
        node.parent.mkdir(parents=True)
        node.write_text("#!/bin/sh\nexit 0\n")
        node.chmod(0o755)
        cli = runtime / "kit" / "node_modules" / "@deepseek-ai" / "libreoffice-kit" / "lib" / "cli.js"
        cli.parent.mkdir(parents=True)
        cli.write_text("")
        self.script = tools / "dsoffice.py"
        self.root = root

    def run_dsoffice(self, *args):
        env = {"PATH": "/usr/bin:/bin", "HOME": str(self.root)}
        return subprocess.run([sys.executable, "-I", "-B", str(self.script), *args],
                              capture_output=True, text=True, timeout=10, env=env)

    @unittest.skipIf(os.name == "nt", "假 node 是 shell 脚本")
    def test_output_equals_form_creates_parent(self):
        out = self.root / "new" / "sub" / "out.pdf"
        p = self.run_dsoffice("convert", "in.docx", f"--output={out}")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(out.parent.is_dir(), "--output= 写法的父目录没建")

    @unittest.skipIf(os.name == "nt", "假 node 是 shell 脚本")
    def test_output_dir_equals_form_creates_parent(self):
        out = self.root / "new2" / "sub" / "outdir"
        p = self.run_dsoffice("convert", "in.docx", f"--output-dir={out}")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(out.parent.is_dir(), "--output-dir= 写法的父目录没建")

    # 防改坏（现在就绿）：分开写的 --output PATH 照旧建父目录。
    @unittest.skipIf(os.name == "nt", "假 node 是 shell 脚本")
    def test_output_separate_form_creates_parent(self):
        out = self.root / "new3" / "sub" / "out.pdf"
        p = self.run_dsoffice("convert", "in.docx", "--output", str(out))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(out.parent.is_dir())


@unittest.skipUnless(have("pptx", "docx"),
                     "要 python-pptx、python-docx：用 skills/office/runtime/python/bin/python3 跑")
class SetRunFontsLatinNone(unittest.TestCase):
    # 审计 #181-1：set_run_fonts(run, latin=None) 时 python-pptx 的 font.name = None 会删掉
    # a:latin，随后 rpr.find("a:latin").addnext(ea) 对 None 调方法，AttributeError。
    # 应照常把东亚字体设上。
    def setUp(self):
        sys.dont_write_bytecode = True
        spec = importlib.util.spec_from_file_location("officestyle_under_test", TOOLS / "officestyle.py")
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        from pptx import Presentation
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        self.frame = slide.shapes.add_textbox(0, 0, 100, 100).text_frame

    def ea_typeface(self, run):
        from pptx.oxml.ns import qn
        ea = run._r.get_or_add_rPr().find(qn("a:ea"))
        return None if ea is None else ea.get("typeface")

    def test_latin_none_still_sets_east_asian(self):
        run = self.frame.paragraphs[0].add_run()
        run.text = "y"
        self.mod.set_run_fonts(run, latin=None, east_asian="Noto Sans CJK SC")
        self.assertEqual(self.ea_typeface(run), "Noto Sans CJK SC")

    # 防改坏（现在就绿）：默认参数照旧。
    def test_default_fonts(self):
        run = self.frame.paragraphs[0].add_run()
        run.text = "x"
        self.mod.set_run_fonts(run)
        self.assertEqual(self.ea_typeface(run), self.mod.EAST_ASIAN)


if __name__ == "__main__":
    unittest.main()
