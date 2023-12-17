from abc import ABC, abstractmethod


class RhymesAPI(ABC):
    """Abstract class for an API that fetches rhymes for a given word."""

    @abstractmethod
    def fetch_rhymes(self, term: str) -> list[str]:
        """Fetch rhymes for a given term."""
        ...