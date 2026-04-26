import customtkinter as ctk
from PIL import Image

# Fonts and constants used across all views — defined once here and passed down
FONT_TITLE   = None
FONT_COURSE  = None
FONT_BUTTON  = None
FONT_POPUP   = None
BACK_ARROW   = None

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MarkManager")
        self.geometry("1280x720")
        self.resizable(True, True)

        global FONT_TITLE, FONT_COURSE, FONT_BUTTON, FONT_POPUP, BACK_ARROW
        FONT_TITLE  = ctk.CTkFont(family="Arial", size=40, weight="bold")
        FONT_COURSE = ctk.CTkFont(family="Arial", size=20, weight="bold")
        FONT_BUTTON = ctk.CTkFont(family="Arial", weight="bold")
        FONT_POPUP  = ctk.CTkFont(family="Arial", size=15, weight="bold")
        BACK_ARROW  = ctk.CTkImage(
            light_image=Image.open("assets/back.png"), size=(15, 15)
        )

        self.sidebar = ctk.CTkFrame(self, corner_radius=20)
        self.sidebar.place(relx=0.01, rely=0.01, relwidth=0.275, relheight=0.98)

        self.content = ctk.CTkScrollableFrame(self, corner_radius=20)
        self.content.place(relx=0.30, rely=0.01, relwidth=0.69, relheight=0.98)

        # Disable the scrollable frame's own resize bindings — we manage this
        self.content._parent_canvas.configure(yscrollincrement=8)

        self._resize_job = None
        self.bind("<Configure>", self._on_resize)

        from ui.views.dashboard import DashboardView
        self._current_view = None
        self.show_view(DashboardView)

    def _on_resize(self, event):
        # Only care about the root window resizing, not child widgets
        if event.widget is not self:
            return
        # Cancel any previously scheduled redraw
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        # Wait 150ms after the last resize event before doing anything
        self._resize_job = self.after(150, self._on_resize_done)

    def _on_resize_done(self):
        self._resize_job = None
        # Reposition the two main frames in case proportions shifted
        self.sidebar.place(relx=0.01, rely=0.01, relwidth=0.275, relheight=0.98)
        self.content.place(relx=0.30, rely=0.01, relwidth=0.69, relheight=0.98)

    def show_view(self, view_class, **kwargs):
        self._clear_frame(self.sidebar)
        self._clear_frame(self.content)
        self._current_view = view_class(self, self.sidebar, self.content, **kwargs)
        self._reset_scroll()

    def _reset_scroll(self):
        """Scroll content back to top after every view switch."""
        try:
            self.content._parent_canvas.yview_moveto(0)
        except Exception:
            pass

    def _clear_frame(self, frame):
        # Schedule destruction of each child on the next event loop tick
        # rather than all at once — avoids a cascade of geometry recalculations
        for widget in frame.winfo_children():
            widget.destroy()
        # Force CTk to process pending geometry updates before rendering new view
        frame.update_idletasks()

    def invalidate_gpa_cache(self):
        from ui.components import gpa_panel
        gpa_panel._gpa_cache.clear()