import sys
from typing import NoReturn

from rich.console import Console

console = Console()
_err_console = Console(stderr=True)

BANNER_HTB = (
    "[bold red]"
    "\n  ██╗  ██╗████████╗██████╗ "
    "\n  ██║  ██║╚══██╔══╝██╔══██╗"
    "\n  ███████║   ██║   ██████╔╝"
    "\n  ██╔══██║   ██║   ██╔══██╗"
    "\n  ██║  ██║   ██║   ██████╔╝"
    "\n  ╚═╝  ╚═╝   ╚═╝   ╚═════╝ "
    "\n[/bold red]"
)

BANNER_DONE = (
    "[bold red]"
    "\n  ██████╗  ██████╗ ███╗   ██╗███████╗"
    "\n  ██╔══██╗██╔═══██╗████╗  ██║██╔════╝"
    "\n  ██║  ██║██║   ██║██╔██╗ ██║█████╗  "
    "\n  ██║  ██║██║   ██║██║╚██╗██║██╔══╝  "
    "\n  ██████╔╝╚██████╔╝██║ ╚████║███████╗"
    "\n  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚══════╝"
    "\n[/bold red]"
)


def header(title: str):
    console.print(f"\n[bold cyan]══ {title} ══[/bold cyan]")


def ok(msg: str):
    console.print(f"  [green]✔[/green]  {msg}")


def warn(msg: str):
    console.print(f"  [yellow]⚠[/yellow]  {msg}")


def die(msg: str) -> NoReturn:
    _err_console.print(f"  [red]✘[/red]  {msg}")
    sys.exit(1)


def ask(question: str) -> bool:
    try:
        ans = input(f"  {question} [y/N] ")
        return ans.strip().lower() == "y"
    except EOFError:
        print()
        return False
    except KeyboardInterrupt:
        print()
        sys.exit(0)


def ask_input(prompt: str) -> str:
    try:
        return input(f"  {prompt} ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
