from textual import on
from textual.app import App, ComposeResult
from src.tui.widgets.timer import TimerWidget
from textual.containers import Container
from textual.widgets import Footer, Input

import json
from pathlib import Path
from src.tui.socket import send_command, send_time_command
from src.tui.widgets.menu import CollapsibleMenu
from src.tui.omarchy_theme import load_omarchy_theme

STATE_FILE = Path("/tmp/pomodoro_state.json")


class PomodoroApp(App):
    status: str = ""

    CSS = """
    #menu-panel {
        dock: right;
        width: 40;
        height: 1fr;
    }
    """

    BINDINGS = [
        ("q", "quit_app", "Quit app"),
        ("space", "start_stop_timer", "Start / Stop"),
        ("s", "skip_timer", "Skip phase"),
        ("m", "toggle_menu", "Menu"),
        ("escape", "close_menu", "Close menu"),
    ]

    def compose(self) -> ComposeResult:
        yield TimerWidget()
        with Container(id="menu-panel"):
            yield CollapsibleMenu()
        yield Footer()

    def on_mount(self) -> None:
        omarchy_theme = load_omarchy_theme()
        if omarchy_theme is not None:
            self.register_theme(omarchy_theme)
            self.theme = "omarchy"

        self.query_one("#menu-panel").display = False
        self.call_after_refresh(self.set_focus, None)

        self.set_interval(0.5, self.poll_state)

    def poll_state(self) -> None:
        remaining, phase, status = self._read_state()
        self.status = status
        self.query_one(TimerWidget).refresh_state(remaining, phase)

    def _read_state(self) -> tuple[int, str, str]:
        try:
            with STATE_FILE.open() as f:
                state = json.load(f)
            return (int(state["remaining"]), str(state["phase"]), str(state["status"]))
        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
            return (0, "ERROR", "")

    def action_quit_app(self):
        self.exit()

    def action_start_stop_timer(self):
        if self.status == "NOT_STARTED" or self.status == "PAUSED":
            self.run_worker(lambda: send_command("start"), thread=True)

        else:
            self.run_worker(lambda: send_command("pause"), thread=True)

    def action_skip_timer(self):
        self.run_worker(lambda: send_command("skip"), thread=True)

    def action_toggle_menu(self):
        menu = self.query_one("#menu-panel")
        menu.display = not menu.display
        if not menu.display:
            self.set_focus(None)

    def action_close_menu(self):
        menu = self.query_one("#menu-panel")
        if menu.display:
            menu.display = False
            self.set_focus(None)

    @on(Input.Submitted, "#pomodoro-input")
    def on_pomodoro_time_submitted(self, event: Input.Submitted):
        new_pomodoro_time = event.value
        self.run_worker(
            lambda: send_time_command(f"change_pomo {int(new_pomodoro_time) * 60}"), thread=True
        )

    @on(Input.Submitted, "#break-input")
    def on_break_time_submitted(self, event: Input.Submitted):
        new_break_time = event.value
        self.run_worker(
            lambda: send_time_command(f"change_break {int(new_break_time) * 60}"), thread=True
        )


if __name__ == "__main__":
    PomodoroApp().run()
