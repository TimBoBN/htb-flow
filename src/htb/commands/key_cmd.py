import getpass
import os

import keyring
import keyring.errors

from ..api import KEYRING_SERVICE, KEYRING_USER
from ..config import HTB_KEY_FILE
from ..ui import console, die, header, ok, warn


def run(subcmd: str):
    if subcmd == "set":
        _cmd_set()
    elif subcmd == "clear":
        _cmd_clear()
    elif subcmd == "status":
        _cmd_status()
    else:
        die(f"Unknown subcommand: {subcmd}\nUsage: htb key set|clear|status")


def _cmd_set():
    header("Set API Key")

    # Auto-migrate: plaintext file present and no key in keyring yet
    existing_file_key = HTB_KEY_FILE.read_text().strip() if HTB_KEY_FILE.exists() else ""
    existing_ring_key = ""
    try:
        existing_ring_key = keyring.get_password(KEYRING_SERVICE, KEYRING_USER) or ""
    except Exception:
        pass

    if existing_file_key and not existing_ring_key:
        ok(
            f"Plaintext file found — migrating key [{existing_file_key[:6]}...{existing_file_key[-4:]}]"
        )
        key = existing_file_key
    else:
        key = getpass.getpass("  HTB API Key: ").strip()
        if not key:
            die("No key entered")

    try:
        keyring.set_password(KEYRING_SERVICE, KEYRING_USER, key)
        ok(f"Key stored in keyring [{key[:6]}...{key[-4:]}]")
    except Exception as e:
        die(f"Keyring not available: {e}\nAlternative: set HTB_API_KEY=<key>")

    if HTB_KEY_FILE.exists():
        HTB_KEY_FILE.unlink()
        ok("Plaintext file deleted")
    print()


def _cmd_clear():
    header("Delete API Key")
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_USER)
        ok("Key removed from keyring")
    except keyring.errors.PasswordDeleteError:
        warn("No key found in keyring")
    except Exception as e:
        warn(f"Keyring error: {e}")
    print()


def _cmd_status():
    header("API Key Status")
    if os.environ.get("HTB_API_KEY"):
        ok("HTB_API_KEY env var is set")
    try:
        key = keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
        if key:
            ok(f"Keyring: [{key[:6]}...{key[-4:]}]")
        else:
            warn("Keyring: no key stored")
    except Exception as e:
        warn(f"Keyring not available: {e}")
    if HTB_KEY_FILE.exists():
        warn(f"Warning: plaintext file still present: {HTB_KEY_FILE}")
        console.print("  → Migrate with: [cyan]htb key set[/cyan]")
    print()
