"""Controller.

This module contains the controller,
which bridges the View and Model of the program.
"""
import os
import traceback
from typing import Any
from threading import Thread

from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askyesno, askyesnocancel, showerror, showinfo

import matplotlib as mpl

from config import launch_file
from model.model import Model
from utils.color import ColorGenerator
from view.view import View
from view.results_frames import MultiFrame, CriteriaFrame, NgramsFrame, GraphsFrame
from view.popups import SavePopup
from view.text_frame import TextFrame

mpl.use('agg')


class Controller:
    """
    Controller.

    This class bridges the View and Model of the program.
    """
    def __init__(self):
        """
        Create model and view, and load patterns and settings.
        """
        self.model = Model()

        settings = self.model.get_settings()

        self.view = View()
        self.view.configure_fonts(size=settings["font_size"],family=settings["font_family"])

        ColorGenerator.generate_gradient(settings["first_color"], settings["last_color"])
        self.view.bind(
            "<<ColorChanged>>",
            lambda e:self.model.set_settings(
                first_color = ColorGenerator.get_gradient()[0],
                last_color = ColorGenerator.get_gradient()[-1]
            ),
            True
        )

        frame = self.init_frame("TextFrame")
        frame.set_settings(settings)

        self.view.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.view.set_geometry(settings["geometry"], settings["win_state"])

    def run(self):
        """Run application."""
        self.view.deiconify()
        self.view.mainloop()

    def init_frame(self, frameclass, **kw):
        # type: (str, Any) -> TextFrame | NgramsFrame | MultiFrame | GraphsFrame | CriteriaFrame | None
        """
        Create frames, usually asignating
        callback functions. Supported frames are:
        TextFrame, NgramsFrame, MultiFrame, GraphsFrame and CriteriaFrame.

        Args:
            `frameclass`: Class of the frame.

            `**kw`: Arguments for the frame's initialization.

        Returns initialized frame.
        If the type is not found, returns None.
        """
        match frameclass:
            case "TextFrame":
                frame = self.view.create_frame(TextFrame, True, **kw)
                frame.open_button.configure(
                    command=lambda:
                        self.load_text(frame)
                    )
                frame.next_button.configure(
                    command=lambda:
                        self.process_text(frame)
                    )

            case "NgramsFrame":
                frame = self.view.create_frame(NgramsFrame, **kw)
                frame.search_btn.configure(command=lambda: self.search_ngrams(frame))
                frame.remove_btn.configure(command=lambda: self.remove_ngrams_result(frame))
                frame.save_btn.configure(command=lambda: self.save_ngrams_result(frame))

            case "MultiFrame":
                frame = self.view.create_frame(MultiFrame, **kw)
                frame.back_button.configure(command=self.back_to_text)
                frame.save_button.configure(command=self.save_results)

            case "GraphsFrame":
                frame = self.view.create_frame(GraphsFrame, **kw)

            case "CriteriaFrame":
                frame = self.view.create_frame(CriteriaFrame, **kw)

            case _:
                frame = None
        return frame

    def change_frame(self, framename):
        # type: (str) -> None
        """
        Change to another frame.
        """
        if not framename in self.view.saved_frames:
            self.view.change_frame(self.init_frame(framename))
        else:
            self.view.change_frame(framename)

    def on_closing(self):
        """
        Save program settings before closing.
        """
        try:
            geometry = self.view.get_unscaled_geometry()
            win_state = self.view.get_state()
            colors = ColorGenerator.get_gradient()
            self.model.set_settings(
                geometry = geometry,
                win_state = win_state,
                font_size = self.view.font["size"],
                font_family = self.view.font_family.get(),
                first_color = colors[0],
                last_color = colors[-1],
                **self.view.saved_frames["TextFrame"].get_settings()
            )
            self.model.save_settings()
        except IOError as exc:
            showerror("Error while closing: ", exc)
            traceback.print_exc()
        finally:
            self.view.destroy()

#***************
#*  TEXTFRAME  *
#***************

    def load_text(self, frame):
        # type: (ttk.Frame) -> None
        """
        Load text from file.

        Args:
            `frame`: Frame that handles the text.
        """
        file_route = askopenfilename(
            filetypes=[
                ("All files", "*.*"),
                ("Word", '*.doc *.docx'),
                ("RTF", "*.rtf"),
                ("Text document", "*.txt"),
                ("PDF", "*.pdf")
            ]
        )
        if not file_route:
            return

        try:
            text = self.model.load_text(file_route)

            if not text:
                showinfo("This is weird...", "Could not find any text in the document.")
                return

            frame.set_text(text)
            frame.update_info("\"" + str(os.path.basename(file_route)) + "\" loaded.")
        except (IOError, AttributeError) as exc:
            showerror("File error", exc)
            traceback.print_exc()

    def process_text(self, frame):
        # type: (ttk.Frame) -> Thread
        """
        Text processing method.

        WARNING: Launches a thread as a daemon
        to avoid the blocking of tkinter, and disables
        all the elements of the frame to avoid race conditions.
        Do NOT call other methods while the thread is running.

        Args:
            `frame`: Frame with the text to process.
        
        Returns:
            `Thread`: New running thread.
        """
        frame.set_all(disabled=True) #Block user input

        thread = Thread(target=self._process_text, args=(frame,), daemon=True)
        thread.start()
        return thread

    def _process_text(self, frame):
        # type: (ttk.Frame) -> None

        text = frame.get_text()
        settings = frame.get_settings()
        try:
            self.model.set_settings(**settings)
            frame.update_info("Analyzing text...")
            self.model.process_text(text)

            frame.update_info("Searching patterns...")
            self.model.search_patterns(text)
        except Exception as exc:
            showerror("Error.", f"Error processing text:\n{type(exc).__name__}: {exc}")
            traceback.print_exc()
            frame.update_info("")
            frame.set_all(disabled=False)
            return

        settings = self.model.get_settings()
        data = self._data_for_multiframe(frame, settings["sentiment"])

        # Execution continues on the main thread (blocking call)
        funcid = frame.bind(
                "<<Multiframe>>",
                lambda e: self._create_multiframe(
                    frame, data,
                    settings["ngrams"], settings["sentiment"]
                )
            )
        frame.event_generate("<<Multiframe>>")
        frame.unbind("<<Multiframe>>", funcid)

    def _data_for_multiframe(self, frame, check_sentiment):
        results = {}
        results["criteria"] = self.model.get_criteria_results()

        if check_sentiment:
            frame.update_info("Checking criteria and sentiment...")
            self.model.get_sentiment()

            fig = self.model.get_sentiment_graphs(copy=False)
            results["sentiment"] = fig
        else:
            frame.update_info("Checking criteria...")

        frame.update_info("")

        return results

    def _create_multiframe(self, frame, data, add_ngrams, add_sentiment):
        # type: (ttk.Frame, dict, bool, bool) -> None

        #frames must be created on the main thread or they will spawn windows
        multiframe = self.init_frame("MultiFrame")

        criteria = self.init_frame("CriteriaFrame", master=multiframe)
        multiframe.add_frame(criteria)

        if add_ngrams:
            ngrams = self.init_frame("NgramsFrame", master=multiframe)
            multiframe.add_frame(ngrams)

        if add_sentiment:
            graphs = self.init_frame("GraphsFrame", master=multiframe)
            multiframe.add_frame(graphs)

        self.view.change_frame(multiframe)
        criteria.set_criteria(data["criteria"])
        if add_sentiment:
            graphs.set_graphs(data["sentiment"])
        frame.set_all(disabled=False)

#*****************
#*  NGRAMSFRAME  *
#*****************

    def back_to_text(self):
        """
        Go back to TextFrame and ask the user if
        they want to save their last analysis.
        """
        answer = askyesnocancel(
                "Warning",
                "Anything not saved will be lost. Do you want to save the current results?"
            )

        if (answer is False
            or (answer is True and self.save_results())
        ):
            self.change_frame('TextFrame')

    def search_ngrams(self, frame):
        # type: (ttk.Frame) -> Thread
        """
        N-grams search based on user-defined parameters.

        WARNING: Launches a thread as a daemon
        to avoid the blocking of tkinter, and disables
        all the elements of the frame to avoid race conditions.
        Do NOT call other methods while the thread is running.

        Args:
            `frame`: Frame with the n-gram information.
        
        Returns:
            `Thread`: New running thread.
        """
        thread = Thread(target=self._search_ngrams, args=(frame,), daemon=True)
        thread.start()
        return thread

    def _search_ngrams(self, frame):
        multiframe = self.view.current_frame
        multiframe.set_all(disabled=True)

        multiframe.update_info("Searching ngrams...")
        query = frame.query_ngrams()
        ngrams = self._get_ngrams(query)
        if not ngrams:
            showinfo("Oopsie","Nothing found!")
            multiframe.update_info("")
            multiframe.set_all(disabled=False)
            return

        multiframe.update_info("Retrieving sentences...")
        try:
            with_sentences = self._get_ngrams_sentences(ngrams)
        except IndexError as exc:
            showerror("Error in controller.search_ngrams", exc)
            traceback.print_exc()
            multiframe.update_info("")
            multiframe.set_all(disabled=False)
            return

        multiframe.update_info("Loading ngrams...")
        # Execution continues on the main thread (blocking call)
        funcid = frame.bind("<<FillNgrams>>",
                lambda e: frame.set_current_search(query, with_sentences)
            )
        frame.event_generate("<<FillNgrams>>")
        frame.unbind("<<FillNgrams>>", funcid)
        self.view.current_frame.set_all(disabled=False)
        multiframe.update_info("")

    def _get_ngrams(self, query):
        try:
            ngrams = self.model.query_ngrams(
                n=query["n"],
                min_length=query["min_length"],
                max_length=query["max_length"],
                frequency=query["frequency"],
                stopwords=query["stopwords"],
                remove_words=query["remove_words"],
                contains_words=query["contains_words"]
            )
        except AttributeError as exc:
            showerror("Error", exc)
            return None

        return ngrams

    def _get_ngrams_sentences(self, ngrams):
        """Returns [(ngram), [sentences]]"""
        results = []
        for ngram, freq in ngrams:
            sentences = self.model.get_ngram_sentences(ngram)
            if len(sentences) != freq: # will never happen under normal circumstances
                raise IndexError().with_traceback()

            results.append((ngram, sentences))

        return results

    def save_ngrams_result(self, frame):
        # type: (NgramsFrame) -> None
        """
        Store temporary results of query on model.

        Args:
            frame: Frame handling n-grams queries.
        """
        query, result = frame.get_current_search()
        self.model.add_ngrams_search(query, result)
        frame.save_current_search()

    def remove_ngrams_result(self, frame):
        # type: (NgramsFrame) -> None
        """
        Remove selected results of queries from model.

        Args:
            frame: Frame handling n-grams queries.
        """
        index_list = frame.remove_selected_results()
        self.model.remove_ngrams_result(index_list)

#*************
#*  GENERAL  *
#*************

    def save_results(self):
        # type: () -> bool
        """
        Save all analysis' results.

        Returns `True` if the results were saved.
        Otherwise, returns `False`.
        """
        win_save = SavePopup(self.view, self.model.get_settings())

        win_save.save_btn.configure(command=lambda: self._save_results(win_save))

        win_save.wait_window(win_save)
        return win_save.saved

    def _save_results(self, win_save):
        self.model.set_settings(**win_save.get_settings())
        filename = os.path.splitext(self.model.get_last_file())[0]
        file_route = asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[("Excel", '*.xlsx')],
                initialfile=filename
            )
        if not file_route:
            return

        try:
            self.model.save_results(file_route)
        except Exception as exc:
            showerror("Error saving results", exc)
            traceback.print_exc()
            return

        if askyesno(
            "Results saved.",
            "Results saved. Do you want to open the file?"
        ):
            launch_file(file_route)

        win_save.result = True
        win_save.destroy()
