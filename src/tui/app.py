from textual.app import App, ComposeResult
from src.tui.widgets.timer import TimerWidget


class PomodoroApp(App):

    def compose(self) -> ComposeResult:
        yield TimerWidget()
