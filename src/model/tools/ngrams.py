"""N-grams module.

This module provides methods for simple
management of n-grams' analysis, using the `collocations` and
`stopwords` modules from NLTK.
"""
from nltk.corpus import stopwords
import nltk.collocations as col


def get_finder(words, n):
    # type: (list[str], int) -> col.BigramCollocationFinder|col.TrigramCollocationFinder|col.QuadgramCollocationFinder
    """
    Get n-CollocationFinder with the words loaded.

    Args:
        `words`: Words of the text in order.
        `n`: Degree of the n-gram. Must be 2, 3 or 4.

    Raises:
        AttributeError: `n` must be 2, 3 or 4.

    Returns:
        `BigramCollocationFinder`|`TrigramCollocationFinder`|`QuadgramCollocationFinder`
        with the words loaded.
    """
    match n:
        case 2:
            finder = col.BigramCollocationFinder
        case 3:
            finder = col.TrigramCollocationFinder
        case 4:
            finder = col.QuadgramCollocationFinder
        case _:
            raise AttributeError("n must be 2, 3 or 4.")

    return finder.from_words(words)

#*************
#*  Filters  *
#*************

def ngram_length(finder, min_length=None, max_length=None):
    # type: (col.BigramCollocationFinder|col.TrigramCollocationFinder|col.QuadgramCollocationFinder, int, int) -> None
    """
    Apply a minimum/maximum number of words filter to `finder`.

    Args:
        `finder`: CollocationFinder with ngrams.

        `min_length` (optional): Minimum length of the words on the ngrams.
        Defaults to None.

        `max_length` (optional): Maximum length of the words on the ngrams.
        Defaults to None.
    """
    if max_length:
        finder.apply_word_filter(lambda w: len(w) > max_length)
    if min_length:
        finder.apply_word_filter(lambda w: len(w) < min_length)


def ngram_frequency(finder, frequency):
    # type: (col.BigramCollocationFinder|col.TrigramCollocationFinder|col.QuadgramCollocationFinder, int) -> None
    """
    Filter n-grams by a minimum frequency.

    Args:
        `finder`: CollocationFinder with ngrams.
        `frequency`: Minimum frequency.
    """
    finder.apply_freq_filter(frequency)


def ngram_stopwords(finder, words=None):
    # type: (col.BigramCollocationFinder|col.TrigramCollocationFinder|col.QuadgramCollocationFinder, list[str]) -> None
    """
    Remove n-grams which have at least one word of a list.
    If not specified, apply a filter of stopwords from the Stopwords Corpus.

    Args:
        `finder`: CollocationFinder with ngrams.
        `words` (optional): Words to remove. Defaults to None.
    """
    if not words:
        words = set(stopwords.words('english'))

    finder.apply_word_filter(lambda w: w in words)


def ngram_match_words(finder, words):
    # type: (col.BigramCollocationFinder|col.TrigramCollocationFinder|col.QuadgramCollocationFinder, list[str]) -> None
    """
    Filter n-grams which have at least one word of a list.

    Args:
        `finder`: CollocationFinder with ngrams.
        `words`: Words to filter.
    """
    words = [item.lower() for item in words]
    finder.apply_ngram_filter(lambda *w: True not in [x in words for x in w])


def ngrams_from_finder(finder):
    # type: (col.BigramCollocationFinder|col.TrigramCollocationFinder|col.QuadgramCollocationFinder) -> list[tuple[tuple[str,str], int]]
    """
    Get n-grams from the CollocationFinder.
    These are sorted by frequency and then alphabetically.

    Args:
        `finder`: CollocationFinder with ngrams.

    Returns:
        `list[tuple[tuple[str, str], int]`: List of ngrams
        with its words and frequency.
    """
    return sorted(finder.ngram_fd.items(), key=lambda t: (-t[1], t[0]))
