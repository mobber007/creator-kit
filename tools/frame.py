#!/usr/bin/env python3
"""frame.py — fit pictures to a platform's shape, and strip their location data, with Pillow.

  frame.py <image>... [--ratio 9:16] [--width 1080] [--mode blur|crop|pad] [--out <dir>]
  frame.py --selftest

  blur  the whole picture, centred on a blurred, darkened copy of itself (nothing cut off)   (default)
  crop  fill the frame, cutting the edges that do not fit
  pad   the whole picture on black

Writes <out>/<name>-<w>x<h>.jpg (default out: beside each image). Every output is saved without EXIF, so no GPS
position or camera serial leaves with it. Common shapes: reels and stories 9:16, feed 4:5, square 1:1, YouTube 16:9.
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

try:
    from PIL import Image, ImageFilter, ImageEnhance, ImageOps
except ImportError:
    sys.exit("frame: Pillow is not installed (pip install pillow)")


def fit(im: Image.Image, w: int, h: int, mode: str) -> Image.Image:
    im = ImageOps.exif_transpose(im).convert("RGB")       # honour the camera's rotation before dropping EXIF
    if mode == "crop":
        return ImageOps.fit(im, (w, h), Image.LANCZOS)
    inner = ImageOps.contain(im, (w, h), Image.LANCZOS)
    if mode == "pad":
        bg = Image.new("RGB", (w, h))
    else:
        bg = ImageOps.fit(im, (w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(max(w, h) // 30))
        bg = ImageEnhance.Brightness(bg).enhance(0.55)
    bg.paste(inner, ((w - inner.width) // 2, (h - inner.height) // 2))
    return bg


def size(ratio: str, width: int) -> tuple[int, int]:
    try:
        a, b = (int(x) for x in ratio.split(":"))
        if a <= 0 or b <= 0 or width <= 0: raise ValueError
    except ValueError:
        sys.exit(f"frame: bad --ratio {ratio!r} or --width {width} (want like 9:16 and a positive width)")
    return width, round(width * b / a)


def selftest() -> int:
    wide = Image.new("RGB", (400, 200), (200, 30, 30))
    checks = {}
    for mode in ("blur", "crop", "pad"):
        out = fit(wide, 90, 160, mode)
        checks[f"{mode} gives 90x160"] = out.size == (90, 160)
    checks["crop fills with the picture"] = fit(wide, 90, 160, "crop").getpixel((5, 5)) == (200, 30, 30)
    checks["pad leaves black above"] = fit(wide, 90, 160, "pad").getpixel((45, 2)) == (0, 0, 0)
    checks["ratio maths"] = size("9:16", 1080) == (1080, 1920) and size("4:5", 1080) == (1080, 1350)
    for name, ok in checks.items(): print(f"{'ok  ' if ok else 'FAIL'} {name}")
    return 0 if all(checks.values()) else 1


def main() -> int:
    if sys.argv[1:] == ["--selftest"]: return selftest()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+", type=Path)
    ap.add_argument("--ratio", default="9:16")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--mode", choices=("blur", "crop", "pad"), default="blur")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    w, h = size(a.ratio, a.width)
    bad = 0
    for p in a.images:
        try:
            with Image.open(p) as im: out = fit(im, w, h, a.mode)
        except (OSError, ValueError) as e:
            print(f"frame: skipped {p}: {e}", file=sys.stderr); bad += 1; continue
        d = a.out or p.parent; d.mkdir(parents=True, exist_ok=True)
        dest = d / f"{p.stem}-{w}x{h}.jpg"
        out.save(dest, "JPEG", quality=92, optimize=True)      # no exif= argument: metadata is not written
        print(dest)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
