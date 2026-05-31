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
    "notes",
    "flag",
    "scan",
    "creds",
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
        list)
            COMPREPLY=($(compgen -W "--retired --os --diff" -- "$cur")) ;;
        scan)
            COMPREPLY=($(compgen -W "--full" -- "$cur")) ;;
        completion)
            COMPREPLY=($(compgen -W "bash zsh" -- "$cur")) ;;
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
        list)       _arguments '--retired[Retired Machines]' '--os[OS-Filter]:os:(Linux Windows)' '--diff[Difficulty-Filter]:diff:(Easy Medium Hard Insane)' ;;
        scan)       _arguments '--full[Full scan]' '2:ip:' ;;
        completion) _arguments '2:shell:(bash zsh)' ;;
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
        die(f"Unbekannte Shell: {shell} (bash oder zsh)")
