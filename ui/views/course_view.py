import customtkinter as ctk
from ui.app import FONT_TITLE, FONT_COURSE, FONT_BUTTON, FONT_POPUP, BACK_ARROW
from ui.utils import mark_color, display_error, sidebar_title, back_button
from services.course_service import get_full_course
from services.calculator import get_course_grade, get_letter_grade, get_required_grade, get_completion
from services.scale_service import get_all_scales


class CourseView:
    def __init__(self, app, sidebar, content, course_id: int):
        self.app       = app
        self.sidebar   = sidebar
        self.content   = content
        self.course    = get_full_course(course_id)
        self._build_sidebar()
        self._build_content()

    def _go_dashboard(self):
        from ui.views.dashboard import DashboardView
        self.app.show_view(DashboardView, active_semester_id=self.course.semester_id)

    # ── Sidebar ────────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sidebar_title(self.sidebar, FONT_TITLE)

        ctk.CTkButton(
            master=self.sidebar, text="Add Category",
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=self._show_add_category
        ).pack(pady=(0, 10))

        ctk.CTkButton(
            master=self.sidebar, text="Add Assignment",
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=self._show_add_assignment
        ).pack(pady=(0, 10))

        ctk.CTkButton(
            master=self.sidebar, text="Edit Categories",
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=self._show_edit_categories
        ).pack(pady=(0, 10))

        # What-if calculator — smarter than the old finals calculator
        # because it knows the actual weights from the database
        self._build_whatif_panel()

    def _build_whatif_panel(self):
        """Inline what-if calculator using actual course data."""
        grade   = get_course_grade(self.course)
        completion = get_completion(self.course)

        panel = ctk.CTkFrame(master=self.sidebar, width=300, height=220, corner_radius=20)
        panel.pack(pady=15)
        panel.pack_propagate(False)

        ctk.CTkLabel(master=panel, text="What-If Calculator", font=FONT_COURSE).pack(pady=10)

        ctk.CTkLabel(master=panel, text="Target Grade (%):", font=FONT_POPUP).pack()
        target_entry = ctk.CTkEntry(master=panel)
        target_entry.pack()

        if grade is not None:
            ctk.CTkLabel(
                master=panel,
                text=f"Current: {round(grade, 1)}% ({int(completion)}% graded)",
                font=FONT_BUTTON
            ).pack(pady=5)

        result_label = ctk.CTkLabel(master=panel, text="", font=FONT_POPUP, wraplength=260, justify="center")
        result_label.pack()

        def calculate():
            try:
                target = float(target_entry.get())
                if not (0 <= target <= 100):
                    raise ValueError
                if grade is None:
                    result_label.configure(text="No grades entered yet.", text_color="gray")
                    return
                needed = get_required_grade(grade, completion, target)
                if needed is None:
                    result_label.configure(text="Course is fully graded.", text_color="gray")
                elif needed <= 0:
                    result_label.configure(
                        text="You've already achieved that target!",
                        text_color="#4d9e3a"
                    )
                elif needed > 100:
                    result_label.configure(
                        text=f"You'd need {round(needed, 1)}% — not achievable.",
                        text_color="#c91c1c"
                    )
                else:
                    result_label.configure(
                        text=f"You need {round(needed, 1)}% on remaining work.",
                        text_color="#92c91c"
                    )
            except ValueError:
                result_label.configure(text="Enter a number between 0–100.", text_color="#f13636")

        ctk.CTkButton(
            master=panel, text="Calculate", width=100, height=28,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=calculate
        ).pack(pady=8)

    # ── Content ────────────────────────────────────────────────────────────────

    def _build_content(self):
        back_button(self.content, BACK_ARROW, self._go_dashboard)

        grade  = get_course_grade(self.course)
        scales = get_all_scales()
        scale  = getattr(self.course, "_scale", scales[0] if scales else None)
        letter = get_letter_grade(grade, scale) if grade is not None and scale else "N/A"

        # Course title + overall grade
        ctk.CTkLabel(
            master=self.content,
            text=f"{self.course.code} — {self.course.name}",
            font=FONT_TITLE
        ).pack(anchor="n", pady=(50, 5))

        grade_text = f"{round(grade, 1)}%  ({letter})" if grade is not None else "No grades entered yet"
        grade_lbl = ctk.CTkLabel(master=self.content, text=grade_text, font=FONT_COURSE)
        grade_lbl.pack(anchor="n", pady=(0, 20))
        if grade is not None:
            mark_color(grade_lbl, grade)

        # Categories with assignment rows under each heading
        if not self.course.categories:
            ctk.CTkLabel(
                master=self.content,
                text="No categories yet — add one using the sidebar.",
                font=FONT_COURSE
            ).pack(pady=200)
            return

        for category in self.course.categories:
            self._render_category(category)

    def _render_category(self, category):
        """Render a category heading card followed by its assignment rows."""
        cat_grade = category.current_grade

        # Category heading card — darker than assignment rows
        heading = ctk.CTkFrame(master=self.content, corner_radius=15, fg_color="#2a2a2a")
        heading.pack(fill="x", padx=10, pady=(15, 2))

        ctk.CTkLabel(
            master=heading,
            text=f"{category.name}",
            font=FONT_COURSE
        ).pack(side="left", padx=15, pady=10)

        # Category weight + average on the right
        weight_text = f"{category.weight}% of course"
        ctk.CTkLabel(master=heading, text=weight_text, font=FONT_BUTTON).pack(side="right", padx=10, pady=10)

        avg_text = f"Avg: {round(cat_grade, 1)}%" if cat_grade is not None else "No grades yet"
        avg_lbl = ctk.CTkLabel(master=heading, text=avg_text, font=FONT_BUTTON)
        avg_lbl.pack(side="right", padx=15, pady=10)
        if cat_grade is not None:
            mark_color(avg_lbl, cat_grade)

        # Assignment rows under the heading
        if not category.assignments:
            ctk.CTkLabel(
                master=self.content,
                text="  No assignments yet", font=FONT_BUTTON
            ).pack(anchor="w", padx=25)
        else:
            item_weight = category.item_weight
            for assignment in category.assignments:
                self._render_assignment(assignment, item_weight)

    def _render_assignment(self, assignment, item_weight: float | None):
        """Render one assignment row card."""
        row = ctk.CTkFrame(master=self.content, height=80, corner_radius=12, fg_color="#333333")
        row.pack(fill="x", padx=25, pady=3)
        row.pack_propagate(False)

        # Grade on the far right
        grade_text = f"{assignment.grade}%" if assignment.is_graded else "—"
        grade_lbl = ctk.CTkLabel(master=row, text=grade_text, font=FONT_COURSE)
        grade_lbl.pack(side="right", padx=15)
        if assignment.is_graded:
            mark_color(grade_lbl, assignment.grade)

        # Item weight (derived) to the left of grade
        weight_text = f"{round(item_weight, 1)}%" if item_weight is not None else ""
        ctk.CTkLabel(master=row, text=weight_text, font=FONT_BUTTON).pack(side="right", padx=30)

        # Assignment name
        ctk.CTkLabel(master=row, text=assignment.name, font=FONT_COURSE).pack(
            side="left", padx=15, pady=10
        )

        # Edit grade button
        ctk.CTkButton(
            master=row, text="Edit Grade", width=90, height=26,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=lambda a=assignment: self._show_edit_grade(a)
        ).pack(side="left", padx=10)

    # ── Navigation ─────────────────────────────────────────────────────────────

    def _show_add_category(self):
        from ui.views.add_category import AddCategoryView
        self.app.show_view(AddCategoryView, course=self.course)

    def _show_add_assignment(self):
        from ui.views.add_assignment import AddAssignmentView
        self.app.show_view(AddAssignmentView, course=self.course)

    def _show_edit_categories(self):
        from ui.views.edit_categories import EditCategoriesView
        self.app.show_view(EditCategoriesView, course=self.course)

    def _show_edit_grade(self, assignment):
        from ui.views.edit_grade import EditGradeView
        self.app.show_view(EditGradeView, assignment=assignment, course=self.course)