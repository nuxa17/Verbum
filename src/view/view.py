"""View module.

This module stores the View class,
which manages different tasks like window geometry,
styling and frame changes.
"""
import re
from typing import TYPE_CHECKING, Any, Type
import tkinter as tk
from tkinter import ttk

from config import ICON_FILE, OS_SYSTEM
from view.custom_widgets import get_default_font
from view.popups import HelpPopup, ColorPopup, AboutPopup

if TYPE_CHECKING:
    from tkinter.font import Font


WINDOW_WIDTH  = 775
WINDOW_HEIGHT = 600


class View(tk.Tk):
    """
    View.

    This class manages the multiple view elements
    and their styles.
    """

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.wm_withdraw()
        self.ratio = 1 if OS_SYSTEM != 'Windows' else round(self.winfo_fpixels('1i'))/96

        self._width = WINDOW_WIDTH
        self._height = WINDOW_HEIGHT

        self.wm_title("Verbum")
        if OS_SYSTEM == "Windows":
            self.wm_iconbitmap(ICON_FILE)

        self.style = ttk.Style()
        self.saved_frames = {}
        self.current_frame = None
        self.focus_set()

        self._init_menu()
        self._init_fonts()
        self._init_style()

    def _init_menu(self):
        menubar = tk.Menu(self)
        self.configure(menu=menubar)

        #* View menu

        view_menu = tk.Menu(
            menubar,
            tearoff=0
        )
        mod_key = "Command" if OS_SYSTEM == "Darwin" else "Control"
        view_menu.add_command(
            label='Zoom up',
            accelerator=f"{mod_key}++",
            command=self._zoom_up_all
        )
        view_menu.add_command(
            label='Zoom down',
            accelerator=f"{mod_key}+-",
            command=self._zoom_down_all
        )
        self.bind(f"<{mod_key}-plus>", lambda e: self._zoom_up_all(), True)
        self.bind(f"<{mod_key}-minus>", lambda e: self._zoom_down_all(), True)
        self.bind(f"<{mod_key}-MouseWheel>",
            lambda e: self._zoom_up_all() if e.delta > 0 else self._zoom_down_all(),
            True
        )

        font_menu = tk.Menu(
            view_menu,
            tearoff=0
        )
        self.font_family = tk.StringVar()
        self.font_family.set("*Default*")
        font_menu.add_radiobutton(
            label="Default",
            variable=self.font_family,
            value="*Default*",
            command=lambda:self.configure_fonts(family="*Default*")
        )
        font_menu.add_radiobutton(
            label="Times New Roman",
            variable=self.font_family,
            value="Times New Roman",
            command=lambda:self.configure_fonts(family="Times New Roman")
        )
        font_menu.add_radiobutton(
            label="Comic Sans MS",
            variable=self.font_family,
            value="Comic Sans MS",
            command=lambda:self.configure_fonts(family="Comic Sans MS")
        )
        view_menu.add_cascade(menu=font_menu, label="Font")

        view_menu.add_command(
            label="Change colors",
            command=lambda:ColorPopup(self)
        )

        menubar.add_cascade(
            label="View",
            menu=view_menu,
            underline=0
        )

        #* Help menu

        help_menu = tk.Menu(
            menubar,
            tearoff=0
        )
        help_menu.add_command(
            label='This window',
            command=lambda: HelpPopup(self, help_text=self.current_frame.help_text())
        )
        help_menu.add_command(
            label='About...',
            command=lambda: AboutPopup(self)
        )
        menubar.add_cascade(
            label="Help",
            menu=help_menu,
            underline=0
        )

    def _init_fonts(self, font_size=9):
        font_size = max(7, font_size)
        self.font = get_default_font(size=font_size)
        self.font_tooltip = get_default_font(size=max(7, font_size-1))
        self.font_title = get_default_font(weight='bold', slant='italic', size=font_size+4)
        self.font_subtitle = get_default_font(slant='italic', size=font_size+4)
        self.font_i = get_default_font(slant='italic', size=font_size)
        self.font_b = get_default_font(weight='bold', size=font_size)
        self.font_u = get_default_font(underline=True, size=font_size)
        self.font_bu = get_default_font(weight='bold', underline=True, size=font_size)
        self.font_biu = get_default_font(weight='bold', slant='italic', underline=True, size=font_size+1)
        self.fonts = [
            self.font, self.font_tooltip, self.font_title,
            self.font_subtitle, self.font_i, self.font_b,
            self.font_u, self.font_bu, self.font_biu
        ]

    def _init_style(self):
        self.style.configure("TCheckbutton",font=self.font)
        self.style.configure("TButton",font=self.font)
        self.style.configure("TLabelframe.Label",font=self.font)
        self.style.configure("Treeview",font=self.font)
        self.style.configure("Treeview.Heading",font=self.font)
        self.style.configure("Treeview",rowheight=self.font.metrics('linespace'))
        self.style.configure("Treeview",font=self.font)
        self.style.configure("TNotebook.Tab",font=self.font)
        self.option_add('*TCombobox*Listbox.font', self.font)

    #************
    #*  Window  *
    #************

    def get_unscaled_geometry(self):
        # type: () -> str
        """Get the unscaled geometry of the window."""
        self.update_idletasks()

        geometry = re.split(r'[x+]', self.wm_geometry())
        geometry[0] = str(float(geometry[0]) / self.ratio)
        geometry[1] = str(float(geometry[1]) / self.ratio)

        return geometry[0]+"x"+ "+".join(geometry[1:])

    def set_geometry(self, geometry=None, state=0):
        # type: (str, int) -> None
        """
        Set geometry of the window and its state.

        Args:
            `geometry` (optional): Geometry of the window.
            If None, the default geometry will be used.

            `state` (optional): State of the window.
            0 -> normal; 1 -> zoomed; 2 -> fullscreen.
            Defaults to 0.
        """
        try:
            if geometry and state == 0:
                geometry = re.split(r'[x+]',geometry)
                if (len(geometry) == 4
                    and self.winfo_screenwidth() > float(geometry[0]) > 0
                    and self.winfo_screenheight() > float(geometry[1]) > 0
                ):
                    self._width = float(geometry[0])
                    self._height = float(geometry[1])
        except ValueError:
            print("Geometry is not valid. Restoring default values.")

        scaled_w = int(self._width*self.ratio)
        scaled_h = int(self._height*self.ratio)

        x = int((self.winfo_screenwidth() / 2) -
                (scaled_w / 2))
        y = int((self.winfo_screenheight() / 2) -
                (scaled_h / 2))

        self.wm_geometry(f'{scaled_w}x{scaled_h}+{x}+{y}')
        self.wm_minsize(int(200*self.ratio), int(200*self.ratio))
        if OS_SYSTEM != "Darwin":
            self.update_idletasks()

        self.set_state(state)

    def get_state(self):
        # type: () -> int
        """
        Return the current window state.

        States of the window: 0 -> normal; 1 -> zoomed; 2 -> fullscreen.
        """
        if self.wm_attributes("-fullscreen",) == 1:
            return 2
        return 1 if self.state() == "zoomed" else 0

    def set_state(self, state):
        # type: (int) -> None
        """
        Set state of the window.
        Otherwise, return the current state.

        States of the window: 1 -> zoomed; 2 -> fullscreen; other -> normal.
        """

        match state:
            case 1:
                self.state("zoomed")
            case 2:
                self.wm_attributes("-fullscreen", 1)
            case _:
                self.state("normal")

    def destroy(self):
        self.event_generate("<<WinDestroy>>")
        tk.Tk.destroy(self)

    #************
    #*  Frames  *
    #************

    def create_frame(self, frameclass, keep=False, **kw):
        # type: (Type[ttk.Frame], bool, Any) -> ttk.Frame
        """
        Create new `frameclass` object. If `keep` is `True`,
        the frame will be saved, avoiding destruction after changing it.
        Frame's initialization variables can be passed by.
        """
        frame = frameclass(self, **kw)
        if keep:
            self.saved_frames[frameclass.__name__] = frame
        if not self.current_frame:  # only for the first frame
            self.current_frame = frame
        return frame

    def change_frame(self, frame):
        # type: (ttk.Frame|str) -> None
        """
        Change visible main frame. If `frame` is a string,
        a frame of that class must have been created and saved.
        """
        if isinstance(frame, str):
            frame = self.saved_frames[frame]

        frame.pack(fill='both', expand=True)
        if self.current_frame.__class__.__name__ in self.saved_frames:
            self.current_frame.pack_forget()
        else:
            self.current_frame.destroy()
        self.current_frame = frame

    #***********
    #*  Fonts  *
    #***********

    def new_font(self):
        # type: () -> Font
        """
        Create a copy of `self.font`. This copy's configuration
        will change with the rest of the fonts.
        """
        font = self.font.copy()
        self.fonts.append(font)
        return font

    def remove_font(self, font):
        # type: (Font) -> None
        """Unbind font from this view."""
        self.fonts.remove(font)

    def configure_fonts(self, **options):
        # type: (Any) -> None
        """Change configuration values of all fonts."""

        if "size" in options:
            size = options["size"] - self.font["size"]
            if size > 0:
                self._zoom_up_all(size=size)
            else:
                self._zoom_down_all(size=-size)
            options.pop("size")

        if "family" in options:
            self.font_family.set(options["family"])
            if options["family"] == "*Default*":
                options["family"] = get_default_font().cget('family')

        for font in self.fonts:
            font.config(**options)

    def _zoom_up_all(self, size=1):
        if self.font["size"] <30:
            for font in self.fonts:
                font.configure(size=font["size"]+size)
        self.event_generate("<<ZoomUp>>")
        self.style.configure("Treeview", rowheight=self.font.metrics('linespace'))
        self.event_generate("<<TSUpdate>>")

    def _zoom_down_all(self, size=1):
        if self.font["size"]>7:
            for font in self.fonts:
                font.configure(size=font["size"]-size)
        self.event_generate("<<ZoomDown>>")
        self.style.configure("Treeview", rowheight=self.font.metrics('linespace'))
        self.event_generate("<<TSUpdate>>")
