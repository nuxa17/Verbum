"""Color manager.

This module contains the class ColorGenerator for managing
different colors, create gradients and more.
"""

from copy import deepcopy


class ColorGenerator:
    """
    This class manages the different colors of the app
    and generate an HEX gradient of both.

    Predetermined colors are an orange-ish yellow and purple,
    with five colors in-between (seven in total).

    Constants:
        `FIRST_PRED`: First color of the gradient.
        Its value is '#ffc000'.

        `LAST_PRED`: Last color of the gradient.
        Its value is '#7030a0'.

        `STEPS_PRED`: Total of colors of the gradient.
        Its value is 7.
    """
    
    FIRST_PRED: str = "#ffc000"
    LAST_PRED: str = "#7030a0"
    STEPS_PRED: str = 7
    _gradient = ['#ffc000', '#e7a81a', '#cf9035', '#b77850', '#9f606a', '#874885', '#7030a0']

    @classmethod
    def generate_gradient(cls, first=None, last=None, steps=None):
        # type: (str, str, int) -> list[str]
        """
        Generate and set a gradient from the given colors.

        Args:
            `first` (optional): First color in HEX (#rrggbb) or RGB (r, g, b) format.
            If not specified, the current first color will be used.

            `last` (optional): Last color in HEX (#rrggbb) or RGB (r, g, b) format.
            If not specified, the current last color will be used.

            `steps` (optional): Number of total colors. If not specified or lower than 2,
            the current number of steps will be used.

        Returns:
            `list[str]`: colors of the gradient in HEX format.
        """
        if not first:
            first = cls._gradient[0]
        if isinstance(first, str):
            first = tuple(int(first[i:i+2], 16) for i in (1, 3, 5))

        if not last:
            last = cls._gradient[-1]
        if isinstance(last, str):
            last = tuple(int(last[i:i+2], 16) for i in (1, 3, 5))

        steps = steps if steps and steps >= 2 else len(cls._gradient)

        jumps = [(last[i] - first[i])/(steps-1) for i in range(3)]

        colors_hex = []
        for step in range(steps):
            color = tuple(int(c + jump*step) for c, jump in zip(first, jumps))
            colors_hex.append('#%02x%02x%02x' % color)

        cls._gradient = colors_hex
        return deepcopy(colors_hex)

    @classmethod
    def get_gradient(cls):
        # type: () -> list[str]
        """
        Get copy of the actual gradient.

        Returns:
            `list[str]`: colors of the gradient in HEX format.
        """
        return deepcopy(cls._gradient)

    @classmethod
    def reset_gradient(cls):
        # type: () -> list[str]
        """
        Restore the default values of the class.

        Returns:
            `list[str]`: colors of the gradient in HEX format.
        """
        return cls.generate_gradient(cls.FIRST_PRED, cls.LAST_PRED, cls.STEPS_PRED)

    @staticmethod
    def best_foreground(color):
        # type: (str) -> str
        """
        Gives best font color for contrast
        to the given background color.
        Returned color may be black or white.

        Args:
            `color`: Background color.

        Returns:
            `str`: contrast-friendly font color.
        """
        if isinstance(color, str):
            color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))

        rgb = []
        for idx in range(3):
            srgb = color[idx] / 255.0
            rgb.append(srgb/12.92 if srgb <= 0.03928 else ((srgb + 0.055)/1.055)**2.4)

        luminance = 0.2126*rgb[0] + 0.7152*rgb[1] + 0.0722*rgb[2]
        return "#000000" if luminance > 0.179 else "#ffffff"
