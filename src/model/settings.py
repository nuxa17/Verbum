"""Settings management.

This module stores the Settings class, used for managing
and changing different parameters of the application.
"""
from copy import deepcopy

class Settings:
    """
    Stores all the configuration parameters
    for text processing, analysis and window settings.
    """
    _critical_settings = ['clean_words', 'decontract', 'promising_contr', 'tags']

    def __init__(self,
            clean_words=False, tags=False,
            decontract=False, promising_contr=False,
            ngrams=False, sentiment=False,
            save_tags=False, decoded_tags=False,
            unmatched=False, graphs_on_excel=False,
            font_size=9, textfont=9, font_family="*Default*",
            first_color="#fb9b2a", last_color="#7030a0",
            geometry="", win_state=0
        ):
        """
        Configuration parameters for text processing,
        analysis and window settings.

        Args:
            `tags` (bool, optional): Enable tag matching. Defaults to False.

            `decontract` (bool, optional): Enable decontractions. Defaults to False.

            `promising_contr` (bool, optional): If uncertain, use the best guess
            for a contraction. Defaults to False.

            `clean_words` (bool, optional): Remove symbols from the text. Defaults to False.

            `ngrams` (bool, optional): Enable N-grams tab. Defaults to False.

            `sentiment` (bool, optional): Analyze sentiment. Defaults to False.

            `font_size` (int, optional): Base font size. Defaults to 9.

            `textfont` (int, optional): Textbox font size. Defaults to 9.

            `font_family` (str, optional): Font used on the program.
            "*Default*" (used as default) is tkinter's base font.

            `geometry` (str, optional): Dimensions of the window. Defaults to "".

            `win_state` (int, optional): 1 -> maximized; 2 -> fullscreen; other -> windowed.
            Defaults to 0.

            `save_tags` (bool, optional): Include tags on the results' report.
            Defaults to False.

            `unmatched` (bool, optional): Include unmatched patterns on the results' report.
            Defaults to False.

            `graphs_on_excel` (bool, optional): Include sentiment graphs on the results' report.
            Defaults to False.

            `decoded_tags` (bool, optional): Include meaning of tags on the results' report.
            Defaults to False.

            `first_color` (str, optional): First color of the gradient. Defaults to "#fb9b2a".
            
            `last_color` (str, optional): Last color of the gradient. Defaults to "#7030a0".
        """
        self.clean_words = clean_words
        self.tags = tags
        self.decontract = decontract
        self.promising_contr = promising_contr

        self.ngrams = ngrams
        self.sentiment = sentiment

        self.save_tags = save_tags
        self.decoded_tags = decoded_tags
        self.unmatched = unmatched
        self.graphs_on_excel = graphs_on_excel

        self.font_size = font_size
        self.textfont = textfont
        self.font_family = font_family

        self.first_color = first_color
        self.last_color = last_color

        self.geometry = geometry
        self.win_state = win_state

    def set_setting(self, **settings):
        """
        Change multiple settings at once.

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

        Raises:
            `AttributeError`: The setting does not exist.
        """
        errors = []
        for k, v in settings.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                errors.append(k)
        if errors:
            raise AttributeError(
                'Settings object has no attributes: ' + str(errors))

    def changes_critical_setting(self, **settings):
        """
        Checks if a setting is critical, that is,
        text needs to be reprocessed and reanalyzed.
        """
        return any(settings[key] != getattr(self, key) for key in settings if key in self._critical_settings)

    def to_dict(self):
        """Return all settings as a dictionary."""
        return deepcopy(self.__dict__)
