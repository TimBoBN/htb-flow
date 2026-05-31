from rich.table import Table

from ..api import get_api_key, get_fortresses
from ..ui import console, die, header, warn


def run():
    key = get_api_key()
    if not key:
        die("No API key — run: htb key set")

    header("Fortresses")
    fortresses = get_fortresses(key)

    if not fortresses:
        warn("No fortresses found or API unavailable")
        return

    table = Table(show_header=True, header_style="bold cyan", border_style="dim")
    table.add_column("Name", style="bold", min_width=14)
    table.add_column("Flags", justify="right", min_width=6)
    table.add_column("Owned", justify="right", min_width=6)
    table.add_column("New", justify="center", min_width=4)

    for f in fortresses:
        new_marker = "[yellow]★[/yellow]" if f.get("new") else ""
        table.add_row(
            f.get("name", "?"),
            str(f.get("number_of_flags", "?")),
            str(f.get("owned_flags", "?")),
            new_marker,
        )

    console.print(f"  {len(fortresses)} fortress(es)\n")
    console.print(table)
    print()
