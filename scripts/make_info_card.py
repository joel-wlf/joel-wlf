#!/usr/bin/env python3
"""Generate Joel's animated terminal info card."""

from __future__ import annotations

import os
from pathlib import Path


WIDTH = 510
HEIGHT = 500


ROWS = [
    ("role", "product-minded full-stack developer"),
    ("based", "Germany"),
    ("focus", "operational software + embedded systems"),
    ("stack", "TypeScript · React · Next.js · Electron"),
    ("data", "PostgreSQL · Prisma · Supabase · PocketBase"),
    ("infra", "AWS · Docker · Linux · Cloudflare"),
    ("method", "understand the workflow, then simplify it"),
    ("contact", "joel377wolf@gmail.com"),
]


def escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(static: bool = False) -> str:
    row_nodes: list[str] = []
    for index, (key, value) in enumerate(ROWS):
        y = 161 + index * 35
        delay = 0 if static else 0.30 + index * 0.13
        klass = "row static" if static else "row"
        row_nodes.append(
            f'<g class="{klass}" style="animation-delay:{delay:.2f}s">'
            f'<text x="31" y="{y}" class="key">{escape(key)}</text>'
            f'<text x="121" y="{y}" class="value">{escape(value)}</text></g>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">Joel Wolf developer information card</title>
  <desc id="desc">A terminal-style card describing Joel's role, focus, stack and contact information.</desc>
  <defs>
    <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#111827" />
      <stop offset="1" stop-color="#07111f" />
    </linearGradient>
    <linearGradient id="name" x1="0" y1="0" x2="1" y2="0">
      <stop stop-color="#5eead4" />
      <stop offset="1" stop-color="#60a5fa" />
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="508" height="498" rx="16" fill="url(#panel)" stroke="#253349" />
  <circle cx="22" cy="19" r="4" fill="#fb7185" />
  <circle cx="36" cy="19" r="4" fill="#fbbf24" />
  <circle cx="50" cy="19" r="4" fill="#34d399" />
  <text x="255" y="22" text-anchor="middle" class="chrome">joel@github: ~</text>
  <text x="30" y="72" class="prompt">$ whoami</text>
  <text x="30" y="109" class="name">Joel Wolf</text>
  <text x="30" y="132" class="tagline">I build useful software for real-world work.</text>
  <line x1="30" y1="145" x2="480" y2="145" stroke="#253349" />
  {''.join(row_nodes)}
  <rect x="30" y="461" width="450" height="1" fill="#253349" />
  <text x="30" y="483" class="footer">available for thoughtful products &amp; hard operational problems</text>
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .chrome {{ fill: #7f8da3; font-size: 10px; font-weight: 600; }}
    .prompt {{ fill: #5eead4; font-size: 13px; font-weight: 700; }}
    .name {{ fill: url(#name); font-size: 28px; font-weight: 800; letter-spacing: -.5px; }}
    .tagline {{ fill: #c8d3e2; font-size: 12px; }}
    .key {{ fill: #60a5fa; font-size: 12px; font-weight: 700; }}
    .value {{ fill: #d7e0ec; font-size: 11.5px; }}
    .footer {{ fill: #7f8da3; font-size: 9.6px; }}
    .row {{ opacity: 0; transform: translateX(-9px); animation: reveal .38s ease-out forwards; }}
    .row.static {{ opacity: 1; transform: none; animation: none; }}
    @keyframes reveal {{ to {{ opacity: 1; transform: translateX(0); }} }}
    @media (prefers-reduced-motion: reduce) {{ .row {{ opacity: 1; transform: none; animation: none; }} }}
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
