"""Stringblock module.

This module contains the Stringblock class,
a structure dedicated to text management.
Includes a child class for regex patterns.
"""

class StringBlock:
    """
    Stores a word/group of words that forms the string
    and useful information for working easily with the text.
    """

    def __init__(self, words,
            pos_text = None,
            n_sent = None,
            pos_sent = None,
            tags = None,
            category = ""
        ):
        # type:(list[str], list[int], list[int], list[list[int]], list[list[str]], str) -> None
        """
        Args:
            `words`: List of words that forms the pattern.

            `pos_text`: Positions of the first word in the text.
            Defaults to an empty list.

            `n_sent`: Which sentences contains the pattern.
            Defaults to an empty list.

            `pos_sent`: Position of each word relative to the original sentences.
            Defaults to an empty list.

            `tags`: Grammatical group of each word for every occurrence.
            Defaults to an empty list.

            `category`: Equivalent to the criteria.
            Defaults to an empty string.
        """
        self.words = words

        self.pos_text = [] if not pos_text else pos_text
        self.n_sent = [] if not n_sent else n_sent
        self.pos_sent = [] if not pos_sent else pos_sent
        self.tags = [] if not tags else tags
        self.category = category


    def add_occurrence(self, pos_text, n_sent, pos_sent, tags):
        # type: (int, int, int|list[int], str|list[str]) -> None
        """
        Add new occurrence.

        Args:
            `pos_text`: Position of the first word in the text.

            `n_sent`: Which sentence contains the pattern.

            `pos_sent`: Position of each word relative to the original sentence.
            It is assumed that the number of positions is the same
            as the number of words.

            `tags`: Grammatical group of each word. It is assumed that
            the number of tags is the same as the number of words.
        """
        self.pos_text.append(pos_text)
        self.n_sent.append(n_sent)
        self.pos_sent.append(pos_sent if isinstance(pos_sent, list) else [pos_sent])
        self.tags.append(tags if isinstance(tags, list) else [tags])

    def get_occurrence(self, index):
        # type: (int) -> tuple(int, int, list[int], list[str])
        """
        Get `index` occurrence.

        Returns:
            `int`: Position of the first word in the text (`pos_text`).

            `int`: Which sentence contains the pattern (`n_sent`).

            `list[int]`: Position of each word relative to the original sentence (`pos_sent`).

            `list[str]`: Grammatical group of each word (`tags`).
        """
        return self.pos_text[index], self.n_sent[index], self.pos_sent[index], self.tags[index]

    def n_occurrences(self):
        # type: () -> int
        """
        Get number of occurrences.

        Returns:
            `int`: Number of occurrences.
        """
        return len(self.pos_text)


class StringBlockRegex(StringBlock):
    """
    Stores a regex pattern and useful information
    for working easily with the text.
    """
    def __init__(self, words,
            pos_text = None,
            n_sent = None,
            pos_sent = None,
            tags = None,
            category = "",
            reg_matched = None,
            meaning = ""
        ):
        # type:(list[str], list[int], list[int], list[list[int]], list[list[str]], str, list[list[str]], str) -> None
        """
        Args:
            `words`: List of words that forms the pattern.

            `pos_text`: Positions of the first word in the text.
            Defaults to an empty list.

            `n_sent`: Which sentences contains the pattern.
            Defaults to an empty list.

            `pos_sent`: Positions of each word relative to the original sentences.
            Defaults to an empty list.

            `tags`: Grammatical group of each word for every occurrence.
            Defaults to an empty list.

            `category`: Equivalent to the criteria.
            Defaults to an empty string.

            `reg_matched`: Strores the list of words words for every occurrence.
            Defaults to an empty list.

            `meaning`: Explanation of the regex pattern.
            Defaults to an empty string.
        """
        super().__init__(words, pos_text, n_sent, pos_sent, tags, category)

        self.reg_matched = [] if not reg_matched else reg_matched
        self.meaning = meaning


    def add_occurrence(self, pos_text, n_sent, pos_sent, tags, reg_matched):
        # type:(int, int, int|list[int], int|list[str], list[str]) -> None
        """
        Add new occurrence.

        Args:
            `pos_text`: Position of the first word in the text.

            `n_sent`: Which sentence contains the pattern.

            `pos_sent`: Position of each word relative to the original sentence.
            It is assumed that the number of positions is the same
            as the number of words.

            `tags`: Grammatical group of each word. It is assumed that
            the number of tags is the same as the number of words.

            `reg_matched`: List of words of the matched occurence.
            It is assumed that the number of items is the same as the number of words.
        """
        super().add_occurrence(pos_text, n_sent, pos_sent, tags)
        self.reg_matched.append(reg_matched)

    def get_occurrence(self, index):
        # type: (int) -> tuple(int, int, list[int], list[str], list[str])
        """
        Get `index` occurrence.

        Returns:
            `int`: Position of the first word in the text (`pos_text`).

            `int`: Which sentence contains the pattern (`n_sent`).

            `list[int]`: Position of each word relative to the original sentence (`pos_sent`).

            `list[str]`: Grammatical group of each word (`tags`).

            `list[str]`: List of words of the matched occurence (`tags`).
        """
        from_parent = super().get_occurrence(index)
        return *from_parent, self.reg_matched[index]
