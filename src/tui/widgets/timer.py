import pyfiglet
from textual.widgets import Static


class TimerWidget(Static):
    def render_time(self, remaining: int, gap: int = 2) -> str:
        """Render remaining seconds (0-3599) as a bordered, figlet-style MM:SS clock."""
        remaining = max(0, min(remaining, 59 * 60 + 59))
        minutes, seconds = divmod(remaining, 60)
        time_str = f"{minutes:02d}:{seconds:02d}"

        fig = pyfiglet.Figlet(font="colossal")

        char_lines = []
        height = None
        for ch in time_str:
            art = fig.renderText(ch).rstrip("\n").split("\n")
            if height is None:
                height = len(art)
            width = max(len(line) for line in art)
            char_lines.append([line.ljust(width) for line in art])

        spacer = " " * gap
        rows = [
            spacer.join(char_lines[i][row] for i in range(len(char_lines))) for row in range(height)
        ]

        rows = [row for row in rows if row.strip()]

        width = max(len(row) for row in rows)
        rows = [row.ljust(width) for row in rows]

        top = "┌" + "─" * (width + 2) + "┐"
        bottom = "└" + "─" * (width + 2) + "┘"
        body = [f"│ {row} │" for row in rows]

        return "\n".join([top] + body + [bottom])


if __name__ == "__main__":
    print(TimerWidget().render_time(125))
