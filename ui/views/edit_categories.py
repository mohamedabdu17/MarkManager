import customtkinter as ctk
from ui.app import FONT_TITLE, FONT_COURSE, FONT_BUTTON, FONT_POPUP
from ui.utils import display_error, sidebar_title
from services.grade_service import (
    get_categories_for_course, edit_category, remove_category,
    remove_assignment, edit_assignment_name
)


class EditCategoriesView:
    def __init__(self, app, sidebar, content, course):
        self.app     = app
        self.sidebar = sidebar
        self.content = content
        self.course  = course
        self._build_sidebar()
        self._build_content()

    def _go_back(self):
        from ui.views.course_view import CourseView
        self.app.show_view(CourseView, course_id=self.course.id)

    def _reload(self):
        """Reload this view with fresh data from the database."""
        from ui.views.edit_categories import EditCategoriesView
        # Re-fetch the course so category lists are up to date
        from services.course_service import get_full_course
        fresh_course = get_full_course(self.course.id)
        self.app.show_view(EditCategoriesView, course=fresh_course)

    # ── Sidebar ────────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sidebar_title(self.sidebar, FONT_TITLE)

        ctk.CTkButton(
            master=self.sidebar, text="Finish Editing",
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=self._go_back
        ).pack(pady=10)

        ctk.CTkLabel(
            master=self.sidebar,
            text="Edit category weights or names,\nor drop individual assignments.",
            font=FONT_BUTTON, text_color="gray",
            justify="center", wraplength=260
        ).pack(pady=10)

    # ── Content ────────────────────────────────────────────────────────────────

    def _build_content(self):
        ctk.CTkLabel(
            master=self.content,
            text=f"Edit — {self.course.code}",
            font=FONT_TITLE
        ).pack(pady=20)

        # Refresh categories from DB so counts are accurate
        self.course.categories = get_categories_for_course(self.course.id)

        if not self.course.categories:
            ctk.CTkLabel(
                master=self.content,
                text="No categories yet.", font=FONT_COURSE
            ).pack(pady=200)
            return

        for category in self.course.categories:
            self._render_category_section(category)

    def _render_category_section(self, category):
        """Render a category heading with edit/drop controls,
        followed by each of its assignments with their own controls."""

        # ── Category heading ──────────────────────────────────────────────────
        heading = ctk.CTkFrame(
            master=self.content, corner_radius=15, fg_color="#2a2a2a"
        )
        heading.pack(fill="x", padx=10, pady=(15, 2))

        ctk.CTkLabel(
            master=heading,
            text=f"{category.name}  —  {category.weight}% of course",
            font=FONT_COURSE
        ).pack(side="left", padx=15, pady=10)

        # Category-level action buttons on the right of the heading
        cat_btn_frame = ctk.CTkFrame(master=heading, fg_color="transparent")
        cat_btn_frame.pack(side="right", padx=10, pady=10)

        ctk.CTkButton(
            master=cat_btn_frame, text="Edit", width=70, height=26,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=lambda c=category: self._show_edit_category_form(c)
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            master=cat_btn_frame, text="Drop", width=70, height=26,
            font=FONT_BUTTON, fg_color="#7a2020", hover_color="#a83030",
            command=lambda c=category: self._confirm_drop_category(c)
        ).pack(side="left", padx=4)

        # ── Assignment rows under heading ─────────────────────────────────────
        if not category.assignments:
            ctk.CTkLabel(
                master=self.content,
                text="  No assignments yet.", font=FONT_BUTTON
            ).pack(anchor="w", padx=25)
        else:
            item_weight = category.item_weight
            for assignment in category.assignments:
                self._render_assignment_row(assignment, item_weight)

    def _render_assignment_row(self, assignment, item_weight: float | None):
        row = ctk.CTkFrame(
            master=self.content, height=70,
            corner_radius=12, fg_color="#333333"
        )
        row.pack(fill="x", padx=25, pady=3)
        row.pack_propagate(False)

        # Assignment name — left
        ctk.CTkLabel(
            master=row, text=assignment.name, font=FONT_COURSE
        ).pack(side="left", padx=15)

        # Item weight — middle right
        weight_text = f"{round(item_weight, 1)}%" if item_weight is not None else ""
        ctk.CTkLabel(master=row, text=weight_text, font=FONT_BUTTON).pack(side="right", padx=30)

        # Action buttons — right side
        btn_frame = ctk.CTkFrame(master=row, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)

        ctk.CTkButton(
            master=btn_frame, text="Rename", width=80, height=26,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=lambda a=assignment: self._show_rename_assignment_form(a)
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            master=btn_frame, text="Drop", width=70, height=26,
            font=FONT_BUTTON, fg_color="#7a2020", hover_color="#a83030",
            command=lambda a=assignment: self._confirm_drop_assignment(a)
        ).pack(side="left", padx=4)

    # ── Edit category form ─────────────────────────────────────────────────────

    def _show_edit_category_form(self, category):
        """Render an edit form for a category in the sidebar."""
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        sidebar_title(self.sidebar, FONT_TITLE)

        # Show how much weight is available (excluding this category's own weight)
        other_weight = sum(
            c.weight for c in self.course.categories if c.id != category.id
        )
        available = 100.0 - other_weight

        form = ctk.CTkFrame(master=self.sidebar, width=300, height=260, corner_radius=20)
        form.pack(pady=10)
        form.pack_propagate(False)

        ctk.CTkLabel(
            master=form, text=f"Edit: {category.name}", font=FONT_COURSE
        ).pack(pady=(15, 5))

        ctk.CTkLabel(master=form, text="Category Name:", font=FONT_POPUP).pack()
        name_entry = ctk.CTkEntry(master=form, width=240)
        name_entry.insert(0, category.name)
        name_entry.pack(pady=(0, 8))

        ctk.CTkLabel(
            master=form,
            text=f"Weight (max {available:.1f}%):",
            font=FONT_POPUP
        ).pack()
        weight_entry = ctk.CTkEntry(master=form, width=240)
        weight_entry.insert(0, str(category.weight))
        weight_entry.pack(pady=(0, 8))

        def handle_submit():
            new_name = name_entry.get().strip()
            if not new_name:
                display_error(form, "Name cannot be empty.", FONT_BUTTON)
                return
            try:
                new_weight = float(weight_entry.get())
                if not (0 < new_weight <= available + 0.01):
                    display_error(form, f"Weight must be between 0 and {available:.1f}%.", FONT_BUTTON)
                    return
            except ValueError:
                display_error(form, "Enter a valid number for weight.", FONT_BUTTON)
                return
            edit_category(category.id, new_name, new_weight)
            self._reload()

        btn_row = ctk.CTkFrame(master=form, fg_color="transparent")
        btn_row.pack(pady=8)

        ctk.CTkButton(
            master=btn_row, text="Cancel", width=90, height=26,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=self._reload
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            master=btn_row, text="Save", width=90, height=26,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=handle_submit
        ).pack(side="left", padx=5)

    # ── Rename assignment form ─────────────────────────────────────────────────

    def _show_rename_assignment_form(self, assignment):
        """Render a rename form for an assignment in the sidebar."""
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        sidebar_title(self.sidebar, FONT_TITLE)

        form = ctk.CTkFrame(master=self.sidebar, width=300, height=180, corner_radius=20)
        form.pack(pady=10)
        form.pack_propagate(False)

        ctk.CTkLabel(
            master=form, text=f"Rename\n{assignment.name}",
            font=FONT_COURSE, justify="center"
        ).pack(pady=(15, 8))

        ctk.CTkLabel(master=form, text="New Name:", font=FONT_POPUP).pack()
        name_entry = ctk.CTkEntry(master=form, width=240)
        name_entry.insert(0, assignment.name)
        name_entry.pack(pady=(0, 8))

        def handle_submit():
            new_name = name_entry.get().strip()
            if not new_name:
                display_error(form, "Name cannot be empty.", FONT_BUTTON)
                return
            edit_assignment_name(assignment.id, new_name)
            self._reload()

        btn_row = ctk.CTkFrame(master=form, fg_color="transparent")
        btn_row.pack(pady=8)

        ctk.CTkButton(
            master=btn_row, text="Cancel", width=90, height=26,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=self._reload
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            master=btn_row, text="Save", width=90, height=26,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=handle_submit
        ).pack(side="left", padx=5)

    # ── Drop confirmations ─────────────────────────────────────────────────────

    def _confirm_drop_category(self, category):
        """Confirm before dropping a category and all its assignments."""
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        sidebar_title(self.sidebar, FONT_TITLE)

        frame = ctk.CTkFrame(master=self.sidebar, width=300, height=200, corner_radius=20)
        frame.pack(pady=10)
        frame.pack_propagate(False)

        ctk.CTkLabel(
            master=frame,
            text=f"Drop '{category.name}'?",
            font=FONT_COURSE
        ).pack(pady=(20, 5))

        assignment_count = len(category.assignments)
        ctk.CTkLabel(
            master=frame,
            text=f"This will also delete\n{assignment_count} assignment(s)\nunder this category.",
            font=FONT_BUTTON, text_color="gray", justify="center", wraplength=260
        ).pack()

        btn_row = ctk.CTkFrame(master=frame, fg_color="transparent")
        btn_row.pack(pady=15)

        ctk.CTkButton(
            master=btn_row, text="Cancel", width=90, height=26,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=self._reload
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            master=btn_row, text="Drop", width=90, height=26,
            font=FONT_BUTTON, fg_color="#7a2020", hover_color="#a83030",
            command=lambda c=category: self._do_drop_category(c)
        ).pack(side="left", padx=5)

    def _confirm_drop_assignment(self, assignment):
        """Confirm before dropping a single assignment."""
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        sidebar_title(self.sidebar, FONT_TITLE)

        frame = ctk.CTkFrame(master=self.sidebar, width=300, height=180, corner_radius=20)
        frame.pack(pady=10)
        frame.pack_propagate(False)

        ctk.CTkLabel(
            master=frame,
            text=f"Drop\n'{assignment.name}'?",
            font=FONT_COURSE, justify="center"
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            master=frame,
            text="The remaining assignments\nin this category will rebalance.",
            font=FONT_BUTTON, text_color="gray", justify="center", wraplength=260
        ).pack()

        btn_row = ctk.CTkFrame(master=frame, fg_color="transparent")
        btn_row.pack(pady=15)

        ctk.CTkButton(
            master=btn_row, text="Cancel", width=90, height=26,
            font=FONT_BUTTON, fg_color="#858585", hover_color="#c3c0c0",
            command=self._reload
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            master=btn_row, text="Drop", width=90, height=26,
            font=FONT_BUTTON, fg_color="#7a2020", hover_color="#a83030",
            command=lambda a=assignment: self._do_drop_assignment(a)
        ).pack(side="left", padx=5)

    def _do_drop_category(self, category):
        remove_category(category.id)
        self._reload()

    def _do_drop_assignment(self, assignment):
        remove_assignment(assignment.id)
        self._reload()