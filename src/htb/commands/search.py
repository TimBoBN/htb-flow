from ..api import get_api_key, search_machines
from ..ui import console, die, header, warn
from .list_machines import _machine_table


def run(query: str):
    key = get_api_key()
    if not key:
        die("No API key — run: htb key set")

    header(f"Suche: {query}")
    machines = search_machines(key, query)

    if not machines:
        warn(f"No machines found for '{query}'")
        return

    console.print(f"  {len(machines)} result(s)\n")
    console.print(_machine_table(machines))
    print()
