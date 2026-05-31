from ..api import load_machine_profile
from ..config import HTB_BASE
from ..ui import console, header, warn


def run(machine: str):
    header(f"Info: {machine}")

    profile = load_machine_profile(machine)
    if not profile:
        warn("Maschine nicht gefunden oder API nicht erreichbar")
        return

    diff = profile.get("difficulty", "?")
    diff_colors = {"Easy": "green", "Medium": "yellow", "Hard": "red", "Insane": "magenta"}
    color = diff_colors.get(diff, "white")

    console.print(f"  [bold]OS:[/bold]            {profile.get('os', '?')}")
    console.print(f"  [bold]Schwierigkeit:[/bold] [{color}]{diff}[/{color}]")
    console.print(f"  [bold]Punkte:[/bold]        {profile.get('points', '?')}")
    console.print(f"  [bold]Release:[/bold]       {profile.get('release', '?')}")
    console.print(f"  [bold]Rating:[/bold]        ★ {profile.get('stars', '?')}")

    ip = profile.get("ip", "")
    if ip:
        console.print(f"  [bold]Aktive IP:[/bold]     [cyan]{ip}[/cyan]")
    else:
        console.print(f"  [bold]Aktive IP:[/bold]     [dim]nicht aktiv[/dim]")

    box_dir = HTB_BASE / machine
    if box_dir.exists():
        console.print(f"  [bold]Lokal:[/bold]         [green]✔[/green] {box_dir}")
    else:
        console.print(f"  [bold]Lokal:[/bold]         [dim]nicht vorhanden[/dim]")
    print()
