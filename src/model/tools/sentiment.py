"""Sentiment analyzers.

This module contains methods for analyzing the sentiment
of a text in a TextBlob and get a figure from such results.
"""

from typing import TYPE_CHECKING

from nltk.sentiment.vader import SentimentIntensityAnalyzer

from matplotlib import figure

if TYPE_CHECKING:
    from textblob import TextBlob
    from matplotlib.figure import Figure


def sentiment_analysis(textblob):
    #type: (TextBlob) -> tuple[list[float], list[tuple[float, float]]]
    """Get sentiment analysis of the sentences in `textblob`.

    Args:
        `textblob`: A TextBlob object with sentences.

    Returns:
        `list(float)`: Sentiment compound for each sentence
        analyzed with VADER.

        `list(tuple(float, float))`: List of tuples for each sentence
        analyzed with TextBlob.
    """

    sentences = textblob.raw_sentences

    # keys = ['neg', 'neu', 'pos', 'compound']
    sid = SentimentIntensityAnalyzer()
    sent_vader = [sid.polarity_scores(sentence)["compound"] for sentence in sentences]

    #[0] sentiment, [1] subjectivity
    sent_blob = [sentence.sentiment for sentence in textblob.sentences]

    return sent_vader, sent_blob

def create_graphs(sent_vader, sent_blob):
    # type: (list[float], list[tuple[float, float]]) -> Figure
    """Create a Matplotlib figure with sentiment results from VADER and TextBlob.
    Inputs are expected to be on the same format
    as the returned values from `sentiment_analysis`.

    Args:
        `sent_vader`: Sentiment list from VADER.

        `sent_blob`: Sentiment list from TextBlob.

    Returns:
        `Figure`: Matplotlib figure.
    """
    blob_sent, blob_subj = zip(*sent_blob)

    fig = figure.Figure()

    ax1 = fig.add_subplot(131)
    ax1.hist(sent_vader, 40, color="red")
    ax1.set_title('VADER - Compound')
    ax1.set_xlim((-1,1))
    ax1.set_xlabel("-1 - 0: Negative\n0 - 1: Positive")

    ax2 = fig.add_subplot(132, sharey = ax1)
    ax2.hist(blob_sent, 40, color="blue")
    ax2.set_title('TextBlob - Sentiment')
    ax2.set_xlim((-1,1))
    ax2.set_xlabel("-1 - 0: Negative\n0 - 1: Positive")

    ax3 = fig.add_subplot(133, sharey = ax1)
    ax3.hist(blob_subj, 40, color="blue")
    ax3.set_title('TextBlob - Subjectivity')
    ax3.set_xlim((0,1))
    ax3.set_xlabel("Percentage")

    ax1.set_ylabel("Count")
    fig.suptitle("Sentiment counts")
    fig.set_tight_layout(True)

    return fig
