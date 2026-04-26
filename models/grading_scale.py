from dataclasses import dataclass, field

@dataclass
class GradeBoundary:
    letter: str         # "A+", "A", "B+", ...
    min_percent: float  # lowest % that earns this letter
    id: int | None = None
    scale_id: int | None = None

@dataclass
class GradingScale:
    name: str
    boundaries: list[GradeBoundary] = field(default_factory=list)
    id: int | None = None

    def get_letter(self, percent: float) -> str:
        """Map a percentage to a letter grade using this scale's boundaries.
        Boundaries must be sorted highest first, which repository.py guarantees.
        We walk down until we find the first boundary the percent qualifies for.
        If somehow no boundary matches, we return 'N/A' as a safe fallback."""
        for boundary in self.boundaries:
            if percent >= boundary.min_percent:
                return boundary.letter
        return "N/A"

    def __str__(self) -> str:
        return self.name