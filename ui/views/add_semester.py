import sqlite3
import customtkinter as ctk
from ui.app import FONT_TITLE, FONT_BUTTON, FONT_POPUP
from ui.utils import display_error, sidebar_title
from services.course_service import add_semester


class AddSemesterView:
    def __init__(self, app, sidebar, content):
        self.app     = app
        self.sidebar = sidebar
        self.content = content
        self._build()

    def _go_back(self):
        from ui.views.dashboard import DashboardView
        self.app.show_view(DashboardView)

    def _build(self):
        sidebar_title(self.sidebar, FONT_TITLE)

        ctk.CTkLabel(master=self.content, text="Add Semester", font=FONT_TITLE).pack(pady=30)

        form = ctk.CTkFrame(master=self.content, width=400, height=240, corner_radius=20)
        form.pack(pady=15)
        form.pack_propagate(False)

        ctk.CTkLabel(master=form, text="Season:", font=FONT_POPUP).pack(pady=(20, 0))
        season_var = ctk.StringVar(value="F")
        ctk.CTkSegmentedButton(
            master=form,
            values=["F  (Fall)", "W  (Winter)", "S  (Summer)"],
            variable=season_var,
            font=FONT_BUTTON
        ).pack(pady=5)

        ctk.CTkLabel(master=form, text="Year (e.g. 2025):", font=FONT_POPUP).pack(pady=(10, 0))
        year_entry = ctk.CTkEntry(master=form, width=200)
        year_entry.pack()

        def handle_submit():
            season = season_var.get()[0]   # grab "F", "W", or "S"
            year   = year_entry.get().strip()
            if not year.isdigit() or len(year) != 4:
                display_error(form, "Enter a valid 4-digit year.", FONT_BUTTON)
                return
            term = f"{season}{year}"       # e.g. "F2025"
            try:
                add_semester(term)
                self._go_back()
            except sqlite3.IntegrityError:
                display_error(form, f"{term} already exists.", FONT_BUTTON)

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