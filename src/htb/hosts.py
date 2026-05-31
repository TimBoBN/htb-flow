import re
import subprocess
from pathlib import Path


def _read() -> str:
    return Path("/etc/hosts").read_text()


def _write(content: str):
    subprocess.run(
        ["sudo", "tee", "/etc/hosts"], input=content.encode(), check=True, capture_output=True
    )


def contains(hostname: str) -> bool:
    return hostname in _read()


def get_ip(hostname: str) -> str | None:
    for line in _read().splitlines():
        if hostname in line and not line.strip().startswith("#"):
            parts = line.split()
            return parts[0] if parts else None
    return None


def add(ip: str, hostname: str):
    subprocess.run(
        ["sudo", "tee", "-a", "/etc/hosts"],
        input=f"{ip}    {hostname}\n".encode(),
        check=True,
        capture_output=True,
    )


def remove(hostname: str):
    lines = [line for line in _read().splitlines(keepends=True) if hostname not in line]
    _write("".join(lines))


def update_ip(old_ip: str, new_ip: str, hostname: str):
    content = re.sub(
        rf"^{re.escape(old_ip)}\s[^\n]*{re.escape(hostname)}",
        f"{new_ip}    {hostname}",
        _read(),
        flags=re.MULTILINE,
    )
    _write(content)
