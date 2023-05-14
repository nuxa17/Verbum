import traceback
from tkinter.messagebox import showerror

import pyi_splash

from controller.controller import Controller


def main():
    try:
        pyi_splash.close()
        app = Controller()
        app.run()
    except Exception as exc:
        traceback.print_exc()
        showerror("Error", f"{type(exc).__name__}: {exc}")


if __name__ == '__main__':
    main()
