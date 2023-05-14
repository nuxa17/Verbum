import os
from queue import Queue
import tkinter as tk
from tkinter import ttk, END

from tktooltip import ToolTip

from config import OS_SYSTEM, MANUAL_FILE
from view.custom_widgets import EmptyCheckbutton
from view.popups import HelpPopup

class TextFrame(ttk.Frame):

    def __init__(self, view, **kw):
        if "master" in kw:
            master = kw["master"]
            kw.pop("master")
        else: master=view
        ttk.Frame.__init__(self, master, **kw)

        self.view = view

        self.text_panel_frame = ttk.Frame(self)
        self.text_panel_frame.configure(height=40, width=550)

        self.text_panel = tk.Text(self.text_panel_frame, padx=5, pady=5)
        self.panel_font = self.view.new_font()
        self.text_panel.configure(
            font=self.panel_font,
            setgrid="false",
            takefocus=False,
            wrap="word")
        scroll = ttk.Scrollbar(self.text_panel_frame,command=self.text_panel.yview)
        self.text_panel['yscrollcommand'] = scroll.set
        self.text_panel.grid(column=1, row=0, rowspan=5, padx=(10,0), sticky="nsew")
        scroll.grid(column=2, row=0, rowspan=5, sticky="nsew")

        self.settings_chk = ttk.Labelframe(self.text_panel_frame)
        self.settings_chk.configure(
            labelanchor="n",
            text='Settings',
            width=200)
        self.chk_clean_words = EmptyCheckbutton(self.settings_chk)
        self.chk_clean_words.configure(text=' Letters only ')
        self.chk_clean_words.grid(column=0, padx=15, row=0, sticky="w")
        self.chk_decontract = EmptyCheckbutton(self.settings_chk)
        self.chk_decontract.configure(text=' Decontract ', command=self.alternate_chk)
        self.chk_decontract.grid(column=0, padx=15, row=1, sticky="w")
        self.chk_promising_contr = EmptyCheckbutton(self.settings_chk)
        self.chk_promising_contr.configure(text=' Promising contractions ')
        self.chk_promising_contr.grid(column=0, padx=15, row=2, sticky="w")
        self.chk_tags = EmptyCheckbutton(self.settings_chk)
        self.chk_tags.configure(text=' Match tags ')
        self.chk_tags.grid(column=0, padx=15, pady=(0,5), row=3, sticky="w")
        self.settings_chk.grid(
            column=0,
            ipady=15,
            pady=(0,20),
            row=1,
            sticky="new")
        self.settings_chk.rowconfigure("all", weight=1)
        self.settings_chk.columnconfigure("all", weight=1)

        self.excel_chk = ttk.Labelframe(self.text_panel_frame)
        self.excel_chk.configure(
            labelanchor="n",
            text='Analysis',
            width=200)
        self.chk_ngrams = EmptyCheckbutton(self.excel_chk)
        self.chk_ngrams.configure(text=' Search collocations ')
        self.chk_ngrams.grid(column=0, padx=15, row=0, sticky="w")
        self.chk_sentiment = EmptyCheckbutton(self.excel_chk)
        self.chk_sentiment.configure(text=' Sentiment ')
        self.chk_sentiment.grid(column=0, padx=15, pady=(0,5), row=1, sticky="w")
        self.excel_chk.grid(
            column=0,
            ipady=10,
            pady=(0,20),
            row=2,
            sticky="new")
        self.excel_chk.rowconfigure("all", weight=1)
        self.excel_chk.columnconfigure("all", weight=1)

        self.intro_frame = ttk.Frame(self.text_panel_frame)
        self.intro_frame.configure(height=150, width=200)
        label2 = ttk.Label(self.intro_frame)
        label2.configure(
            anchor="center",
            justify="center",
            font=self.view.font_biu,
            text='Information')
        label2.grid(column=0, row=0, sticky="enw", pady=(0,10))
        ttk.Label(self.intro_frame,
            anchor="center",
            justify="center",
            font=self.view.font_u,
            text='Tagger: ').grid(column=0, row=1, sticky="enw")
        ttk.Label(self.intro_frame,
            anchor="center",
            justify='center',
            font=self.view.font,
            text='MaxEntTreeBank').grid(column=0, row=2, sticky="enw")
        ttk.Label(self.intro_frame,
            anchor="center",
            justify='center',
            font=self.view.font_u,
            text='Sentiment:').grid(column=0, row=3, sticky="enw")
        ttk.Label(self.intro_frame,
            anchor="center",
            justify='center',
            font=self.view.font,
            text='TextBlob, VADER').grid(column=0, row=4, sticky="enw")
        ttk.Label(self.intro_frame,
            anchor="center",
            justify='center',
            font=self.view.font_u,
            text='Tokenizer:').grid(column=0, row=5, sticky="enw")
        ttk.Label(self.intro_frame,
            anchor="center",
            justify='center',
            font=self.view.font,
            text='Modified Whitespace').grid(column=0, row=6, sticky="enw")

        self.intro_frame.grid(column=0, row=0, sticky="new")
        self.intro_frame.columnconfigure("all", weight=1)

        self.open_button = ttk.Button(self.text_panel_frame)
        self.open_button.configure(text='Load text file')
        if OS_SYSTEM != "Darwin":
            self.open_button.configure(width=13)
        self.open_button.grid(column=0, pady=10, row=3)

        self.zoom_text_frame = ttk.Frame(self.text_panel_frame)
        self.zoom_text_frame.configure(width=10)
        self.zoom_up_btn = ttk.Button(self.zoom_text_frame)
        self.zoom_up_btn.configure(text='+', command=self._zoom_up_scrolledtext)
        if OS_SYSTEM != "Darwin":
            self.zoom_up_btn.configure(width=6)
        else:
            self.zoom_up_btn.configure(width=1)
        self.zoom_up_btn.grid(column=1, row=0)
        self.zoom_down_btn = ttk.Button(self.zoom_text_frame)
        self.zoom_down_btn.configure(text='-', command=self._zoom_down_scrolledtext)
        if OS_SYSTEM != "Darwin":
            self.zoom_down_btn.configure(width=6)
        else:
            self.zoom_down_btn.configure(width=1)
        self.zoom_down_btn.grid(column=0, row=0)
        self.zoom_text_frame.grid(column=0, row=4)
        self.text_panel_frame.grid(column=0, padx=20, pady=(10,0), row=0, sticky="nsew")
        self.text_panel_frame.rowconfigure(0, weight=1)
        self.text_panel_frame.columnconfigure(0, minsize=260)
        self.text_panel_frame.columnconfigure(1, weight=1)
        self.botones_abajo = ttk.Frame(self)
        self.next_button = ttk.Button(self.botones_abajo)
        self.next_button.configure(state="disabled", text='Next')
        if OS_SYSTEM != "Darwin":
            self.next_button.configure(width=10)
        self.next_button.grid(column=2, row=0)

        self.info_label = ttk.Label(self.botones_abajo)
        self.info_var = tk.StringVar()
        self.info_label.configure(
            anchor="center",
            justify="center",
            font=self.view.font,
            text='',
            textvariable=self.info_var)
        self.info_label.grid(column=1, row=0)
        label4 = ttk.Label(self.botones_abajo)
        label4.grid(column=0, row=0)
        self.botones_abajo.grid(column=0, pady=15, row=1, sticky="ews")
        self.botones_abajo.columnconfigure("all",weight=1, uniform=1)
        self.pack(expand="true", fill="both")
        self.grid_propagate(0)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._info_queue = Queue()
        self.bind("<<UpdateInfo>>", self._update_info, True)
        self.text_panel.bind("<KeyRelease>", lambda e:self.text_trace(),True)
        self.funcid_down = self.view.bind("<<ZoomDown>>", lambda e:self._zoom_down_scrolledtext(size=0),True)
        self.funcid_up = self.view.bind("<<ZoomUp>>", lambda e:self._zoom_up_scrolledtext(size=0),True)

        self.tooltips()
        self.open_button.focus_set()

    def tooltips(self):
        ToolTip(self.chk_clean_words,
            msg="RECOMMENDED: Removes any non-alphabetic\ncharacter except apostrophes",
            delay=0.25, font=self.view.font_tooltip
        )
        ToolTip(self.chk_decontract,
            msg="RECOMMENDED: Expands contractions",
            delay=0.25, font=self.view.font_tooltip
        )
        ToolTip(self.chk_promising_contr,
            msg="If uncertain, takes the best guess\nfor a contraction",
            delay=0.25, font=self.view.font_tooltip
        )        
        ToolTip(self.chk_tags,
            msg="Use word classes for better matching",
            delay=0.25, font=self.view.font_tooltip
        )
        ToolTip(self.chk_ngrams,
            msg="Check n-grams after analysis",
            delay=0.25, font=self.view.font_tooltip
        )
        ToolTip(self.chk_sentiment,
            msg="Analize sentiment of text",
            delay=0.25, font=self.view.font_tooltip
        )

    def help_text(self):
        help_text = HelpPopup.HelpText("Help")

        help_text.body.append(
            "This is the main page, where\n\
            you can write/select a text\nand set its analysis options."
        )

        help_text.url = 'file://' + os.path.realpath(MANUAL_FILE) + "#Principal"

        return help_text

    def set_all(self, disabled=False):
        option = tk.DISABLED if disabled else tk.NORMAL

        self.chk_clean_words['state'] = option
        self.chk_decontract['state'] = option
        self.chk_tags['state'] = option
        self.chk_ngrams['state'] = option
        self.chk_sentiment['state'] = option
        self.open_button['state'] = option
        self.text_panel['state'] = option
        self.next_button['state'] = option
        self.zoom_up_btn['state'] = option
        self.zoom_down_btn['state'] = option

        if disabled:
            self.chk_promising_contr['state'] = option
        else:
            self.alternate_chk()

    def get_settings(self):
        return {
            "textfont": self.panel_font["size"],
            "clean_words": self.chk_clean_words.var.get(),
            "decontract": self.chk_decontract.var.get(),
            "promising_contr": self.chk_promising_contr.var.get(),
            "tags": self.chk_tags.var.get(),
            "ngrams": self.chk_ngrams.var.get(),
            "sentiment": self.chk_sentiment.var.get()
        }

    def set_settings(self, settings):
        self.panel_font["size"] = settings["textfont"]

        self.chk_clean_words.var.set(settings["clean_words"])
        self.chk_decontract.var.set(settings["decontract"])
        self.chk_promising_contr.var.set(settings["promising_contr"])
        self.chk_tags.var.set(settings["tags"])
        self.chk_ngrams.var.set(settings["ngrams"])
        self.chk_sentiment.var.set(settings["sentiment"])
        
        self.alternate_chk()

    def alternate_chk(self):
        if self.chk_decontract.var.get():
            self.chk_promising_contr['state'] = tk.NORMAL
        else:
            self.chk_promising_contr['state'] = tk.DISABLED

    def text_trace(self):
        if self.text_panel['state'] == tk.NORMAL:
            if len(self.text_panel.get("1.0", "end-1c").split()) == 0:
                state = tk.DISABLED
            else:
                state = tk.NORMAL
            self.next_button.configure(state=state)

    def _zoom_up_scrolledtext(self, size=1):
        top = 30
        if self.panel_font["size"] < top:
            self.panel_font["size"] += size
        else:
            self.panel_font["size"] = top

        if self.panel_font["size"] == top:
            self.zoom_up_btn.configure(state="disabled")

        if 'disabled' in self.zoom_down_btn.state():
            self.zoom_down_btn.configure(state="normal", default="normal")

    def _zoom_down_scrolledtext(self, size=1):
        bottom = 7
        if self.panel_font["size"] > bottom:
            self.panel_font["size"] -= size
        else:
            self.panel_font["size"] = bottom

        if self.panel_font["size"] == bottom:
            self.zoom_down_btn.configure(state="disabled")

        if 'disabled' in self.zoom_up_btn.state():
            self.zoom_up_btn.configure(state="normal", default="normal")

    def get_text(self):
        return self.text_panel.get("1.0", "end-1c")

    def set_text(self, text):
        self.text_panel.delete("1.0", "end")
        self.text_panel.insert(END, text)
        self.text_trace()

    def update_info(self, message):
        self._info_queue.put(message)
        self.event_generate("<<UpdateInfo>>")

    def _update_info(self, e):
        self.info_var.set(self._info_queue.get())
        self.info_label.update()

    def destroy(self):
        self.view.unbind("<<ZoomDown>>",self.funcid_down)
        self.view.unbind("<<ZoomUp>>",self.funcid_up)
        tk.Frame.destroy(self)
