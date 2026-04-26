import customtkinter as ctk
from ui.app import FONT_TITLE, FONT_BUTTON, FONT_POPUP
from ui.utils import display_error, sidebar_title
from services.grade_service import add_assignment


class AddAssignmentView:
    def __init__(self, app, sidebar, content, course):
        self.app     = app
        self.sidebar = sidebar
        self.content = content
        self.course  = course
        self._build()

    def _go_back(self):
        from ui.views.course_view import CourseView
        self.app.show_view(CourseView, course_id=self.course.id)

    def _build(self):
        sidebar_title(self.sidebar, FONT_TITLE)

        ctk.CTkLabel(master=self.content, text="Add Assignment", font=FONT_TITLE).pack(pady=30)

        form = ctk.CTkFrame(master=self.content, width=400, height=300, corner_radius=20)
        form.pack(pady=15)
        form.pack_propagate(False)

        # Category selector — user picks which category this assignment belongs to
        ctk.CTkLabel(master=form, text="Category:", font=FONT_POPUP).pack(pady=(20, 0))
        if not self.course.categories:
            ctk.CTkLabel(
                master=form,
                text="No categories yet — add a category first.",
                font=FONT_BUTTON, text_color="#f13636"
            ).pack(pady=20)
            ctk.CTkButton(
                master=form, text="Back", width=100, height=28,
                font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
                command=self._go_back
            ).pack()
            return

        cat_names = [c.name for c in self.course.categories]
        cat_var   = ctk.StringVar(value=cat_names[0])
        ctk.CTkOptionMenu(
            master=form, values=cat_names, variable=cat_var,
            font=FONT_BUTTON, fg_color="#858585",
            button_color="#626262", button_hover_color="#c3c0c0"
        ).pack(pady=5)

        ctk.CTkLabel(master=form, text="Assignment Name:", font=FONT_POPUP).pack(pady=(10, 0))
        name_entry = ctk.CTkEntry(master=form, width=280)
        name_entry.pack()

        ctk.CTkLabel(master=form, text="Grade % (optional — leave blank if not yet graded):", font=FONT_POPUP, wraplength=320).pack(pady=(10, 0))
        grade_entry = ctk.CTkEntry(master=form, width=280)
        grade_entry.pack()

        def handle_submit():
            name = name_entry.get().strip()
            if not name:
                display_error(form, "Assignment name cannot be empty.", FONT_BUTTON)
                return

            grade = None
            raw = grade_entry.get().strip()
            if raw:
                try:
                    grade = float(raw)
                    if not (0 <= grade <= 100):
                        raise ValueError
                except ValueError:
                    display_error(form, "Grade must be a number between 0 and 100.", FONT_BUTTON)
                    return

            selected_cat = next(c for c in self.course.categories if c.name == cat_var.get())
            add_assignment(selected_cat.id, name, grade)
            self._go_back()

        btn_frame = ctk.CTkFrame(master=form, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            master=btn_frame, text="Cancel", width=100, height=28,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=self._go_back
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            master=btn_frame, text="Add", width=100, height=28,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=handle_submit
        ).pack(side="left", padx=10)