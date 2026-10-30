"""Run the bundled LibreOffice Kit CLI (dsoffice) with the bundled Node.js.

Usage: <bundled python> dsoffice.py <capabilities|convert|recalculate|render> [options...]
"""
import os
import subprocess
import sys

here = os.path.dirname(os.path.abspath(__file__))
runtime = os.path.join(os.path.dirname(here), "runtime")
node = os.path.join(runtime, "node", "node.exe" if os.name == "nt" else "node")
cli = os.path.join(runtime, "kit", "node_modules", "@deepseek-ai", "libreoffice-kit", "lib", "cli.js")

for path in (node, cli):
    if not os.path.isfile(path):
        print(f"dsoffice: missing {path}; reinstall the package for this system", file=sys.stderr)
        sys.exit(127)

if os.name == "nt":
    sys.exit(subprocess.call([node, cli, *sys.argv[1:]]))
os.execv(node, [node, cli, *sys.argv[1:]])
