import re
from datetime import date

from .. import hosts
from ..config import HTB_BASE
from ..ui import BANNER_HTB, console, die, header, ok


def run(machine: str, ip: str):
    box_dir = HTB_BASE / machine
    hostname = f"{machine.lower()}.htb"
    notes = box_dir / "notes.md"

    if not box_dir.exists():
        die(f"Machine '{machine}' not found at {box_dir}")

    console.print(BANNER_HTB)
    console.print(f"  [bold]Machine:[/bold]  {machine}")
    console.print(f"  [bold]IP:[/bold]       {ip}")
    console.print("  [bold]Mode:[/bold]     [yellow]IP Update[/yellow]")
    console.print(f"  [bold]Date:[/bold]     {date.today().strftime('%Y-%m-%d')}\n")

    header("/etc/hosts")
    if hosts.contains(hostname):
        old_ip = hosts.get_ip(hostname) or ""
        if old_ip == ip:
            ok(f"IP is already {ip} — nothing to do")
        else:
            hosts.update_ip(old_ip, ip, hostname)
            ok(f"IP updated: {old_ip}  →  {ip}")
    else:
        hosts.add(ip, hostname)
        ok(f"Added: {ip}  →  {hostname}")

    header("notes.md")
    if notes.exists():
        text = notes.read_text()
        old_ips = re.findall(r"`(\d+\.\d+\.\d+\.\d+)`", text)
        if old_ips and old_ips[0] != ip:
            notes.write_text(text.replace(old_ips[0], ip))
            ok(f"IP updated in notes.md: {old_ips[0]}  →  {ip}")
        else:
            ok("notes.md already up to date")

    console.print("\n[bold cyan]══════════════════════════════════[/bold cyan]")
    console.print("[bold]  Update complete[/bold]")
    console.print("[bold cyan]══════════════════════════════════[/bold cyan]")
    console.print(f"  [bold]Machine:[/bold]  {machine}")
    console.print(f"  [bold]New IP:[/bold]   {ip}")
    console.print(f"  [bold]Hostname:[/bold] {hostname}\n")
