import time
from enum import Enum, auto


class TimerStatus(Enum):
    NOT_STARTED = auto()
    RUNNING = auto()
    PAUSED = auto()


class Phase(Enum):
    WORK = auto()
    BREAK = auto()


class Timer:
    def __init__(self, pomo=1800, break_time=300) -> None:
        self.pomo_duration: int = pomo
        self.break_duration: int = break_time

        self.status: TimerStatus = TimerStatus.NOT_STARTED
        self.phase: Phase = Phase.WORK

        self._end_time: float | None = None  # timestamp, only meaningful while RUNNING
        self._remaining: int = (
            self.pomo_duration
        )  # snapshot, only meaningful while NOT running

    def start(self):
        if self.status == TimerStatus.NOT_STARTED:
            self._end_time = time.time() + self._remaining
            self.status = TimerStatus.RUNNING

    def pause(self):
        if self.status == TimerStatus.RUNNING:
            self._remaining = round(self._end_time - time.time())
            self.status = TimerStatus.PAUSED

    def resume(self):
        if self.status == TimerStatus.PAUSED:
            self._end_time = time.time() + self._remaining
            self.status = TimerStatus.RUNNING

    @property
    def remaining(self) -> int:
        if self.status == TimerStatus.RUNNING:
            return max(0, round(self._end_time - time.time()))
        return self._remaining

    def check_phase_complete(self) -> bool:
        if self.remaining <= 0:
            return True

        return False

    def advance_phase(self):
        if self.check_phase_complete() == True:
            if self.phase == Phase.WORK:
                self.phase == Phase.BREAK
                self._remaining = self.break_duration
                self.status = TimerStatus.NOT_STARTED

            if self.phase == Phase.BREAK:
                self.phase == Phase.WORK
                self._remaining = self.pomo_duration
                self.status = TimerStatus.NOT_STARTED
