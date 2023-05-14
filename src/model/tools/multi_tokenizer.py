"""MultiTokenizer.

This module contains MultiTokenizer, a multipurpose
tokenizer based on WhitespaceTokenizer.
- Clean the words smartly for contraction management.
- Expand contractions based on a dictionary or by guessing them.
- Get the original position of the words after decontracting.
"""
import re

from nltk.tokenize import WhitespaceTokenizer

from config import CONTRACTIONS_FILE
from model.file_op import load_json

class MultiTokenizer(WhitespaceTokenizer):
    """
    WhitespaceTokenizer with extra options.
    """

    def __init__(self, contractions=None):
        # type: (dict[str, list[str]]) -> None
        """
        Args:
            `contr_dict` (optional): Use custom dictionary for contractions.
            Defaults to a default dictionary (contractions.json).
        """
        WhitespaceTokenizer.__init__(self)
        self.contractions = contractions if contractions else load_json(
            CONTRACTIONS_FILE)

    def tokenize(self, text,
            clean_words=False, decontract=False,
            promising_contr=True, output_position=False
        ):
        # type: (str, bool, bool, bool, bool) -> list | tuple[list,list]
        """
        Tokenize by whitespaces (WhitespaceTokenizer)
        with extra options. If `decontract` is True and no dictionary has been set,
        a default dictionary from contractions.json will be used.

        Args:
            `text`: Text to tokenize.

            `clean_words` (optional): Remove any character that is not a letter,
            a hyphen inside the word or an apostrophe.
            Defaults to False.

            `decontract` (optional): Expand contractions if there is only one possibility.
            Defaults to False.

            `promising_contr` (optional): If True (default), expands contractions using
            the most used case. Otherwise, tries to recover the "secure" parts.

                True: he's -> he is. False: he's -> he.

            If this fails, returns the word without an apostrophe and prints
            an informative message. Only checked when `decontract` is True.

            `output_position` (optional): Return words' positions relative
            to a whitespace-tokenized text. Useful for locating
            the original position of words after cleaning or decontracting.
            Defaults to False.

        Returns:
            `list`: List of tokenized words.
            
            `list` (if `output_position` is True): Words' positions relative
            to a whitespace-tokenized text.
        """
        words = []
        positions = []
        for idx, word in enumerate(super().tokenize(text)):
            word = self.clean_word(word) if clean_words else word
            if not word:
                continue

            if decontract:
                new_words = self.expand_contraction(word, promising_contr)
                words += new_words
            else:
                words.append(word)

            if output_position:
                positions += [idx] if not decontract else [idx] * len(new_words)

        return (words, positions) if output_position else words

    def expand_contraction(self, word, promising_contr=True):
        # type: (str, bool) -> list[str]
        """
        Returns expanded contraction if posible.
        In case of finding a possible contraction which can't be expanded,
        this will also print an informative message.

        Args:
            `word`: Word to decontract.

            `promising_contr` (optional): If True (default), expands contractions using
            the most used case. Otherwise, tries to recover the "secure" parts.

                True: he's -> he is. False: he's -> he.

            If this fails, returns the word without an apostrophe and prints
            an informative message.
        
        Returns:
            `list`: List of decontracted words.
        """
        if word in self.contractions:
            options = self.contractions[word]
            if len(options) == 1 or not promising_contr:
                decontracted = options[0].split()
            else:
                decontracted = options[1].split()

        else:
            decontracted = self._guess_contr(word, promising_contr)
            if not decontracted:
                decontracted = [word]
                if "'" in word:
                    print(f"Possible unhandled contraction: {word}. Cleaning...")

            decontracted = [re.sub(r'\'', '', each) for each in decontracted]
        return decontracted

    def _guess_contr(self, word, promising_contr=True):
        aux = []
        if word.endswith("'s"):
            aux = [word[:-2], "is"]

        elif word.endswith("'re"):
            aux = [word[:-3], "are"]

        elif word.endswith("'ll"):
            aux = [word[:-3], "will"]

        elif word.endswith("'d"):
            aux = [word[:-2], "would"]

        elif word.endswith("n't"):
            aux = [word[:-3], "not"]

        if aux and not promising_contr:
            aux.pop()   # just the "secure" part
        return aux

    def clean_word(self, word):
        # type: (str) -> str
        """
        Remove any character that is not a letter,
        a hyphen inside the word or an apostrophe.
        """
        if word[0] == '-':
            word = word[1:]
        if word and word[-1] == '-':
            word = word[:-1]

        aux = re.sub(r'[^\w\'-]', '', word)
        if not aux or aux.isdigit():
            return ""

        return aux