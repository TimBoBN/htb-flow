from rich.table import Table

from ..api import get_api_key, get_tracks
from ..ui import console, die, header, warn

_DIFF_COLORS = {"Easy": "green", "Medium": "yellow", "Hard": "red", "Insane": "magenta"}


def run():
    key = get_api_key()
    if not key:
        die("Kein API-Key — htb key set")

    header("Tracks / Lernpfade")
    tracks = get_tracks(key)

    if not tracks:
        warn("Keine Tracks gefunden oder API nicht verfügbar")
        return

    table = Table(show_header=True, header_style="bold cyan", border_style="dim")
    table.add_column("Name", style="bold", min_width=28)
    table.add_column("Difficulty", min_width=10)
    table.add_column("Official", justify="center", min_width=8)

    for t in tracks:
        diff = t.get("difficulty", "?") or "?"
        color = _DIFF_COLORS.get(diff, "white")
        official = "[green]✔[/green]" if t.get("official") else ""
        table.add_row(
            t.get("name", "?"),
            f"[{color}]{diff}[/{color}]",
            official,
        )

    console.print(f"  {len(tracks)} Tracks\n")
    console.print(table)
    print()
