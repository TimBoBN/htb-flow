import shutil
import subprocess
import sys

from ..api import get_api_key
from ..config import HTB_BASE, HTB_OVPN
from ..ui import console, header, ok, warn


def _check(label: str, cmd: str | None, *, required: bool = True):
    if cmd and shutil.which(cmd):
        ok(f"{label:<20} {cmd}")
    elif required:
        warn(f"{label:<20} not found  →  install: {cmd}")
    else:
        console.print(f"  [dim]✗  {label:<18} not found (optional)[/dim]")


def run():
    header("Doctor — Dependency Check")

    # Python version
    major, minor = sys.version_info[:2]
    if (major, minor) >= (3, 11):
        ok(f"{'Python':<20} {major}.{minor}")
    else:
        warn(f"{'Python':<20} {major}.{minor} — requires 3.11+")

    # Required tools
    _check("nmap", "nmap", required=True)
    _check("openvpn", "openvpn", required=True)
    _check("git", "git", required=False)

    # Optional tools
    _check("sshpass", "sshpass", required=False)
    _check("evil-winrm", "evil-winrm", required=False)
    _check("xdg-open", "xdg-open", required=False)

    # Config / paths
    console.print()
    header("Paths & Config")

    if HTB_BASE.exists():
        ok(f"{'HTB_BASE':<20} {HTB_BASE}")
    else:
        warn(f"{'HTB_BASE':<20} {HTB_BASE}  (not created yet — run htb init)")

    if HTB_OVPN.exists():
        ok(f"{'HTB_OVPN':<20} {HTB_OVPN}")
    else:
        warn(f"{'HTB_OVPN':<20} {HTB_OVPN}  (not found)")

    # API key
    console.print()
    header("API Key")
    key = get_api_key()
    if key:
        ok(f"API key found  [{key[:6]}...{key[-4:]}]")
    else:
        warn("No API key — run: htb key set")

    # VPN status
    console.print()
    header("VPN")
    result = subprocess.run(["ip", "link", "show", "tun0"], capture_output=True)
    if result.returncode == 0:
        ok("tun0 active")
    else:
        console.print("  [dim]tun0 inactive[/dim]")
    print()
