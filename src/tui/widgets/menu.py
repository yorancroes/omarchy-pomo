from textual.widgets import Static, Input, Label
from textual.app import ComposeResult


class CollapsibleMenu(Static):

    def compose(self) -> ComposeResult:
        yield Label("Set pomodoro time")
        yield Input(placeholder="minutes", type="integer", id="pomodoro-input")

        yield Label("Set break time")
        yield Input(placeholder="minutes", type="integer", id="break-input")
