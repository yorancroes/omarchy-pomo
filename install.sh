#!/usr/bin/env bash
# Install/update omarchy-pomo: daemon (systemd --user), Waybar module, and floating TUI.
# Safe to re-run any time - it converges config in place rather than duplicating it.
set -euo pipefail

REPO_URL="https://github.com/yorancroes/omarchy-pomo.git"

backup_file() {
    local f="$1"
    [[ -f "$f" ]] && cp "$f" "$f.bak.$(date +%s)"
}

# ---------------------------------------------------------------------------
# Resolve INSTALL_DIR: reuse an existing checkout if we're running from one,
# otherwise clone (curl | bash case, where $BASH_SOURCE isn't a real file).
# ---------------------------------------------------------------------------
SOURCE="${BASH_SOURCE[0]:-}"
SCRIPT_DIR=""
if [[ -n "$SOURCE" && -f "$SOURCE" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "$SOURCE")" && pwd)"
fi

if [[ -n "$SCRIPT_DIR" && -f "$SCRIPT_DIR/src/daemon.py" ]]; then
    INSTALL_DIR="$SCRIPT_DIR"
    echo "Using existing checkout: $INSTALL_DIR"
else
    INSTALL_DIR="${OMARCHY_POMO_INSTALL_DIR:-$HOME/.local/share/omarchy-pomo}"
    if [[ -d "$INSTALL_DIR/.git" ]]; then
        echo "Updating existing install at $INSTALL_DIR"
        command -v git >/dev/null || { echo "ERROR: git is required." >&2; exit 1; }
        git -C "$INSTALL_DIR" pull --ff-only
    elif [[ -e "$INSTALL_DIR" ]]; then
        echo "ERROR: $INSTALL_DIR exists but isn't a git checkout of omarchy-pomo." >&2
        echo "Remove it or set OMARCHY_POMO_INSTALL_DIR to a different path." >&2
        exit 1
    else
        echo "Cloning omarchy-pomo into $INSTALL_DIR"
        command -v git >/dev/null || { echo "ERROR: git is required." >&2; exit 1; }
        git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
    fi
fi

# ---------------------------------------------------------------------------
# Prerequisite checks
# ---------------------------------------------------------------------------
command -v python3 >/dev/null || { echo "ERROR: python3 is required." >&2; exit 1; }
command -v systemctl >/dev/null || { echo "ERROR: systemd (systemctl) is required." >&2; exit 1; }

HAVE_WAYBAR=0
[[ -f "$HOME/.config/waybar/config.jsonc" ]] && command -v waybar >/dev/null 2>&1 && HAVE_WAYBAR=1

HAVE_HYPR=0
[[ -f "$HOME/.config/hypr/hyprland.conf" ]] && command -v hyprctl >/dev/null 2>&1 && HAVE_HYPR=1

command -v omarchy-launch-or-focus-tui >/dev/null 2>&1 \
    || echo "WARNING: omarchy-launch-or-focus-tui not found on PATH; right-click TUI launch may not work."

# ---------------------------------------------------------------------------
# venv + Python deps (textual, pyfiglet - only needed by the TUI)
# ---------------------------------------------------------------------------
VENV_DIR="$INSTALL_DIR/.venv"
if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating virtualenv at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install --quiet "$INSTALL_DIR"

chmod +x "$INSTALL_DIR/bin/omarchy-pomo-tui"

# ---------------------------------------------------------------------------
# systemd --user unit
# ---------------------------------------------------------------------------
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/pomodoro_timer.service"
mkdir -p "$SERVICE_DIR"

NEW_SERVICE_CONTENT="[Unit]
Description=Pomodoro timer daemon
After=default.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $INSTALL_DIR/src/daemon.py
Restart=on-failure
RestartSec=2

[Install]
WantedBy=default.target
"

UNIT_CHANGED=0
if [[ "$(cat "$SERVICE_FILE" 2>/dev/null || true)" != "${NEW_SERVICE_CONTENT%$'\n'}" ]]; then
    UNIT_CHANGED=1
    backup_file "$SERVICE_FILE"
    printf '%s' "$NEW_SERVICE_CONTENT" > "$SERVICE_FILE"
fi

# Restart the daemon whenever its source changed too, not just the unit file -
# otherwise editing timer.py/daemon.py and rerunning install.sh silently
# leaves the old code running.
DAEMON_HASH_FILE="$SERVICE_DIR/.omarchy-pomo-daemon.sha256"
NEW_DAEMON_HASH="$(cat "$INSTALL_DIR/src/daemon.py" "$INSTALL_DIR/src/timer.py" | sha256sum | cut -d' ' -f1)"
OLD_DAEMON_HASH="$(cat "$DAEMON_HASH_FILE" 2>/dev/null || true)"
DAEMON_SRC_CHANGED=0
[[ "$NEW_DAEMON_HASH" != "$OLD_DAEMON_HASH" ]] && DAEMON_SRC_CHANGED=1

systemctl --user daemon-reload
systemctl --user enable pomodoro_timer.service

if [[ "$UNIT_CHANGED" == "1" || "$DAEMON_SRC_CHANGED" == "1" ]]; then
    systemctl --user restart pomodoro_timer.service
    reason=""
    [[ "$UNIT_CHANGED" == "1" ]] && reason+="unit file changed"
    if [[ "$DAEMON_SRC_CHANGED" == "1" ]]; then
        [[ -n "$reason" ]] && reason+=", "
        reason+="daemon source changed"
    fi
    echo "systemd: daemon restarted ($reason)."
else
    systemctl --user is-active --quiet pomodoro_timer.service || systemctl --user start pomodoro_timer.service
    echo "systemd: unit and daemon source unchanged, nothing to restart."
fi

printf '%s' "$NEW_DAEMON_HASH" > "$DAEMON_HASH_FILE"

# ---------------------------------------------------------------------------
# Waybar module merge (surgical text edit - JSONC has comments, never
# round-trip through a JSON parser)
# ---------------------------------------------------------------------------
if [[ "$HAVE_WAYBAR" == "1" ]]; then
    WAYBAR_CONFIG="$HOME/.config/waybar/config.jsonc"
    python3 - "$INSTALL_DIR" "$WAYBAR_CONFIG" <<'PYEOF'
import re
import shutil
import sys
import time
from pathlib import Path

install_dir, config_path = sys.argv[1], sys.argv[2]
path = Path(config_path)
text = path.read_text()
original = text


def find_matching_close(s, open_idx):
    open_ch = s[open_idx]
    close_ch = {"{": "}", "[": "]"}[open_ch]
    depth = 0
    in_string = False
    escape = False
    i = open_idx
    while i < len(s):
        ch = s[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    raise ValueError("no matching closer found")


new_block = (
    '"custom/pomodoro": {\n'
    '  "format": "{}",\n'
    f'  "exec": "/usr/bin/python3 {install_dir}/src/waybar_timer/waybar_timer.py",\n'
    '  "return-type": "json",\n'
    '  "interval": 1,\n'
    f'  "on-click": "/usr/bin/python3 {install_dir}/src/waybar_timer/toggle.py",\n'
    f'  "on-click-right": "omarchy-launch-or-focus-tui {install_dir}/bin/omarchy-pomo-tui",\n'
    '  "tooltip": true\n'
    "}"
)

m = re.search(r'"custom/pomodoro"\s*:\s*(\{)', text)
if m:
    open_idx = m.start(1)
    close_idx = find_matching_close(text, open_idx)
    text = text[: m.start()] + new_block + text[close_idx + 1 :]
else:
    stripped_end = len(text.rstrip())
    end_idx = text.rfind("}", 0, stripped_end)
    if end_idx == -1:
        print("waybar: could not find a closing brace to insert into, skipping", file=sys.stderr)
        sys.exit(0)
    before, after = text[:end_idx], text[end_idx:]
    before_r = before.rstrip()
    if before_r and before_r[-1] not in ("{", ","):
        before = before_r + ",\n"
    else:
        before = before_r + "\n"
    text = before + new_block + "\n" + after

mc = re.search(r'"modules-center"\s*:\s*(\[)', text)
if mc:
    close = find_matching_close(text, mc.start(1))
    array_body = text[mc.start(1) : close]
    if '"custom/pomodoro"' not in array_body:
        text = text[:close] + ', "custom/pomodoro"' + text[close:]
else:
    print('waybar: "modules-center" array not found, skipping module registration', file=sys.stderr)

if text == original:
    print("waybar: custom/pomodoro block already up to date, no changes")
else:
    shutil.copy(config_path, f"{config_path}.bak.{int(time.time())}")
    path.write_text(text)
    print("waybar: custom/pomodoro block installed/updated")
PYEOF
else
    echo "Waybar not detected, skipping Waybar integration."
fi

# ---------------------------------------------------------------------------
# Waybar style merge - give the modules-center cluster a bit more breathing
# room, since custom/pomodoro joining it makes the row feel cramped.
# ---------------------------------------------------------------------------
if [[ "$HAVE_WAYBAR" == "1" ]]; then
    WAYBAR_STYLE="$HOME/.config/waybar/style.css"
    if [[ -f "$WAYBAR_STYLE" ]]; then
        python3 - "$WAYBAR_STYLE" <<'PYEOF'
import re
import shutil
import sys
import time
from pathlib import Path

style_path = sys.argv[1]
path = Path(style_path)
text = path.read_text()
original = text

marker = "/* omarchy-pomo: extra breathing room in the waybar center cluster (managed by install.sh) */"
new_block = (
    f"{marker}\n"
    "#clock,\n"
    "#custom-weather,\n"
    "#custom-pomodoro,\n"
    "#custom-update,\n"
    "#custom-voxtype,\n"
    "#custom-screenrecording-indicator,\n"
    "#custom-idle-indicator,\n"
    "#custom-notification-silencing-indicator {\n"
    "  margin: 0 4.5px;\n"
    "}"
)

managed_re = re.compile(re.escape(marker) + r"\n(?:[^\n]*\n){1,10}?\}")

if managed_re.search(text):
    text = managed_re.sub(new_block, text)
else:
    text = text.rstrip("\n") + "\n\n" + new_block + "\n"

if text == original:
    print("waybar: center-cluster spacing already up to date, no changes")
else:
    shutil.copy(style_path, f"{style_path}.bak.{int(time.time())}")
    path.write_text(text)
    print("waybar: center-cluster spacing installed/updated")
PYEOF
    else
        echo "waybar: style.css not found at $WAYBAR_STYLE, skipping spacing tweak"
    fi
fi

# ---------------------------------------------------------------------------
# Hyprland window rule merge
# ---------------------------------------------------------------------------
if [[ "$HAVE_HYPR" == "1" ]]; then
    HYPR_CONFIG="$HOME/.config/hypr/hyprland.conf"
    python3 - "$HYPR_CONFIG" <<'PYEOF'
import re
import shutil
import sys
import time
from pathlib import Path

config_path = sys.argv[1]
path = Path(config_path)
text = path.read_text()
original = text

# Remove the old ad-hoc pomodoro-tui class rule from earlier manual setups.
old_re = re.compile(
    r"\n?# Float the pomodoro TUI terminal opened from waybar\n"
    r"windowrule = float on, match:class \^\(pomodoro-tui\)\$\n"
    r"windowrule = size 800 500, match:class \^\(pomodoro-tui\)\$\n"
    r"windowrule = center on, match:class \^\(pomodoro-tui\)\$\n?"
)
text = old_re.sub("\n", text)

new_block = (
    "# omarchy-pomo: float the TUI window opened from Waybar (managed by install.sh)\n"
    "windowrule = float on, match:class ^(org.omarchy.omarchy-pomo-tui)$\n"
    "windowrule = size 800 500, match:class ^(org.omarchy.omarchy-pomo-tui)$\n"
    "windowrule = center on, match:class ^(org.omarchy.omarchy-pomo-tui)$"
)
managed_re = re.compile(
    r"# omarchy-pomo: float the TUI window opened from Waybar.*?\n"
    r"(?:windowrule = .*\n?){3}"
)

if managed_re.search(text):
    text = managed_re.sub(new_block + "\n", text)
else:
    anchor = "# Add any other personal Hyprland configuration below"
    if anchor in text:
        text = text.replace(anchor, anchor + "\n\n" + new_block, 1)
    else:
        text = text.rstrip("\n") + "\n\n" + new_block + "\n"

if text == original:
    print("hyprland: pomodoro window rule already up to date, no changes")
else:
    shutil.copy(config_path, f"{config_path}.bak.{int(time.time())}")
    path.write_text(text)
    print("hyprland: pomodoro window rule installed/updated")
PYEOF
else
    echo "Hyprland not detected, skipping window rule."
fi

# ---------------------------------------------------------------------------
# Reload / restart
# ---------------------------------------------------------------------------
if [[ "$HAVE_HYPR" == "1" ]]; then
    hyprctl reload >/dev/null
    ERRS="$(hyprctl configerrors 2>/dev/null || true)"
    if [[ -n "$ERRS" ]]; then
        echo "WARNING: hyprctl configerrors reported issues:" >&2
        echo "$ERRS" >&2
    fi
fi

if [[ "$HAVE_WAYBAR" == "1" ]]; then
    if command -v omarchy >/dev/null 2>&1; then
        omarchy restart waybar
    else
        pkill -x waybar 2>/dev/null || true
        setsid waybar >/dev/null 2>&1 &
        disown
    fi
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
cat <<EOF

omarchy-pomo installed.
  Install dir:   $INSTALL_DIR
  Daemon:        systemctl --user status pomodoro_timer.service
  Waybar:        left-click start/pause, right-click opens the TUI
  TUI directly:  $INSTALL_DIR/bin/omarchy-pomo-tui
  CLI:           python3 $INSTALL_DIR/src/cli.py <start|pause|skip>
  State file:    /tmp/pomodoro_state.json
  Socket:        /tmp/pomodoro.sock

Re-run this script any time to update to the latest version.
EOF
