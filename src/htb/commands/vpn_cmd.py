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
        die(f"Unknown subcommand: {subcmd}\nUsage: htb vpn [status|start|stop|switch]")


def _cmd_status():
    header("VPN Status")
    if vpn.active():
        ok(f"tun0 active  →  {vpn.get_ip()}")
    else:
        warn("VPN inactive")
    console.print(f"  [bold]Profile:[/bold]  {HTB_OVPN.name}")
    print()


def _cmd_start():
    header("Start VPN")
    if vpn.active():
        ok(f"VPN already active ({vpn.get_ip()})")
        return
    vpn.start()
    print()


def _cmd_stop():
    header("Stop VPN")
    if not vpn.active():
        ok("VPN already inactive")
        return
    vpn.stop()
    print()


def _cmd_switch():
    header("Switch VPN Profile")
    ovpn_dir = HTB_OVPN.parent
    profiles = sorted(ovpn_dir.glob("*.ovpn"))
    if not profiles:
        die(f"No .ovpn files found in {ovpn_dir}")

    console.print("  Available profiles:")
    for i, p in enumerate(profiles):
        active = " [green](active)[/green]" if p.resolve() == HTB_OVPN.resolve() else ""
        console.print(f"    [{i + 1}] {p.name}{active}")

    choice = ask_input(f"Which profile? (1-{len(profiles)}):")
    try:
        selected = profiles[int(choice) - 1]
    except (ValueError, IndexError):
        die("Invalid selection")

    if vpn.active():
        vpn.stop()

    subprocess.Popen(
        ["sudo", "openvpn", "--config", str(selected), "--daemon", "--log", "/tmp/htb-vpn.log"]  # nosec B108
    )
    print("  Waiting for tun0", end="", flush=True)
    for _ in range(15):
        time.sleep(1)
        print(".", end="", flush=True)
        if vpn.active():
            break
    print()
    if vpn.active():
        ok(f"VPN started: {selected.name}  →  {vpn.get_ip()}")
    else:
        die("VPN could not be started (log: /tmp/htb-vpn.log)")
    print()
