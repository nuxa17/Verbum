import traceback
from tkinter.messagebox import showerror

from controller.controller import Controller


def main():
    try:
        Controller().run()
    except Exception as exc:
        traceback.print_exc()
        showerror("Error", f"{type(exc).__name__}: {exc}")


if __name__ == '__main__':
    main()
