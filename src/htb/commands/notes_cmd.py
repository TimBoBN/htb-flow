import os
import subprocess

from ..config import HTB_BASE, EDITOR
from ..ui import console, header, ok, warn, die


def run(machine: str):
    notes_path = HTB_BASE / machine / "notes.md"

    if not notes_path.exists():
        die(f"notes.md nicht gefunden: {notes_path}\nHinweis: htb init {machine} erstellt die Datei")

    header(f"Notes: {machine}")

    editor = EDITOR or os.environ.get("EDITOR", "")
    if editor:
        subprocess.run([editor, str(notes_path)])
        return

    try:
        subprocess.run(["xdg-open", str(notes_path)], check=True,
                       capture_output=True)
        ok(f"Geöffnet: {notes_path}")
    except Exception:
        console.print(f"\n  [cyan]{notes_path}[/cyan]\n")
        warn("Kein Editor konfiguriert — Pfad oben kopieren oder EDITOR setzen")
