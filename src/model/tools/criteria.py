"""Criteria analyzer.

This module contains methods for analyzing different manipulation criterias.
"""
from typing import Any


def get_criterias(categories_info, tag_counters, category_counters, ranking):
    # type: (dict[str, dict], dict[str, int], dict[str, int], list[str]) -> dict[str, dict]
    """
    Analyze all criterias from `categories_info`.

    Args:
        `categories_info`: The keys are the criteria title,
        the values are dictionaries with this keys:
            + "against" (list[str]): Tags to compare to. "*" uses all.
            + "ratios" (dict[str, int]): The keys are numbers from 0-100,
            the values are their correspondig ranking number.
            + "criteria" (str): Explanation of the criteria.
        
        `tag_counters`: The keys are tags, the values the number of appearances.

        `category_counters`: The keys are categories, the values the total of matches.

        `ranking`: List of manipulation ranks.

    Returns:
        `dict[str, dict]`: Dictionaries with results and information for each criteria.
    """
    criterias = {}
    for category, info in categories_info.items():
        found = category_counters[category]
        criterias[category] = get_generic_criteria(info, tag_counters, found, ranking)

    return criterias

def get_generic_criteria(info, tag_counters, found, ranking):
    # type: (dict[str, Any], dict[str, int], int, list[str]) -> dict[str, Any]
    """
    Analyze a single criteria.

    Args:
        `info`: Dictionary with information of the category.
        Must contain this keys:
            + "against" (list[str]): Tags to compare to. "*" uses all.
            + "ratios" (dict[str, int]): The keys are percentages from 0-100,
            the values are their corresponding ranking number for such percentages.
            + "criteria" (str): Explanation of the criteria.

        `tag_counters`: The keys are tags, the values the number of appearances.

        `found`: Number of matches for the given category.

        `ranking`: List of manipulation ranks.

    Returns:
        `dict[str, Any]`:        
            + "criteria": Explanation of the criteria. 
            + "found": Number of matches for the given category.
            + "against": Total number of words for the "against" tags.
            + "percentage": Manipulation ratio.
            + "rank": Manipulation rank value.
            + "str": Manipulation rank string (from `ranking`).
    """
    tags = info["against"]

    against = 0
    if "*" in tags:
        against = sum(tag_counters.values())
    else:
        for tag in tags:
            against += tag_counters.get(tag)

    percentage = 0.00
    if against > 0:
        percentage = round(found/against * 100, 2)

    rank = 0
    for k, v in info["ratios"].items():
        if int(k) <= percentage:
            rank = v
        else:
            break

    result = {
        "criteria": info["criteria"],
        "found": found,
        "against": against,
        "percentage": percentage,
        "rank": rank,
        "str": ranking[rank]
        }
    return result
