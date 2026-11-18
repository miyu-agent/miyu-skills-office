# build/runtime.sh 里 fetch() 的测试（审计 2026-11-18 #146，只测 .part 那半）。
#
# 跑法（在仓库根）：
#   python3 -I -B -m unittest discover -s .github/tests
# （不加 -t .：.github 不是合法的包名，加了 unittest 会报 Start directory is not importable。）
#
# 只用标准库和 bash，不联网：从 runtime.sh 里把 fetch() 的定义原样抠出来，
# curl 换成记账的 shell 函数桩，在临时目录里跑。
# 放在 .github/tests/ 而不是 tests/：打包会跳过 .github，测试不会进包。

import pathlib
import re
import subprocess
import tempfile
import unittest

RUNTIME = pathlib.Path(__file__).resolve().parents[2] / "build" / "runtime.sh"

# curl 桩：记下调用；-o 指的文件写进 $CURL_BODY；$CURL_FAIL 非空时照 curl -f 失败（退出码 22）。
CURL_STUB = r'''
curl() {
  echo "$*" >> "$CURL_LOG"
  [ -z "${CURL_FAIL:-}" ] || return 22
  local out=""
  while [ $# -gt 0 ]; do
    case "$1" in -o) out=$2; shift 2 ;; *) shift ;; esac
  done
  printf '%s' "$CURL_BODY" > "$out"
}
'''


def fetch_definition():
    """runtime.sh 里 fetch() { ... } 的原文（可以是一行，也可以是多行）。"""
    src = RUNTIME.read_text(encoding="utf-8")
    m = re.search(r"^fetch\(\) \{.*?^\}", src, re.M | re.S)
    if not m:
        raise AssertionError("runtime.sh 里找不到 fetch() 的定义")
    return m.group(0)


class Fetch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = pathlib.Path(self.tmp.name)
        self.file = self.dir / "python-SHA256SUMS"
        self.part = self.dir / "python-SHA256SUMS.part"
        self.log = self.dir / "curl.log"

    def fetch(self, body="NEW", fail=False):
        script = "set -euo pipefail\n" + CURL_STUB + fetch_definition() + \
            '\nfetch "https://example.invalid/SHA256SUMS" "$TARGET"\n'
        env = {"PATH": "/usr/bin:/bin", "TARGET": str(self.file), "CURL_LOG": str(self.log),
               "CURL_BODY": body, "CURL_FAIL": "1" if fail else "", "HOME": str(self.dir)}
        p = subprocess.run(["bash", "-c", script], env=env, capture_output=True, text=True,
                           timeout=10)
        calls = self.log.read_text().splitlines() if self.log.exists() else []
        return p.returncode, calls

    # 审计 #146（.part 那半）：`[ -s "$2" ] || curl ... -o "$2.part" "$1" && { mv ... }`
    # 在 bash 里是 `(a || b) && c`：缓存的好文件非空、旁边又留着上次的残片 .part 时，
    # 不下载却照样把 .part 挪过去盖掉好文件。应保持好文件不变。
    def test_stale_part_does_not_clobber_good_cache(self):
        self.file.write_text("GOOD")
        self.part.write_text("BROKEN")
        code, calls = self.fetch()
        self.assertEqual(code, 0)
        self.assertEqual(calls, [], "缓存非空时不该下载")
        self.assertEqual(self.file.read_text(), "GOOD")

    # 防改坏（现在就绿）：没有缓存时下载到 .part 再改名。
    def test_downloads_when_missing(self):
        code, calls = self.fetch(body="NEW")
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.file.read_text(), "NEW")
        self.assertFalse(self.part.exists())

    # 防改坏（现在就绿）：下载失败时 fetch 失败，不留下目标文件。
    def test_failed_download_fails(self):
        code, calls = self.fetch(fail=True)
        self.assertNotEqual(code, 0)
        self.assertEqual(len(calls), 1)
        self.assertFalse(self.file.exists())


if __name__ == "__main__":
    unittest.main()
