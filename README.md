# MarkManager

A desktop grade tracking app for university students, built with Python and CustomTkinter. Track your courses, assignments, and categories across semesters — with automatic weighted grade calculations, GPA tracking, and a what-if calculator to project the grades you need to hit your targets.

---

## Features

- **Semester management** — Organize courses by semester using Fall, Winter, and Summer terms
- **Course tracking** — Store course codes, names, and optionally assign a grading scale per course
- **Category-based weighting** — Define categories (Labs, Midterm, Final, etc.) with a combined weight, and let the app automatically divide that weight evenly across all assignments in the category
- **Automatic grade calculations** — Current course grade and letter grade are always computed from live data, never stored
- **Term & Cumulative GPA** — Term GPA updates instantly when switching semesters; Cumulative GPA accounts for course retakes by always using the most recent attempt
- **What-if calculator** — Per-course calculator that tells you exactly what you need on remaining work to hit a target grade
- **Finals calculator** — Standalone calculator on the dashboard for quick what-if scenarios without needing to open a course
- **Grading scales** — Define custom letter grade boundaries per university or course, with a sensible default scale included out of the box
- **Course retake handling** — Retaking a course in a later semester automatically uses the newer grade for CGPA calculations
- **Clean dark UI** — Colour-coded grade labels, category headings, progress bars, and confirmation prompts for destructive actions

---

## Project Structure

The project follows a strict layered architecture to keep concerns separated and prevent circular imports. Data flows in one direction only: `database → models → services → ui`.

```
markmanager/
│
├── database/
│   ├── __init__.py         # init_db() — runs schema.sql on startup
│   ├── connection.py       # SQLite connection management
│   ├── repository.py       # All SQL queries — the only layer that touches the DB
│   └── schema.sql          # CREATE TABLE statements + default grading scale seed
│
├── models/
│   ├── __init__.py
│   ├── semester.py         # Semester dataclass with display_name property
│   ├── course.py           # Course dataclass with current_grade and completion
│   ├── category.py         # Category dataclass with item_weight and current_grade
│   ├── assignment.py       # Assignment dataclass with is_graded property
│   └── grading_scale.py    # GradingScale + GradeBoundary dataclasses
│
├── services/
│   ├── __init__.py
│   ├── course_service.py   # Semester and course CRUD, builds nested Course objects
│   ├── grade_service.py    # Category and assignment CRUD
│   ├── scale_service.py    # Grading scale and boundary management
│   └── calculator.py       # Grade calculations, GPA, what-if, retake deduplication
│
├── ui/
│   ├── __init__.py
│   ├── app.py              # CTk root window, persistent frames, view navigation
│   ├── utils.py            # Shared helpers: mark_color, display_error, back_button
│   ├── views/
│   │   ├── dashboard.py        # Home screen — semester dropdown, course list, GPA
│   │   ├── course_view.py      # Per-course view with category headings and what-if
│   │   ├── add_course.py
│   │   ├── add_category.py     # Preset names + remaining weight display
│   │   ├── add_assignment.py
│   │   ├── add_semester.py     # Season picker + year entry
│   │   ├── edit_courses.py     # Rename/drop courses with confirmation
│   │   ├── edit_categories.py  # Edit weights, rename/drop assignments
│   │   └── edit_grade.py       # Edit grade or drop an assignment
│   └── components/
│       ├── finals_calculator.py  # Standalone sidebar calculator widget
│       └── gpa_panel.py          # Term + cumulative GPA display with caching
│
├── assets/
│   └── back.png            # Back arrow icon
│
├── .env                    # Local config (never committed)
├── .env.example            # Template for required environment variables
├── .gitignore
├── requirements.txt
└── main.py                 # Entry point — runs init_db() then launches the app
```

---

## Download

Go to the [Releases](https://github.com/mohamedabdu17/MarkManager/releases) 
page and download the latest `MarkManager.exe`. No installation required — 
just run it.

Your data is saved automatically at:
`C:\Users\YOU\AppData\Roaming\MarkManager\markmanager.db`

## For Developers

If you want to run from source:

1. Clone the repo
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `.venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python main.py`

## Dependencies

| Package | Purpose |
|---|---|
| `customtkinter` | Modern themed UI framework built on tkinter |
| `Pillow` | Image loading for the back arrow icon |
| `python-dotenv` | Loads environment variables from `.env` |

Install all at once:
```bash
pip install customtkinter Pillow python-dotenv
```

---

## Usage

### Adding your first semester
Click **Add Semester** in the sidebar, select a season (Fall / Winter / Summer) and enter a 4-digit year. Semesters are displayed in proper academic calendar order.

### Setting up a course
Select a semester from the dropdown, click **Add Course**, and enter the course code and name. Optionally assign a grading scale if your university uses non-standard letter grade cutoffs.

### Building your course outline
Open a course and click **Add Category** to define your assessment structure — for example, Labs at 15%, Midterm at 30%, Final at 40%, Assignments at 15%. The app enforces that weights don't exceed 100%.

### Adding assignments
Click **Add Assignment**, select the category it belongs to, and give it a name. Leave the grade blank if you haven't received it yet — the app will exclude ungraded items from your current average automatically.

### Entering grades
From the course view, click **Edit Grade** on any assignment to enter or update your percentage. You can also drop the assignment from this screen.

### Retaking a course
Just add the course again under the new semester as normal. The Cumulative GPA calculation automatically picks the most recent attempt for each course code, so your CGPA will reflect the retake correctly.

---

## License

MIT License. See `LICENSE` for details.
