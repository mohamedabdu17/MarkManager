import customtkinter as ctk
from ui.app import FONT_TITLE, FONT_BUTTON, FONT_POPUP
from ui.utils import display_error, sidebar_title
from services.grade_service import add_category


class AddCategoryView:
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

        ctk.CTkLabel(master=self.content, text="Add Category", font=FONT_TITLE).pack(pady=30)

        # Show remaining weight so the user knows how much they have left to assign
        used_weight = sum(c.weight for c in self.course.categories)
        remaining   = 100.0 - used_weight
        ctk.CTkLabel(
            master=self.content,
            text=f"Weight remaining: {remaining:.1f}%",
            font=FONT_BUTTON
        ).pack()

        form = ctk.CTkFrame(master=self.content, width=400, height=260, corner_radius=20)
        form.pack(pady=15)
        form.pack_propagate(False)

        ctk.CTkLabel(master=form, text="Category Name:", font=FONT_POPUP).pack(pady=(20, 0))
        # Preset options matching common engineering course structures
        presets = ["Lab", "Assignment", "Midterm", "Final", "Quiz", "Project", "Other"]
        name_var = ctk.StringVar(value="Lab")
        ctk.CTkOptionMenu(
            master=form, values=presets,
            variable=name_var,
            font=FONT_BUTTON, fg_color="#858585",
            button_color="#626262", button_hover_color="#c3c0c0"
        ).pack(pady=5)

        # Custom name override
        ctk.CTkLabel(master=form, text="Or enter custom name:", font=FONT_POPUP).pack()
        custom_entry = ctk.CTkEntry(master=form, width=280, placeholder_text="Leave blank to use preset")
        custom_entry.pack()

        ctk.CTkLabel(master=form, text="Combined Weight (%):", font=FONT_POPUP).pack(pady=(10, 0))
        weight_entry = ctk.CTkEntry(master=form, width=280)
        weight_entry.pack()

        def handle_submit():
            name = custom_entry.get().strip() or name_var.get()
            try:
                weight = float(weight_entry.get())
                if not (0 < weight <= remaining + 0.01):
                    display_error(form, f"Weight must be between 0 and {remaining:.1f}%.", FONT_BUTTON)
                    return
            except ValueError:
                display_error(form, "Enter a valid number for weight.", FONT_BUTTON)
                return
            add_category(self.course.id, name, weight)
            self._go_back()

        btn_frame = ctk.CTkFrame(master=form, fg_color="transparent")
        btn_frame.pack(pady=8)

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