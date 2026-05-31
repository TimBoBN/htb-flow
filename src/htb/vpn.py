import re
import subprocess
import time

from .config import HTB_OVPN
from .ui import die, ok, warn


def active() -> bool:
    return subprocess.run(["ip", "link", "show", "tun0"], capture_output=True).returncode == 0


def get_ip() -> str:
    r = subprocess.run(["ip", "-4", "addr", "show", "tun0"], capture_output=True, text=True)
    m = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", r.stdout)
    return m.group(1) if m else ""


def start():
    if not HTB_OVPN.exists():
        die(f"HTB.ovpn not found at {HTB_OVPN}")
    subprocess.Popen(
        ["sudo", "openvpn", "--config", str(HTB_OVPN), "--daemon", "--log", "/tmp/htb-vpn.log"]  # nosec B108
    )
    print("  Waiting for tun0", end="", flush=True)
    for _ in range(15):
        time.sleep(1)
        print(".", end="", flush=True)
        if active():
            break
    print()
    if not active():
        die("VPN could not be started (log: /tmp/htb-vpn.log)")
    ok("VPN started")


def stop():
    subprocess.run(["sudo", "pkill", "openvpn"], capture_output=True)
    time.sleep(1)
    if active():
        warn("tun0 still active")
    else:
        ok("VPN stopped")
