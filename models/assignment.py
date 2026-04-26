from dataclasses import dataclass

@dataclass
class Assignment:
    name: str
    category_id: int
    grade: float | None = None  # None = not graded yet, 0.0-100.0 otherwise
    id: int | None = None

    @property
    def is_graded(self) -> bool:
        return self.grade is not None

    def __str__(self) -> str:
        return self.name