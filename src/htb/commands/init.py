import re
import subprocess
from datetime import date

from .. import hosts, notes, vpn
from ..config import HTB_BASE
from ..ui import BANNER_HTB, console, header, ok, warn


def run(machine: str, ip: str, profile: dict, ip_auto: bool):
    box_dir = HTB_BASE / machine
    hostname = f"{machine.lower()}.htb"

    console.print(BANNER_HTB)
    console.print(f"  [bold]Machine:[/bold]  {machine}")
    if ip_auto:
        console.print(f"  [bold]IP:[/bold]       {ip}  [cyan](via HTB API)[/cyan]")
    else:
        console.print(f"  [bold]IP:[/bold]       {ip}")
    console.print(f"  [bold]Hostname:[/bold] {hostname}")
    console.print(f"  [bold]Zeit:[/bold]     {date.today().strftime('%d.%m.%Y')}\n")

    # VPN
    header("VPN")
    if vpn.active():
        ok(f"tun0 aktiv  →  {vpn.get_ip()}")
    else:
        warn("tun0 nicht aktiv")
        ans = input("  OpenVPN jetzt starten? [j/N] ")
        if ans.strip().lower() == "j":
            vpn.start()
        else:
            warn("Weiter ohne VPN")

    # API Info
    header("HTB API")
    if profile.get("os", "?") != "?" or profile.get("difficulty", "?") != "?":
        ok(f"OS:            {profile.get('os', '?')}")
        ok(f"Schwierigkeit: {profile.get('difficulty', '?')}")
        ok(f"Punkte:        {profile.get('points', '?')}")
        ok(f"Release:       {profile.get('release', '?')}")
        ok(f"Rating:        ★ {profile.get('stars', '?')}")
        if ip_auto:
            ok(f"IP:            {ip}  (automatisch erkannt)")
    else:
        warn("API: Maschine nicht gefunden oder nicht erreichbar — Felder manuell ausfüllen")

    # Ordnerstruktur
    header("Ordnerstruktur")
    if box_dir.exists():
        warn(f"Ordner existiert bereits: {box_dir}")
    else:
        for sub in ("nmap", "web", "exploits", "loot", "creds"):
            (box_dir / sub).mkdir(parents=True)
        ok(f"Erstellt: {box_dir}")
        ok("  nmap/ web/ exploits/ loot/ creds/")

    # /etc/hosts
    header("/etc/hosts")
    if hosts.contains(hostname):
        warn(f"{hostname} bereits in /etc/hosts — für IP-Update: htb update {machine}")
    else:
        hosts.add(ip, hostname)
        ok(f"Hinzugefügt: {ip}  →  {hostname}")

    # Notes
    notes_path = box_dir / "notes.md"
    if not notes_path.exists():
        notes.create(
            notes_path,
            machine=machine,
            ip=ip,
            hostname=hostname,
            date=date.today().strftime("%d.%m.%Y"),
            os=profile.get("os", "?"),
            difficulty=profile.get("difficulty", "?"),
            points=profile.get("points", "?"),
            release=profile.get("release", "?"),
            stars=profile.get("stars", "?"),
        )
        ok(f"Notes erstellt: {notes_path}")

    # Nmap
    header("Nmap")
    console.print("  [bold][1/2][/bold] Quick scan (Top 1000 Ports)...")
    subprocess.run(
        ["nmap", "-sV", "-sC", "--open", "-oN", str(box_dir / "nmap/quick.txt"), ip],
        check=False,
    )
    ok("Quick scan fertig → nmap/quick.txt")

    console.print("\n  [bold][2/2][/bold] Full scan (alle Ports) läuft im Hintergrund...")
    proc = subprocess.Popen(
        ["nmap", "-p-", "--min-rate", "5000", "-oN", str(box_dir / "nmap/full.txt"), ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    ok(f"Full scan PID {proc.pid} → nmap/full.txt (läuft noch)")

    console.print("\n[bold cyan]══════════════════════════════════[/bold cyan]")
    console.print("[bold]  Setup abgeschlossen[/bold]")
    console.print("[bold cyan]══════════════════════════════════[/bold cyan]")
    console.print(f"  [bold]Arbeitsverzeichnis:[/bold] {box_dir}")
    console.print(f"  [bold]Hostname:[/bold]           {hostname}")
    console.print(f"  [bold]OS:[/bold]                 {profile.get('os', '?')}")
    console.print(f"  [bold]Schwierigkeit:[/bold]      {profile.get('difficulty', '?')}")
    console.print(f"  [bold]Punkte:[/bold]             {profile.get('points', '?')}")
    console.print(f"  [bold]Quick-Scan:[/bold]         {box_dir}/nmap/quick.txt")
    console.print(f"  [bold]Full-Scan:[/bold]          läuft (PID {proc.pid})")
    console.print(f"  [bold]Notes:[/bold]              {notes_path}")
    console.print(f"\n  [cyan]cd {box_dir}[/cyan]")

    console.print("\n[bold cyan]══ Offene Ports (Quick Scan) ══[/bold cyan]")
    quick = box_dir / "nmap/quick.txt"
    if quick.exists():
        ports = [
            line for line in quick.read_text().splitlines() if re.match(r"^\d+/(tcp|udp)", line)
        ]
        for p in ports:
            console.print(f"  {p}")
        if not ports:
            warn("Keine offenen Ports gefunden")
    print()
