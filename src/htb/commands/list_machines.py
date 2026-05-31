from rich.table import Table

from ..api import get_api_key, list_machines, search_machines
from ..config import HTB_BASE
from ..ui import console, die, header, warn

_DIFF_COLORS = {
    "easy": "green",
    "medium": "yellow",
    "hard": "red",
    "insane": "magenta",
}


def _machine_table(machines: list[dict]) -> Table:
    table = Table(show_header=True, header_style="bold cyan", border_style="dim")
    table.add_column("Name", style="bold", min_width=12)
    table.add_column("OS", min_width=8)
    table.add_column("Schwierigkeit", min_width=10)
    table.add_column("Punkte", justify="right", min_width=6)
    table.add_column("Rating", min_width=6)
    table.add_column("Release", min_width=10)
    table.add_column("Lokal", justify="center", min_width=5)

    local_names = (
        {d.name.lower() for d in HTB_BASE.iterdir() if d.is_dir()} if HTB_BASE.exists() else set()
    )

    for m in machines:
        diff = m.get("difficultyText") or m.get("difficulty") or "?"
        color = _DIFF_COLORS.get(diff.lower(), "white")
        pts = m.get("static_points") or m.get("points") or "?"
        name = m.get("name", "?")
        local = "[green]●[/green]" if name.lower() in local_names else ""
        table.add_row(
            name,
            m.get("os", "?"),
            f"[{color}]{diff}[/{color}]",
            str(pts),
            f"★ {m.get('star') or m.get('stars', '?')}",
            (m.get("release") or "?")[:10],
            local,
        )
    return table


def run(args: list[str]):
    key = get_api_key()
    if not key:
        die("Kein API-Key — HTB_API_KEY oder ~/.config/htb/api_key")

    retired = "--retired" in args
    os_filter = None
    diff_filter = None
    search_query = None
    for i, a in enumerate(args):
        if a == "--os" and i + 1 < len(args):
            os_filter = args[i + 1].lower()
        if a == "--diff" and i + 1 < len(args):
            diff_filter = args[i + 1].lower()
        if a == "--search" and i + 1 < len(args):
            search_query = args[i + 1]

    if search_query:
        label = f"Suche: {search_query}"
    elif retired:
        label = "Retired Machines"
    else:
        label = "Active Machines"
    header(label)

    if search_query:
        machines = search_machines(key, search_query)
    else:
        machines = list_machines(key, retired=retired)
    if not machines:
        warn("Keine Maschinen gefunden oder API nicht erreichbar")
        return

    if os_filter:
        machines = [m for m in machines if os_filter in (m.get("os") or "").lower()]
    if diff_filter:
        machines = [
            m
            for m in machines
            if diff_filter in (m.get("difficultyText") or m.get("difficulty") or "").lower()
        ]

    console.print(f"  {len(machines)} Maschinen\n")
    console.print(_machine_table(machines))
    print()
