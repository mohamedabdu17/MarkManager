from database import repository
from models import Assignment, Category


# ── Categories ─────────────────────────────────────────────────────────────────

def get_categories_for_course(course_id: int) -> list[Category]:
    """Fetch all categories for a course, with their assignments nested inside.
    This is the main function the UI calls when loading a course view —
    it returns everything needed to render the full grade breakdown."""
    rows = repository.get_categories_for_course(course_id)
    categories = []

    for row in rows:
        assignments = get_assignments_for_category(row["id"])
        category = Category(
            id=row["id"],
            name=row["name"],
            weight=row["weight"],
            course_id=course_id,
            assignments=assignments
        )
        categories.append(category)

    return categories

def add_category(course_id: int, name: str, weight: float) -> Category:
    """Create a new category and return it as a model object.
    The UI can immediately append it to its local list without refetching."""
    new_id = repository.create_category(course_id, name, weight)
    return Category(id=new_id, name=name, weight=weight,
                    course_id=course_id, assignments=[])

def edit_category(category_id: int, name: str, weight: float) -> None:
    """Update a category's name or weight.
    Per-item weights recalculate automatically since they're derived."""
    repository.update_category(category_id, name, weight)

def remove_category(category_id: int) -> None:
    """Delete a category and all its assignments via CASCADE."""
    repository.delete_category(category_id)


# ── Assignments ────────────────────────────────────────────────────────────────

def get_assignments_for_category(category_id: int) -> list[Assignment]:
    """Fetch all assignments in a category as model objects."""
    rows = repository.get_assignments_for_category(category_id)
    return [
        Assignment(
            id=row["id"],
            name=row["name"],
            grade=row["grade"],
            category_id=category_id
        )
        for row in rows
    ]

def add_assignment(category_id: int, name: str,
                   grade: float | None = None) -> Assignment:
    """Add a new assignment to a category.
    grade is None by default since assignments are often added before
    the student receives their mark."""
    new_id = repository.create_assignment(category_id, name, grade)
    return Assignment(id=new_id, name=name, grade=grade, category_id=category_id)

def edit_assignment_grade(assignment_id: int, grade: float | None) -> None:
    """Update the grade on an assignment. Pass None to mark it as ungraded."""
    repository.update_assignment_grade(assignment_id, grade)

def edit_assignment_name(assignment_id: int, name: str) -> None:
    """Rename an assignment."""
    repository.update_assignment_name(assignment_id, name)

def remove_assignment(assignment_id: int) -> None:
    """Delete an assignment. The remaining assignments in its category
    will have their per-item weights recalculate automatically next
    time item_weight is accessed on the Category model."""
    repository.delete_assignment(assignment_id)