#!/usr/bin/env python3
"""Turn Joel's portrait into a self-revealing monochrome ASCII SVG."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


RAMP = "@%#*+=-:. "
COLS = 62
ROWS = 54
WIDTH = 390
HEIGHT = 500


def prepare_portrait(source: Path) -> Image.Image:
    image = Image.open(source).convert("RGB")
    width, height = image.size

    # The attached portrait is tall. This crop keeps the head and shoulders and
    # drops most of the bright bokeh around the subject.
    left = int(width * 0.035)
    top = int(height * 0.035)
    right = int(width * 0.965)
    bottom = int(height * 0.94)
    image = image.crop((left, top, right, bottom))

    # A soft, hand-tuned silhouette isolates the subject without committing the
    # original photo or requiring an ML background-removal model.
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    w, h = image.size
    head = [
        (0.18 * w, 0.12 * h),
        (0.30 * w, 0.055 * h),
        (0.55 * w, 0.045 * h),
        (0.76 * w, 0.12 * h),
        (0.83 * w, 0.28 * h),
        (0.81 * w, 0.50 * h),
        (0.72 * w, 0.64 * h),
        (0.61 * w, 0.70 * h),
        (0.40 * w, 0.70 * h),
        (0.27 * w, 0.62 * h),
        (0.17 * w, 0.47 * h),
        (0.13 * w, 0.27 * h),
    ]
    shoulders = [
        (0.35 * w, 0.58 * h),
        (0.20 * w, 0.69 * h),
        (0.0, 0.78 * h),
        (0.0, h),
        (w, h),
        (w, 0.72 * h),
        (0.72 * w, 0.63 * h),
        (0.62 * w, 0.57 * h),
    ]
    draw.polygon(head, fill=255)
    draw.polygon(shoulders, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=max(3, int(w * 0.012))))

    prepared = Image.composite(image, Image.new("RGB", image.size, "white"), mask)
    gray = ImageOps.grayscale(prepared)
    gray = ImageOps.autocontrast(gray, cutoff=(1.0, 2.0))
    gray = ImageEnhance.Contrast(gray).enhance(1.22)
    gray = gray.filter(ImageFilter.UnsharpMask(radius=1.2, percent=125, threshold=4))
    return gray


def ascii_rows(image: Image.Image) -> list[str]:
    sample = image.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    pixels = np.asarray(sample, dtype=np.float32)
    indices = np.clip((pixels / 255.0 * (len(RAMP) - 1)).astype(int), 0, len(RAMP) - 1)
    rows = ["".join(RAMP[value] for value in row).rstrip() for row in indices]
    return [row if row else " " for row in rows]


def escape_xml(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_svg(rows: list[str]) -> str:
    x = 31
    y0 = 34
    line_height = 8.25
    reveal_width = 330

    clips: list[str] = []
    lines: list[str] = []
    cursors: list[str] = []
    for index, row in enumerate(rows):
        y = y0 + index * line_height
        begin = 0.16 + index * 0.035
        clips.append(
            f'<clipPath id="row-{index}"><rect x="{x}" y="{y - 7:.2f}" width="0" height="9">'
            f'<animate attributeName="width" from="0" to="{reveal_width}" dur="0.48s" '
            f'begin="{begin:.3f}s" fill="freeze" /></rect></clipPath>'
        )
        lines.append(
            f'<text x="{x}" y="{y:.2f}" clip-path="url(#row-{index})" '
            f'xml:space="preserve">{escape_xml(row)}</text>'
        )
        cursors.append(
            f'<rect class="cursor" x="{x}" y="{y - 6.8:.2f}" width="4" height="7.6" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.9;1" '
            f'dur="0.48s" begin="{begin:.3f}s" fill="freeze" />'
            f'<animate attributeName="x" from="{x}" to="{x + reveal_width}" dur="0.48s" '
            f'begin="{begin:.3f}s" fill="freeze" /></rect>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">ASCII portrait of Joel Wolf</title>
  <desc id="desc">A monochrome terminal-style portrait that reveals itself line by line.</desc>
  <defs>
    {''.join(clips)}
    <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#111827" />
      <stop offset="1" stop-color="#07111f" />
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="388" height="498" rx="16" fill="url(#panel)" stroke="#253349" />
  <circle cx="22" cy="19" r="4" fill="#fb7185" />
  <circle cx="36" cy="19" r="4" fill="#fbbf24" />
  <circle cx="50" cy="19" r="4" fill="#34d399" />
  <text x="195" y="22" text-anchor="middle" class="chrome">portrait.sh</text>
  <g fill="#b9f6de" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="7.7" font-weight="600">
    {''.join(lines)}
  </g>
  <g fill="#5eead4">{''.join(cursors)}</g>
  <style>
    .chrome {{ fill: #7f8da3; font: 600 10px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    @media (prefers-reduced-motion: reduce) {{
      animate {{ display: none; }}
      clipPath rect {{ width: {reveal_width}px; }}
      .cursor {{ display: none; }}
    }}
  </style>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="Portrait photo")
    parser.add_argument("--output", type=Path, default=Path("assets/joel-ascii.svg"))
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_svg(ascii_rows(prepare_portrait(args.source))), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
