import re
from datetime import date

from .. import hosts
from ..config import HTB_BASE
from ..ui import console, header, ok, warn, die, BANNER_HTB


def run(machine: str, ip: str):
    box_dir  = HTB_BASE / machine
    hostname = f"{machine.lower()}.htb"
    notes    = box_dir / "notes.md"

    if not box_dir.exists():
        die(f"Maschine '{machine}' nicht gefunden unter {box_dir}")

    console.print(BANNER_HTB)
    console.print(f"  [bold]Machine:[/bold]  {machine}")
    console.print(f"  [bold]IP:[/bold]       {ip}")
    console.print(f"  [bold]Modus:[/bold]    [yellow]IP-Update[/yellow]")
    console.print(f"  [bold]Zeit:[/bold]     {date.today().strftime('%d.%m.%Y')}\n")

    header("/etc/hosts")
    if hosts.contains(hostname):
        old_ip = hosts.get_ip(hostname)
        if old_ip == ip:
            ok(f"IP ist bereits {ip} — nichts zu tun")
        else:
            hosts.update_ip(old_ip, ip, hostname)
            ok(f"IP aktualisiert: {old_ip}  →  {ip}")
    else:
        hosts.add(ip, hostname)
        ok(f"Neu eingetragen: {ip}  →  {hostname}")

    header("notes.md")
    if notes.exists():
        text = notes.read_text()
        old_ips = re.findall(r"`(\d+\.\d+\.\d+\.\d+)`", text)
        if old_ips and old_ips[0] != ip:
            notes.write_text(text.replace(old_ips[0], ip))
            ok(f"IP in notes.md aktualisiert: {old_ips[0]}  →  {ip}")
        else:
            ok("notes.md bereits aktuell")

    console.print(f"\n[bold cyan]══════════════════════════════════[/bold cyan]")
    console.print("[bold]  Update abgeschlossen[/bold]")
    console.print(f"[bold cyan]══════════════════════════════════[/bold cyan]")
    console.print(f"  [bold]Maschine:[/bold]  {machine}")
    console.print(f"  [bold]Neue IP:[/bold]   {ip}")
    console.print(f"  [bold]Hostname:[/bold]  {hostname}\n")
