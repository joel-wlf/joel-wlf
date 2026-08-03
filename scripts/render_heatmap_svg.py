#!/usr/bin/env python3
"""Render contribution JSON as an animated terminal heatmap SVG."""

from __future__ import annotations

import calendar
import json
from datetime import date, timedelta
from pathlib import Path


WIDTH = 920
HEIGHT = 230
PALETTE = ["#182333", "#123d3c", "#0f6b5c", "#12a884", "#35d7a5"]


def render(payload: dict[str, object]) -> str:
    raw_days = payload["days"]
    days = sorted(raw_days, key=lambda item: item["day"])
    stats = payload["stats"]
    start = date.fromisoformat(days[0]["day"])
    start -= timedelta(days=(start.weekday() + 1) % 7)

    grid_x = 47
    grid_y = 74
    step = 14
    size = 10
    cells: list[str] = []
    for item in days:
        current = date.fromisoformat(item["day"])
        offset = (current - start).days
        week = offset // 7
        weekday = (current.weekday() + 1) % 7
        x = grid_x + week * step
        y = grid_y + weekday * step
        level = max(0, min(int(item["level"]), len(PALETTE) - 1))
        delay = 0.15 + week * 0.012 + weekday * 0.018
        label = f'{item["day"]}: {item["count"]} contributions'
        cells.append(
            f'<rect class="day" x="{x}" y="{y}" width="{size}" height="{size}" rx="2" '
            f'fill="{PALETTE[level]}" style="animation-delay:{delay:.3f}s">'
            f'<title>{label}</title></rect>'
        )

    # Month labels are placed over the first week containing the first day of a month.
    months: list[str] = []
    seen: set[tuple[int, int]] = set()
    for item in days:
        current = date.fromisoformat(item["day"])
        key = (current.year, current.month)
        if current.day <= 7 and key not in seen:
            week = (current - start).days // 7
            months.append(
                f'<text x="{grid_x + week * step}" y="61" class="month">{calendar.month_abbr[current.month]}</text>'
            )
            seen.add(key)

    legend_x = 804
    legend = [
        f'<rect x="{legend_x + i * 15}" y="178" width="10" height="10" rx="2" fill="{color}" />'
        for i, color in enumerate(PALETTE)
    ]

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">Joel Wolf's GitHub contributions</title>
  <desc id="desc">{stats['total']} contributions in the last year, shown as an animated calendar heatmap.</desc>
  <defs>
    <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#111827" />
      <stop offset="1" stop-color="#07111f" />
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="918" height="228" rx="16" fill="url(#panel)" stroke="#253349" />
  <circle cx="22" cy="19" r="4" fill="#fb7185" />
  <circle cx="36" cy="19" r="4" fill="#fbbf24" />
  <circle cx="50" cy="19" r="4" fill="#34d399" />
  <text x="460" y="22" text-anchor="middle" class="chrome">contributions.sh</text>
  <text x="30" y="48" class="prompt">$ git log --graph --since="1 year ago"</text>
  {''.join(months)}
  <text x="21" y="87" class="weekday">Mon</text>
  <text x="21" y="115" class="weekday">Wed</text>
  <text x="21" y="143" class="weekday">Fri</text>
  <g>{''.join(cells)}</g>
  <line x1="30" y1="165" x2="890" y2="165" stroke="#253349" />
  <text x="30" y="190" class="total">{stats['total']:,} contributions</text>
  <text x="210" y="190" class="stat">current streak  <tspan class="strong">{stats['current_streak']}d</tspan></text>
  <text x="382" y="190" class="stat">longest  <tspan class="strong">{stats['longest_streak']}d</tspan></text>
  <text x="500" y="190" class="stat">best day  <tspan class="strong">{stats['best_day_count']}</tspan></text>
  <text x="764" y="187" class="legend-label">less</text>
  {''.join(legend)}
  <text x="881" y="187" class="legend-label">more</text>
  <text x="30" y="213" class="foot">updated daily from GitHub's public contribution calendar</text>
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .chrome {{ fill: #7f8da3; font-size: 10px; font-weight: 600; }}
    .prompt {{ fill: #5eead4; font-size: 12px; font-weight: 700; }}
    .month, .weekday, .legend-label, .foot {{ fill: #7f8da3; font-size: 9px; }}
    .total {{ fill: #d7e0ec; font-size: 11px; font-weight: 700; }}
    .stat {{ fill: #8f9db0; font-size: 10px; }}
    .strong {{ fill: #5eead4; font-weight: 800; }}
    .day {{ opacity: 0; transform: translateY(-8px); animation: drop .36s ease-out forwards; }}
    @keyframes drop {{ to {{ opacity: 1; transform: translateY(0); }} }}
    @media (prefers-reduced-motion: reduce) {{ .day {{ opacity: 1; transform: none; animation: none; }} }}
  </style>
</svg>
'''


def main() -> None:
    source = Path("data/contributions.json")
    output = Path("assets/contrib-heatmap.svg")
    payload = json.loads(source.read_text(encoding="utf-8"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(payload), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
