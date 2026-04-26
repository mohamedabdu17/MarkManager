from database import repository
from models import Course, Semester
from services.grade_service import get_categories_for_course
from services.scale_service import get_scale_for_course


# ── Semesters ──────────────────────────────────────────────────────────────────

def get_all_semesters() -> list[Semester]:
    """Return all semesters as model objects, most recent first."""
    rows = repository.get_all_semesters()
    return [
        Semester(id=row["id"], term=row["term"])
        for row in rows
    ]

def add_semester(term: str) -> Semester:
    """Create a new semester. term should follow 'F2024', 'W2025', 'S2025'.
    Raises sqlite3.IntegrityError if the term already exists."""
    new_id = repository.create_semester(term)
    return Semester(id=new_id, term=term)

def remove_semester(semester_id: int) -> None:
    """Delete a semester and everything under it via CASCADE."""
    repository.delete_semester(semester_id)


# ── Courses ────────────────────────────────────────────────────────────────────

def get_courses_for_semester(semester_id: int,
                              load_categories: bool = True) -> list[Course]:
    """Return all courses in a semester as model objects.

    load_categories controls whether assignments and categories are fetched too.
    Pass False for a lightweight list view where you only need codes and names.
    Pass True (default) when you need grade data, e.g. for the dashboard."""
    rows = repository.get_courses_for_semester(semester_id)
    courses = []

    for row in rows:
        categories = get_categories_for_course(row["id"]) if load_categories else []
        scale = get_scale_for_course(row["scale_id"]) if row["scale_id"] else None

        course = Course(
            id=row["id"],
            code=row["code"],
            name=row["name"],
            semester_id=semester_id,
            scale_id=row["scale_id"],
            categories=categories
        )
        # Attach the scale object so the UI can call scale.get_letter(grade)
        course._scale = scale
        courses.append(course)

    return courses

def get_full_course(course_id: int) -> Course | None:
    """Load a single course with all its categories and assignments.
    Returns None if the course doesn't exist.
    Used when navigating into a specific course view."""
    row = repository.get_course(course_id)
    if row is None:
        return None

    scale = get_scale_for_course(row["scale_id"]) if row["scale_id"] else None
    categories = get_categories_for_course(row["id"])

    course = Course(
        id=row["id"],
        code=row["code"],
        name=row["name"],
        semester_id=row["semester_id"],
        scale_id=row["scale_id"],
        categories=categories
    )
    course._scale = scale
    return course

def add_course(semester_id: int, code: str, name: str,
               scale_id: int | None = None) -> Course:
    """Create a new course with no categories yet."""
    new_id = repository.create_course(semester_id, code, name, scale_id)
    return Course(id=new_id, code=code, name=name,
                  semester_id=semester_id, scale_id=scale_id, categories=[])

def edit_course(course_id: int, code: str, name: str,
                scale_id: int | None = None) -> None:
    """Update a course's editable fields."""
    repository.update_course(course_id, code, name, scale_id)

def remove_course(course_id: int) -> None:
    """Delete a course and all its categories and assignments via CASCADE."""
    repository.delete_course(course_id)