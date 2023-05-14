"""Results Frames.

This module provides frames for showing the different analysis' results.
This includes MultiFrame, whitch handles the frames using tabs.
"""

import traceback
import os
from copy import deepcopy
from queue import Queue

import tkinter as tk
from tkinter import ttk, StringVar, Frame

from tkscrolledframe import ScrolledFrame
from tktooltip import ToolTip

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from config import OS_SYSTEM, MANUAL_FILE
from view.custom_widgets import EntryScrollX, NumericEntry, EmptyCheckbutton, TreeviewScroll
from view.popups import HelpPopup
from utils.color import ColorGenerator


class MultiFrame(ttk.Frame):
    def __init__(self, view, name='mf', **kw):
        if "master" in kw:
            master = kw["master"]
            kw.pop("master")
        else: master=view
        ttk.Frame.__init__(self, master, name=name, **kw)

        self.view = view

        self.tab_names = []
        self.current = None

        self.notebook = ttk.Notebook(self, name='nb')
        self.notebook.grid(column=0, padx=9, pady=(5,0), row=0, sticky="news")
        self.notebook.bind('<<NotebookTabChanged>>', self._change_tab)

        botones_abajo = ttk.Frame(self)
        self.back_button = ttk.Button(botones_abajo, text='Back')
        if OS_SYSTEM != "Darwin":
            self.back_button.configure(width=10)
        self.back_button.grid(row=0, column=0)

        self.info_label = tk.Label(botones_abajo)
        self.info_var = tk.StringVar()
        self.info_label.configure(
            anchor="center",
            justify="center",
            font=self.view.font,
            text='',
            textvariable=self.info_var)
        self.info_label.grid(column=1, row=0)

        self.save_button = ttk.Button(botones_abajo, text='Save')
        if OS_SYSTEM != "Darwin":
            self.save_button.configure(width=10)
        self.save_button.grid(row=0, column=2)
        botones_abajo.grid(column=0, pady=15, row=1, sticky="ews")
        botones_abajo.columnconfigure("all",weight=1, uniform=1)

        self._info_queue = Queue()
        self.bind("<<UpdateInfo>>", self._update_info, True)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def help_text(self):
        return self.notebook.nametowidget(self.notebook.select()).help_text()

    def set_all(self, disabled=False):
        option = tk.DISABLED if disabled else tk.NORMAL

        self.save_button['state'] = option
        self.back_button['state'] = option

        current = self.notebook.nametowidget(self.notebook.select())
        if hasattr(current, "set_all") and callable(current.set_all):
            current.set_all(disabled=disabled)

    def add_frame(self, frame):
        self.notebook.add(frame, sticky='nswe', text=frame.alias)
        self.tab_names.append(frame.alias)
        frame.master = self.notebook
    
    def tabs(self):
        return self.tab_names
    
    def _change_tab(self, e):
        self.notebook.nametowidget(self.notebook.select()).event_generate('<<Selected>>')

    def update_info(self, message):
        self._info_queue.put(message)
        self.event_generate("<<UpdateInfo>>")

    def _update_info(self, e):
        self.info_var.set(self._info_queue.get())
        self.info_label.update()


class GraphsFrame(ttk.Frame):
    def __init__(self, view, name="sentiment", **kw):
        if "master" in kw:
            master = kw["master"]
            kw.pop("master")
        else: master=view
        ttk.Frame.__init__(self, master, name=name,**kw)

        self.view = view

        self.alias = "Sentiment"
        self._drawn = False
        self._after_id = ''
        self._still = False

        self._fig = None
        self._canvas = None
        self._dtr_id = None

    class myToolbar(NavigationToolbar2Tk):
        def __init__(self, canvas, window=None, pack_toolbar=True):
            NavigationToolbar2Tk.__init__(self, canvas, window=window, pack_toolbar=pack_toolbar)
            self._buttons["Home"].pack_forget()
            self._buttons["Subplots"].pack_forget()

    def set_graphs(self, fig: Figure):
        self._canvas = FigureCanvasTkAgg(fig, self)
        self._fig = fig

        self._update_colors()
        self.view.bind('<<ColorChanged>>', lambda e: self._update_colors(), True)
        self._dtr_id = self.view.bind('<<WinDestroy>>', lambda e: self._destroy_with_fig(), True)

        toolbar = self.myToolbar(self._canvas, self, pack_toolbar=False)
        toolbar.update()

        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.bind('<<Selected>>', lambda e: self.show_graphs() if not self._drawn else None)
        self._canvas.get_tk_widget().bind('<Configure>', self._slow_update)

    def _slow_update(self, event):
        if self._after_id != '':
            self._canvas.get_tk_widget().after_cancel(self._after_id)

        self._after_id = self._canvas.get_tk_widget().after(200, lambda:self._update(event))

    def _update(self,event):

        event.height=self._canvas.get_tk_widget().winfo_height()
        event.width=self._canvas.get_tk_widget().winfo_width()
        self._canvas.resize(event) # Don't worry, it's okay
        self._after_id = ''

    def show_graphs(self):
        self._drawn = True
        self._canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._canvas.get_tk_widget().update_idletasks()

        self._canvas.get_tk_widget().event_generate('<Configure>',
                height=self._canvas.get_tk_widget().winfo_height(),
                width=self._canvas.get_tk_widget().winfo_width())

    def _update_colors(self):
        colors = ColorGenerator.get_gradient()
        
        for idx, axis in enumerate(self._fig.axes):
            bars = [artist for artist in axis.get_children()
                if isinstance(artist, mpl.patches.Rectangle)
                and isinstance(artist.clipbox, mpl.transforms.TransformedBbox)
            ]
            for b in bars:
                color = colors[0] if idx == 0 else colors[-1]
                b.set_facecolor(color)
            
        self._canvas.get_tk_widget().event_generate('<Configure>')

    def _destroy_with_fig(self):
        try:
            plt.close(self._fig)
            self.view.unbind('<<WinDestroy>>', self._dtr_id)
        except AttributeError as exc:
            print(exc)
            traceback.print_exc()
        finally:
            ttk.Frame.destroy(self)

    def help_text(self):
        help_text = HelpPopup.HelpText("Help")

        help_text.body.append(
            "This graphs shows\nsentiment analysis results\nfrom TextBlob and VADER.\n\n"+
            "Both of this tools search a list\nof words with different weights\n" +
            "(VADER is trained specifically\nwith social media corpora)."
        )

        help_text.url = 'file://' + os.path.realpath(MANUAL_FILE) + "#Sentiment"
        return help_text


class CriteriaFrame(ScrolledFrame):
    def __init__(self, view, **kw):
        if "relief" not in kw:
            kw["relief"] = "flat"

        master = kw.pop("master") if "master" in kw else view
        ScrolledFrame.__init__(self, master,**kw)

        self.view = view
        self.alias = "Criteria"

        self._colored_labels = []
        self.view.bind('<<ColorChanged>>', lambda e: self._update_colors(), True)

    def set_criteria(self, criteria):
        # type: (dict[str,dict]) -> None
        frm = self.display_widget(ttk.Frame, width=self.winfo_width(), height=self.winfo_height(), fit_width=True)
        self.bind_scroll_wheel(frm)
        frm.columnconfigure(0, weight=1)
        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(2, weight=1)

        colors = ColorGenerator.get_gradient()
        nrow = 0
        ncol = 0
        self._colored_labels = []
        for category, info in criteria.items():
            container = ttk.Frame(frm)
            self.bind_scroll_wheel(container)

            lbl1 = ttk.Label(container, font=self.view.font_bu,text=category, justify="center", anchor="center")
            lbl1.grid(row=0, column=0, sticky="ew")
            self.bind_scroll_wheel(lbl1)

            lbl2 = ttk.Label(container, font=self.view.font,
                    text=str(info["found"]) + "/" + str(info["against"]) +  ": " + str(info["percentage"]) +"%", 
                    justify="center",
                    anchor="center")
            lbl2.grid(row=1, column=0, sticky="ew")
            self.bind_scroll_wheel(lbl2)

            foreground = ColorGenerator.best_foreground(colors[info["rank"]])
            colored = tk.Label(container, font=self.view.font_b,
                    text=info["str"], justify="center", anchor="center",
                    background=colors[info["rank"]], foreground=foreground)
            colored.grid(row=2, column=0, pady=5)
            self.bind_scroll_wheel(colored)
            self._colored_labels.append((colored, info["rank"]))

            container.grid(row=nrow, column=ncol, sticky="nwe",padx=15, pady=15)
            container.columnconfigure("all", weight=1)
            if ncol == 2:
                ncol = 0
                nrow += 1
            else: ncol += 1
    
    def _update_colors(self):
        colors = ColorGenerator.get_gradient()
        for label, rank in self._colored_labels:
            foreground = ColorGenerator.best_foreground(colors[rank])
            label.configure(background=colors[rank], foreground=foreground)

    def help_text(self):
        help_text = HelpPopup.HelpText("Help")

        help_text.body.append(
            "This tab shows the different\nmanipulation rates\nin a color-coded scale.\n" +
            "Check the guide for more\ninformation about\nthe different criterias."
        )

        help_text.url = 'file://' + os.path.realpath(MANUAL_FILE) + "#CriteriaTable"

        return help_text


class NgramsFrame(ttk.Frame):
    def __init__(self, view, name='collocations',**kw):
        if "master" in kw:
            master = kw["master"]
            kw.pop("master")
        else: master=view
        ttk.Frame.__init__(self, master, name=name,**kw)

        self.view = view
        
        self.alias= "Collocations"

        self.results_list = []  # saved results
        self.current_query = {}
        self.current_result = []

        work_frame = Frame(self)

        work_frame.columnconfigure(0)
        work_frame.columnconfigure(1, weight=1)
        work_frame.rowconfigure(0, weight=2)
        work_frame.rowconfigure(2, weight=2)

        self.config_frame = ttk.Labelframe(
            work_frame,
            text='Settings',
            labelanchor='n')
        self.create_config_elems()
        self.config_frame.grid(row=0, column=0, sticky='nwes', rowspan=2)

        actions_frame = ttk.Labelframe(
            work_frame,
            text='Queries',
            labelanchor='n')
        actions_frame.columnconfigure(0, weight=1)
        actions_frame.rowconfigure(0, weight=1, uniform="config")
        actions_frame.rowconfigure(1, weight=1, uniform="config")
        self.save_btn = ttk.Button(
            actions_frame, text='Add', state='disabled')
        if OS_SYSTEM != "Darwin":
            self.save_btn.configure(width=10)
        self.save_btn.grid(row=0, column=0, padx=10, pady=(7, 3), sticky='s')
        self.remove_btn = ttk.Button(
            actions_frame, text='Remove', state='disabled')
        if OS_SYSTEM != "Darwin":
            self.remove_btn.configure(width=10)
        self.remove_btn.grid(row=1, column=0, padx=10,
                             pady=(3, 10), sticky='n')
        
        actions_frame.grid(row=2, column=0, sticky='news', rowspan=2)

        self.ngram_tree = TreeviewScroll(
            work_frame, self.view, show="tree", takefocus=0, height=1, selectmode='none')
        self.ngram_tree.grid_configure(row=0, column=1, sticky='nesw',
                              padx=(10, 0))
        self.results_cols = ("N-grams", "Min. length",
                             "Max. length", "Min. freq.", "SW")
        self.results_tree = TreeviewScroll(
            work_frame, self.view, show="headings", takefocus=0, height=1, columns=self.results_cols)
        self.results_tree.grid_configure(
            row=2, column=1, sticky='nesw', pady=(10, 0), padx=(10, 0))

        for text in self.results_cols:
            self.results_tree.heading(text, text=text)
            self.results_tree.column(text, width=418//5, anchor='center')

        self.results_tree.bind(
            "<<TreeviewSelect>>",
            lambda e: self.remove_btn.configure(state='normal')
        )

        work_frame.grid(padx=5,pady=5, sticky="nesw")

        self.grid_propagate(0)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.tooltips()

    def tooltips(self):
        ToolTip(self.min_length_label,
                msg="Minimum length of the words in the n-gram",
                delay=0.25, font=self.view.font_tooltip)

        ToolTip(self.max_length_label,
                msg="Maximum length of the words in the n-gram",
                delay=0.25, font=self.view.font_tooltip)

        ToolTip(self.frequency_label,
                msg="Filter by minimum frequency of\nappearance of the n-grams",
                delay=0.25, font=self.view.font_tooltip)

        ToolTip(self.stopwords_chk,
                msg="Remove stopwords contained in\nnltk's Stopwords Corpora",
                delay=0.25, font=self.view.font_tooltip)

        ToolTip(self.remove_words_label,
                msg="Exclude n-grams that contain\nany of these words",
                delay=0.25, font=self.view.font_tooltip)

        ToolTip(self.contains_words_label,
                msg="Get n-grams that contain any of this words",
                delay=0.25, font=self.view.font_tooltip)

        ToolTip(self.save_btn,
                msg="Save query and its results",
                delay=0.25, font=self.view.font_tooltip)

        ToolTip(self.remove_btn,
                msg="Remove selected queries",
                delay=0.25, font=self.view.font_tooltip)

    def help_text(self):
        help_text = HelpPopup.HelpText("Help")

        help_text.body.append(
            "This is the N-grams page,\nwhere you can search\nfor connections between words\n" +
            "(also named Collocations)."
        )

        help_text.url = 'file://' + os.path.realpath(MANUAL_FILE) + "#Collocations"

        return help_text

    def set_all(self, disabled=False):
        option = tk.DISABLED if disabled else tk.NORMAL

        for v in self.elems.values():
            v['state'] = option

    def create_config_elems(self):
        frame = self.config_frame
        self.elems = {}

        frame.columnconfigure(0, weight=20, uniform="config")
        frame.columnconfigure(1, weight=12, uniform="config")
        nrow = 0
        pady_d = 7

        self.ng_values = ["Bigrams", "Trigrams", "Quadgrams"]
        self.ngram_var = StringVar()
        self.ngram_var.set("Search n-grams...")
        self.ngram = ttk.Combobox(
            frame, font=self.view.font,
            textvariable=self.ngram_var, values=self.ng_values, state='readonly')
        self.ngram.grid(row=nrow, columnspan=2, pady=(7, 20))
        self.ngram.bind('<<ComboboxSelected>>',
                        lambda e: self.set_all())
        
        self.elems['ngram'] =self.ngram
        nrow += 1
        
        self.min_length_label = ttk.Label(
            frame, font=self.view.font,
            text='Minimum length', state='disabled')
        self.min_length_label.grid(row=nrow, column=0, padx=(
            10, 0), pady=(0, pady_d), sticky='w')
        self.elems['min_length_label'] = self.min_length_label
        self.min_length = NumericEntry(
            frame, font=self.view.font,
            width=7, char_limit=5, from_=1, to=99999, state='disabled')
        self.min_length.grid(row=nrow, column=1, padx=5, pady=(0, pady_d), sticky='we')
        self.elems['min_length'] = self.min_length
        nrow += 1

        self.max_length_label = ttk.Label(
            frame, font=self.view.font,
            text='Maximum length', state='disabled')
        self.max_length_label.grid(row=nrow, column=0, padx=(
            10, 0), pady=(0, pady_d), sticky='w')
        self.elems['max_length_label'] = self.max_length_label
        self.max_length = NumericEntry(
            frame, font=self.view.font,
            width=7, char_limit=5, from_=1, to=99999, state='disabled')
        self.max_length.grid(row=nrow, column=1, padx=5, pady=(0, pady_d), sticky='we')
        self.elems['max_length'] = self.max_length
        nrow += 1

        self.frequency_label = ttk.Label(
            frame, font=self.view.font,
            text='Min. appearance freq.', state='disabled')
        self.frequency_label.grid(row=nrow, column=0, padx=(
            10, 0), pady=(0, pady_d), sticky='w')
        self.elems['frequency_label'] = self.frequency_label
        self.frequency = NumericEntry(
            frame, font=self.view.font,
            width=7, char_limit=5, from_=1, to=99999, state='disabled')
        self.frequency.grid(row=nrow, column=1, padx=5, pady=(0, pady_d), sticky='we')
        self.elems['frequency'] = self.frequency
        nrow += 1

        self.stopwords_chk = EmptyCheckbutton(
            frame, text=' Filter with stopwords ')
        self.stopwords_chk.state(['disabled'])
        self.stopwords_chk.grid(row=nrow, columnspan=2, padx=(
            10, 0), pady=(0, pady_d), sticky='w')
        self.elems['stopwords'] = self.stopwords_chk
        nrow += 1

        self.remove_words_label = ttk.Label(
            frame, font=self.view.font,
            text='Remove words', state='disabled')
        self.remove_words_label.grid(row=nrow, columnspan=2, padx=10, pady=(0, 5))
        self.elems['remove_words_label'] = self.remove_words_label
        nrow += 1
        self.remove_words = EntryScrollX(
            frame, self.view, row=nrow, padx=10, columnspan=2, backtext='Divided by spaces', state='disabled')
        self.elems['remove_words'] = self.remove_words
        nrow += 2

        self.contains_words_label = ttk.Label(
            frame, font=self.view.font,
            text='Filter words', state='disabled')
        self.contains_words_label.grid(row=nrow, columnspan=2, padx=10, pady=(0, 5))
        self.elems['contains_words_label'] = self.contains_words_label
        nrow += 1
        self.contains_words = EntryScrollX(
            frame, self.view, row=nrow, padx=10, columnspan=2, backtext='Divided by spaces', state='disabled')
        self.elems['contains_words'] = self.contains_words
        nrow += 2

        self.search_btn = ttk.Button(
            frame, text='Search', state='disabled')
        if OS_SYSTEM != "Darwin":
            self.search_btn.configure(width=10)
        self.search_btn.grid(row=nrow, columnspan=2, padx=10, pady=(10, 10))
        self.elems['search'] = self.search_btn
        nrow += 1

    def query_ngrams(self):
        query = {}

        n = self.ngram.current()+2
        query["n"]=n

        min_length = self.min_length.get()
        min_length = int(min_length) if min_length else None
        query["min_length"]=min_length

        max_length = self.max_length.get()
        max_length = int(max_length) if max_length else None
        query["max_length"]=max_length

        frequency = self.frequency.get()
        frequency = int(frequency) if frequency else None
        query["frequency"]=frequency

        if self.remove_words.get():
            remove_words = self.remove_words.get().split()
        else:
            remove_words = ""
        query["remove_words"]=remove_words

        stopwords = 'selected' in self.stopwords_chk.state()
        query["stopwords"]=stopwords

        if self.contains_words.get():
            contains_words = self.contains_words.get().split()
        else:
            contains_words = ""
        query["contains_words"]=contains_words
        return query

    def set_current_search(self, query, results):
        # type: (dict, tuple[tuple[str,...], list[str]]) -> None
        for i in self.ngram_tree.get_children():
            self.ngram_tree.delete(i, update_width=False)

        for ngram, sentences in results:
            top = self.ngram_tree.insert('', 'end',
                    text=str(ngram) + ": " + str(len(sentences)) + " match/es.",
                    update_width=False
                )
            for sent in sentences:
                self.ngram_tree.insert(top, "end", text=sent, update_width=False)

        tree_query = {}
        tree_query["N-grams"] = self.ng_values[query["n"]-2]
        tree_query["Min. len."] = query["min_length"]
        tree_query["Max. len."] = query["max_length"]
        tree_query["Min. freq."] = query["frequency"]
        tree_query["Contains"] = query["contains_words"]
        tree_query["SW"] = "Yes" if query["stopwords"] else "No"
        tree_query["Removed"] = query["remove_words"]

        self.ngram_tree.update_width()
        self.current_query = tree_query
        self.current_result = results
        self.save_btn.configure(state='enabled')

    def get_current_search(self):
        return deepcopy(self.current_query), deepcopy(self.current_result)

    def save_current_search(self):
        query = self.current_query
        query.pop("Contains")
        query.pop("Removed")
        out = ["--" if not v else str(v) for k, v in query.items()]
        self.results_tree.insert(
            '', 'end', values=out)

        self.save_btn['state'] = 'disabled'

    def remove_selected_results(self):
        iids = self.results_tree.selection()
        index_list = []
        for i in iids:
            index = self.results_tree.index(i)
            self.results_tree.delete(i, update_width=False)
            index_list.append(index)
        self.update()  # needed
        self.remove_btn['state'] = 'disabled'
        return index_list
        