"""Search module.

This module provides a class for finding the location
of patterns and n-grams in a StringBlocked text.


"""

import re
from copy import deepcopy
from operator import attrgetter
from bisect import bisect_left

from model.tools.string_block import StringBlock, StringBlockRegex
from model.settings import Settings
from model.tools.multi_tokenizer import MultiTokenizer

class Search:
    """
    Search object for finding patterns in a StringBlocked text.
    """

    def __init__(self,
            text_blocks: list[StringBlock],
            sorted_blocks: list[StringBlock],
            sentences: list[str],
            tags: list[str],
            settings: Settings,
            tokenizer: MultiTokenizer = None
        ) -> None:
        """
        Args:
            `text_blocks`: Text composed by StringBlocks.

            `sorted_blocks`: List of StringBlocks in alphabeticall order.
            Theremust be one StringBlock per word, containing all its occurrences.

            `sentences`: List of sentences that forms the text.

            `tags`: List of tags.

            `settings`: Settings object containing the options
            used for processing the text.

            `tokenizer` (optional): MultiTokenizer object.
            If unspecified, one will be created.
        """
        self.text_blocks = text_blocks
        self.sorted_blocks = sorted_blocks
        self.sentences = sentences
        self.tags = tags
        self.settings = settings

        self.tokenizer = tokenizer if tokenizer else MultiTokenizer()

    def update(self, **kw):
        """
        Change multiple attributes at once.

        Args:
            `text_blocks`: Text composed by StringBlocks.

            `sorted_blocks`: List of StringBlocks in alphabeticall order.
            Theremust be one StringBlock per word, containing all its occurrences.

            `sentences`: List of sentences that forms the text.

            `tags`: List of tags.

            `settings`: Settings object containing the options
            used for processing the text.

            `tokenizer`: MultiTokenizer object.

        Raises:
            `AttributeError`: The attribute does not exists.
        """
        errors = []
        for k, v in kw.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                errors.append(k)
        if errors:
            raise AttributeError(
                'Search object has no attributes: ' + str(errors))


#**************
#*  Patterns  *
#**************

    def find_pattern(self, pattern, tags=None):
        # type: (str, list[str]) -> StringBlock|StringBlockRegex
        """
        Search and get the occurrences of a pattern in the text.
        Regular expressions must be specified as '{ expression }',
        p.ex.: { pre.* }

        Args:
            `pattern`: Pattern of words to find.

            `tags`: If specified, matches the tags of each word.

        NOTICE: It is recommended that the pattern does not contains contractions
        if the tags are specified. If a contraction is found and decontraction
        has been applied to the text, the number of tags could not be the same
        as the number of the decontracted words. This does not apply to regular expressions.

        Raises:
            `AttributeError`: The number of words and tags is not the same.

        Returns:
            `StringBlock`: Occurrences of the pattern in the text.
        """
        if pattern[0] == '{' and pattern[-1] == '}':
            regex = True
            words = pattern.split()[1:-1]
        else:
            regex = False
            words = self.tokenizer.tokenize(
                    pattern,
                    clean_words=self.settings.clean_words,
                    decontract=self.settings.decontract,
                    promising_contr=self.settings.promising_contr
                )

        if not tags:
            tags = []
        elif len(tags) != len(words):
            raise AttributeError("The number of words and tags is not the same!")

        if len(words) == 1:
            if regex:
                result = self._monoregex(words, tags)
            else:
                result = self._monoword(words, tags)
        elif regex:
            raise NotImplementedError(
                "Regex is not currently supported for strings with more than one word.")
        else:
            result = self._multiword(words, tags)

        return result

    def _monoword(self, pattern, tags):
        # type: (list[str], list[str]) -> StringBlock
        using_tags = self.settings.tags and tags

        result = StringBlock(words=pattern)

        found_word = self.search_sorted_block(pattern[0])

        if not found_word:
            return result   # Empty StringBlock

        if using_tags:
            for i in range(found_word.n_occurrences()):
                if self.is_child_tag(tags[0], found_word.tags[i][0]):
                    result.add_occurrence(*found_word.get_occurrence(i))
        else:
            result = found_word

        return deepcopy(result)

    def _multiword(self, pattern, tags):
        # type: (list[str], list[str]) -> StringBlock
        find_tags = tags and self.settings.tags

        promising_results = self._monoword(pattern, tags)

        if promising_results.n_occurrences() == 0:
            return promising_results # Empty StringBlock

        result = StringBlock(words=pattern)

        for idx in range(promising_results.n_occurrences()):
            occ = promising_results.get_occurrence(idx)

            section = self.text_blocks[occ[0]+1 : occ[0]+len(pattern)]
            words_chain = [w.words[0] for w in section]
            tags_chain = [w.tags[0][0] for w in section]

            if (pattern[1:] != words_chain
                or self._in_same_sentence(section) is False
                or (find_tags and self.is_child_tag(tags[1:],tags_chain) is False)
            ):
                continue

            result.add_occurrence(
                pos_text=occ[0],
                n_sent=occ[1],
                pos_sent=occ[2] + [w.pos_sent[0][0] for w in section],
                tags=occ[3] + [w.tags[0][0] for w in section]
            )

        return deepcopy(result)

    def _monoregex(self, pattern, tags):
        # type: (list[str], list[str]) -> StringBlock
        using_tags = self.settings.tags and tags

        myreg = pattern[0]
        matcher = re.compile(myreg)

        result = StringBlockRegex(words=pattern)

        for word in self.sorted_blocks:
            if (matcher.fullmatch(word.words[0]) is None or
                    (using_tags and self.is_child_tag(tags[0], word.tags[0][0]) is False)
                ):
                # the word or the tag doesn't match
                continue

            result.add_occurrence(
                pos_text=word.pos_text,
                n_sent=word.n_sent,
                pos_sent=word.pos_sent,
                tags=word.tags,
                reg_matched=word.words
            )

        return deepcopy(result)


#*************
#*  N-grams  *
#*************

    def find_ngram_sentences(self, ngram):
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
        sb_word = self.search_sorted_block(ngram[0])
        if not sb_word: # will never happen under normal circumstances
            raise IndexError().with_traceback()

        results = []

        for pos in sb_word.pos_text:
            section = self.text_blocks[pos:pos+len(ngram)]
            if ngram != tuple(w.words[0] for w in section):
                continue

            # ngrams may occupy multiple sentences
            n_sent = sorted(set(w.n_sent[0] for w in section))
            results.append(' '.join([self.sentences[n] for n in n_sent]))
        return results

    def _in_same_sentence(self, blocks):
        # type: (list[StringBlock]) -> bool
        sents = [w.n_sent[0] for w in blocks]

        return len(set(sents)) == 1


#***********
#*  Utils  *
#***********

    def search_sorted_block(self, word):
        # type: (str) -> StringBlock|None
        """
        Get the first StringBlock of `self.sorted_list` that contains that word.
        Only the first word is compared. It is assumed that `sorted_list` is sorted
        (as its name suggests). 

        Args:
            `word`: Word to search.

        Returns:
            `StringBlock`: If found, returns the StringBlock that has that word.
            Otherwise, returns None.
        """
        index = bisect_left(self.sorted_blocks, [word], key=attrgetter('words'))

        if (index < len(self.sorted_blocks)
            and self.sorted_blocks[index].words[0] == word):
            return self.sorted_blocks[index]

        return None

    def is_child_tag(self, parent_tag, child_tag):
        # type: (str|list[str], str|list[str]) -> bool
        """
        Checks if `parent_tag` is a parent of or the same as `child_tag`.
        If two lists are passed as arguments, checks by index and return True
        if all tags are matched.
        It is assumed that `parent_tag` and `child_tag` have the same type.

        Args:
            `parent_tag`: Most generic tag.
            `child_tag`: Most specific tag.

        Raises:
            `ValueError`: If list are passed, they must have the same length.

        Returns:
            `bool`: True if it's its parent.
        """
        if isinstance(parent_tag, str) and isinstance(child_tag, str):
            return self._is_child_tag(parent_tag, child_tag)

        if len(parent_tag) != len(child_tag):
            raise ValueError("Lists must have the same length")

        for parent, child in zip(parent_tag, child_tag):
            if not self._is_child_tag(parent, child):
                return False
        return True

    def _is_child_tag(self, parent_tag, child_tag):
        # type: (str, str) -> bool
        if parent_tag == '*':
            return True

        while True:
            if child_tag == parent_tag:
                return True

            if "parent" not in self.tags[child_tag]:
                return False

            child_tag = self.tags[child_tag]['parent']
