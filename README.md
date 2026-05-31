# htbflow

A command-line workflow tool for HackTheBox. Manage the full machine lifecycle from initial setup to completion: spawn machines, run recon, track credentials, submit flags, and archive finished boxes — all without leaving the terminal.

## Installation

**Requirements:** Python 3.11+, `pipx`, `nmap`

```bash
git clone https://github.com/timbobn/htbflow
cd htbflow
pipx install .
```

Set your API key (stored encrypted in the system keyring):

```bash
htb key set
```

## Commands

### Workflow

```bash
htb init  <machine> [ip]   # Setup: VPN check, folders, /etc/hosts, notes.md, nmap
htb done  <machine>        # Finish: submit flags, terminate, cleanup, archive
htb update <machine> [ip]  # Update IP in /etc/hosts and notes.md
```

### Recon

```bash
htb list                          # All active machines
htb list --retired                # Retired machines
htb list --os Linux --diff Easy   # With filters (os/diff)
htb search <query>                # Search by name
htb info  <machine>               # Machine details + local status
htb status                        # Currently active machine + time remaining
```

### Lifecycle

```bash
htb spawn <machine>   # Start a machine via API, waits for IP
htb reset <machine>   # Reset a running machine
```

### Quick actions

```bash
htb notes <machine>              # Open notes.md in $EDITOR
htb flag  <machine>              # Submit a flag without running done
htb scan  <machine> [ip]         # Re-run nmap quick scan
htb scan  <machine> [ip] --full  # Re-run full port scan (background)
htb creds <machine>              # Save found credentials to notes.md
```

### Auth

```bash
htb key set     # Store API key encrypted in system keyring
htb key status  # Show where the key is coming from
htb key clear   # Remove key from keyring
```

### Shell completion

```bash
htb completion bash >> ~/.bashrc   # Bash
htb completion zsh  >> ~/.zshrc    # Zsh
```

## Configuration

Optional config file at `~/.config/htb/config.toml`:

```toml
htb_base  = "~/Data/Cyber/HTB"       # Where machine folders are created
ovpn_path = "~/Data/Cyber/HTB.ovpn"  # Path to your .ovpn file
editor    = "nvim"                    # Editor for htb notes (fallback: $EDITOR)
```

## API Key

The API key is read in this order:

1. `$HTB_API_KEY` environment variable (CI/scripts)
2. System keyring — set with `htb key set`
3. `~/.config/htb/api_key` plaintext file (legacy fallback)

Get your API key from [HackTheBox → Profile → Settings → API Key](https://app.hackthebox.com/profile/settings).

## Machine folder structure

`htb init` creates the following layout under `htb_base`:

```
<machine>/
├── notes.md      ← metadata, flags, credentials, write-up notes
├── nmap/
│   ├── quick.txt
│   └── full.txt
├── web/
├── exploits/
├── loot/
└── creds/
```

## License

MIT
