import customtkinter as ctk
from ui.app import FONT_TITLE, FONT_COURSE, FONT_BUTTON, FONT_POPUP
from ui.utils import mark_color, display_error, sidebar_title
from services.course_service import (
    get_courses_for_semester, edit_course, remove_course
)
from services.calculator import get_course_grade
from services.scale_service import get_all_scales


class EditCoursesView:
    def __init__(self, app, sidebar, content, semester):
        self.app      = app
        self.sidebar  = sidebar
        self.content  = content
        self.semester = semester
        self._build_sidebar()
        self._build_content()

    def _go_back(self):
        from ui.views.dashboard import DashboardView
        self.app.show_view(DashboardView)

    # ── Sidebar ────────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sidebar_title(self.sidebar, FONT_TITLE)

        ctk.CTkButton(
            master=self.sidebar, text="Finish Editing",
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=self._go_back
        ).pack(pady=10)

        # Hint label so the user knows what to do
        ctk.CTkLabel(
            master=self.sidebar,
            text="Click a course card\nto rename or drop it.",
            font=FONT_BUTTON, text_color="gray", justify="center"
        ).pack(pady=10)

    # ── Content ────────────────────────────────────────────────────────────────

    def _build_content(self):
        ctk.CTkLabel(
            master=self.content, text="Edit Courses", font=FONT_TITLE
        ).pack(pady=20)

        if not self.semester:
            ctk.CTkLabel(
                master=self.content, text="No semester selected.", font=FONT_COURSE
            ).pack(pady=200)
            return

        self.courses = get_courses_for_semester(self.semester.id, load_categories=True)

        if not self.courses:
            ctk.CTkLabel(
                master=self.content, text="No courses yet.", font=FONT_COURSE
            ).pack(pady=200)
            return

        for course in self.courses:
            self._render_course_card(course)

    def _render_course_card(self, course):
        grade = get_course_grade(course)
        grade_text = f"{round(grade, 1)}%" if grade is not None else "No grades yet"

        card = ctk.CTkFrame(
            master=self.content, height=110,
            corner_radius=20, fg_color="#333333"
        )
        card.pack(fill="x", padx=10, pady=10)
        card.pack_propagate(False)

        # Grade label — right side
        grade_lbl = ctk.CTkLabel(master=card, text=grade_text, font=FONT_COURSE)
        grade_lbl.pack(side="right", padx=15)
        if grade is not None:
            mark_color(grade_lbl, grade)

        # Course name — top left
        ctk.CTkLabel(
            master=card,
            text=f"{course.code} — {course.name}",
            font=FONT_COURSE
        ).pack(pady=15, padx=15, anchor="nw")

        btn_row = ctk.CTkFrame(master=card, fg_color="transparent")
        btn_row.pack(padx=15, anchor="sw", pady=(0, 10))

        ctk.CTkButton(
            master=btn_row, text="Rename Course", width=130, height=26,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=lambda c=course: self._show_rename_form(c)
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            master=btn_row, text="Drop Course", width=110, height=26,
            font=FONT_BUTTON, fg_color="#7a2020", hover_color="#a83030",
            command=lambda c=course: self._confirm_drop(c)
        ).pack(side="left")

    # ── Rename form ────────────────────────────────────────────────────────────

    def _show_rename_form(self, course):
        """Open a rename dialog as an overlay inside the sidebar."""
        # Clear sidebar below the title and finish button
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        sidebar_title(self.sidebar, FONT_TITLE)

        form = ctk.CTkFrame(master=self.sidebar, width=300, height=280, corner_radius=20)
        form.pack(pady=10)
        form.pack_propagate(False)

        ctk.CTkLabel(
            master=form, text=f"Rename\n{course.code}", font=FONT_COURSE, justify="center"
        ).pack(pady=(15, 5))

        ctk.CTkLabel(master=form, text="New Course Code:", font=FONT_POPUP).pack()
        code_entry = ctk.CTkEntry(master=form, width=240)
        code_entry.insert(0, course.code)
        code_entry.pack(pady=(0, 5))

        ctk.CTkLabel(master=form, text="New Course Name:", font=FONT_POPUP).pack()
        name_entry = ctk.CTkEntry(master=form, width=240)
        name_entry.insert(0, course.name)
        name_entry.pack(pady=(0, 5))

        # Grading scale reassignment
        ctk.CTkLabel(master=form, text="Grading Scale:", font=FONT_POPUP).pack()
        scales     = get_all_scales()
        scale_names = ["None"] + [s.name for s in scales]
        current_scale = next((s.name for s in scales if s.id == course.scale_id), "None")
        scale_var  = ctk.StringVar(value=current_scale)
        ctk.CTkOptionMenu(
            master=form, values=scale_names, variable=scale_var,
            font=FONT_BUTTON, fg_color="#858585",
            button_color="#626262", button_hover_color="#c3c0c0", width=240
        ).pack(pady=(0, 8))

        def handle_submit():
            new_code = code_entry.get().strip()
            new_name = name_entry.get().strip()
            if not new_code or not new_name:
                display_error(form, "Both fields must be filled in.", FONT_BUTTON)
                return
            selected_scale = next((s for s in scales if s.name == scale_var.get()), None)
            edit_course(
                course.id, new_code, new_name,
                scale_id=selected_scale.id if selected_scale else None
            )
            # Reload the whole view so the card updates
            from ui.views.edit_courses import EditCoursesView
            self.app.show_view(EditCoursesView, semester=self.semester)

        btn_row = ctk.CTkFrame(master=form, fg_color="transparent")
        btn_row.pack(pady=5)

        ctk.CTkButton(
            master=btn_row, text="Cancel", width=90, height=26,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=lambda: self.app.show_view(
                EditCoursesView, semester=self.semester
            )
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            master=btn_row, text="Save", width=90, height=26,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=handle_submit
        ).pack(side="left", padx=5)

    # ── Drop confirmation ──────────────────────────────────────────────────────

    def _confirm_drop(self, course):
        """Show a confirmation prompt in the sidebar before permanently deleting."""
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        sidebar_title(self.sidebar, FONT_TITLE)

        confirm_frame = ctk.CTkFrame(master=self.sidebar, width=300, height=180, corner_radius=20)
        confirm_frame.pack(pady=10)
        confirm_frame.pack_propagate(False)

        ctk.CTkLabel(
            master=confirm_frame,
            text=f"Drop {course.code}?",
            font=FONT_COURSE
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            master=confirm_frame,
            text="This will permanently delete\nthe course and all its grades.",
            font=FONT_BUTTON, text_color="gray", justify="center", wraplength=260
        ).pack()

        btn_row = ctk.CTkFrame(master=confirm_frame, fg_color="transparent")
        btn_row.pack(pady=15)

        ctk.CTkButton(
            master=btn_row, text="Cancel", width=90, height=26,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=lambda: self.app.show_view(
                EditCoursesView, semester=self.semester
            )
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            master=btn_row, text="Drop", width=90, height=26,
            font=FONT_BUTTON, fg_color="#7a2020", hover_color="#a83030",
            command=lambda c=course: self._do_drop(c)
        ).pack(side="left", padx=5)

    def _do_drop(self, course):
        remove_course(course.id)
        self.app.show_view(EditCoursesView, semester=self.semester)