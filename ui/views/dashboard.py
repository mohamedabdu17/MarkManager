import customtkinter as ctk
from ui.app import FONT_TITLE, FONT_COURSE, FONT_BUTTON, FONT_POPUP
from ui.utils import mark_color, display_error, sidebar_title
from ui.components.finals_calculator import FinalsCalculator
from ui.components.gpa_panel import GPAPanel
from services.course_service import get_all_semesters, add_semester, get_courses_for_semester
from services.calculator import get_course_grade, get_letter_grade, get_semester_gpa
from services.scale_service import get_all_scales


class DashboardView:
    def __init__(self, app, sidebar, content, active_semester_id=None):
        self.app      = app
        self.sidebar  = sidebar
        self.content  = content
        self.semesters = get_all_semesters()

        # Use the passed-in semester ID if provided, otherwise default to first
        if active_semester_id is not None:
            match = next((s for s in self.semesters if s.id == active_semester_id), None)
            self.current_semester = match if match else (self.semesters[0] if self.semesters else None)
        else:
            self.current_semester = self.semesters[0] if self.semesters else None

        self._build_sidebar()
        self._build_content()

    # ── Sidebar ────────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sidebar_title(self.sidebar, FONT_TITLE)

        # Finals calculator widget lives in the sidebar just like before
        FinalsCalculator(self.sidebar, FONT_COURSE, FONT_BUTTON, FONT_POPUP)

        ctk.CTkButton(
            master=self.sidebar, text="Add Course",
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=self._show_add_course
        ).pack(pady=10)

        ctk.CTkButton(
            master=self.sidebar, text="Edit Courses",
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=self._show_edit_courses
        ).pack()

        ctk.CTkButton(
            master=self.sidebar, text="Add Semester",
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=self._show_add_semester
        ).pack(pady=10)

        self._refresh_gpa()

    # ── Content ────────────────────────────────────────────────────────────────

    def _build_content(self):
        # Semester dropdown — term strings formatted as display names
        sem_values = [s.display_name for s in self.semesters] if self.semesters else ["No Semesters"]
        current_val = self.current_semester.display_name if self.current_semester else "No Semesters"

        sem_dropdown = ctk.CTkOptionMenu(
            master=self.content,
            values=sem_values,
            font=FONT_BUTTON, fg_color="#858585",
            button_color="#626262", button_hover_color="#c3c0c0",
            command=self._on_semester_change
        )
        sem_dropdown.set(current_val)
        sem_dropdown.place(relx=0.035, rely=0.04)

        ctk.CTkLabel(
            master=self.content, text="Courses", font=FONT_TITLE
        ).pack(pady=20)

        self._render_courses()

    def _render_courses(self):
        # Destroy old course cards if re-rendering
        for widget in self.content.winfo_children():
            if hasattr(widget, "_is_course_card"):
                widget.destroy()

        if not self.current_semester:
            ctk.CTkLabel(
                master=self.content, text="No semesters yet — add one to get started.",
                font=FONT_COURSE
            ).pack(pady=225)
            return

        courses = get_courses_for_semester(self.current_semester.id, load_categories=True)

        if not courses:
            lbl = ctk.CTkLabel(
                master=self.content, text="No courses yet — add one using the sidebar.",
                font=FONT_COURSE
            )
            lbl._is_course_card = True
            lbl.pack(pady=225)
            return

        scales = get_all_scales()
        default_scale = scales[0] if scales else None

        for course in courses:
            grade   = get_course_grade(course)
            scale   = getattr(course, "_scale", default_scale)
            letter  = get_letter_grade(grade, scale) if grade is not None and scale else "N/A"
            completion = sum(cat.weight for cat in course.categories if cat.current_grade is not None)

            card = ctk.CTkFrame(
                master=self.content, height=130, 
                corner_radius=20, fg_color="#333333"
            )
            
            card._is_course_card = True
            card.pack(fill="x", padx=10, pady=10)
            card.pack_propagate(False)

            # Grade label — right side, coloured by threshold
            grade_text = f"{round(grade, 1)}% ({letter})" if grade is not None else "No grades yet"
            mark_lbl = ctk.CTkLabel(master=card, text=grade_text, font=FONT_COURSE)
            mark_lbl.pack(side="right", padx=15)
            if grade is not None:
                mark_color(mark_lbl, grade)

            # Course name — top left
            ctk.CTkLabel(
                master=card, text=f"{course.code} — {course.name}", font=FONT_COURSE
            ).pack(pady=15, padx=15, anchor="nw")

            # Progress bar — shows how much of the course has been graded
            progress_frame = ctk.CTkFrame(master=card, fg_color="transparent")
            progress_frame.pack(padx=15, anchor="sw", fill="x")

            ctk.CTkProgressBar(
                master=progress_frame, width=200, height=8,
                progress_color="#858585"
            ).pack(side="left", pady=(0, 10))
            # Set progress value (0.0 – 1.0)
            progress_frame.winfo_children()[0].set(completion / 100)

            ctk.CTkLabel(
                master=progress_frame,
                text=f"{int(completion)}% graded",
                font=FONT_BUTTON
            ).pack(side="left", padx=8, pady=(0, 10))

            # Open Course button — bottom left
            ctk.CTkButton(
                master=card, text="Open Course",
                font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
                command=lambda c=course: self._open_course(c)
            ).pack(padx=15, anchor="sw", pady=(0, 10))

    # ── Semester handling ──────────────────────────────────────────────────────

    def _on_semester_change(self, display_name: str):
        match = next((s for s in self.semesters if s.display_name == display_name), None)
        if match:
            self.current_semester = match
            self._render_courses()
            self._refresh_gpa()

    def _refresh_gpa(self):
        if hasattr(self, "_gpa_widget") and self._gpa_widget is not None:
            self._gpa_widget.destroy()
        self._gpa_widget = GPAPanel(self.sidebar, self.current_semester, self.semesters, FONT_COURSE)

    # ── Navigation ─────────────────────────────────────────────────────────────

    def _open_course(self, course):
        from ui.views.course_view import CourseView
        self.app.show_view(CourseView, course_id=course.id)

    def _show_add_course(self):
        from ui.views.add_course import AddCourseView
        self.app.show_view(AddCourseView, semester=self.current_semester)

    def _show_edit_courses(self):
        from ui.views.edit_courses import EditCoursesView
        self.app.show_view(EditCoursesView, semester=self.current_semester)

    def _show_add_semester(self):
        from ui.views.add_semester import AddSemesterView
        self.app.show_view(AddSemesterView)