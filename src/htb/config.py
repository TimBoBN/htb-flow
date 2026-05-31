import tomllib
from pathlib import Path

CONFIG_FILE = Path.home() / ".config/htb/config.toml"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def _path(key: str, default: Path) -> Path:
    cfg = _CFG
    if val := cfg.get(key):
        return Path(val).expanduser()
    return default


_CFG = load_config()

HTB_API_BASE = "https://labs.hackthebox.com/api/v4"
HTB_KEY_FILE = Path.home() / ".config/htb/api_key"
HTB_BASE     = _path("htb_base",  Path.home() / "Data/Cyber/HTB")
HTB_OVPN     = _path("ovpn_path", Path.home() / "Data/Cyber/HTB.ovpn")
EDITOR       = _CFG.get("editor", "")
WL_DIR       = Path("/usr/share/wordlists")
WL_WEB       = WL_DIR / "dirbuster/directory-list-2.3-medium.txt"
WL_WEB_SMALL = WL_DIR / "dirb/common.txt"
