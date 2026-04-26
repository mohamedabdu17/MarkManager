import customtkinter as ctk
from ui.app import FONT_TITLE, FONT_COURSE, FONT_BUTTON, FONT_POPUP
from ui.utils import display_error, sidebar_title
from services.course_service import add_course
from services.scale_service import get_all_scales


class AddCourseView:
    def __init__(self, app, sidebar, content, semester):
        self.app      = app
        self.sidebar  = sidebar
        self.content  = content
        self.semester = semester
        self._build()

    def _build(self):
        sidebar_title(self.sidebar, FONT_TITLE)

        ctk.CTkLabel(master=self.content, text="Add Course", font=FONT_TITLE).pack(pady=30)

        form = ctk.CTkFrame(master=self.content, width=400, height=320, corner_radius=20)
        form.pack(pady=15)
        form.pack_propagate(False)

        ctk.CTkLabel(master=form, text="Course Code:", font=FONT_POPUP).pack(pady=(20, 0))
        code_entry = ctk.CTkEntry(master=form, width=280)
        code_entry.pack()

        ctk.CTkLabel(master=form, text="Course Name:", font=FONT_POPUP).pack(pady=(10, 0))
        name_entry = ctk.CTkEntry(master=form, width=280)
        name_entry.pack()

        # Grading scale selector
        ctk.CTkLabel(master=form, text="Grading Scale (optional):", font=FONT_POPUP).pack(pady=(10, 0))
        scales = get_all_scales()
        scale_names = ["None"] + [s.name for s in scales]
        scale_var = ctk.StringVar(value="None")
        ctk.CTkOptionMenu(
            master=form, values=scale_names,
            variable=scale_var,
            font=FONT_BUTTON, fg_color="#858585",
            button_color="#626262", button_hover_color="#c3c0c0"
        ).pack(pady=(0, 10))

        def handle_submit():
            code = code_entry.get().strip()
            name = name_entry.get().strip()
            if not code or not name:
                display_error(form, "Both fields must be filled in.", FONT_BUTTON)
                return
            if not self.semester:
                display_error(form, "No semester selected.", FONT_BUTTON)
                return
            selected_scale = next((s for s in scales if s.name == scale_var.get()), None)
            add_course(
                semester_id=self.semester.id,
                code=code, name=name,
                scale_id=selected_scale.id if selected_scale else None
            )
            self.app.invalidate_gpa_cache()
            from ui.views.dashboard import DashboardView
            self.app.show_view(DashboardView, active_semester_id=self.semester.id)  # ← pass semester id

        def handle_cancel():
            from ui.views.dashboard import DashboardView
            self.app.show_view(DashboardView, active_semester_id=self.semester.id if self.semester else None)

        btn_frame = ctk.CTkFrame(master=form, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            master=btn_frame, text="Cancel", width=100, height=28,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=handle_cancel
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            master=btn_frame, text="Add Course", width=100, height=28,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=handle_submit
        ).pack(side="left", padx=10)