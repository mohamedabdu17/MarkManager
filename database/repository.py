import sqlite3
from typing import Optional
from database.connection import get_connection


# ── Grading Scales ─────────────────────────────────────────────────────────────

def get_all_scales() -> list[sqlite3.Row]:
    """Return all grading scales. Used to populate a dropdown when editing a course."""
    with get_connection() as conn:
        return conn.execute("SELECT * FROM grading_scales ORDER BY name").fetchall()

def create_scale(name: str) -> int:
    """Create a new grading scale. Returns the new scale's ID."""
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO grading_scales (name) VALUES (?)", (name,))
        return cur.lastrowid

def delete_scale(scale_id: int) -> None:
    """Delete a grading scale. Cascades to all its grade_boundaries.
    Courses using this scale will have scale_id set to NULL (ON DELETE SET NULL)."""
    with get_connection() as conn:
        conn.execute("DELETE FROM grading_scales WHERE id = ?", (scale_id,))


# ── Grade Boundaries ───────────────────────────────────────────────────────────

def get_boundaries_for_scale(scale_id: int) -> list[sqlite3.Row]:
    """Return all grade boundaries for a scale, highest first.
    Used by calculator.py to map a percentage to a letter grade."""
    with get_connection() as conn:
        return conn.execute(
            """SELECT * FROM grade_boundaries
               WHERE scale_id = ?
               ORDER BY min_percent DESC""",
            (scale_id,)
        ).fetchall()

def set_boundaries_for_scale(scale_id: int, boundaries: list[tuple[str, float]]) -> None:
    """Replace all boundaries for a scale in one go.
    Pass a list of (letter, min_percent) tuples.
    Deletes existing boundaries first so you don't have to diff them manually."""
    with get_connection() as conn:
        conn.execute("DELETE FROM grade_boundaries WHERE scale_id = ?", (scale_id,))
        conn.executemany(
            "INSERT INTO grade_boundaries (scale_id, letter, min_percent) VALUES (?, ?, ?)",
            [(scale_id, letter, pct) for letter, pct in boundaries]
        )


# ── Semesters ──────────────────────────────────────────────────────────────────

def get_all_semesters() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """SELECT * FROM semesters
               ORDER BY
                   CAST(SUBSTR(term, 2) AS INTEGER) DESC,
                   CASE SUBSTR(term, 1, 1)
                       WHEN 'F' THEN 3
                       WHEN 'S' THEN 2
                       WHEN 'W' THEN 1
                   END DESC"""
        ).fetchall()

def get_semester(semester_id: int) -> Optional[sqlite3.Row]:
    """Return a single semester by ID, or None if it doesn't exist."""
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM semesters WHERE id = ?", (semester_id,)
        ).fetchone()

def create_semester(term: str) -> int:
    """Create a semester. term should follow the format 'F2024', 'W2025', 'S2025'.
    Raises sqlite3.IntegrityError if the term already exists (UNIQUE constraint)."""
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO semesters (term) VALUES (?)", (term,))
        return cur.lastrowid

def delete_semester(semester_id: int) -> None:
    """Delete a semester. Cascades to all its courses, which cascade
    to their categories, which cascade to their assignments."""
    with get_connection() as conn:
        conn.execute("DELETE FROM semesters WHERE id = ?", (semester_id,))


# ── Courses ────────────────────────────────────────────────────────────────────

def get_courses_for_semester(semester_id: int) -> list[sqlite3.Row]:
    """Return all courses in a semester, alphabetically by code."""
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM courses WHERE semester_id = ? ORDER BY code",
            (semester_id,)
        ).fetchall()

def get_course(course_id: int) -> Optional[sqlite3.Row]:
    """Return a single course by ID, or None if it doesn't exist."""
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM courses WHERE id = ?", (course_id,)
        ).fetchone()

def create_course(semester_id: int, code: str, name: str,
                  scale_id: Optional[int] = None) -> int:
    """Create a course. scale_id is optional — NULL means no grading scale assigned yet."""
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO courses (semester_id, scale_id, code, name)
               VALUES (?, ?, ?, ?)""",
            (semester_id, scale_id, code, name)
        )
        return cur.lastrowid

def update_course(course_id: int, code: str, name: str,
                  scale_id: Optional[int] = None) -> None:
    """Update a course's editable fields. Call this when the user
    edits course details in the UI."""
    with get_connection() as conn:
        conn.execute(
            """UPDATE courses SET code = ?, name = ?, scale_id = ?
               WHERE id = ?""",
            (code, name, scale_id, course_id)
        )

def delete_course(course_id: int) -> None:
    """Delete a course. Cascades to its categories and assignments."""
    with get_connection() as conn:
        conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))


# ── Categories ─────────────────────────────────────────────────────────────────

def get_categories_for_course(course_id: int) -> list[sqlite3.Row]:
    """Return all categories for a course, ordered by weight descending
    so heavier items (Final, Midterm) appear at the top."""
    with get_connection() as conn:
        return conn.execute(
            """SELECT * FROM categories
               WHERE course_id = ?
               ORDER BY weight DESC""",
            (course_id,)
        ).fetchall()

def get_category(category_id: int) -> Optional[sqlite3.Row]:
    """Return a single category by ID, or None if it doesn't exist."""
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM categories WHERE id = ?", (category_id,)
        ).fetchone()

def create_category(course_id: int, name: str, weight: float) -> int:
    """Create a category (e.g. Labs, Midterm, Final) with its combined weight."""
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO categories (course_id, name, weight) VALUES (?, ?, ?)",
            (course_id, name, weight)
        )
        return cur.lastrowid

def update_category(category_id: int, name: str, weight: float) -> None:
    """Update a category's name or weight. Recalculating per-item weights
    happens automatically in calculator.py since they're never stored."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE categories SET name = ?, weight = ? WHERE id = ?",
            (name, weight, category_id)
        )

def delete_category(category_id: int) -> None:
    """Delete a category. Cascades to all assignments under it."""
    with get_connection() as conn:
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))


# ── Assignments ────────────────────────────────────────────────────────────────

def get_assignments_for_category(category_id: int) -> list[sqlite3.Row]:
    """Return all assignments in a category, ordered by name.
    Per-item weight is not stored — compute it as category.weight / len(results)."""
    with get_connection() as conn:
        return conn.execute(
            """SELECT * FROM assignments
               WHERE category_id = ?
               ORDER BY name""",
            (category_id,)
        ).fetchall()

def get_assignments_for_course(course_id: int) -> list[sqlite3.Row]:
    """Return all assignments across all categories for a course.
    Joins through categories so the caller also gets category name and weight,
    which are needed to compute per-item weights in one pass."""
    with get_connection() as conn:
        return conn.execute(
            """SELECT
                   a.id,
                   a.name,
                   a.grade,
                   a.category_id,
                   c.name  AS category_name,
                   c.weight AS category_weight
               FROM assignments a
               JOIN categories c ON a.category_id = c.id
               WHERE c.course_id = ?
               ORDER BY c.weight DESC, a.name""",
            (course_id,)
        ).fetchall()

def create_assignment(category_id: int, name: str,
                      grade: Optional[float] = None) -> int:
    """Create an assignment. grade is None if not yet graded."""
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO assignments (category_id, name, grade) VALUES (?, ?, ?)",
            (category_id, name, grade)
        )
        return cur.lastrowid

def update_assignment_grade(assignment_id: int, grade: Optional[float]) -> None:
    """Update the grade on an assignment. Pass None to mark it as ungraded."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE assignments SET grade = ? WHERE id = ?",
            (grade, assignment_id)
        )

def update_assignment_name(assignment_id: int, name: str) -> None:
    """Rename an assignment."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE assignments SET name = ? WHERE id = ?",
            (name, assignment_id)
        )

def delete_assignment(assignment_id: int) -> None:
    """Delete an assignment. After deleting, per-item weights for the remaining
    assignments in the same category automatically recalculate in calculator.py
    since they're derived from COUNT(*), not stored."""
    with get_connection() as conn:
        conn.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))