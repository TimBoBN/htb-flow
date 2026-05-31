from ..api import get_api_key, get_profile
from ..ui import console, die, header, warn


def run():
    key = get_api_key()
    if not key:
        die("No API key — run: htb key set")

    header("Profile")
    p = get_profile(key)
    if not p:
        warn("Profile not available")
        return

    rank_colors = {
        "Noob": "dim",
        "Script Kiddie": "white",
        "Hacker": "cyan",
        "Pro Hacker": "green",
        "Elite Hacker": "yellow",
        "Guru": "magenta",
        "Omniscient": "bold red",
    }
    rank = p.get("rank", "?")
    color = rank_colors.get(rank, "white")

    console.print(f"  [bold]Name:[/bold]         {p.get('name', '?')}")
    console.print(f"  [bold]Rank:[/bold]         [{color}]{rank}[/{color}]")
    console.print(f"  [bold]Punkte:[/bold]       {p.get('points', '?')}")
    console.print(f"  [bold]Ranking:[/bold]      #{p.get('ranking', '?')}")
    console.print(f"  [bold]User Owns:[/bold]    {p.get('user_owns', '?')}")
    console.print(f"  [bold]System Owns:[/bold]  {p.get('system_owns', '?')}")
    console.print(f"  [bold]User Bloods:[/bold]  {p.get('user_bloods', '?')}")
    console.print(f"  [bold]Root Bloods:[/bold]  {p.get('system_bloods', '?')}")
    if p.get("country_name"):
        console.print(f"  [bold]Country:[/bold]         {p['country_name']}")
    print()
