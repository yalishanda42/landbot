"""Pure functions, encapsulating the functioinality of the bot messaging and commands."""

import transliterate

import random
import re

from landbot.external_api import RhymesAPI
from landbot.external_api.rhymes import MixedFallbackAPI
from landbot.data.songs import LandcoreSongs

def rhymes(
    term: str, 
    max_rhymes: int,
    api: RhymesAPI
) -> list[str] | None:
    """Fetch at most `max_rhymes` rhymes for a given term."""
    result = api.fetch_rhymes(term)

    if not result: 
        return None

    return result[:max_rhymes]

def ping() -> str:
    return random.choice(LandcoreSongs.QUOTES)

def random_link():
    return random.choice(LandcoreSongs.URLS)

def link( name: str):
    # translit + lowercase

    if re.match("[а-яА-Я]", name):
        name = transliterate.translit(name, "bg", reversed=True)

    name = name.lower()

    # find full match

    full_match_index = next(
        (
            i for i, names_tuple in enumerate(LandcoreSongs.NAMES)
            if names_tuple[0] == name
        ),
        None  # default if not found
    )

    if full_match_index is not None:
        return LandcoreSongs.URLS[full_match_index]
    
    # find partial matches
    
    partial_match_indices = [
        i for i, names_tuple in enumerate(LandcoreSongs.NAMES)
        if name in names_tuple[1:]
    ]

    if not partial_match_indices:
        return "хм? пробвай пак"

    if len(partial_match_indices) == 1:
        return LandcoreSongs.URLS[partial_match_indices[0]]

    result = "\n".join(
        "[{0}]({1})".format(
            LandcoreSongs.NAMES[i][0],
            LandcoreSongs.URLS[i]
        )
        for i in partial_match_indices
    )

    return f"Може би имахте предвид:\n{result}"