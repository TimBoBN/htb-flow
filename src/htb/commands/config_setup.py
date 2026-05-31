from pathlib import Path

from ..config import EDITOR, HTB_BASE, HTB_OVPN
from ..ui import ask_input, console, header, ok, warn

_CONFIG_FILE = Path.home() / ".config/htb/config.toml"


def run():
    header("Config Setup")

    if _CONFIG_FILE.exists():
        console.print(f"  Existing config: [cyan]{_CONFIG_FILE}[/cyan]\n")

    console.print("  Press Enter to keep the current/default value.\n")

    htb_base = ask_input(f"HTB base directory [{HTB_BASE}]:")
    ovpn = ask_input(f"OpenVPN profile path [{HTB_OVPN}]:")
    editor = ask_input(f"Editor [{EDITOR or '$EDITOR'}]:")

    lines = []
    if htb_base:
        lines.append(f'htb_base  = "{htb_base}"')
    if ovpn:
        lines.append(f'ovpn_path = "{ovpn}"')
    if editor:
        lines.append(f'editor    = "{editor}"')

    if not lines:
        warn("No changes — config unchanged")
        return

    _CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CONFIG_FILE.write_text("\n".join(lines) + "\n")
    ok(f"Config saved: {_CONFIG_FILE}")
    console.print()
    for line in lines:
        console.print(f"  [dim]{line}[/dim]")
    print()
