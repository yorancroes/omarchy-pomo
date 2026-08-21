import pyfiglet
from textual.widgets import Static

_PHASE_LABELS = {
    "WORK": "WORK",
    "BREAK": "BREAK",
}
_ERROR_LABEL = "ERROR"


class TimerWidget(Static):
    DEFAULT_CSS = """
    TimerWidget {
        content-align: center middle;
        width: 100%;
        height: 100%;
    }
    """

    def refresh_state(self, remaining: int, phase: str) -> None:
        self.update(self.render_state(remaining, phase))

    @staticmethod
    def _figlet_block(text: str, font: str, gap: int = 2) -> list[str]:
        """Render text as rows using the given figlet font, one char at a time
        (avoids glyph fusion), with fully-blank rows stripped."""
        fig = pyfiglet.Figlet(font=font)
        char_lines = []
        height = None
        for ch in text:
            art = fig.renderText(ch).rstrip("\n").split("\n")
            if height is None:
                height = len(art)
            width = max(len(line) for line in art)
            char_lines.append([line.ljust(width) for line in art])

        spacer = " " * gap
        rows = [
            spacer.join(char_lines[i][row] for i in range(len(char_lines))) for row in range(height)
        ]
        return [row for row in rows if row.strip()]

    def render_state(self, remaining: int, phase: str, gap: int = 2) -> str:
        """Render remaining seconds (0-3599) plus a phase label as a
        figlet-style ASCII display: label on top, MM:SS clock below."""
        remaining = max(0, min(remaining, 59 * 60 + 59))
        minutes, seconds = divmod(remaining, 60)
        time_str = f"{minutes:02d}:{seconds:02d}"

        time_rows = self._figlet_block(time_str, font="colossal", gap=gap)

        label_text = _PHASE_LABELS.get(phase, _ERROR_LABEL)
        label_rows = self._figlet_block(label_text, font="small", gap=1)

        content_width = max(max(len(r) for r in time_rows), max(len(r) for r in label_rows))

        rows = [r.center(content_width) for r in label_rows]
        rows.append("")  # blank separator between label and time
        rows.extend(r.center(content_width) for r in time_rows)

        return "\n".join(rows)
