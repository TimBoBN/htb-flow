from collections import defaultdict

from ..api import get_activity, get_api_key
from ..ui import console, die, header, warn

BAR_WIDTH = 28


def run():
    key = get_api_key()
    if not key:
        die("Kein API-Key — htb key set")

    header("Solve-Timeline")
    acts = get_activity(key)
    if not acts:
        warn("Keine Aktivität gefunden")
        return

    by_month: dict[str, int] = defaultdict(int)
    for a in acts:
        month = (a.get("date") or "")[:7]
        if month:
            by_month[month] += 1

    if not by_month:
        warn("Keine Daten")
        return

    max_count = max(by_month.values())
    total = sum(by_month.values())

    for month in sorted(by_month.keys(), reverse=True):
        count = by_month[month]
        bar_len = max(1, int(count / max_count * BAR_WIDTH))
        bar = "█" * bar_len
        console.print(f"  {month}  [cyan]{bar:<{BAR_WIDTH}}[/cyan]  {count:>3}")

    console.print(f"\n  [dim]Gesamt: {total} Solves in {len(by_month)} Monaten[/dim]")
    print()
