import getpass
import os

import keyring
import keyring.errors

from ..api import KEYRING_SERVICE, KEYRING_USER
from ..config import HTB_KEY_FILE
from ..ui import ask, console, die, header, ok, warn


def run(subcmd: str):
    if subcmd == "set":
        _cmd_set()
    elif subcmd == "clear":
        _cmd_clear()
    elif subcmd == "status":
        _cmd_status()
    else:
        die(f"Unbekannter Unterbefehl: {subcmd}\nUsage: htb key set|clear|status")


def _cmd_set():
    header("API Key setzen")
    key = getpass.getpass("  HTB API Key: ").strip()
    if not key:
        die("Kein Key eingegeben")
    try:
        keyring.set_password(KEYRING_SERVICE, KEYRING_USER, key)
        ok(f"Key im Keyring gespeichert [{key[:6]}...{key[-4:]}]")
    except Exception as e:
        die(f"Keyring nicht verfügbar: {e}\nAlternative: HTB_API_KEY=<key> setzen")

    if HTB_KEY_FILE.exists():
        warn(f"Plaintext-Datei noch vorhanden: {HTB_KEY_FILE}")
        if ask("Jetzt löschen?"):
            HTB_KEY_FILE.unlink()
            ok("Plaintext-Datei gelöscht")
    print()


def _cmd_clear():
    header("API Key löschen")
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_USER)
        ok("Key aus Keyring gelöscht")
    except keyring.errors.PasswordDeleteError:
        warn("Kein Key im Keyring gefunden")
    except Exception as e:
        warn(f"Keyring-Fehler: {e}")
    print()


def _cmd_status():
    header("API Key Status")
    if os.environ.get("HTB_API_KEY"):
        ok("HTB_API_KEY Env-Var gesetzt")
    try:
        key = keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
        if key:
            ok(f"Keyring: [{key[:6]}...{key[-4:]}]")
        else:
            warn("Keyring: kein Key gespeichert")
    except Exception as e:
        warn(f"Keyring nicht verfügbar: {e}")
    if HTB_KEY_FILE.exists():
        warn(f"Achtung: Plaintext-Datei noch vorhanden: {HTB_KEY_FILE}")
        console.print("  → Migrieren mit: [cyan]htb key set[/cyan]")
    print()
