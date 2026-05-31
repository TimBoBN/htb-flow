from datetime import datetime, timezone

from ..api import get_api_key, get_season
from ..ui import console, die, header, warn


def _days_left(end_date: str) -> str:
    try:
        dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        delta = dt - datetime.now(timezone.utc)
        days = delta.days
        if days < 0:
            return "ended"
        return f"{days} days left"
    except Exception:
        return "?"


def run():
    key = get_api_key()
    if not key:
        die("No API key — run: htb key set")

    header("Season")
    season = get_season(key)

    if not season:
        warn("No active season found")
        return

    state = season.get("state", "?")
    color = "green" if state == "active" else "yellow"

    console.print(f"  [bold]Name:[/bold]     {season.get('name', '?')}")
    console.print(f"  [bold]Subtitle:[/bold] {season.get('subtitle', '?')}")
    console.print(f"  [bold]Status:[/bold]   [{color}]{state}[/{color}]")
    console.print(
        f"  [bold]Week:[/bold]     {season.get('current_week', '?')} / "
        f"{season.get('weeks', '?')}"
    )
    console.print(f"  [bold]Players:[/bold]  {season.get('players', '?')}")

    if end := season.get("end_date"):
        console.print(f"  [bold]Ends:[/bold]     {end[:10]}  [dim]({_days_left(end)})[/dim]")

    if start := season.get("start_date"):
        console.print(f"  [bold]Started:[/bold]  {start[:10]}")
    print()
