import subprocess

from ..ui import console, header, ok, warn


def run(machine: str):
    url = f"https://app.hackthebox.com/machines/{machine}"
    header(f"Open: {machine}")
    try:
        subprocess.run(["xdg-open", url], check=True, capture_output=True)
        ok(f"Opened in browser: {url}")
    except Exception:
        warn("Could not open browser")
        console.print(f"  [cyan]{url}[/cyan]")
    print()
