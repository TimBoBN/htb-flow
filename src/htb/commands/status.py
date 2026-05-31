from datetime import datetime, timezone

from ..api import get_active_machine, get_api_key
from ..ui import console, die, header, ok


def _time_remaining(expires_at: str) -> str:
    try:
        dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        delta = dt - datetime.now(timezone.utc)
        if delta.total_seconds() <= 0:
            return "[red]abgelaufen[/red]"
        h, rem = divmod(int(delta.total_seconds()), 3600)
        m = rem // 60
        return f"{h}h {m}m"
    except Exception:
        return "?"


def run():
    key = get_api_key()
    if not key:
        die("Kein API-Key — HTB_API_KEY oder ~/.config/htb/api_key")

    header("Aktive Maschine")
    info = get_active_machine(key)

    if not info:
        ok("Keine Maschine aktiv")
        return

    diff = info.get("difficultyText") or "?"
    diff_colors = {"Easy": "green", "Medium": "yellow", "Hard": "red", "Insane": "magenta"}
    diff_fmt = f"[{diff_colors.get(diff, 'white')}]{diff}[/{diff_colors.get(diff, 'white')}]"

    console.print(f"  [bold]Name:[/bold]          {info.get('name', '?')}")
    console.print(f"  [bold]IP:[/bold]            {info.get('ip', '?')}")
    console.print(f"  [bold]OS:[/bold]            {info.get('os', '?')}")
    console.print(f"  [bold]Schwierigkeit:[/bold] {diff_fmt}")

    if expires_at := info.get("expires_at"):
        console.print(f"  [bold]Verbleibend:[/bold]   {_time_remaining(expires_at)}")
    print()
