#!/usr/bin/env python3
"""Generate Joel's animated terminal info card."""

from __future__ import annotations

import os
from pathlib import Path


WIDTH = 920
HEIGHT = 310


LEFT_ROWS = [
    ("role", "product-minded full-stack developer"),
    ("based", "Germany"),
    ("focus", "operational + embedded systems"),
    ("contact", "joel377wolf@gmail.com"),
]

RIGHT_ROWS = [
    ("stack", "TypeScript · React · Next.js · Electron"),
    ("data", "PostgreSQL · Prisma · Supabase · PocketBase"),
    ("infra", "AWS · Docker · Linux · Cloudflare"),
    ("method", "understand the workflow, then simplify it"),
]


def escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(static: bool = False) -> str:
    row_nodes: list[str] = []
    for column, rows in enumerate((LEFT_ROWS, RIGHT_ROWS)):
        key_x = 24 + column * 465
        value_x = key_x + 92
        for index, (key, value) in enumerate(rows):
            y = 151 + index * 31
            delay = 0 if static else 0.28 + (index + column * len(LEFT_ROWS)) * 0.10
            klass = "row static" if static else "row"
            row_nodes.append(
                f'<g class="{klass}" style="animation-delay:{delay:.2f}s">'
                f'<text x="{key_x}" y="{y}" class="key">{escape(key)}</text>'
                f'<text x="{value_x}" y="{y}" class="value">{escape(value)}</text></g>'
            )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">Joel Wolf developer information card</title>
  <desc id="desc">A terminal-style card describing Joel's role, focus, stack and contact information.</desc>
  <text x="24" y="24" class="prompt">$ whoami</text>
  <text x="24" y="69" class="name">Joel Wolf</text>
  <text x="24" y="96" class="tagline">I build useful software for real-world work.</text>
  <line x1="24" y1="116" x2="896" y2="116" class="divider" />
  {''.join(row_nodes)}
  <line x1="24" y1="279" x2="896" y2="279" class="divider" />
  <text x="24" y="301" class="footer">available for thoughtful products &amp; hard operational problems</text>
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .prompt {{ fill: #5eead4; font-size: 13px; font-weight: 700; }}
    .name {{ fill: #5eead4; font-size: 32px; font-weight: 800; letter-spacing: -.5px; }}
    .tagline {{ fill: #cbd5e1; font-size: 13px; }}
    .key {{ fill: #60a5fa; font-size: 12px; font-weight: 700; }}
    .value {{ fill: #dbe5f1; font-size: 11.5px; }}
    .footer {{ fill: #94a3b8; font-size: 9.8px; }}
    .divider {{ stroke: #334155; stroke-width: 1; }}
    .row {{ opacity: 0; transform: translateX(-9px); animation: reveal .38s ease-out forwards; }}
    .row.static {{ opacity: 1; transform: none; animation: none; }}
    @keyframes reveal {{ to {{ opacity: 1; transform: translateX(0); }} }}
    @media (prefers-reduced-motion: reduce) {{ .row {{ opacity: 1; transform: none; animation: none; }} }}
    @media (prefers-color-scheme: light) {{
      .prompt, .name {{ fill: #0f766e; }}
      .tagline, .value {{ fill: #0f172a; }}
      .key {{ fill: #2563eb; }}
      .footer {{ fill: #64748b; }}
      .divider {{ stroke: #cbd5e1; }}
    }}
  </style>
</svg>
'''


def main() -> None:
    output = Path("assets/info-card.svg")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(static=os.getenv("STATIC") == "1"), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
