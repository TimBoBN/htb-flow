from rich.table import Table

from ..api import get_activity, get_api_key
from ..ui import console, die, header, warn


def run(limit: int = 20):
    key = get_api_key()
    if not key:
        die("Kein API-Key — htb key set")

    header("Aktivität")
    acts = get_activity(key)
    if not acts:
        warn("Keine Aktivität gefunden")
        return

    table = Table(show_header=True, header_style="bold cyan", border_style="dim")
    table.add_column("Datum", min_width=12)
    table.add_column("Box", style="bold", min_width=14)
    table.add_column("Typ", min_width=6)
    table.add_column("Punkte", justify="right", min_width=6)
    table.add_column("Blood", justify="center", min_width=5)

    for a in acts[:limit]:
        flag_type = a.get("type", "?")
        color = "green" if flag_type == "user" else "red"
        blood = "[red]🩸[/red]" if a.get("first_blood") else ""
        table.add_row(
            (a.get("date") or "")[:10],
            a.get("name", "?"),
            f"[{color}]{flag_type}[/{color}]",
            str(a.get("points", "?")),
            blood,
        )

    console.print(table)
    print()
