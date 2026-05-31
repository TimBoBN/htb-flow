import subprocess
import time

from .. import vpn
from ..config import HTB_OVPN
from ..ui import ask_input, console, die, header, ok, warn


def run(subcmd: str = "status"):
    if subcmd == "status":
        _cmd_status()
    elif subcmd == "start":
        _cmd_start()
    elif subcmd == "stop":
        _cmd_stop()
    elif subcmd == "switch":
        _cmd_switch()
    else:
        die(f"Unbekannter Unterbefehl: {subcmd}\nUsage: htb vpn [status|start|stop|switch]")


def _cmd_status():
    header("VPN Status")
    if vpn.active():
        ok(f"tun0 aktiv  →  {vpn.get_ip()}")
    else:
        warn("VPN inaktiv")
    console.print(f"  [bold]Profil:[/bold]  {HTB_OVPN.name}")
    print()


def _cmd_start():
    header("VPN starten")
    if vpn.active():
        ok(f"VPN bereits aktiv ({vpn.get_ip()})")
        return
    vpn.start()
    print()


def _cmd_stop():
    header("VPN stoppen")
    if not vpn.active():
        ok("VPN bereits inaktiv")
        return
    vpn.stop()
    print()


def _cmd_switch():
    header("VPN Profil wechseln")
    ovpn_dir = HTB_OVPN.parent
    profiles = sorted(ovpn_dir.glob("*.ovpn"))
    if not profiles:
        die(f"Keine .ovpn Dateien gefunden in {ovpn_dir}")

    console.print("  Verfügbare Profile:")
    for i, p in enumerate(profiles):
        active = " [green](aktiv)[/green]" if p.resolve() == HTB_OVPN.resolve() else ""
        console.print(f"    [{i + 1}] {p.name}{active}")

    choice = ask_input(f"Welches Profil? (1-{len(profiles)}):")
    try:
        selected = profiles[int(choice) - 1]
    except (ValueError, IndexError):
        die("Ungültige Auswahl")

    if vpn.active():
        vpn.stop()

    subprocess.Popen(
        ["sudo", "openvpn", "--config", str(selected), "--daemon", "--log", "/tmp/htb-vpn.log"]
    )
    print("  Warte auf tun0", end="", flush=True)
    for _ in range(15):
        time.sleep(1)
        print(".", end="", flush=True)
        if vpn.active():
            break
    print()
    if vpn.active():
        ok(f"VPN gestartet: {selected.name}  →  {vpn.get_ip()}")
    else:
        die("VPN konnte nicht gestartet werden (Log: /tmp/htb-vpn.log)")
    print()
