import time
from src.timer import Timer

if __name__ == "__main__":
    timer = Timer(pomo=20, break_time=5)
    timer.start()

    while True:
        timer.print()
        print("sleeping for 3 seconds...")
        time.sleep(3)

        if timer.check_phase_complete():
            timer.advance_phase()
            timer.print()
            print("sleeping for 3 seconds...")
            time.sleep(3)
            timer.start()
