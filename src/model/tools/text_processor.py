"""Text management.

This module contains methods to help handling texts:

- sanitize_text: prepares the text reconstructing words,
unifying quotes and removing unnecesary whitespaces.

- process_text: process the text and returns elements
for better management and easier analysis.
"""

import re
from typing import TYPE_CHECKING

from operator import attrgetter
from bisect import bisect_left

from nltk.data import load as nltk_load
from textblob import TextBlob

from config import TAGGER_FILE
from model.tools.string_block import StringBlock
from model.tools.multi_tokenizer import MultiTokenizer

if TYPE_CHECKING:
    from model.settings import Settings


def sanitize_text(text):
    # type: (str) -> str
    """
    Sanitize the text with the following operations:
    - “ or ” -> "
    - ‘ or ’ -> '
    - {space} — -> {space}
    - Consecutives whitespaces are replaced to a single space.
    - -{space} is replated to an empty chain (for words divided at the end of a line).

    Args:
        `text`: Text to sanitize.

    Returns:
        `str`: Sanitized text.
    """
    text = re.sub('[“”]', '"', text)
    text = re.sub('[‘’]', '\'', text)
    text = re.sub(r"[\s—]| +", " ", text)
    text = re.sub(r"- ", "", text)

    return text


def process_text(text, settings, tags):
    # type: (str, Settings, list[str]) -> tuple(list[StringBlock], TextBlob, list[StringBlock], dict[str,int])
    """
    Convert text to StringBlocks and more structures for easier handling.

    Args:
        `text`: Text to process.

        `settings`: Settings applied to the processing.

        `tags`: List of tags for counting.

    Returns:
        `list[StringBlock]`: List of StringBlocks in order of appearance.

        `TextBlob`: Initialized with the text.
        
        `list[StringBlock]`: List of StringBlocks in alphabeticall order.
        There is one StringBlock per word, containing all its occurrences.
        
        `dict[str,int]`: Tags with their number of occurences.
    """
    text = sanitize_text(text)
    blob = TextBlob(text)

    text_blocks, sorted_blocks, tag_counter = _process_text(
        blob.raw_sentences, settings, tags)

    return text_blocks, blob, sorted_blocks, tag_counter


def _process_text(sentence_list, settings, tags):
    # type: (list[str], Settings, list[str]) -> tuple(list[StringBlock], list[StringBlock], dict[str,int])
    my_tokenizer = MultiTokenizer()
    tagger = nltk_load(TAGGER_FILE)

    text_blocks = []
    sorted_blocks = []
    pos = 0

    tag_counter = {tag: 0 for tag in tags}

    for n_sentence, sentence in enumerate(sentence_list):

        tok_words, positions = my_tokenizer.tokenize(
            sentence.lower(),
            clean_words=settings.clean_words,
            decontract=settings.decontract,
            promising_contr=settings.promising_contr,
            output_position=True
        )

        for (word, tag), position in zip(tagger.tag(tok_words), positions):
            block = StringBlock(words=[word])
            block.add_occurrence(
                pos_text=pos,
                n_sent=n_sentence,
                pos_sent=position,
                tags=tag
            )

            _count_tag(tag, tag_counter, tags, word)
            text_blocks.append(block)
            _add_block_sorted(block, sorted_blocks)

            pos += 1

    return text_blocks, sorted_blocks, tag_counter


def _count_tag(tag, tag_counter, tags, word=""):
    # type: (str, dict[str,int], list[str], str) -> None
    if tag not in tags:
        print(word, "Tag", tag, "not recognized.")
        if tag not in tag_counter:
            tag_counter[tag] = 0

    tag_counter[tag] += 1


def _add_block_sorted(block, sorted_blocks):
    # type: (StringBlock, list[StringBlock]) -> None
    index = bisect_left(sorted_blocks, block.words, key=attrgetter('words'))

    if index == len(sorted_blocks):
        sorted_blocks.append(block)
    elif sorted_blocks[index].words[0] == block.words[0]:
        sorted_blocks[index].add_occurrence(*block.get_occurrence(0))
    else:
        sorted_blocks.insert(index, block)
