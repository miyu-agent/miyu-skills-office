# build/runtime.sh 的测试（审计 2026-11-18 #146，.pyc 那半）。
#
# 跑法（在仓库根）：
#   python3 -I -B -m unittest discover -s .github/tests
# （不加 -t .：.github 不是合法的包名，加了 unittest 会报 Start directory is not importable。）
#
# 只用标准库，不联网、不跑 runtime.sh：只读它的命令行（去掉注释）。
# 放在 .github/tests/ 而不是 tests/：打包会跳过 .github，测试不会进包。

import pathlib
import re
import unittest

RUNTIME = pathlib.Path(__file__).resolve().parents[2] / "build" / "runtime.sh"


def commands():
    """runtime.sh 里去掉注释以后的每一行（heredoc 里的照样算，宁可多看）。"""
    lines = []
    for line in RUNTIME.read_text(encoding="utf-8").splitlines():
        code = re.sub(r"(^|\s)#.*$", "", line).strip()
        if code:
            lines.append(code)
    return lines


class Precompile(unittest.TestCase):
    # 审计 #146（.pyc 那半）：`miyu pkg pack`（本地打的和 pack.yml 打的同一套）在哪一层都跳过
    # `__pycache__` 和 `*.pyc`（核心 crates/miyu-source/src/archive.rs 的 SKIPPED / SKIPPED_SUFFIX），
    # runtime.sh 再编 .pyc 也进不了包，白花构建时间。应不再预编字节码。
    def test_no_precompile_step(self):
        hits = [line for line in commands() if re.search(r"\bcompileall\b|\bpy_compile\b", line)]
        self.assertEqual(hits, [], "打包会剔掉 .pyc，runtime.sh 不该再编")


if __name__ == "__main__":
    unittest.main()
