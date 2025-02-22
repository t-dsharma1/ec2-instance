from collections.abc import Iterable
from typing import Optional

import Levenshtein


def match_string_exact(target: str, candidates: Iterable[str]) -> Optional[str]:
    """
    Find the string that exactly matches the target.
    Parameters:
        target (str): The string to be matched
        candidates (Iterable[str]): The candidate strings to be matched against

    Returns:
        Optional[str]: The exact string match, if any
    """
    return next((ele for ele in candidates if ele == target), None)


def match_string_fuzzy(
    target: str, candidates: Iterable[str], threshold: float = 0.6, is_case_matter: bool = False
) -> Optional[str]:
    """
    Find the string that approximately matches the target.
    Parameters:
        target (str): The string to be matched
        candidates (Iterable[str]): The candidate strings to be matched against

    Returns:
        Optional[str]: The string in candidates that most closely matches the target string,
                       and is above a given similarity threshold
    """
    if not candidates:
        return None
    if is_case_matter:
        similarities = [Levenshtein.ratio(ele, target) for ele in candidates]
    else:
        similarities = [Levenshtein.ratio(ele.lower(), target.lower()) for ele in candidates]
    max_similarity = max(similarities)
    similarities = zip(candidates, similarities)

    if max_similarity < threshold:
        return None
    else:
        closest_match = next(ele[0] for ele in similarities if ele[1] == max_similarity)
        return closest_match
