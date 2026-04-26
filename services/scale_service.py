from database import repository
from models import GradingScale, GradeBoundary


def get_all_scales() -> list[GradingScale]:
    """Return all grading scales without their boundaries.
    Used to populate dropdowns — boundaries aren't needed just for selection."""
    rows = repository.get_all_scales()
    return [GradingScale(id=row["id"], name=row["name"]) for row in rows]

def get_scale_for_course(scale_id: int) -> GradingScale | None:
    """Return a fully loaded GradingScale with all its boundaries.
    Returns None if scale_id is None or the scale doesn't exist.
    This is what calculator.py uses to map a percentage to a letter."""
    rows = repository.get_all_scales()
    scale_row = next((r for r in rows if r["id"] == scale_id), None)
    if scale_row is None:
        return None

    boundary_rows = repository.get_boundaries_for_scale(scale_id)
    boundaries = [
        GradeBoundary(
            id=row["id"],
            scale_id=scale_id,
            letter=row["letter"],
            min_percent=row["min_percent"]
        )
        for row in boundary_rows
    ]

    return GradingScale(id=scale_id, name=scale_row["name"], boundaries=boundaries)

def add_scale(name: str, boundaries: list[tuple[str, float]]) -> GradingScale:
    """Create a new grading scale with its boundaries in one step.
    boundaries is a list of (letter, min_percent) tuples,
    e.g. [("A+", 90.0), ("A", 85.0), ...]"""
    new_id = repository.create_scale(name)
    repository.set_boundaries_for_scale(new_id, boundaries)
    boundary_objects = [
        GradeBoundary(scale_id=new_id, letter=l, min_percent=p)
        for l, p in boundaries
    ]
    return GradingScale(id=new_id, name=name, boundaries=boundary_objects)

def edit_scale_boundaries(scale_id: int,
                           boundaries: list[tuple[str, float]]) -> None:
    """Replace all boundaries for a scale. Used when the user edits
    their grading scale in settings."""
    repository.set_boundaries_for_scale(scale_id, boundaries)

def remove_scale(scale_id: int) -> None:
    """Delete a grading scale. Any courses using it will have
    scale_id set to NULL automatically via ON DELETE SET NULL."""
    repository.delete_scale(scale_id)