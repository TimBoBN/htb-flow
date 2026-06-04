import os
import re
import sys
import time

from . import __version__
from .api import load_machine_profile
from .ui import console, die

GLOBAL_CMDS = {
    "status",
    "list",
    "search",
    "completion",
    "key",
    "todo",
    "profile",
    "activity",
    "timeline",
    "tracks",
    "fortresses",
    "vpn",
    "stats",
    "season",
    "export",
    "doctor",
    "config",
}
MACHINE_CMDS = {
    "init",
    "done",
    "update",
    "info",
    "notes",
    "flag",
    "scan",
    "creds",
    "spawn",
    "reset",
    "shell",
    "port",
    "writeup",
    "open",
    "diff",
    "note",
}
ALL_CMDS = GLOBAL_CMDS | MACHINE_CMDS


def usage(exit_code: int = 1):
    console.print(f"[bold]htb[/bold] v{__version__} — HackTheBox Workflow Helper\n")
    console.print("[bold]Workflow:[/bold]")
    console.print("  htb init   <machine> \\[ip]         Setup: VPN, folders, hosts, notes, nmap")
    console.print("  htb done   <machine>                Finish: submit flags, terminate, archive")
    console.print("  htb update <machine> \\[ip]         Update IP in hosts + notes")
    console.print("")
    console.print("[bold]Recon:[/bold]")
    console.print("  htb status                          Active machine + time remaining")
    console.print("  htb list   \\[--retired] \\[--os OS] \\[--diff DIFF] \\[--search Q]")
    console.print("  htb search <query>                  Search all machines")
    console.print("  htb info   <machine>                Machine details + local status")
    console.print("")
    console.print("[bold]Lifecycle:[/bold]")
    console.print("  htb spawn  <machine>                Start machine via API, waits for IP")
    console.print("  htb reset  <machine>                Reset a running machine")
    console.print("  htb vpn    status|start|stop|switch VPN management")
    console.print("")
    console.print("[bold]Quick actions:[/bold]")
    console.print("  htb notes   <machine>               Open notes.md in \\$EDITOR")
    console.print("  htb note    <machine> <text>        Append timestamped note")
    console.print("  htb flag    <machine>               Submit a flag")
    console.print("  htb scan    <machine> \\[ip] \\[--full] \\[--ports PORTS]")
    console.print("  htb creds   <machine>               Save credentials to notes.md")
    console.print("  htb shell   <machine>               SSH/evil-winrm with creds from notes.md")
    console.print("  htb port    <machine> <port> <svc>  Add port to notes.md")
    console.print("  htb writeup <machine>               Export clean writeup")
    console.print("  htb open    <machine>               Open machine page in browser")
    console.print("  htb diff    <machine>               Git diff of notes.md")
    console.print("")
    console.print("[bold]Profile & Stats:[/bold]")
    console.print("  htb profile                         Your profile (rank, points, owns)")
    console.print("  htb activity \\[n]                   Last n solves (default 20)")
    console.print("  htb timeline                        Solve history as ASCII chart")
    console.print("  htb stats                           Personal statistics + OS distribution")
    console.print("  htb season                          Current season info")
    console.print("  htb todo                            Local machines with flag status")
    console.print("  htb tracks                          Learning paths")
    console.print("  htb fortresses                      Fortresses")
    console.print("")
    console.print("[bold]Tools:[/bold]")
    console.print("  htb export \\[--notes-only]          Export all machines as ZIP")
    console.print("  htb doctor                          Check all dependencies")
    console.print("  htb config                          Interactive config setup")
    console.print("  htb completion bash|zsh             Shell completion script")
    console.print("")
    console.print("[bold]Auth:[/bold]")
    console.print("  htb key set                         Store API key in system keyring")
    console.print("  htb key status                      Show key source")
    console.print("  htb key clear                       Remove key from keyring")
    console.print("")
    console.print("  [cyan]Alias:[/cyan]  htb -u <machine> \\[ip]  →  htb update")
    sys.exit(exit_code)


def main():
    argv = sys.argv[1:]

    if not argv or argv[0] in ("-h", "--help"):
        usage(0)

    if argv[0] in ("-v", "--version"):
        try:
            import keyring as _kr

            from .config import HTB_KEY_FILE as _kf

            key_source = (
                "env"
                if os.environ.get("HTB_API_KEY")
                else "keyring"
                if _kr.get_password("htbflow", "api_key")
                else "file"
                if _kf.exists()
                else "none"
            )
        except Exception:
            key_source = "?"
        import sys as _sys

        console.print(f"htb v{__version__}  Python {_sys.version.split()[0]}  Key: {key_source}")
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

    elif mode == "todo":
        from .commands import todo

        todo.run()

    elif mode == "profile":
        from .commands import profile

        profile.run()

    elif mode == "activity":
        limit = int(rest[0]) if rest and rest[0].isdigit() else 20
        from .commands import activity

        activity.run(limit)

    elif mode == "timeline":
        from .commands import timeline

        timeline.run()

    elif mode == "tracks":
        from .commands import tracks

        tracks.run()

    elif mode == "fortresses":
        from .commands import fortresses

        fortresses.run()

    elif mode == "vpn":
        subcmd = rest[0] if rest else "status"
        from .commands import vpn_cmd

        vpn_cmd.run(subcmd)

    elif mode == "stats":
        from .commands import stats

        stats.run()

    elif mode == "season":
        from .commands import season

        season.run()

    elif mode == "export":
        notes_only = "--notes-only" in rest
        from .commands import export

        export.run(notes_only=notes_only)

    elif mode == "doctor":
        from .commands import doctor

        doctor.run()

    elif mode == "config":
        from .commands import config_setup

        config_setup.run()

    # ── Machine Commands ───────────────────────────────────────────────────────
    else:
        if not rest:
            die(f"Usage: htb {mode} <machine>")
        machine = rest[0]
        extra = rest[1:]

        if mode == "init":
            ip = next((a for a in extra if not a.startswith("--")), "")
            if ip and not re.fullmatch(r"(\d{1,3}\.){3}\d{1,3}", ip):
                die(f"Invalid IP address: {ip}")
            profile = load_machine_profile(machine)
            ip_auto = False
            if not ip:
                if api_ip := profile.get("ip"):
                    ip, ip_auto = api_ip, True
                else:
                    machine_id = profile.get("id")
                    if not machine_id:
                        die(
                            f"Machine '{machine}' not found — check name or specify IP manually: htb init {machine} <ip>"
                        )
                    from .api import get_active_machine, get_api_key, spawn_machine
                    from .ui import ask

                    if ask("Machine not active — spawn it now?"):
                        key = get_api_key()
                        if not key:
                            die("No API key — run: htb key set")
                        msg = spawn_machine(key, machine_id)
                        if msg:
                            console.print(f"  {msg}")
                        print("  Waiting for IP", end="", flush=True)
                        for _ in range(30):
                            time.sleep(1)
                            print(".", end="", flush=True)
                            active = get_active_machine(key)
                            if ip_addr := active.get("ip"):
                                print()
                                ip, ip_auto = ip_addr, True
                                profile["ip"] = ip
                                break
                        else:
                            print()
                            die("IP not available after 30s — try: htb status")
                    else:
                        die(
                            f"No IP provided and machine not active — specify manually: htb init {machine} <ip>"
                        )
            from .commands import init

            init.run(machine, ip, profile, ip_auto)

        elif mode == "done":
            profile = load_machine_profile(machine)
            from .commands import done

            done.run(machine, profile)

        elif mode == "update":
            ip = next((a for a in extra if not a.startswith("--")), "")
            if ip and not re.fullmatch(r"(\d{1,3}\.){3}\d{1,3}", ip):
                die(f"Invalid IP address: {ip}")
            if not ip:
                profile = load_machine_profile(machine)
                if api_ip := profile.get("ip"):
                    ip = api_ip
                else:
                    die(
                        f"No IP provided and machine not active — specify manually: htb update {machine} <ip>"
                    )
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
            ports = next(
                (
                    extra[i + 1]
                    for i, a in enumerate(extra)
                    if a == "--ports" and i + 1 < len(extra)
                ),
                "",
            )
            ip = next((a for a in extra if not a.startswith("--")), "")
            from .commands import scan

            scan.run(machine, ip=ip, full=full, ports=ports)

        elif mode == "note":
            if not extra:
                die("Usage: htb note <machine> <text>")
            from .commands import notes_add

            notes_add.run(machine, " ".join(extra))

        elif mode == "creds":
            from .commands import creds

            creds.run(machine)

        elif mode == "spawn":
            from .commands import spawn

            spawn.run(machine)

        elif mode == "reset":
            from .commands import reset

            reset.run(machine)

        elif mode == "shell":
            from .commands import shell

            shell.run(machine)

        elif mode == "port":
            if len(extra) < 2:
                die("Usage: htb port <machine> <port> <service> [version]")
            port_num = extra[0]
            service = extra[1]
            version = extra[2] if len(extra) > 2 else ""
            from .commands import port

            port.run(machine, port_num, service, version)

        elif mode == "writeup":
            from .commands import writeup

            writeup.run(machine)

        elif mode == "open":
            from .commands import open_machine

            open_machine.run(machine)

        elif mode == "diff":
            from .commands import diff

            diff.run(machine)


if __name__ == "__main__":
    main()
