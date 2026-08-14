from textual.app import App, ComposeResult
from src.tui.widgets.timer import TimerWidget
from textual.widgets import Footer

from src.tui.socket import send_command


class PomodoroApp(App):

    BINDINGS = [
        ("q", "quit_app", "Quit app"),
        ("s", "start_timer", "Start"),
        ("S", "skip_timer", "Skip phase"),
        ("p", "pause_timer", "Pause"),
    ]

    def compose(self) -> ComposeResult:
        yield TimerWidget()
        yield Footer()

    def action_quit_app(self):
        self.exit()

    def action_start_timer(self):
        self.run_worker(lambda: send_command("start"), thread=True)

    def action_pause_timer(self):
        self.run_worker(lambda: send_command("pause"), thread=True)

    def action_skip_timer(self):
        self.run_worker(lambda: send_command("skip"), thread=True)


if __name__ == "__main__":
    PomodoroApp().run()
