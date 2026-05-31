import re
import sys

from .api import load_machine_profile
from .ui import console, die
from . import __version__

GLOBAL_CMDS  = {"status", "list", "search", "completion", "key"}
MACHINE_CMDS = {"init", "done", "update", "info", "notes",
                "flag", "scan", "creds", "spawn", "reset"}
ALL_CMDS = GLOBAL_CMDS | MACHINE_CMDS


def usage(exit_code: int = 1):
    console.print(f"[bold]htb[/bold] v{__version__} — HackTheBox Workflow Helper\n")
    console.print("[bold]Workflow:[/bold]")
    console.print("  htb init   <machine> \\[ip]        Setup: VPN, Ordner, hosts, notes, nmap")
    console.print("  htb done   <machine>               Abschluss: flags, terminieren, archivieren")
    console.print("  htb update <machine> \\[ip]        IP aktualisieren")
    console.print("")
    console.print("[bold]Recherche:[/bold]")
    console.print("  htb status                         Aktive Maschine anzeigen")
    console.print("  htb list   \\[--retired] \\[--os OS] \\[--diff DIFF]  Maschinen listen")
    console.print("  htb search <query>                 Maschinen suchen")
    console.print("  htb info   <machine>               Maschineninfo")
    console.print("")
    console.print("[bold]Lifecycle:[/bold]")
    console.print("  htb spawn  <machine>               Maschine starten")
    console.print("  htb reset  <machine>               Maschine resetten")
    console.print("")
    console.print("[bold]Schnellaktionen:[/bold]")
    console.print("  htb notes  <machine>               notes.md im Editor öffnen")
    console.print("  htb flag   <machine>               Flag einreichen")
    console.print("  htb scan   <machine> \\[ip] \\[--full]  Nmap erneut ausführen")
    console.print("  htb creds  <machine>               Credentials speichern")
    console.print("")
    console.print("[bold]Shell:[/bold]")
    console.print("  htb completion bash|zsh            Shell-Completion ausgeben")
    console.print("")
    console.print("[bold]Auth:[/bold]")
    console.print("  htb key set                        API Key im Keyring speichern")
    console.print("  htb key clear                      API Key löschen")
    console.print("  htb key status                     Key-Status anzeigen")
    console.print("")
    console.print("  [cyan]Alias:[/cyan]  htb -u <machine> \\[ip]  →  htb update")
    sys.exit(exit_code)


def main():
    argv = sys.argv[1:]

    if not argv or argv[0] in ("-h", "--help"):
        usage(0)

    if argv[0] in ("-v", "--version"):
        console.print(f"htb v{__version__}")
        sys.exit(0)

    if argv[0] in ("-u", "--update"):
        argv[0] = "update"

    mode = argv[0]
    if mode not in ALL_CMDS:
        usage()

    rest = argv[1:]

    # ── Global Commands ────────────────────────────────────────────────────────
    if mode == "status":
        from .commands import status
        status.run()

    elif mode == "list":
        from .commands import list_machines
        list_machines.run(rest)

    elif mode == "search":
        if not rest:
            die("Usage: htb search <query>")
        from .commands import search
        search.run(" ".join(rest))

    elif mode == "completion":
        shell = rest[0] if rest else "bash"
        from .commands import completion
        completion.run(shell)

    elif mode == "key":
        subcmd = rest[0] if rest else "status"
        from .commands import key_cmd
        key_cmd.run(subcmd)

    # ── Machine Commands ───────────────────────────────────────────────────────
    else:
        if not rest:
            die(f"Usage: htb {mode} <machine>")
        machine = rest[0]
        extra   = rest[1:]

        if mode == "init":
            ip = next((a for a in extra if not a.startswith("--")), "")
            if ip and not re.fullmatch(r"(\d{1,3}\.){3}\d{1,3}", ip):
                die(f"Ungültige IP-Adresse: {ip}")
            profile = load_machine_profile(machine)
            ip_auto = False
            if not ip:
                if api_ip := profile.get("ip"):
                    ip, ip_auto = api_ip, True
                else:
                    die(f"Keine IP angegeben und Maschine nicht aktiv — bitte manuell: htb init {machine} <ip>")
            from .commands import init
            init.run(machine, ip, profile, ip_auto)

        elif mode == "done":
            profile = load_machine_profile(machine)
            from .commands import done
            done.run(machine, profile)

        elif mode == "update":
            ip = next((a for a in extra if not a.startswith("--")), "")
            if ip and not re.fullmatch(r"(\d{1,3}\.){3}\d{1,3}", ip):
                die(f"Ungültige IP-Adresse: {ip}")
            if not ip:
                profile = load_machine_profile(machine)
                if api_ip := profile.get("ip"):
                    ip = api_ip
                else:
                    die(f"Keine IP angegeben und Maschine nicht aktiv — bitte manuell: htb update {machine} <ip>")
            from .commands import update
            update.run(machine, ip)

        elif mode == "info":
            from .commands import info
            info.run(machine)

        elif mode == "status":
            from .commands import status
            status.run()

        elif mode == "notes":
            from .commands import notes_cmd
            notes_cmd.run(machine)

        elif mode == "flag":
            from .commands import flag
            flag.run(machine)

        elif mode == "scan":
            full = "--full" in extra
            ip   = next((a for a in extra if not a.startswith("--")), "")
            from .commands import scan
            scan.run(machine, ip=ip, full=full)

        elif mode == "creds":
            from .commands import creds
            creds.run(machine)

        elif mode == "spawn":
            from .commands import spawn
            spawn.run(machine)

        elif mode == "reset":
            from .commands import reset
            reset.run(machine)


if __name__ == "__main__":
    main()
