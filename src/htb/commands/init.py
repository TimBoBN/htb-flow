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
    console.print(f"  [bold]Date:[/bold]     {date.today().strftime('%Y-%m-%d')}\n")

    header("VPN")
    if vpn.active():
        ok(f"tun0 active  →  {vpn.get_ip()}")
    else:
        warn("tun0 not active")
        ans = input("  Start OpenVPN now? [y/N] ")
        if ans.strip().lower() == "y":
            vpn.start()
        else:
            warn("Continuing without VPN")

    header("HTB API")
    if profile.get("os", "?") != "?" or profile.get("difficulty", "?") != "?":
        ok(f"OS:         {profile.get('os', '?')}")
        ok(f"Difficulty: {profile.get('difficulty', '?')}")
        ok(f"Points:     {profile.get('points', '?')}")
        ok(f"Release:    {profile.get('release', '?')}")
        ok(f"Rating:     ★ {profile.get('stars', '?')}")
        if ip_auto:
            ok(f"IP:         {ip}  (auto-detected)")
    else:
        warn("API: machine not found or unreachable — fill in fields manually")

    header("Folder structure")
    if box_dir.exists():
        warn(f"Folder already exists: {box_dir}")
    else:
        for sub in ("nmap", "web", "exploits", "loot", "creds"):
            (box_dir / sub).mkdir(parents=True)
        ok(f"Created: {box_dir}")
        ok("  nmap/ web/ exploits/ loot/ creds/")

    header("/etc/hosts")
    if hosts.contains(hostname):
        warn(f"{hostname} already in /etc/hosts — to update IP: htb update {machine}")
    else:
        hosts.add(ip, hostname)
        ok(f"Added: {ip}  →  {hostname}")

    notes_path = box_dir / "notes.md"
    if not notes_path.exists():
        notes.create(
            notes_path,
            machine=machine,
            ip=ip,
            hostname=hostname,
            date=date.today().strftime("%Y-%m-%d"),
            os=profile.get("os", "?"),
            difficulty=profile.get("difficulty", "?"),
            points=profile.get("points", "?"),
            release=profile.get("release", "?"),
            stars=profile.get("stars", "?"),
        )
        ok(f"Notes created: {notes_path}")

    header("Nmap")
    console.print("  [bold][1/2][/bold] Quick scan (top 1000 ports)...")
    subprocess.run(
        ["nmap", "-sV", "-sC", "--open", "-oN", str(box_dir / "nmap/quick.txt"), ip],
        check=False,
    )
    ok("Quick scan done → nmap/quick.txt")

    console.print("\n  [bold][2/2][/bold] Full scan (all ports) running in background...")
    proc = subprocess.Popen(
        ["nmap", "-p-", "--min-rate", "5000", "-oN", str(box_dir / "nmap/full.txt"), ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    ok(f"Full scan PID {proc.pid} → nmap/full.txt (running)")

    console.print("\n[bold cyan]══════════════════════════════════[/bold cyan]")
    console.print("[bold]  Setup complete[/bold]")
    console.print("[bold cyan]══════════════════════════════════[/bold cyan]")
    console.print(f"  [bold]Working directory:[/bold] {box_dir}")
    console.print(f"  [bold]Hostname:[/bold]          {hostname}")
    console.print(f"  [bold]OS:[/bold]                {profile.get('os', '?')}")
    console.print(f"  [bold]Difficulty:[/bold]        {profile.get('difficulty', '?')}")
    console.print(f"  [bold]Points:[/bold]            {profile.get('points', '?')}")
    console.print(f"  [bold]Quick scan:[/bold]        {box_dir}/nmap/quick.txt")
    console.print(f"  [bold]Full scan:[/bold]         running (PID {proc.pid})")
    console.print(f"  [bold]Notes:[/bold]             {notes_path}")
    console.print(f"\n  [cyan]cd {box_dir}[/cyan]")

    console.print("\n[bold cyan]══ Open Ports (Quick Scan) ══[/bold cyan]")
    quick = box_dir / "nmap/quick.txt"
    if quick.exists():
        ports = [
            line for line in quick.read_text().splitlines() if re.match(r"^\d+/(tcp|udp)", line)
        ]
        for p in ports:
            console.print(f"  {p}")
        if not ports:
            warn("No open ports found")
    print()
