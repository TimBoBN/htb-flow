from ..api import load_machine_profile
from ..config import HTB_BASE
from ..ui import console, header, warn


def run(machine: str):
    header(f"Info: {machine}")

    profile = load_machine_profile(machine)
    if not profile:
        warn("Machine not found or API unreachable")
        return

    diff = profile.get("difficulty", "?")
    diff_colors = {"Easy": "green", "Medium": "yellow", "Hard": "red", "Insane": "magenta"}
    color = diff_colors.get(diff, "white")

    console.print(f"  [bold]OS:[/bold]            {profile.get('os', '?')}")
    console.print(f"  [bold]Difficulty:[/bold] [{color}]{diff}[/{color}]")
    console.print(f"  [bold]Points:[/bold]        {profile.get('points', '?')}")
    console.print(f"  [bold]Release:[/bold]       {profile.get('release', '?')}")
    console.print(f"  [bold]Rating:[/bold]        ★ {profile.get('stars', '?')}")

    ip = profile.get("ip", "")
    if ip:
        console.print(f"  [bold]Active IP:[/bold]     [cyan]{ip}[/cyan]")
    else:
        console.print("  [bold]Active IP:[/bold]     [dim]not active[/dim]")

    box_dir = HTB_BASE / machine
    if box_dir.exists():
        console.print(f"  [bold]Local:[/bold]         [green]✔[/green] {box_dir}")
    else:
        console.print("  [bold]Local:[/bold]         [dim]not present[/dim]")
    print()
