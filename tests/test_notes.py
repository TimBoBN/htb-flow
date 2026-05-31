import pytest
from pathlib import Path
from textwrap import dedent

from htb.notes import parse, parse_creds, add_port, append_creds, create


@pytest.fixture
def notes_file(tmp_path) -> Path:
    p = tmp_path / "notes.md"
    p.write_text(dedent("""\
        # TestBox

        - **IP:** `10.10.10.1`
        - **OS:** Linux
        - **Schwierigkeit:** Easy
        - **Punkte:** 20
        - **Rating:** ★ 4.5

        ## Flags

        - **User:**  `abc123def456abc1`
        - **Root:**  `deadbeef12345678`

        ## Credentials

        | Kontext | User | Password |
        |---------|------|----------|
        | SSH | `admin` | `hunter2` |
        | Web | `guest` | `pass123` |

        ## Ports / Services

        | Port   | Service  | Version |
        |--------|----------|---------|
        | 22     | ssh      | OpenSSH 8.0 |

        ## Notizen

    """))
    return p


def test_parse_basic(notes_file):
    n = parse(notes_file)
    assert n["ip"] == "10.10.10.1"
    assert n["os"] == "Linux"
    assert n["difficulty"] == "Easy"
    assert n["points"] == "20"
    assert n["stars"] == "4.5"


def test_parse_flags(notes_file):
    n = parse(notes_file)
    assert n["user_flag"] == "abc123def456abc1"
    assert n["root_flag"] == "deadbeef12345678"


def test_parse_missing_flag(tmp_path):
    p = tmp_path / "notes.md"
    p.write_text("# Box\n- **User:**  ``\n- **Root:**  ``\n")
    n = parse(p)
    assert n["user_flag"] == ""
    assert n["root_flag"] == ""


def test_parse_creds(notes_file):
    creds = parse_creds(notes_file)
    assert len(creds) == 2
    assert creds[0] == {"context": "SSH", "user": "admin", "password": "hunter2"}
    assert creds[1] == {"context": "Web", "user": "guest", "password": "pass123"}


def test_parse_creds_empty(tmp_path):
    p = tmp_path / "notes.md"
    p.write_text("# Box\n## Notizen\n\n")
    assert parse_creds(p) == []


def test_add_port(notes_file):
    add_port(notes_file, "80", "http", "nginx 1.18")
    text = notes_file.read_text()
    assert "| 80     | http     | nginx 1.18 |" in text


def test_add_port_creates_section(tmp_path):
    p = tmp_path / "notes.md"
    p.write_text("# Box\n## Notizen\n\n")
    add_port(p, "443", "https")
    assert "443" in p.read_text()
    assert "Ports / Services" in p.read_text()


def test_append_creds_new_section(tmp_path):
    p = tmp_path / "notes.md"
    p.write_text("# Box\n## Notizen\n\n")
    append_creds(p, "root", "toor", "SSH")
    text = p.read_text()
    assert "## Credentials" in text
    assert "`root`" in text
    assert "`toor`" in text


def test_append_creds_existing_section(notes_file):
    append_creds(notes_file, "newuser", "newpass", "FTP")
    creds = parse_creds(notes_file)
    names = [c["user"] for c in creds]
    assert "newuser" in names
