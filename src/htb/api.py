import os
import keyring
import requests
from .config import HTB_API_BASE, HTB_KEY_FILE

KEYRING_SERVICE = "htbflow"
KEYRING_USER    = "api_key"


def get_api_key() -> str | None:
    # 1. Env var (CI / Skripte)
    if key := os.environ.get("HTB_API_KEY"):
        return key.strip()
    # 2. System Keyring (verschlüsselt)
    try:
        key = keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
        if key:
            return key
    except Exception:
        pass
    # 3. Fallback: Plaintext-Datei (Migration)
    if HTB_KEY_FILE.exists():
        return HTB_KEY_FILE.read_text().strip() or None
    return None


def _headers(key: str) -> dict:
    return {
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }


def load_machine_profile(machine: str) -> dict:
    key = get_api_key()
    if not key:
        return {}
    try:
        r = requests.get(
            f"{HTB_API_BASE}/machine/profile/{machine}",
            headers=_headers(key),
            timeout=10,
        )
        r.raise_for_status()
        info = r.json().get("info") or {}
        pts = info.get("static_points") or info.get("points")
        return {
            "id":         info.get("id"),
            "ip":         info.get("ip") or "",
            "os":         info.get("os") or "?",
            "difficulty": info.get("difficultyText") or "?",
            "points":     str(pts) if pts else "?",
            "release":    (info.get("release") or "?")[:10],
            "stars":      str(info.get("stars")) if info.get("stars") else "?",
        }
    except Exception:
        return {}


def get_active_machine(key: str) -> dict:
    try:
        r = requests.get(
            f"{HTB_API_BASE}/machine/active",
            headers=_headers(key),
            timeout=10,
        )
        r.raise_for_status()
        return r.json().get("info") or {}
    except Exception:
        return {}


def spawn_machine(key: str, machine_id: int) -> str | None:
    try:
        r = requests.post(
            f"{HTB_API_BASE}/vm/spawn",
            headers=_headers(key),
            json={"machine_id": machine_id},
            timeout=10,
        )
        return r.json().get("message", "")
    except Exception:
        return None


def reset_machine(key: str, machine_id: int) -> str | None:
    try:
        r = requests.post(
            f"{HTB_API_BASE}/vm/reset",
            headers=_headers(key),
            json={"machine_id": machine_id},
            timeout=10,
        )
        data = r.json()
        return data.get("message") or data.get("output", "")
    except Exception:
        return None


def list_machines(key: str, retired: bool = False) -> list[dict]:
    """Fetches all machines via pagination."""
    machines = []
    page = 1
    try:
        while True:
            r = requests.get(
                f"{HTB_API_BASE}/machine/paginated",
                headers=_headers(key),
                params={"per_page": 100, "page": page, "retired": 1 if retired else 0},
                timeout=15,
            )
            r.raise_for_status()
            data = r.json()
            page_data = data.get("data") or []
            machines.extend(page_data)
            meta = data.get("meta", {})
            if page >= (meta.get("last_page") or 1):
                break
            page += 1
        return machines
    except Exception:
        return machines


def search_machines(key: str, query: str) -> list[dict]:
    seen, results = set(), []
    for m in list_machines(key, retired=False) + list_machines(key, retired=True):
        mid = m.get("id")
        if mid in seen:
            continue
        seen.add(mid)
        if query.lower() in (m.get("name") or "").lower():
            results.append(m)
    return results


def terminate_machine(key: str) -> str | None:
    try:
        r = requests.post(
            f"{HTB_API_BASE}/vm/terminate",
            headers=_headers(key),
            json={},
            timeout=10,
        )
        return r.json().get("message", "")
    except Exception:
        return None


def submit_flag(key: str, machine_id: int, flag: str, difficulty: int) -> str | None:
    try:
        r = requests.post(
            f"{HTB_API_BASE}/machine/own",
            headers=_headers(key),
            json={"id": machine_id, "flag": flag, "difficulty": difficulty},
            timeout=10,
        )
        return r.json().get("message", "")
    except Exception:
        return None
