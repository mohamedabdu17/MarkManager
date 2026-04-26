from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.assignment import Assignment

@dataclass
class Category:
    name: str           # "Lab", "Midterm", "Final", "Assignment"
    weight: float       # combined % for all items, e.g. 15.0
    course_id: int
    assignments: list["Assignment"] = field(default_factory=list)
    id: int | None = None

    @property
    def item_weight(self) -> float | None:
        """The weight of each individual assignment in this category.
        Returns None if there are no assignments yet to avoid division by zero."""
        if not self.assignments:
            return None
        return self.weight / len(self.assignments)

    @property
    def current_grade(self) -> float | None:
        """Average percentage across all graded assignments in this category.
        Ungraded assignments (grade=None) are excluded from the average —
        they don't drag your grade down, they just aren't counted yet."""
        graded = [a for a in self.assignments if a.is_graded]
        if not graded:
            return None
        return sum(a.grade for a in graded) / len(graded)

    @property
    def is_complete(self) -> bool:
        """True if every assignment in this category has been graded."""
        return bool(self.assignments) and all(a.is_graded for a in self.assignments)

    def __str__(self) -> str:
        return self.name