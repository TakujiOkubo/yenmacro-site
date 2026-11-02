"""Copy logo files, subset the Mulish font and resize the portrait into assets/.

The branding folder stays the master for the logo; rerun this after a logo rebuild.

    python tools/prep_assets.py
"""
from pathlib import Path
import shutil

from fontTools import subset
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BRAND = Path(r"G:\My Drive\Research\Business related\YMR branding\logo")
FONT_SRC = Path(r"C:\repos\yenmacro-brand\fonts")
ASSETS = ROOT / "assets"

LOGO_FILES = [
    ("svg/yenmacro-horizontal.svg", "logo/yenmacro-horizontal.svg"),
    ("svg/yenmacro-favicon.svg", "logo/yenmacro-favicon.svg"),
    ("favicon.ico", "../favicon.ico"),
    ("png/yenmacro-favicon-180w.png", "logo/apple-touch-icon.png"),
    ("png/yenmacro-horizontal-1200w.png", "logo/yenmacro-horizontal-1200w.png"),
    # Email signature logo (Gmail fetches it from the public site).
    ("png/yenmacro-horizontal-small-300w.png", "logo/yenmacro-horizontal-small-300w.png"),
    ("png/yenmacro-horizontal-small-600w.png", "logo/yenmacro-horizontal-small-600w.png"),
]


def copy_logos():
    for src, dst in LOGO_FILES:
        out = (ASSETS / dst).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BRAND / src, out)


def build_workspace_logo():
    # Google Workspace custom logo (Gmail header): at most 320x132 px; stacked layout fits best.
    src = Image.open(BRAND / "png" / "yenmacro-stacked-1200w.png").convert("RGBA")
    scale = min(304 / src.width, 116 / src.height)
    logo = src.resize((round(src.width * scale), round(src.height * scale)), Image.LANCZOS)
    canvas = Image.new("RGBA", (320, 132), (255, 255, 255, 0))
    canvas.paste(logo, ((320 - logo.width) // 2, (132 - logo.height) // 2), logo)
    # Palette PNG keeps it under Google's 30 KB logo limit.
    canvas = canvas.quantize(colors=128, method=Image.Quantize.FASTOCTREE)
    canvas.save(ASSETS / "logo" / "yenmacro-workspace-320x132.png", optimize=True)


def build_font():
    # Latin-1 plus the punctuation the copy uses (dashes, quotes, middle dot, ellipsis).
    unicodes = list(range(0x20, 0x7F)) + list(range(0xA0, 0x100)) + [
        0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026, 0x00B7, 0x20AC,
    ]
    out_dir = ASSETS / "fonts"
    out_dir.mkdir(parents=True, exist_ok=True)
    opts = subset.Options()
    opts.flavor = "woff"
    opts.layout_features = ["*"]
    font = subset.load_font(str(FONT_SRC / "Mulish-wght.ttf"), opts)
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=unicodes)
    sub.subset(font)
    subset.save_font(font, str(out_dir / "Mulish-wght-latin.woff"), opts)
    shutil.copy2(FONT_SRC / "OFL.txt", out_dir / "OFL.txt")


def build_portrait():
    img = Image.open(ROOT / "tools" / "portrait-source.jpg").convert("RGB")
    img = img.resize((480, 640), Image.LANCZOS)
    (ASSETS / "img").mkdir(parents=True, exist_ok=True)
    img.save(ASSETS / "img" / "takuji-okubo.jpg", quality=84, optimize=True, progressive=True)


if __name__ == "__main__":
    copy_logos()
    build_workspace_logo()
    build_font()
    build_portrait()
    for p in sorted(ASSETS.rglob("*")) + [ROOT / "favicon.ico"]:
        if p.is_file():
            print(f"{p.relative_to(ROOT)}  {p.stat().st_size:,} bytes")
