import json
from pathlib import Path

STATE_FILE = Path("/tmp/pomodoro_state.json")


def read_state() -> tuple[int, str]:
    try:
        with STATE_FILE.open() as f:
            state = json.load(f)
        return (int(state["remaining"]), str(state["phase"]))
    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
        return (0, "ERROR")


def main():
    remaining, phase = read_state()

    remaining = max(0, min(remaining, 59 * 60 + 59))
    minutes, seconds = divmod(remaining, 60)
    time_str = f"{minutes:02d}:{seconds:02d}"

    if phase == "WORK":
        return_dict = {"text": "💻️ " + time_str, "tooltip": "work time remaining ", "class": ""}

    elif phase == "BREAK":
        return_dict = {"text": "🧘‍♂ " + time_str, "tooltip": "break time remaining ", "class": ""}

    else:
        return_dict = {"text": "‼️ ERROR", "tooltip": "try restarting the deamon", "class": ""}

    print(json.dumps(return_dict))


if __name__ == "__main__":
    main()
