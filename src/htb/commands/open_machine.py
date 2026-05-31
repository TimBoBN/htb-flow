import subprocess

from ..ui import console, header, ok, warn


def run(machine: str):
    url = f"https://app.hackthebox.com/machines/{machine}"
    header(f"Open: {machine}")
    try:
        subprocess.run(["xdg-open", url], check=True, capture_output=True)
        ok(f"Browser geöffnet: {url}")
    except Exception:
        warn("Browser konnte nicht geöffnet werden")
        console.print(f"  [cyan]{url}[/cyan]")
    print()
