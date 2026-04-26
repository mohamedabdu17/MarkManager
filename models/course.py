from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.category import Category

@dataclass
class Course:
    code: str               # "ELE202"
    name: str               # "Electric Circuit Analysis"
    semester_id: int
    scale_id: int | None = None
    categories: list["Category"] = field(default_factory=list)
    id: int | None = None

    @property
    def current_grade(self) -> float | None:
        """Weighted average across all graded assignments in all categories.
        Returns None if nothing has been graded yet at all.
        This is the same calculation calculator.py does — having it here
        lets the UI access it directly from the model when it already has
        all the data loaded, without calling a service."""
        total_weight_used = 0.0
        weighted_sum = 0.0

        for category in self.categories:
            cat_grade = category.current_grade
            if cat_grade is not None:
                weighted_sum += cat_grade * (category.weight / 100)
                total_weight_used += category.weight / 100

        if total_weight_used == 0:
            return None

        # Scale to the portion of the course graded so far.
        # e.g. if only 40% of the course weight has been graded
        # and the student scored 80% on it, current grade = 80%.
        return weighted_sum / total_weight_used

    @property
    def completion(self) -> float:
        """Percentage of the total course weight that has been graded.
        e.g. 40.0 means 40% of the course has grades entered so far."""
        return sum(
            cat.weight for cat in self.categories
            if cat.current_grade is not None
        )

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"