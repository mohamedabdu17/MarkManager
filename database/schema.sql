-- Grading scale definitions (e.g. "Default", "UofT", "McGill")
CREATE TABLE IF NOT EXISTS grading_scales (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT    NOT NULL UNIQUE
);

-- Individual letter grade boundaries within a scale.
-- Example row: scale_id=1, letter="A+", min_percent=90.0
-- The letter grade for a given % is the highest boundary <= that %.
CREATE TABLE IF NOT EXISTS grade_boundaries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    scale_id    INTEGER NOT NULL REFERENCES grading_scales(id) ON DELETE CASCADE,
    letter      TEXT    NOT NULL,
    min_percent REAL    NOT NULL
);

-- A semester is just a term code. The ID is internal only.
-- Display order in the UI is handled by sorting the term string.
CREATE TABLE IF NOT EXISTS semesters (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    term    TEXT    NOT NULL UNIQUE  -- "F2024", "W2025", "S2025"
);

-- A course belongs to one semester and optionally uses a grading scale.
-- Current grade and letter grade are always calculated, never stored.
CREATE TABLE IF NOT EXISTS courses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_id INTEGER NOT NULL REFERENCES semesters(id) ON DELETE CASCADE,
    scale_id    INTEGER REFERENCES grading_scales(id) ON DELETE SET NULL,
    code        TEXT    NOT NULL,    -- "ECE101", "MAT137"
    name        TEXT    NOT NULL     -- "Intro to Electrical Eng.", "Calculus"
);

-- A category belongs to one course and holds the combined weight for
-- all assignments under it. Per-item weight = this weight / item count.
CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id   INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    name        TEXT    NOT NULL,    -- "Lab", "Midterm", "Final", "Assignment"
    weight      REAL    NOT NULL     -- combined %, e.g. 15.0 for all labs
);

-- An assignment belongs to a category (and transitively to a course).
-- grade is the student's percentage on this item. NULL = not graded yet.
-- Individual weight is derived: category.weight / COUNT(*) in this category.
CREATE TABLE IF NOT EXISTS assignments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    name        TEXT    NOT NULL,    -- "Lab 1", "Lab 2", "Midterm"
    grade       REAL                 -- NULL = not yet graded, 0.0-100.0
);

-- Insert a sensible default grading scale so new users have something
-- to start with immediately without any setup.
INSERT OR IGNORE INTO grading_scales (name) VALUES ('Default');
INSERT OR IGNORE INTO grade_boundaries (scale_id, letter, min_percent) VALUES
    (1, 'A+', 90.0),
    (1, 'A',  85.0),
    (1, 'A-', 80.0),
    (1, 'B+', 77.0),
    (1, 'B',  73.0),
    (1, 'B-', 70.0),
    (1, 'C+', 67.0),
    (1, 'C',  63.0),
    (1, 'C-', 60.0),
    (1, 'D+', 57.0),
    (1, 'D',  53.0),
    (1, 'D-', 50.0),
    (1, 'F',   0.0);