#!/usr/bin/env python3
"""Fetch and parse GitHub's public contribution calendar without a token."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path


USERNAME = "joel-wlf"


@dataclass
class Contribution:
    day: str
    count: int
    level: int


class ContributionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.cells: dict[str, Contribution] = {}
        self.tooltip_target: str | None = None
        self.tooltip_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = (values.get("class") or "").split()
        if tag == "td" and "ContributionCalendar-day" in classes:
            cell_id = values.get("id")
            day = values.get("data-date")
            if cell_id and day:
                self.cells[cell_id] = Contribution(
                    day=day,
                    count=0,
                    level=int(values.get("data-level") or 0),
                )
        elif tag == "tool-tip":
            target = values.get("for")
            if target in self.cells:
                self.tooltip_target = target
                self.tooltip_text = []

    def handle_data(self, data: str) -> None:
        if self.tooltip_target:
            self.tooltip_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "tool-tip" or not self.tooltip_target:
            return
        text = " ".join(self.tooltip_text).strip()
        match = re.search(r"([\d,]+) contribution", text)
        if match:
            self.cells[self.tooltip_target].count = int(match.group(1).replace(",", ""))
        self.tooltip_target = None
        self.tooltip_text = []


def load_html(input_path: Path | None) -> str:
    if input_path:
        return input_path.read_text(encoding="utf-8")
    import requests

    url = f"https://github.com/users/{USERNAME}/contributions"
    response = requests.get(url, timeout=30, headers={"User-Agent": "profile-art/1.0"})
    response.raise_for_status()
    return response.text


def streaks(days: list[Contribution]) -> tuple[int, int]:
    by_day = {date.fromisoformat(item.day): item.count for item in days}
    if not by_day:
        return 0, 0

    ordered = sorted(by_day)
    longest = 0
    running = 0
    for cursor in ordered:
        if by_day[cursor] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

    latest = min(date.today(), ordered[-1])
    if by_day.get(latest, 0) == 0:
        latest -= timedelta(days=1)
    current = 0
    while by_day.get(latest, 0) > 0:
        current += 1
        latest -= timedelta(days=1)
    return current, longest


def build_payload(html: str) -> dict[str, object]:
    parser = ContributionParser()
    parser.feed(html)
    days = sorted(parser.cells.values(), key=lambda item: item.day)
    if not days:
        raise RuntimeError("GitHub contribution cells were not found")

    current, longest = streaks(days)
    monthly: dict[str, int] = defaultdict(int)
    for item in days:
        monthly[item.day[:7]] += item.count
    best = max(days, key=lambda item: item.count)

    return {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": [item.__dict__ for item in days],
        "stats": {
            "total": sum(item.count for item in days),
            "active_days": sum(item.count > 0 for item in days),
            "current_streak": current,
            "longest_streak": longest,
            "best_day": best.day,
            "best_day_count": best.count,
            "monthly": dict(sorted(monthly.items())),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, help="Parse a saved GitHub response")
    parser.add_argument("--output", type=Path, default=Path("data/contributions.json"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_payload(load_html(args.input)), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
