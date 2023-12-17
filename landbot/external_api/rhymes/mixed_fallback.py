import transliterate

import re

from landbot.external_api import RhymesAPI
from .rimichka import RimichkaAPI
from .datamuse import DatamuseAPI


class MixedFallbackAPI(RhymesAPI):
    def __init__(self):
        self._rimichka = RimichkaAPI()
        self._datamuse = DatamuseAPI()
    
    def fetch_rhymes(self, term: str) -> list[str]:
        """
        If cyrillic or possible maymunitsa, fetch from rimichka. 
        If latin, fetch from datamuse.
        """

        if re.search("[а-яА-Я]", term):
            rhymeslist = self._rimichka.fetch_rhymes(term)
            print(f"Fetched {len(rhymeslist)} rhymes for {term}")
        else:
            rhymeslist = self._datamuse.fetch_rhymes(term)
            print(f"Fetched {len(rhymeslist)} rhymes for {term}")
            if not rhymeslist:  # possible "маймуница", try Bulgarian rhyme
                cyrillic = transliterate.translit(term, "bg")
                rhymeslist = self._rimichka.fetch_rhymes(cyrillic)
                print(f"Fetched {len(rhymeslist)} rhymes for {cyrillic}")

        return rhymeslist