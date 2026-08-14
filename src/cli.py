import sys

from tui.socket import send_command


def main():

    if len(sys.argv) == 1:
        print("ERROR: no command was given")
        return

    command = sys.argv[1]

    print(send_command(command))


if __name__ == "__main__":
    main()
