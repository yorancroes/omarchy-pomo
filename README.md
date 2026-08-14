# omarchy-pomo

A Pomodoro timer for [Omarchy](https://omarchy.org/) — a background daemon, a Waybar module, and a Textual TUI, all sharing state over a local socket.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/yorancroes/omarchy-pomo/main/install.sh | bash
```

Or clone first and run it locally:

```bash
git clone https://github.com/yorancroes/omarchy-pomo.git
cd omarchy-pomo
./install.sh
```

Re-run `install.sh` any time to update — it's safe to run repeatedly and won't duplicate anything it's already set up.

This sets up the `pomodoro_timer` systemd `--user` service, adds a `custom/pomodoro` module to your Waybar config, and adds a Hyprland window rule so its TUI opens floating and centered.

## Usage

In Waybar: **left-click** starts/pauses the timer, **right-click** opens the full TUI (`s` start, `p` pause, `S` skip, `q` quit).

From a terminal: `python3 <install-dir>/src/cli.py <start|pause|skip>`

State lives at `/tmp/pomodoro_state.json`, the daemon listens on `/tmp/pomodoro.sock`.
