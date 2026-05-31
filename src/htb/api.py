import os
import sys

import keyring
import requests

from .config import HTB_API_BASE, HTB_KEY_FILE

_warned_auth = False


def _check_401(r) -> bool:
    """Prints a one-time warning on 401 and returns True if auth failed."""
    global _warned_auth
    if r.status_code == 401 and not _warned_auth:
        _warned_auth = True
        print("\033[31m  ✘  API key invalid or expired — run: htb key set\033[0m", file=sys.stderr)
    return r.status_code == 401


KEYRING_SERVICE = "htbflow"
KEYRING_USER = "api_key"


def get_api_key() -> str | None:
    # 1. Env var (CI / scripts)
    if key := os.environ.get("HTB_API_KEY"):
        return key.strip()
    # 2. System keyring (encrypted)
    try:
        key = keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
        if key:
            return key
    except Exception:
        pass
    # 3. Fallback: plaintext file (legacy migration)
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
            "id": info.get("id"),
            "ip": info.get("ip") or "",
            "os": info.get("os") or "?",
            "difficulty": info.get("difficultyText") or "?",
            "points": str(pts) if pts else "?",
            "release": (info.get("release") or "?")[:10],
            "stars": str(info.get("stars")) if info.get("stars") else "?",
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
    machines: list[dict] = []
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


def get_user_id(key: str) -> int | None:
    try:
        r = requests.get(f"{HTB_API_BASE}/user/info", headers=_headers(key), timeout=8)
        r.raise_for_status()
        return r.json().get("info", {}).get("id")
    except Exception:
        return None


def get_profile(key: str) -> dict:
    uid = get_user_id(key)
    if not uid:
        return {}
    try:
        r = requests.get(f"{HTB_API_BASE}/profile/{uid}", headers=_headers(key), timeout=8)
        r.raise_for_status()
        return r.json().get("profile") or {}
    except Exception:
        return {}


def get_activity(key: str) -> list[dict]:
    uid = get_user_id(key)
    if not uid:
        return []
    try:
        r = requests.get(
            f"{HTB_API_BASE}/user/profile/activity/{uid}", headers=_headers(key), timeout=8
        )
        if _check_401(r):
            return []
        r.raise_for_status()
        return r.json().get("profile", {}).get("activity") or []
    except Exception:
        return []


def get_tracks(key: str) -> list[dict]:
    try:
        r = requests.get(f"{HTB_API_BASE}/tracks", headers=_headers(key), timeout=8)
        if _check_401(r):
            return []
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else []
    except Exception:
        return []


def get_fortresses(key: str) -> list[dict]:
    try:
        r = requests.get(f"{HTB_API_BASE}/fortresses", headers=_headers(key), timeout=8)
        if _check_401(r):
            return []
        r.raise_for_status()
        return r.json().get("data") or []
    except Exception:
        return []


def get_season(key: str) -> dict:
    """Returns the currently active season or empty dict."""
    try:
        r = requests.get(f"{HTB_API_BASE}/season/list", headers=_headers(key), timeout=8)
        r.raise_for_status()
        seasons = r.json().get("data") or []
        for s in seasons:
            if s.get("active"):
                return s
        return seasons[0] if seasons else {}
    except Exception:
        return {}


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
