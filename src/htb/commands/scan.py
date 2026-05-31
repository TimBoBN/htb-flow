import subprocess

from .. import notes
from ..config import HTB_BASE
from ..ui import console, die, header, ok


def run(machine: str, ip: str = "", full: bool = False):
    box_dir = HTB_BASE / machine
    if not box_dir.exists():
        die(f"Maschine '{machine}' nicht gefunden unter {box_dir}")

    # IP aus notes.md wenn nicht angegeben
    if not ip:
        notes_path = box_dir / "notes.md"
        if notes_path.exists():
            n = notes.parse(notes_path)
            ip = n.get("ip", "")
    if not ip:
        die("Keine IP — bitte angeben: htb scan <machine> <ip>")

    nmap_dir = box_dir / "nmap"
    nmap_dir.mkdir(exist_ok=True)

    if full:
        header(f"Nmap Full Scan: {machine}")
        console.print(f"  Ziel: {ip}")
        console.print("  Full scan (alle Ports) läuft im Hintergrund...")
        proc = subprocess.Popen(
            ["nmap", "-p-", "--min-rate", "5000", "-oN", str(nmap_dir / "full.txt"), ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        ok(f"Full scan PID {proc.pid} → nmap/full.txt")
    else:
        header(f"Nmap Quick Scan: {machine}")
        console.print(f"  Ziel: {ip}\n")
        subprocess.run(
            ["nmap", "-sV", "-sC", "--open", "-oN", str(nmap_dir / "quick.txt"), ip],
            check=False,
        )
        ok("Quick scan fertig → nmap/quick.txt")
    print()
