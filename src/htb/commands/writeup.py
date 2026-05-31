import re
from pathlib import Path

from ..config import HTB_BASE
from ..ui import console, header, ok, warn, die


def _clean(text: str) -> str:
    """Remove empty table rows and sections with no content."""
    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Skip empty table rows like "|      |         |         |"
        if re.match(r"^\|\s*\|", line) and all(
            c in " |\t" for c in line.rstrip("\n")
        ):
            i += 1
            continue
        out.append(line)
        i += 1

    # Remove sections that only have a header + blank lines
    result = []
    text_out = "".join(out)
    sections = re.split(r"(?=^## )", text_out, flags=re.MULTILINE)
    for sec in sections:
        body = re.sub(r"^## .+\n", "", sec, count=1).strip()
        if body or not sec.startswith("## "):
            result.append(sec)

    return "".join(result).rstrip() + "\n"


def run(machine: str):
    notes_path = HTB_BASE / machine / "notes.md"
    if not notes_path.exists():
        die(f"notes.md nicht gefunden: {notes_path}")

    header(f"Writeup: {machine}")
    out_path = HTB_BASE / machine / f"{machine}-writeup.md"
    cleaned  = _clean(notes_path.read_text())
    out_path.write_text(cleaned)
    ok(f"Erstellt: {out_path}")
    console.print(f"\n  [cyan]{out_path}[/cyan]")
    print()
