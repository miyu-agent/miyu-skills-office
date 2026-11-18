#!/usr/bin/env bash
# 把一种系统的运行环境拼进 skills/office/runtime/：独立的 Python 和 Office 库、Node、LibreOffice Kit 和它的引擎。
# 用法：build/runtime.sh <linux-x86_64|linux-aarch64|macos-aarch64|windows-x86_64>
# 在 Linux x86_64 上跑（CI 用 ubuntu），别的系统的那一份照样在这里拼：Python 库照目标系统的 wheel 取，npm 照目标系统挑引擎。
# 要 curl、tar、unzip、sha256sum（npm 用下载来的 Node 自带的）。下载的东西都钉了版本，Python、Node 照发布方给的 SHA-256 核对，npm 照锁文件里的完整性哈希核对。
set -euo pipefail

target=${1:?usage: build/runtime.sh <target>}
root=$(cd "$(dirname "$0")/.." && pwd)
out="$root/skills/office/runtime"
work=${RUNTIME_WORK:-"$root/.build"}

PYTHON_RELEASE=20261009
PYTHON_VERSION=3.12.15
NODE_VERSION=22.23.3
KIT_VERSION=0.2.3
PY_PACKAGES=(-r "$root/build/requirements.txt")

case "$target" in
  linux-x86_64)   py=x86_64-unknown-linux-gnu;  node=linux-x64;   npm_os=linux;  npm_cpu=x64;
                  wheel=(--platform manylinux_2_28_x86_64 --platform manylinux_2_17_x86_64 --platform manylinux2014_x86_64) ;;
  linux-aarch64)  py=aarch64-unknown-linux-gnu; node=linux-arm64; npm_os=linux;  npm_cpu=arm64;
                  wheel=(--platform manylinux_2_28_aarch64 --platform manylinux_2_17_aarch64 --platform manylinux2014_aarch64) ;;
  macos-aarch64)  py=aarch64-apple-darwin;      node=darwin-arm64; npm_os=darwin; npm_cpu=arm64;
                  wheel=(--platform macosx_11_0_arm64 --platform macosx_12_0_arm64 --platform macosx_13_0_arm64 --platform macosx_14_0_arm64 --platform macosx_10_9_universal2 --platform macosx_10_13_universal2) ;;
  windows-x86_64) py=x86_64-pc-windows-msvc;    node=win-x64;     npm_os=win32;  npm_cpu=x64;
                  wheel=(--platform win_amd64) ;;
  *) echo "unknown target: $target" >&2; exit 2 ;;
esac

mkdir -p "$work"
rm -rf "$out"
mkdir -p "$out"

fetch() { # url file：缓存非空就直接用（不看也不动 .part）；否则下到 .part，成功了才改名
  if [ -s "$2" ]; then return 0; fi
  curl -fsSL --retry 3 -o "$2.part" "$1" && mv "$2.part" "$2"
}

# ---- Python ----------------------------------------------------------------
py_base="https://github.com/astral-sh/python-build-standalone/releases/download/$PYTHON_RELEASE"
py_name() { echo "cpython-$PYTHON_VERSION+$PYTHON_RELEASE-$1-install_only_stripped.tar.gz"; }
fetch "$py_base/SHA256SUMS" "$work/python-SHA256SUMS"
for triple in x86_64-unknown-linux-gnu "$py"; do
  name=$(py_name "$triple")
  fetch "$py_base/${name/+/%2B}" "$work/$name"
  (cd "$work" && grep " $name\$" python-SHA256SUMS | sha256sum -c --quiet -)
done
# 拼的这台机器上的 Python：用它的 pip 取目标系统的 wheel，用它编 .pyc（同一个小版本，.pyc 各系统通用）
host="$work/host-python"
if [ ! -x "$host/bin/python3" ]; then
  mkdir -p "$host" && tar -xzf "$work/$(py_name x86_64-unknown-linux-gnu)" -C "$host" --strip-components=1
fi
tar -xzf "$work/$(py_name "$py")" -C "$out"   # → $out/python/
if [ "$npm_os" = win32 ]; then site="$out/python/Lib/site-packages"; else site="$out/python/lib/python3.12/site-packages"; fi
"$host/bin/python3" -m pip install --quiet --disable-pip-version-check --no-compile --only-binary=:all: \
  --implementation cp --python-version 3.12 --abi cp312 --abi abi3 --abi none "${wheel[@]}" \
  --target "$site" "${PY_PACKAGES[@]}"
# 包里的东西装上以后是只读的，.pyc 先编好；unchecked-hash：解包换了修改时间也照用
"$host/bin/python3" -m compileall -q -j0 --invalidation-mode unchecked-hash "$out/python" >/dev/null || true
# 用不上的：pip、ensurepip、测试、头文件、tcl/tk、idle；bin/ 只留解释器本身（别的是链接、pip 这些的入口）
rm -rf "$site"/pip "$site"/pip-* "$out/python/include" "$out/python/share"
find "$out/python" -depth -type d \( -name tests -o -name test -o -name idlelib -o -name tkinter -o -name turtledemo \
  -o -name ensurepip -o -name 'tcl*' -o -name 'tk*' -o -name 'itcl*' -o -name 'thread*' \) -path '*/lib*' -exec rm -rf {} + 2>/dev/null || true
find "$out/python" \( -name '_tkinter*' -o -name 'libtcl*' -o -name 'libtk*' -o -name 'tcl*.dll' -o -name 'tk*.dll' \) -exec rm -rf {} + 2>/dev/null || true
if [ "$npm_os" != win32 ]; then
  real=$(readlink -f "$out/python/bin/python3")
  find "$out/python/bin" -mindepth 1 ! -samefile "$real" -exec rm -f {} +
  mv "$real" "$out/python/bin/python3" 2>/dev/null || true
  # 链接用的那一个 .so 是开发用的，运行只认带版本号的那个
  find "$out/python/lib" -maxdepth 1 -type l -name 'libpython*' -delete
fi

# ---- Node ------------------------------------------------------------------
node_base="https://nodejs.org/dist/v$NODE_VERSION"
fetch "$node_base/SHASUMS256.txt" "$work/node-SHASUMS256.txt"
mkdir -p "$out/node"
if [ "$npm_os" = win32 ]; then
  archive="node-v$NODE_VERSION-$node.zip"
  fetch "$node_base/$archive" "$work/$archive"
  (cd "$work" && grep " $archive\$" node-SHASUMS256.txt | sha256sum -c --quiet -)
  unzip -q -o -j "$work/$archive" "node-v$NODE_VERSION-$node/node.exe" "node-v$NODE_VERSION-$node/LICENSE" -d "$out/node"
else
  archive="node-v$NODE_VERSION-$node.tar.gz"
  fetch "$node_base/$archive" "$work/$archive"
  (cd "$work" && grep " $archive\$" node-SHASUMS256.txt | sha256sum -c --quiet -)
  tar -xzf "$work/$archive" -C "$out/node" --strip-components=1 "node-v$NODE_VERSION-$node/bin/node" "node-v$NODE_VERSION-$node/LICENSE"
  mv "$out/node/bin/node" "$out/node/node" && rmdir "$out/node/bin"
fi

# ---- LibreOffice Kit -------------------------------------------------------
# 用这台机器上的 Node 自带的 npm 装（只在拼的时候用，装进包里的是解好的文件）
host_node="$work/host-node"
if [ ! -x "$host_node/bin/npm" ]; then
  archive="node-v$NODE_VERSION-linux-x64.tar.gz"
  fetch "$node_base/$archive" "$work/$archive"
  (cd "$work" && grep " $archive\$" node-SHASUMS256.txt | sha256sum -c --quiet -)
  mkdir -p "$host_node" && tar -xzf "$work/$archive" -C "$host_node" --strip-components=1
fi
export PATH="$host_node/bin:$PATH"
mkdir -p "$out/kit"
cp "$root/build/kit-package.json" "$out/kit/package.json"
cp "$root/build/kit-package-lock.json" "$out/kit/package-lock.json"
# 锁文件钉住每一个包和它的完整性哈希；--os/--cpu 照目标系统挑引擎（Linux 是 WASM，macOS、Windows 是原生）
(cd "$out/kit" && npm ci --ignore-scripts --omit=dev --no-audit --no-fund --os="$npm_os" --cpu="$npm_cpu" --loglevel=error)
rm -rf "$out/kit/node_modules/.bin" "$out/kit/package-lock.json" "$out/kit/node_modules/.package-lock.json"
# WASM 引擎没写系统，哪里都会装上；macOS、Windows 用原生的，它在那里用不上（150 MB）
if [ "$npm_os" != linux ]; then rm -rf "$out/kit/node_modules/@deepseek-ai/libreoffice-kit-wasm"; fi

# ---- 收尾 ------------------------------------------------------------------
# 包里不放链接：换成它指着的文件
while IFS= read -r -d '' link; do
  real=$(readlink -f "$link")
  if [ -f "$real" ]; then rm "$link" && cp -p "$real" "$link"; else rm -rf "$link"; fi
done < <(find "$out" -type l -print0)
cat > "$out/VERSIONS" <<EOF
target=$target
python=$PYTHON_VERSION ($PYTHON_RELEASE)
node=$NODE_VERSION
libreoffice-kit=$KIT_VERSION
python-packages=${PY_PACKAGES[*]}
EOF
du -sh "$out"
