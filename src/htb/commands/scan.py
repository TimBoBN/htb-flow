import subprocess

from .. import notes
from ..config import HTB_BASE
from ..ui import console, die, header, ok


def run(machine: str, ip: str = "", full: bool = False, ports: str = ""):
    box_dir = HTB_BASE / machine
    if not box_dir.exists():
        die(f"Machine '{machine}' not found at {box_dir}")

    if not ip:
        notes_path = box_dir / "notes.md"
        if notes_path.exists():
            n = notes.parse(notes_path)
            ip = n.get("ip", "")
    if not ip:
        die("No IP — please provide: htb scan <machine> <ip>")

    nmap_dir = box_dir / "nmap"
    nmap_dir.mkdir(exist_ok=True)

    if ports:
        header(f"Nmap Custom Scan: {machine}")
        console.print(f"  Target: {ip}  Ports: {ports}\n")
        subprocess.run(
            [
                "nmap",
                "-sV",
                "-sC",
                "--open",
                "-p",
                ports,
                "-oN",
                str(nmap_dir / f"ports-{ports.replace(',', '_')}.txt"),
                ip,
            ],
            check=False,
        )
        ok(f"Custom scan done → nmap/ports-{ports.replace(',', '_')}.txt")
    elif full:
        header(f"Nmap Full Scan: {machine}")
        console.print(f"  Target: {ip}")
        console.print("  Full scan (all ports) running in background...")
        proc = subprocess.Popen(
            ["nmap", "-p-", "--min-rate", "5000", "-oN", str(nmap_dir / "full.txt"), ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        ok(f"Full scan PID {proc.pid} → nmap/full.txt")
    else:
        header(f"Nmap Quick Scan: {machine}")
        console.print(f"  Target: {ip}\n")
        subprocess.run(
            ["nmap", "-sV", "-sC", "--open", "-oN", str(nmap_dir / "quick.txt"), ip],
            check=False,
        )
        ok("Quick scan done → nmap/quick.txt")
    print()
