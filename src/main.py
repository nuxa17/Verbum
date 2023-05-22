import traceback
from tkinter.messagebox import showerror

from config import FROZEN, OS_SYSTEM
from controller.controller import Controller

if FROZEN and OS_SYSTEM == "Windows":
    import pyi_splash
    pyi_splash.close()


def main():
    try:
        Controller().run()
    except Exception as exc:
        traceback.print_exc()
        showerror("Error", f"{type(exc).__name__}: {exc}")


if __name__ == '__main__':
    main()
