from collections import Counter, defaultdict

from ..api import get_activity, get_api_key, get_profile
from ..config import HTB_BASE
from ..ui import console, die, header, warn


def run():
    key = get_api_key()
    if not key:
        die("No API key — run: htb key set")

    header("Statistics")

    profile = get_profile(key)
    acts = get_activity(key)

    if not profile and not acts:
        warn("No data available")
        return

    # Profile summary
    if profile:
        console.print(
            f"  [bold]Rank:[/bold]        {profile.get('rank', '?')} "
            f"(#{profile.get('ranking', '?')})"
        )
        console.print(f"  [bold]Points:[/bold]      {profile.get('points', '?')}")
        console.print(f"  [bold]User Owns:[/bold]   {profile.get('user_owns', '?')}")
        console.print(f"  [bold]System Owns:[/bold] {profile.get('system_owns', '?')}")
        console.print()

    if not acts:
        return

    # OS distribution from local notes
    header("Local Machines")
    os_count: Counter = Counter()
    diff_count: Counter = Counter()
    local_count = 0
    if HTB_BASE.exists():
        for d in HTB_BASE.iterdir():
            if not d.is_dir():
                continue
            np = d / "notes.md"
            if not np.exists():
                continue
            from .. import notes

            n = notes.parse(np)
            local_count += 1
            if n.get("os") and n["os"] != "?":
                os_count[n["os"]] += 1
            if n.get("difficulty") and n["difficulty"] != "?":
                diff_count[n["difficulty"]] += 1

    console.print(f"  [bold]Local boxes:[/bold] {local_count}")

    if os_count:
        console.print("\n  [bold]OS Distribution:[/bold]")
        for os_name, count in os_count.most_common():
            bar = "█" * count
            console.print(f"    {os_name:<10} [cyan]{bar}[/cyan] {count}")

    diff_colors = {"Easy": "green", "Medium": "yellow", "Hard": "red", "Insane": "magenta"}
    if diff_count:
        console.print("\n  [bold]Difficulty Distribution:[/bold]")
        for diff, count in [
            ("Easy", diff_count.get("Easy", 0)),
            ("Medium", diff_count.get("Medium", 0)),
            ("Hard", diff_count.get("Hard", 0)),
            ("Insane", diff_count.get("Insane", 0)),
        ]:
            if count:
                color = diff_colors.get(diff, "white")
                bar = "█" * count
                console.print(f"    [{color}]{diff:<8}[/{color}] [cyan]{bar}[/cyan] {count}")

    # Activity stats
    header("Activity")
    by_month: dict[str, int] = defaultdict(int)
    flag_types: Counter = Counter()
    for a in acts:
        month = (a.get("date") or "")[:7]
        if month:
            by_month[month] += 1
        flag_types[a.get("type", "?")] += 1

    console.print(f"  [bold]Total solves:[/bold] {len(acts)}")
    console.print(f"  [bold]User flags:[/bold]   {flag_types.get('user', 0)}")
    console.print(f"  [bold]Root flags:[/bold]   {flag_types.get('root', 0)}")
    if by_month:
        best_month = max(by_month, key=by_month.__getitem__)
        console.print(f"  [bold]Best month:[/bold]   {best_month} ({by_month[best_month]} solves)")
    print()
