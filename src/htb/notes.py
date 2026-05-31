import re
from pathlib import Path

TEMPLATE = """\
# {machine}

- **IP:** `{ip}`
- **Hostname:** `{hostname}`
- **Datum:** {date}
- **OS:** {os}
- **Schwierigkeit:** {difficulty}
- **Punkte:** {points}
- **Release:** {release}
- **Rating:** ★ {stars}

---

## Ports / Services

| Port | Service | Version |
|------|---------|---------|
|      |         |         |

## Recon



## Foothold



## Privilege Escalation



## Flags

- **User:**  ``
- **Root:**  ``

## Credentials

| Kontext | User | Password |
|---------|------|----------|
|         |      |          |

## Notizen

"""


def parse(path: Path) -> dict:
    text = path.read_text()

    def find(pattern):
        m = re.search(pattern, text)
        return m.group(1).strip() if m else ""

    return {
        "ip": find(r"\*\*IP:\*\*\s*`([^`]+)`"),
        "os": find(r"\*\*OS:\*\*\s*(.+)"),
        "difficulty": find(r"\*\*Schwierigkeit:\*\*\s*(.+)"),
        "points": find(r"\*\*Punkte:\*\*\s*(.+)"),
        "stars": find(r"\*\*Rating:\*\*\s*★\s*(.+)"),
        "user_flag": find(r"\*\*User:\*\*\s*`([^`]+)`"),
        "root_flag": find(r"\*\*Root:\*\*\s*`([^`]+)`"),
    }


def create(path: Path, **kwargs):
    path.write_text(TEMPLATE.format(**kwargs))


def parse_creds(path: Path) -> list[dict]:
    """Parse the Credentials table from notes.md."""
    text = path.read_text()
    creds, in_section = [], False
    for line in text.splitlines():
        if "## Credentials" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not (in_section and line.strip().startswith("|")):
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if len(parts) != 3:
            continue
        context, user_raw, pass_raw = parts
        if not context or set(context) <= set("- ") or "Kontext" in context:
            continue
        user = re.sub(r"`([^`]*)`", r"\1", user_raw).strip()
        password = re.sub(r"`([^`]*)`", r"\1", pass_raw).strip()
        if user and password and user.lower() != "user":
            creds.append({"context": context, "user": user, "password": password})
    return creds


def add_port(path: Path, port: str, service: str, version: str = ""):
    """Append a row to the Ports / Services table in notes.md."""
    text = path.read_text()
    entry = f"| {port:<6} | {service:<8} | {version} |\n"
    section = "## Ports / Services"
    if section not in text:
        path.write_text(
            text.rstrip()
            + f"\n\n{section}\n\n| Port   | Service  | Version |\n|--------|----------|---------|\n{entry}"
        )
        return
    lines = text.splitlines(keepends=True)
    last_row = None
    in_sec = False
    for i, line in enumerate(lines):
        if section in line:
            in_sec = True
        elif in_sec and line.startswith("## "):
            break
        elif in_sec and line.strip().startswith("|"):
            last_row = i
    if last_row is not None:
        lines.insert(last_row + 1, entry)
        path.write_text("".join(lines))


def append_creds(path: Path, user: str, password: str, context: str = ""):
    text = path.read_text()
    entry = f"| {context or '-'} | `{user}` | `{password}` |\n"
    creds_header = "## Credentials"

    if creds_header in text:
        lines = text.splitlines(keepends=True)
        last_table_line = None
        in_section = False
        for i, line in enumerate(lines):
            if creds_header in line:
                in_section = True
            elif in_section and line.startswith("## "):
                break
            elif in_section and line.strip().startswith("|"):
                last_table_line = i
        if last_table_line is not None:
            lines.insert(last_table_line + 1, entry)
            path.write_text("".join(lines))
            return

    creds_section = (
        f"\n{creds_header}\n\n| Kontext | User | Password |\n|---------|------|----------|\n{entry}"
    )
    path.write_text(text.rstrip() + "\n" + creds_section)
