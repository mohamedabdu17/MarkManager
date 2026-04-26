from models import Course, Category, Assignment, GradingScale


def get_category_grade(category: Category) -> float | None:
    """Average percentage across all graded assignments in a category.
    Ungraded assignments are excluded — they don't count against you yet.
    Returns None if nothing in this category has been graded."""
    graded = [a for a in category.assignments if a.is_graded]
    if not graded:
        return None
    return sum(a.grade for a in graded) / len(graded)


def get_course_grade(course: Course) -> float | None:
    """Weighted average across all categories that have at least one grade.
    Categories with no grades yet are excluded entirely.

    Example: Labs=15% (graded, avg 88%), Midterm=30% (graded, 74%), Final=40% (not graded yet)
    Only Labs and Midterm count. Their combined weight is 45%.
    weighted_sum = (88 * 0.15) + (74 * 0.30) = 13.2 + 22.2 = 35.4
    current_grade = 35.4 / 0.45 = 78.67%

    This gives you your current standing based on what's been graded,
    not a projection of your final grade."""
    weighted_sum = 0.0
    total_weight = 0.0

    for category in course.categories:
        cat_grade = get_category_grade(category)
        if cat_grade is not None:
            weighted_sum += cat_grade * (category.weight / 100)
            total_weight += category.weight / 100

    if total_weight == 0:
        return None

    return weighted_sum / total_weight


def get_letter_grade(percent: float, scale: GradingScale) -> str:
    """Map a percentage to a letter grade using the provided scale.
    Delegates to GradingScale.get_letter() which walks boundaries
    sorted highest-first until it finds one the percent qualifies for."""
    return scale.get_letter(percent)


def get_semester_gpa(courses: list[Course],
                     scale: GradingScale) -> float | None:
    """Calculate term GPA across all courses that have a current grade.
    Uses a simple 4.0 scale conversion based on letter grade.
    Returns None if no courses have been graded yet.

    Note: Different universities use different GPA scales.
    This is a standard approximation — you may want to make
    this configurable later."""
    GPA_MAP = {
        "A+": 4.0, "A": 4.0, "A-": 3.7,
        "B+": 3.3, "B": 3.0, "B-": 2.7,
        "C+": 2.3, "C": 2.0, "C-": 1.7,
        "D+": 1.3, "D": 1.0, "D-": 0.7,
        "F":  0.0
    }

    grades = []
    for course in courses:
        grade = get_course_grade(course)
        if grade is not None:
            letter = get_letter_grade(grade, scale)
            gpa_points = GPA_MAP.get(letter)
            if gpa_points is not None:
                grades.append(gpa_points)

    if not grades:
        return None

    return sum(grades) / len(grades)


def get_required_grade(current_percent: float, current_weight: float,
                       target_percent: float) -> float | None:
    """Calculate what grade a student needs on remaining assessments
    to hit their target for the course. This is the 'what-if' feature.

    current_percent: their grade so far (e.g. 78.0)
    current_weight:  how much of the course has been graded (e.g. 60.0 meaning 60%)
    target_percent:  the final grade they're aiming for (e.g. 80.0)

    Returns None if the course is already fully graded (nothing remaining).
    Returns a number over 100 if the target is mathematically impossible."""
    remaining_weight = 100.0 - current_weight
    if remaining_weight <= 0:
        return None

    # Algebra: target = (current * current_weight + required * remaining) / 100
    # Solving for required:
    required = (target_percent * 100 - current_percent * current_weight) / remaining_weight
    return required


def get_completion(course: Course) -> float:
    """Percentage of the total course weight that has been graded.
    e.g. 40.0 means 40% of the course weight has grades entered.
    Used to show a progress indicator in the UI."""
    return sum(
        cat.weight for cat in course.categories
        if get_category_grade(cat) is not None
    )

def get_cumulative_gpa(course_term_pairs: list[tuple], scale: GradingScale) -> float | None:
    """Compute cumulative GPA across all semesters, counting only the most
    recent attempt for any repeated course code.

    course_term_pairs is a list of (Course, term_string) tuples,
    e.g. [(course_obj, "W2025"), (course_obj, "S2025")]

    For each unique course code, only the attempt from the chronologically
    latest semester is kept. Chronological order is determined by year first,
    then season (W < S < F within the same year)."""

    SEASON_ORDER = {"W": 1, "S": 2, "F": 3}

    def term_sort_key(term: str) -> tuple:
        year   = int(term[1:])
        season = SEASON_ORDER.get(term[0], 0)
        return (year, season)

    # For each course code, keep only the entry from the latest semester
    latest: dict[str, tuple] = {}  # code -> (Course, term_string)
    for course, term in course_term_pairs:
        code = course.code.strip().upper()
        if code not in latest:
            latest[code] = (course, term)
        else:
            existing_term = latest[code][1]
            if term_sort_key(term) > term_sort_key(existing_term):
                latest[code] = (course, term)

    # Now compute GPA using only the deduplicated courses
    best_courses = [course for course, _ in latest.values()]
    return get_semester_gpa(best_courses, scale)