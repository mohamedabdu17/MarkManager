import customtkinter as ctk
from ui.app import FONT_TITLE, FONT_BUTTON, FONT_POPUP
from ui.utils import display_error, sidebar_title
from services.grade_service import edit_assignment_grade, edit_assignment_name


class EditGradeView:
    def __init__(self, app, sidebar, content, assignment, course):
        self.app        = app
        self.sidebar    = sidebar
        self.content    = content
        self.assignment = assignment
        self.course     = course
        self._build()

    def _go_back(self):
        from ui.views.course_view import CourseView
        self.app.show_view(CourseView, course_id=self.course.id)

    def _build(self):
        sidebar_title(self.sidebar, FONT_TITLE)

        ctk.CTkLabel(
            master=self.content,
            text=f"Edit: {self.assignment.name}", font=FONT_TITLE
        ).pack(pady=30)

        form = ctk.CTkFrame(master=self.content, width=400, height=280, corner_radius=20)
        form.pack(pady=15)
        form.pack_propagate(False)

        ctk.CTkLabel(master=form, text="New Name (leave blank to keep):", font=FONT_POPUP).pack(pady=(20, 0))
        name_entry = ctk.CTkEntry(master=form, width=280)
        name_entry.insert(0, self.assignment.name)
        name_entry.pack()

        ctk.CTkLabel(master=form, text="Grade (%):", font=FONT_POPUP).pack(pady=(10, 0))
        grade_entry = ctk.CTkEntry(master=form, width=280)
        if self.assignment.is_graded:
            grade_entry.insert(0, str(self.assignment.grade))
        grade_entry.pack()

        ctk.CTkLabel(
            master=form,
            text="Leave grade blank to mark as ungraded.",
            font=FONT_BUTTON, text_color="gray"
        ).pack(pady=5)

        def handle_submit():
            new_name = name_entry.get().strip()
            raw      = grade_entry.get().strip()

            if new_name and new_name != self.assignment.name:
                edit_assignment_name(self.assignment.id, new_name)

            if raw == "":
                edit_assignment_grade(self.assignment.id, None)
            else:
                try:
                    grade = float(raw)
                    if not (0 <= grade <= 100):
                        raise ValueError
                    edit_assignment_grade(self.assignment.id, grade)
                except ValueError:
                    display_error(form, "Grade must be a number between 0 and 100.", FONT_BUTTON)
                    return
            self.app.invalidate_gpa_cache()
            self._go_back()

        btn_frame = ctk.CTkFrame(master=form, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            master=btn_frame, text="Cancel", width=100, height=28,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=self._go_back
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            master=btn_frame, text="Save", width=100, height=28,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=handle_submit
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            master=btn_frame, text="Drop Assignment", width=130, height=28,
            font=FONT_BUTTON, fg_color="#7a2020", hover_color="#a83030",
            command=self._confirm_drop
        ).pack(side="left", padx=10)

    def _confirm_drop(self):
        from ui.utils import display_error
        # Swap sidebar to a confirmation prompt
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        from ui.app import FONT_TITLE
        from ui.utils import sidebar_title
        sidebar_title(self.sidebar, FONT_TITLE)

        frame = ctk.CTkFrame(master=self.sidebar, width=300, height=160, corner_radius=20)
        frame.pack(pady=10)
        frame.pack_propagate(False)

        ctk.CTkLabel(
            master=frame,
            text=f"Drop '{self.assignment.name}'?",
            font=FONT_POPUP, wraplength=260, justify="center"
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            master=frame,
            text="This cannot be undone.",
            font=FONT_BUTTON, text_color="gray"
        ).pack()

        btn_row = ctk.CTkFrame(master=frame, fg_color="transparent")
        btn_row.pack(pady=12)

        ctk.CTkButton(
            master=btn_row, text="Cancel", width=90, height=26,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=self._go_back
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            master=btn_row, text="Drop", width=90, height=26,
            font=FONT_BUTTON, fg_color="#7a2020", hover_color="#a83030",
            command=self._do_drop
        ).pack(side="left", padx=5)

    def _do_drop(self):
        from services.grade_service import remove_assignment
        remove_assignment(self.assignment.id)
        self.app.invalidate_gpa_cache()  # ← add this
        self._go_back()