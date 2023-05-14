"""Model module.

This module manages all the logic of the program.
"""

import os
import tempfile
from copy import deepcopy
import itertools
from typing import TYPE_CHECKING, Any

import nltk

from config import DATA_DIR, PATTERNS_FILE, SETTINGS_FILE
import model.file_op as fo
from model.settings import Settings
from model.tools.string_block import StringBlock, StringBlockRegex
from model.tools.search import Search
import model.tools.text_processor as tp
from model.tools.sentiment import sentiment_analysis, create_graphs
from model.tools import ngrams as ngr
from model.tools import criteria

if TYPE_CHECKING:
    from matplotlib.figure import Figure


class Model():
    """
    This class handles the variables and methods
    composing the logic of the program.
    """
    def __init__(self):
        # settings
        self._settings = Settings()
        # loaded parameters
        self._patterns = {}
        self._criteria_ranking = []
        self._tags = {}
        # meta
        self._filename = ""
        #text processing
        self._text = ''
        self._text_blocks = []
        self._sorted_blocks = []
        self._sentences = []
        self._blob = None
        # counters
        self._tag_counters = {}
        self._category_counters = {}
        # search
        self._search_results = []
        self._searcher = Search(
            self._text_blocks,
            self._sorted_blocks,
            self._sentences,
            self._tags,
            self._settings
        )
        # results
        self._criteria_results = []
        self._ngrams_results = []
        self._sent_vader = []
        self._sent_blob = []
        self._fig = None
        # flags
        self._analized = False  # The text has been analyzed
        self._critical = False   # A critical setting has changed
        # nltk's data directory
        nltk.data.path.append(DATA_DIR)
        self._load_config()

    #*******************
    #*  Configuration  *
    #*******************

    def get_settings(self):
        # type: () -> dict[str, Any]
        """Get the current settings."""
        return deepcopy(self._settings.to_dict())

    def set_settings(self, **settings):
        """
        Change settings.

        Args:
            `tags` (bool): Enable tag matching.

            `decontract` (bool): Enable decontractions.

            `promising_contr` (bool): If uncertain, use the best guess
            for a contraction.

            `clean_words` (bool): Remove symbols from the text.

            `ngrams` (bool): Enable N-grams tab.

            `sentiment` (bool): Analyze sentiment.

            `font_size` (int): Base font size.

            `textfont` (int): Textbox font size.

            `font_family` (str): Font used on the program.
            "*Default*" (used as default) is tkinter's base font.

            `geometry` (str): Dimensions of the window.

            `win_state` (int): 1 -> maximized; 2 -> fullscreen; other -> windowed.

            `save_tags` (bool): Include tags on the results' report.

            `unmatched` (bool): Include unmatched patterns on the results' report.

            `graphs_on_excel` (bool): Include sentiment graphs on the results' report.

            `decoded_tags` (bool): Include meaning of tags on the results' report.

            `first_color` (str): First color of the gradient.
            
            `last_color` (str): Last color of the gradient.
        """
        try:
            if self._settings.changes_critical_setting(**settings):
                self._critical = True
            self._settings.set_setting(**settings)
        except AttributeError as exc:
            print(exc)

    def save_settings(self):
        # type: () -> dict[str, Any]
        """
        Save current settings.
        Returns the settings as a dictionary.
        """
        fo.save_json(SETTINGS_FILE, self._settings.to_dict())
        return self.get_settings()

    def _load_config(self):
        config_dict = fo.load_json(PATTERNS_FILE)
        self._patterns.update(config_dict["patterns"])
        self._criteria_ranking = config_dict["criteria ranking"]
        self._tags.update(config_dict["tags"])
        try:
            settings = fo.load_json(SETTINGS_FILE)
        except FileNotFoundError:
            settings = {}
        self.set_settings(**settings)

    #*********************
    #*  Text Processing  *
    #*********************

    def load_text(self, filepath):
        # type: (str) -> str
        """
        Read text from a file based on its extension.
        Supported extensions: `txt`, `doc/docx`, `pdf` and `rtf`.

        Args:
            `filename`: Name of the text file.

        Raises:
            `AttributeError`: File not compatible.

        Returns:
            `str`: Text inside the file.
        """
        text = fo.read_doc_text(filepath)
        self._filename = os.path.basename(filepath)
        return text

    def get_last_file(self):
        # type: () -> str
        """
        Return the name of the last text file loaded.
        Defaults to an empty string.
        """
        return self._filename

    def process_text(self, text):
        # type: (str) -> None
        """Process `text` for later analysis."""
        if self._is_same_text(text) and not self._critical:
            return

        text_blocks, blob, \
            sorted_blocks, tag_counters = tp.process_text(text, self._settings, self._tags.keys())

        self._text = tp.sanitize_text(text).lower()
        self._text_blocks[:] = text_blocks
        self._blob = blob
        self._sorted_blocks[:] = sorted_blocks
        self._tag_counters = tag_counters
        self._sentences[:] = blob.raw_sentences

        self._clear_results()
        self._analized = False
        self._critical = False

    def _is_same_text(self, text):
        return self._text == tp.sanitize_text(text).lower()

    #***************
    #*  Criterias  *
    #***************

    def analyze_criteria(self, text):
        # type: (str) -> dict[str,dict]
        """
        Get manipulation rates from `text`.
        """
        self.search_patterns(text)
        return self.get_criteria_results()

    def search_patterns(self, text):
        """
        Search manipulation patterns.
        """
        if self._critical or not self._is_same_text(text):
            self.process_text(text)

        if self._analized:
            return

        category_positions = {}
        search_results = []
        category_counters = {}

        for category, body in self._patterns.items():
            count_split = body["count_split"]
            category_positions[category] = set()

            for find_word in body["words"]:
                tags = find_word["tags"] if "tags" in find_word else []

                found_word = self._searcher.find_pattern(find_word["string"], tags)
                found_word.category = category
                if isinstance(found_word, StringBlockRegex) and "meaning"in body:
                    found_word.meaning = body["meaning"]

                search_results.append(found_word)

                self._update_category_positions(
                    found_word, category_positions[category], count_split
                )

            category_counters[category] = len(category_positions[category])

        self._search_results = search_results
        self._category_counters = category_counters
        self._analized = True

    def get_criteria_results(self):
        # type: () -> dict[str,dict]
        """
        Get criteria results.
        Returns `None` if patterns have not been searched.
        """
        if not self._search_results:
            return None

        self._criteria_results = criteria.get_criterias(
                categories_info=self._patterns,
                tag_counters=self._tag_counters,
                category_counters=self._category_counters,
                ranking=self._criteria_ranking
            )
        return deepcopy(self._criteria_results)

    def _update_category_positions(self, found_word, positions, count_split):
        # type: (StringBlock, set, bool) -> None
        if isinstance(found_word, StringBlockRegex):
            new_positions = itertools.chain.from_iterable(found_word.pos_text)
        else:
            new_positions = found_word.pos_text

        length = len(found_word.words)

        for first_pos in new_positions:
            all_pos = tuple(range(first_pos, first_pos + length))

            self._add_category_positions(all_pos, positions, count_split)

    def _add_category_positions(self, new_in, positions, count_split):
        # type: (tuple, set, bool) -> None

        if count_split: #category_positions is a set of numbers
            positions.update(list(new_in))
            return

        # positions contains tuples; they can overlap but never contain each other
        to_remove = set()
        for inside in positions:
            if set(inside).issubset(new_in): #* *inside* is more specific
                return

            if set(new_in).issubset(inside):
                # works in our case because a pattern never overlaps two of 'positions'
                to_remove.update([inside])

        positions.update([new_in])
        positions = positions.difference(to_remove)

    #*************
    #*  N-grams  *
    #*************

    def query_ngrams(self, n=2,
            min_length=None, max_length=None, frequency=None,
            stopwords=False, remove_words=None, contains_words=None
        ):
        # type: (int,int,int,int,bool,list[str],list[str]) -> list[tuple[tuple[str,str], int]]
        """
        Get n-grams from the current text

        Args:
            `n` (optional): Degree of the n-gram. Must be 2, 3 or 4.
            Defaults to 2.

            `min_length` (optional): Minimum length of the words on the ngrams.
            Defaults to None.

            `max_length` (optional): Maximum length of the words on the ngrams.
            Defaults to None.

            `frequency` (optional): Minimum frequency.
            Defaults to None.

            `stopwords` (optional): Apply a filter of stopwords from the Stopwords Corpus.
            Defaults to False.

            `remove_words` (optional): Words to remove.
            Defaults to None.

            `contains_words` (optional): Words to filter.
            Defaults to None.

        Raises:
            `AttributeError`: `remove_words` and `contains_words` cannot share words.

        Returns:
            `list[tuple[tuple[str,str], int]]`: List of ngrams
            with its words and frequency.
        """
        if len(set(remove_words).intersection(contains_words)) > 0:
            raise AttributeError("Cannot exclude and filter the same word.")

        words = [block.words[0] for block in self._text_blocks]
        finder = ngr.get_finder(words, n)

        if min_length or max_length:
            ngr.ngram_length(finder, min_length, max_length)
        if frequency and frequency > 0:
            ngr.ngram_frequency(finder, frequency)
        if stopwords:
            ngr.ngram_stopwords(finder)
        if contains_words:
            ngr.ngram_match_words(finder, contains_words)
        if remove_words:
            ngr.ngram_stopwords(finder, remove_words)

        return ngr.ngrams_from_finder(finder)

    def get_ngram_sentences(self, ngram):
        # type: (tuple[str]) -> list[str]
        """
        Return sentence/s where the ngram appears.

        Args:
            `ngram`: n-gram to find.

        Returns:
            `list[str]`: List of sentences. If an occurrence
            is "bridging" more than one, they will be concatenated.
            If no occurrence is found, returns an empty list.

        """
        return self._searcher.find_ngram_sentences(ngram)

    def add_ngrams_search(self, query, result):
        # type: (dict[str, Any], tuple[tuple[str,...], list[str]]) -> None
        """
        Store a query and its result.

        Args:
            `query`: Query on dictionary format.

            `result`: tuple((n-gram), [sentences])
        """
        self._ngrams_results.append((query, result))

    def remove_ngrams_result(self, index):
        # type: (int|list[int]) -> None
        """Remove a result or a list of results by index."""
        if isinstance(index, list):
            for i in index:
                self._ngrams_results.pop(i)
        else:
            self._ngrams_results.pop(index)

    #***************
    #*  Sentiment  *
    #***************

    def get_sentiment(self):
        #type: () -> tuple[list[float], list[tuple[float, float]]]
        """
        Do a sentiment analysis to the processed text
        with Vader and TextBlob.

        Returns:
            `list(float)`: Sentiment compound for each sentence
            analyzed with VADER.

            `list(tuple(float, float))`: List of tuples for each sentence
            analyzed with TextBlob.
        """
        if not self._sent_vader and not self._sent_blob:
            self._sent_vader, self._sent_blob = sentiment_analysis(self._blob)

        return deepcopy(self._sent_vader), deepcopy(self._sent_blob)

    def get_sentiment_graphs(self, copy=True):
        # type: (bool) -> Figure
        """Create a Matplotlib figure with sentiment results
        from VADER and TextBlob of the processed text.

        Args:
            `copy`: If False, returns the referenced figure.
            Defaults to True.

        Returns:
            `Figure`: Matplotlib figure.
        """
        if self._fig is None:
            self._fig = create_graphs(self._sent_vader, self._sent_blob)
        return deepcopy(self._fig) if copy else self._fig

    #*************
    #*  Results  *
    #*************

    def _clear_results(self):
        self._search_results.clear()
        self._criteria_results.clear()
        self._ngrams_results.clear()

        self._sent_vader.clear()
        self._sent_blob.clear()
        self._fig = None

    def save_results(self, filename):
        # type: (str) -> None
        """
        Save the results on an Excel document.

        Args:
            `filename`: path of the Excel document.

        Raises:
            `Exception`: An error has occurred while saving.
        """
        graphs_filename = ""
        if (self._settings.sentiment and self._settings.graphs_on_excel):
            graphs_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            self._fig.savefig(graphs_file)
            graphs_filename = graphs_file.name
            print(graphs_filename)

        try:
            fo.save_results(
                filename, deepcopy(self._patterns), deepcopy(self._tags), deepcopy(self._blob),
                deepcopy(self._settings), deepcopy(self._search_results),
                deepcopy(self._criteria_results),
                deepcopy(self._ngrams_results),
                graphs_filename=graphs_filename
            )
        except Exception as exc:
            raise Exception(f"Error saving results:\n{type(exc).__name__}: {exc}") from exc
        finally:
            if graphs_filename:
                graphs_file.close()
                os.remove(graphs_filename)
