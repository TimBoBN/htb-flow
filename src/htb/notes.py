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
        "ip":         find(r"\*\*IP:\*\*\s*`([^`]+)`"),
        "os":         find(r"\*\*OS:\*\*\s*(.+)"),
        "difficulty": find(r"\*\*Schwierigkeit:\*\*\s*(.+)"),
        "points":     find(r"\*\*Punkte:\*\*\s*(.+)"),
        "stars":      find(r"\*\*Rating:\*\*\s*★\s*(.+)"),
        "user_flag":  find(r"\*\*User:\*\*\s*`([^`]+)`"),
        "root_flag":  find(r"\*\*Root:\*\*\s*`([^`]+)`"),
    }


def create(path: Path, **kwargs):
    path.write_text(TEMPLATE.format(**kwargs))


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
        f"\n{creds_header}\n\n"
        f"| Kontext | User | Password |\n"
        f"|---------|------|----------|\n"
        f"{entry}"
    )
    path.write_text(text.rstrip() + "\n" + creds_section)
