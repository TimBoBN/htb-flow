from rich.table import Table

from .. import notes
from ..config import HTB_BASE
from ..ui import console, header, ok, warn


def run():
    header("To-Do — Laufende Boxen")

    if not HTB_BASE.exists():
        warn(f"HTB_BASE nicht gefunden: {HTB_BASE}")
        return

    machines = []
    for d in sorted(HTB_BASE.iterdir()):
        if not d.is_dir() or d.name.endswith(".tar.gz"):
            continue
        notes_path = d / "notes.md"
        if not notes_path.exists():
            continue
        n = notes.parse(notes_path)
        machines.append(
            {
                "name": d.name,
                "os": n.get("os", "?"),
                "difficulty": n.get("difficulty", "?"),
                "ip": n.get("ip", ""),
                "user": bool(n.get("user_flag")),
                "root": bool(n.get("root_flag")),
            }
        )

    if not machines:
        ok("Keine laufenden Boxen gefunden")
        return

    diff_colors = {"Easy": "green", "Medium": "yellow", "Hard": "red", "Insane": "magenta"}

    table = Table(show_header=True, header_style="bold cyan", border_style="dim")
    table.add_column("Name", style="bold", min_width=12)
    table.add_column("OS", min_width=8)
    table.add_column("Schwierigkeit", min_width=10)
    table.add_column("IP", min_width=14)
    table.add_column("User", justify="center", min_width=6)
    table.add_column("Root", justify="center", min_width=6)

    for m in machines:
        diff = m["difficulty"]
        color = diff_colors.get(diff, "white")
        table.add_row(
            m["name"],
            m["os"],
            f"[{color}]{diff}[/{color}]",
            m["ip"] or "[dim]—[/dim]",
            "[green]✔[/green]" if m["user"] else "[red]✘[/red]",
            "[green]✔[/green]" if m["root"] else "[red]✘[/red]",
        )

    console.print(f"  {len(machines)} Box(en)\n")
    console.print(table)
    print()
