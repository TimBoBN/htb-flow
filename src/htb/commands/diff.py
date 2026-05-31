import datetime
import subprocess

from ..config import HTB_BASE
from ..ui import console, die, header, ok, warn


def run(machine: str):
    box_dir = HTB_BASE / machine
    notes_path = box_dir / "notes.md"

    if not notes_path.exists():
        die(f"notes.md not found: {notes_path}")

    header(f"Diff: {machine}")

    git_check = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        cwd=str(HTB_BASE),
        capture_output=True,
    )
    if git_check.returncode != 0:
        warn("No git repository in HTB_BASE")
        mtime = notes_path.stat().st_mtime
        dt = datetime.datetime.fromtimestamp(mtime)
        console.print(f"  Last modified: {dt.strftime('%Y-%m-%d %H:%M')}")
        print()
        return

    result = subprocess.run(
        ["git", "diff", "HEAD", "--", str(notes_path.relative_to(HTB_BASE))],
        cwd=str(HTB_BASE),
        capture_output=True,
        text=True,
    )

    if not result.stdout.strip():
        ok("No changes since last commit")
        print()
        return

    for line in result.stdout.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            console.print(f"[green]{line}[/green]")
        elif line.startswith("-") and not line.startswith("---"):
            console.print(f"[red]{line}[/red]")
        elif line.startswith("@@"):
            console.print(f"[cyan]{line}[/cyan]")
        else:
            console.print(line)
    print()
