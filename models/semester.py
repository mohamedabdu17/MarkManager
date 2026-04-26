from dataclasses import dataclass

# Maps the term prefix to a full season name for display purposes.
SEASON_LABELS = {"F": "Fall", "W": "Winter", "S": "Summer"}

@dataclass
class Semester:
    term: str           # "F2024", "W2025", "S2025"
    id: int | None = None

    @property
    def season(self) -> str:
        """Returns "Fall", "Winter", or "Summer"."""
        prefix = self.term[0].upper()
        return SEASON_LABELS.get(prefix, "Unknown")

    @property
    def year(self) -> str:
        """Returns the year portion as a string, e.g. "2024"."""
        return self.term[1:]

    @property
    def display_name(self) -> str:
        """Returns a human-readable label e.g. "Fall 2024"."""
        return f"{self.season} {self.year}"

    def __str__(self) -> str:
        return self.display_name