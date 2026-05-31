from rich.table import Table

from ..api import get_api_key, list_machines
from ..ui import console, header, warn, die


_DIFF_COLORS = {
    "easy":   "green",
    "medium": "yellow",
    "hard":   "red",
    "insane": "magenta",
}


def _machine_table(machines: list[dict]) -> Table:
    table = Table(show_header=True, header_style="bold cyan", border_style="dim")
    table.add_column("Name",          style="bold", min_width=12)
    table.add_column("OS",            min_width=8)
    table.add_column("Schwierigkeit", min_width=10)
    table.add_column("Punkte",        justify="right", min_width=6)
    table.add_column("Rating",        min_width=6)
    table.add_column("Release",       min_width=10)

    for m in machines:
        diff = m.get("difficultyText") or m.get("difficulty") or "?"
        color = _DIFF_COLORS.get(diff.lower(), "white")
        pts = m.get("static_points") or m.get("points") or "?"
        table.add_row(
            m.get("name", "?"),
            m.get("os", "?"),
            f"[{color}]{diff}[/{color}]",
            str(pts),
            f"★ {m.get('star') or m.get('stars', '?')}",
            (m.get("release") or "?")[:10],
        )
    return table


def run(args: list[str]):
    key = get_api_key()
    if not key:
        die("Kein API-Key — HTB_API_KEY oder ~/.config/htb/api_key")

    retired    = "--retired" in args
    os_filter  = None
    diff_filter = None
    for i, a in enumerate(args):
        if a == "--os"   and i + 1 < len(args):
            os_filter   = args[i + 1].lower()
        if a == "--diff" and i + 1 < len(args):
            diff_filter = args[i + 1].lower()

    label = "Retired Machines" if retired else "Active Machines"
    header(label)

    machines = list_machines(key, retired=retired)
    if not machines:
        warn("Keine Maschinen gefunden oder API nicht erreichbar")
        return

    if os_filter:
        machines = [m for m in machines if os_filter in (m.get("os") or "").lower()]
    if diff_filter:
        machines = [m for m in machines
                    if diff_filter in (m.get("difficultyText") or m.get("difficulty") or "").lower()]

    console.print(f"  {len(machines)} Maschinen\n")
    console.print(_machine_table(machines))
    print()
