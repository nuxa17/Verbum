"""Popups module.

This module provides different popups and a
base class for customization.
"""
import tkinter as tk
from tkinter import ttk
from tkinter.colorchooser import askcolor
from dataclasses import dataclass, field
import webbrowser

from tktooltip import ToolTip

from config import OS_SYSTEM, ICON_FILE, MANUAL_FILE, REPO_LINK
from view.custom_widgets import EmptyCheckbutton
from utils.color import ColorGenerator


class BasePopup(tk.Toplevel):
    """
    Centered TopLevel template.
    Override the `_init_widgets` method with your
    widgets initialization's method.

    Contains a `_callback` method for opening an url.
    """
    def __init__(self, master, view=None, title="", cnf=None, **kw):
        cnf = cnf if cnf else {}
        tk.Toplevel.__init__(self, master, cnf, **kw)
        self.view = view if view else master
        self.res = None
        self.attributes('-alpha', 0.0)

        self.title(title)
        if OS_SYSTEM == "Windows":
            self.iconbitmap(ICON_FILE)
        self.configure(padx=25, pady=10)

        self._init_widgets()

        self.resizable(False, False)
        self.geometry("")
        self.update_idletasks()
        self._keep_ratio()
        self.deiconify()
        self.focus()
        self.grab_set()
        self.attributes('-alpha', 1.0)
        self.update()

    def _init_widgets(self):
        pass

    def _keep_ratio(self):
        ratio = self.winfo_width() / self.winfo_height()
        width = self.winfo_width()
        height = int(width / ratio)
        x = int((self.winfo_screenwidth() / 2) -
                (width / 2))
        y = int((self.winfo_screenheight() / 2) -
                (height / 2))
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _callback(self, url):
        webbrowser.open(url, autoraise=True)


class SavePopup(BasePopup):
    """
    Save popup window.
    
    Use the attribute `saved` for save management.

    Buttons:
    - `save_btn`: Save command.
    """
    def __init__(self, master, settings, view=None, cnf=None, **kw):
        self.settings = settings
        self.saved = False
        super().__init__(master, view=view, title="Settings", cnf=cnf, **kw)

    def _init_widgets(self):
        ttk.Label(self, text="Saving Options",
                  font=self.view.font_bu).pack(pady=(0, 10))

        self.chk_save_tags = EmptyCheckbutton(
            self, text=' Save tags ', value=self.settings["save_tags"]
        )
        self.chk_save_tags.configure(command=self._alternate_chk)
        self.chk_save_tags.pack(anchor='w')

        self.chk_decoded_tags = EmptyCheckbutton(
            self, text=' Decoded tags ',
            value=self.settings["decoded_tags"]
        )
        self.chk_decoded_tags.pack(anchor='w')

        self.chk_unmatched = EmptyCheckbutton(
            self, text=' Include unmatched patterns ',
            value=self.settings["unmatched"]
        )
        self.chk_unmatched.pack(anchor='w')

        self.chk_graphs_on_excel = EmptyCheckbutton(
            self, text=' Save sentiment graphs on Excel ',
            value=self.settings["graphs_on_excel"]
        )
        self.chk_graphs_on_excel.pack(anchor='w')

        if not self.settings["sentiment"]:
            self.chk_graphs_on_excel.config(state="disabled")

        self._alternate_chk()

        self.save_btn = ttk.Button(self, text="Save")
        self.save_btn.pack(pady=(20, 10))

        self._tooltips()

    def _tooltips(self):
        ToolTip(self.chk_save_tags,
                msg="Include tags of the patterns and results",
                delay=0.25, font=self.view.font_tooltip)

        ToolTip(self.chk_decoded_tags,
                msg="Use grammatical classes instead\nof part-of-speech tags",
                delay=0.25, font=self.view.font_tooltip)

        ToolTip(self.chk_unmatched,
                msg="Include patterns without results",
                delay=0.25, font=self.view.font_tooltip)

        ToolTip(self.chk_graphs_on_excel,
                msg="Include sentiment graphs\non the report",
                delay=0.25, font=self.view.font_tooltip)

    #**************
    #*  Settings  *
    #**************

    def get_settings(self):
        """
        Get configuration settings.

        Returns:
            `dict[str, bool]`: Settings.
        """
        return {
            "save_tags": self.chk_save_tags.var.get(),
            "unmatched": self.chk_unmatched.var.get(),
            "graphs_on_excel": self.chk_graphs_on_excel.var.get(),
            "decoded_tags": self.chk_decoded_tags.var.get()
        }

    #*************************
    #*  Internal management  *
    #*************************

    def _alternate_chk(self):
        if self.chk_save_tags.var.get():
            self.chk_decoded_tags['state'] = tk.NORMAL
        else:
            self.chk_decoded_tags['state'] = tk.DISABLED


class HelpPopup(BasePopup):
    """Generic Help popup.

    Implements a HelpText class for information management.    
    """
    @dataclass
    class HelpText:
        """
        Dataclass for information management.

        Attributes:
            `header`: Text displayed on the window bar.
            Defaults to "Help".

            `body`: List of strings composing the text, each of them
            being a new line. The last item will be the text
            for the url.
            Defaults to an empty list.
            
            `url`: url for the help page.
            Defaults to "http://www.python.org".
        """
        header: str = "Help"
        body: list[str] = field(default_factory=lambda: [])
        url: str = r"http://www.python.org"

    def __init__(self, master, view=None, help_text=None, cnf=None, **kw):
        self.help_text = help_text if help_text else self.HelpText()
        super().__init__(master, view=view, title=help_text.header, cnf=cnf, **kw)

    def _init_widgets(self):
        ttk.Label(self, text=self.help_text.header,
                  font=self.view.font_bu).pack(pady=10)

        if not self.help_text.body:
            return

        for line in self.help_text.body:
            ttk.Label(self,
                      justify="center",
                      text=line, font=self.view.font,
                      ).pack(pady=(0, 10))

        lbl = tk.Label(self,
                       justify="center",
                       text="Open Manual", font=self.view.font_u,
                       foreground="blue", cursor="hand2"
                       )
        lbl.pack(pady=(5, 15))
        lbl.bind("<Button-1>", lambda e: self._callback(self.help_text.url))


class ColorPopup(BasePopup):
    """
    Color gradient selector popup.
    """
    def __init__(self, master, view=None, cnf=None, **kw):
        super().__init__(master, view=view, title="Change colors", cnf=cnf, **kw)

    def _init_widgets(self):
        self.gradientframe = tk.Frame(self)
        self.gradientframe.grid(
            row=0, column=0, columnspan=3, sticky='ewn', pady=(0, 15))

        self._update_gradient(event=False)

        self.change_first = ttk.Button(self,
                text = "First color",
                command = lambda: self._select_color(first=True)
            )
        self.change_first.grid(row=1, column=0, padx=(0, 10))

        self.reset = ttk.Button(self,
                text = "Reset colors",
                command = lambda: self._update_gradient(reset=True)
            )
        self.reset.grid(row=1, column=1, padx=10)

        self.change_last = ttk.Button(self,
                text = "Last color",
                command = lambda: self._select_color(first=False)
            )
        self.change_last.grid(row=1, column=2, padx=(10, 0))

    def _select_color(self, first=True, default=None):
        if not default:
            gradient = ColorGenerator.get_gradient()
            default = gradient[0] if first else gradient[-1]

        new_color = askcolor(color=default)[0]
        if not new_color:
            return

        if first:
            ColorGenerator.generate_gradient(first=new_color)
        else:
            ColorGenerator.generate_gradient(last=new_color)

        self._update_gradient()

    def _update_gradient(self, reset=False, event=True):
        if reset is False:
            colors = ColorGenerator.get_gradient()
        else:
            colors = ColorGenerator.reset_gradient()

        for label in self.gradientframe.children.values():
            label.pack_forget()

        for idx, color in enumerate(colors):
            foreground = ColorGenerator.best_foreground(color)
            label = tk.Label(self.gradientframe, text=str(idx), font=self.view.font_b,
                             anchor="center", background=color, foreground=foreground)
            label.pack(side="left", fill='both', expand=True)

        if event:
            self.view.event_generate("<<ColorChanged>>")


class AboutPopup(BasePopup):
    """
    About popup.
    """
    def __init__(self, master, view=None, cnf=None, **kw):
        super().__init__(master, view=view, title="Verbum", cnf=cnf, **kw)

    def _init_widgets(self):
        ttk.Label(self,
            text="VERBUM V1.0",
            font=self.view.font_biu
        ).pack(pady=10)

        ttk.Label(self,
            anchor="center",
            justify='center',
            font=self.view.font,
            text='Made by Alessandro de Armas\nand Juan Pablo Corella.'
        ).pack(pady=5)

        ttk.Label(self,
            anchor="center",
            justify='center',
            font=self.view.font,
            text='Powered by nltk, TextBlob and more!'
        ).pack(pady=5)

        manual_lb = tk.Label(self,
                justify="center",
                text="Full Manual", font=self.view.font_u,
                foreground="blue", cursor="hand2"
            )
        manual_lb.pack(pady=5)
        manual_lb.bind(
            "<Button-1>",
            lambda e: self._callback('file://' + os.path.realpath(MANUAL_FILE))
        )

        credits_lbl = tk.Label(self,
                justify="center",
                text="GitHub", font=self.view.font_u,
                foreground="blue", cursor="hand2"
            )
        credits_lbl.pack(pady=(0, 10))
        import os
        credits_lbl.bind(
            "<Button-1>",
            lambda e: self._callback(REPO_LINK)
        )
