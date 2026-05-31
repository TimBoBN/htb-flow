from ..api import get_api_key, search_machines
from ..ui import console, header, warn, die
from .list_machines import _machine_table


def run(query: str):
    key = get_api_key()
    if not key:
        die("Kein API-Key — HTB_API_KEY oder ~/.config/htb/api_key")

    header(f"Suche: {query}")
    machines = search_machines(key, query)

    if not machines:
        warn(f"Keine Maschinen gefunden für '{query}'")
        return

    console.print(f"  {len(machines)} Ergebnis(se)\n")
    console.print(_machine_table(machines))
    print()
