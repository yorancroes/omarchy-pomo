import tomllib
from pathlib import Path

from textual.theme import Theme

COLORS_PATH = Path.home() / ".config/omarchy/current/theme/colors.toml"


def load_omarchy_theme() -> Theme | None:
    """Build a Textual Theme from the current Omarchy color scheme.

    Returns None if Omarchy isn't installed or the palette can't be read,
    so callers can fall back to a default Textual theme.
    """
    try:
        with COLORS_PATH.open("rb") as f:
            colors = tomllib.load(f)
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        return None

    try:
        return Theme(
            name="omarchy",
            background=colors["background"],
            foreground=colors["foreground"],
            accent=colors["accent"],
            primary=colors["color4"],
            secondary=colors["color5"],
            error=colors["color1"],
            warning=colors["color3"],
            success=colors["color2"],
            panel=colors["color8"],
            surface=colors["color0"],
            dark=True,
        )
    except KeyError:
        return None
