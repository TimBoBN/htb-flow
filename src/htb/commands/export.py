import zipfile
from datetime import date

from ..config import HTB_BASE
from ..ui import console, die, header, ok, warn


def run(notes_only: bool = False):
    if not HTB_BASE.exists():
        die(f"HTB_BASE not found: {HTB_BASE}")

    header("Export")

    machines = [d for d in HTB_BASE.iterdir() if d.is_dir()]
    if not machines:
        warn("No machines found")
        return

    suffix = "-notes" if notes_only else ""
    out_path = HTB_BASE / f"htbflow-export{suffix}-{date.today().isoformat()}.zip"

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for machine_dir in sorted(machines):
            if notes_only:
                notes_path = machine_dir / "notes.md"
                if notes_path.exists():
                    zf.write(notes_path, f"{machine_dir.name}/notes.md")
            else:
                for f in machine_dir.rglob("*"):
                    if f.is_file():
                        zf.write(f, f.relative_to(HTB_BASE))

    size_mb = out_path.stat().st_size / (1024 * 1024)
    ok(f"Exported {len(machines)} machine(s) → {out_path} ({size_mb:.1f}M)")
    console.print(f"\n  [cyan]{out_path}[/cyan]")
    print()
