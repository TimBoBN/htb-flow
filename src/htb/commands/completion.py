from ..ui import die

ALL_COMMANDS = (
    "init",
    "done",
    "update",
    "status",
    "list",
    "search",
    "info",
    "spawn",
    "reset",
    "profile",
    "activity",
    "timeline",
    "tracks",
    "fortresses",
    "todo",
    "stats",
    "season",
    "export",
    "doctor",
    "config",
    "vpn",
    "shell",
    "notes",
    "note",
    "flag",
    "scan",
    "creds",
    "port",
    "writeup",
    "open",
    "diff",
    "key",
    "completion",
)

BASH_SCRIPT = """\
_htb() {
    local cur prev cmds
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    cmds="%(cmds)s"

    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=($(compgen -W "$cmds" -- "$cur"))
        return
    fi

    case "$prev" in
        list)       COMPREPLY=($(compgen -W "--retired --os --diff --search" -- "$cur")) ;;
        scan)       COMPREPLY=($(compgen -W "--full --ports" -- "$cur")) ;;
        export)     COMPREPLY=($(compgen -W "--notes-only" -- "$cur")) ;;
        completion) COMPREPLY=($(compgen -W "bash zsh" -- "$cur")) ;;
        vpn)        COMPREPLY=($(compgen -W "status start stop switch" -- "$cur")) ;;
        key)        COMPREPLY=($(compgen -W "set clear status" -- "$cur")) ;;
    esac
}
complete -F _htb htb
""" % {"cmds": " ".join(ALL_COMMANDS)}

ZSH_SCRIPT = """\
#compdef htb
_htb() {
    local -a cmds
    cmds=(%(cmds)s)

    if (( CURRENT == 2 )); then
        _describe 'command' cmds
        return
    fi

    case "${words[2]}" in
        list)       _arguments '--retired[Retired machines]' '--os[OS filter]:os:(Linux Windows)' '--diff[Difficulty filter]:diff:(Easy Medium Hard Insane)' '--search[Search query]:query:' ;;
        scan)       _arguments '--full[Full scan]' '--ports[Custom ports]:ports:' '2:ip:' ;;
        export)     _arguments '--notes-only[Export notes only]' ;;
        completion) _arguments '2:shell:(bash zsh)' ;;
        vpn)        _arguments '2:subcmd:(status start stop switch)' ;;
        key)        _arguments '2:subcmd:(set clear status)' ;;
    esac
}
_htb "$@"
""" % {"cmds": "\n    ".join(f'"{c}"' for c in ALL_COMMANDS)}


def run(shell: str):
    if shell == "bash":
        print(BASH_SCRIPT)
    elif shell == "zsh":
        print(ZSH_SCRIPT)
    else:
        die(f"Unknown shell: {shell} (bash or zsh)")
