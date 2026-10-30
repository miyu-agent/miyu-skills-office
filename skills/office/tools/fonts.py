"""List the font families installed on this machine, the ones the engine can draw with.

Usage: <bundled python> fonts.py [--cjk] [--json] [name ...]

Without names: every family, marked CJK when it has Chinese glyphs. With names: whether each named family is
installed (case-insensitive, exact family name). Scans the same directories the engine reads.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

EXTENSIONS = (".ttf", ".otf", ".ttc", ".otc")


def font_directories():
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        windir = os.environ.get("WINDIR", r"C:\Windows")
        local = os.environ.get("LOCALAPPDATA", os.path.join(home, "AppData", "Local"))
        return [os.path.join(windir, "Fonts"), os.path.join(local, "Microsoft", "Windows", "Fonts")]
    if sys.platform == "darwin":
        return ["/System/Library/Fonts", "/Library/Fonts", os.path.join(home, "Library/Fonts"),
                "/System/Library/AssetsV2"]
    data = os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share"
    dirs = [os.path.join(d, "fonts") for d in data.split(":") if d]
    data_home = os.environ.get("XDG_DATA_HOME") or os.path.join(home, ".local/share")
    return dirs + [os.path.join(home, ".fonts"), os.path.join(data_home, "fonts")]


def _draw(font, text):
    image = Image.new("L", (48, 48))
    ImageDraw.Draw(image).text((4, 4), text, font=font, fill=255)
    return image.tobytes()


def has_cjk(font):
    # A font without the glyph draws its .notdef box; compare with a code point no font covers.
    try:
        han = _draw(font, "中")
        return any(han) and han != _draw(font, "\U0010fffd")
    except Exception:
        return False


def scan():
    families = {}
    for root in font_directories():
        for dirpath, _, files in os.walk(root, onerror=lambda _: None):
            for name in files:
                if not name.lower().endswith(EXTENSIONS):
                    continue
                path = os.path.join(dirpath, name)
                for index in range(16):
                    try:
                        font = ImageFont.truetype(path, 24, index=index)
                    except OSError:
                        break
                    family, style = font.getname()
                    entry = families.setdefault(family, {"family": family, "styles": set(), "cjk": False})
                    entry["styles"].add(style)
                    if not entry["cjk"]:
                        entry["cjk"] = has_cjk(font)
                    if not name.lower().endswith((".ttc", ".otc")):
                        break
    return families


def main():
    args = sys.argv[1:]
    as_json = "--json" in args
    cjk_only = "--cjk" in args
    wanted = [a for a in args if not a.startswith("--")]
    families = scan()
    if wanted:
        lower = {name.lower(): name for name in families}
        result = {name: lower.get(name.lower()) is not None for name in wanted}
        print(json.dumps(result, ensure_ascii=False) if as_json else
              "\n".join(f"{name}: {'installed' if ok else 'not installed'}" for name, ok in result.items()))
        return
    rows = sorted((f for f in families.values() if f["cjk"] or not cjk_only), key=lambda f: f["family"].lower())
    if as_json:
        print(json.dumps([{**f, "styles": sorted(f["styles"])} for f in rows], ensure_ascii=False))
    else:
        for f in rows:
            print(f"{f['family']}{'  [CJK]' if f['cjk'] else ''}  ({', '.join(sorted(f['styles']))})")


if __name__ == "__main__":
    main()
