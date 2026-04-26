import customtkinter as ctk
from ui.utils import display_error
from services.calculator import get_required_grade


class FinalsCalculator:
    """The standalone finals calculator panel that lives in the dashboard sidebar.
    Takes any parent frame and renders itself into it."""

    def __init__(self, parent, font_course, font_button, font_popup):
        self.font_course = font_course
        self.font_button = font_button
        self.font_popup  = font_popup
        self._build(parent)

    def _build(self, parent):
        frame = ctk.CTkFrame(master=parent, width=300, corner_radius=20)
        frame.pack(pady=20, fill="x", padx=10)

        ctk.CTkLabel(master=frame, text="Finals Calculator", font=self.font_course).pack(pady=10)
        ctk.CTkLabel(master=frame, text="Current Average (%):", font=self.font_popup).pack()
        current_entry = ctk.CTkEntry(master=frame)
        current_entry.pack()

        ctk.CTkLabel(master=frame, text="Desired Average (%):", font=self.font_popup).pack()
        desired_entry = ctk.CTkEntry(master=frame)
        desired_entry.pack()

        ctk.CTkLabel(master=frame, text="Final Evaluation Weight (%):", font=self.font_popup).pack()
        weight_entry = ctk.CTkEntry(master=frame)
        weight_entry.pack()

        result_label = ctk.CTkLabel(
            master=frame, text="", font=self.font_popup,
            wraplength=260, justify="center"
        )
        result_label.pack(pady=5)

        def calculate():
            try:
                current = float(current_entry.get())
                desired = float(desired_entry.get())
                weight  = float(weight_entry.get())

                if not (0 <= current <= 100 and 0 <= desired <= 100):
                    raise ValueError("Values must be between 0 and 100.")
                if not (0 < weight <= 100):
                    raise ValueError("Weight must be more than 0%.")

                needed = get_required_grade(current, 100 - weight, desired)
                if needed is None:
                    result_label.configure(text="Nothing remaining.", text_color="gray")
                elif needed <= 0:
                    result_label.configure(
                        text="You already have your desired average!",
                        text_color="#4d9e3a"
                    )
                elif needed > 100:
                    result_label.configure(
                        text=f"You'd need {round(needed, 1)}% — not achievable.",
                        text_color="#c91c1c"
                    )
                else:
                    result_label.configure(
                        text=f"You need {round(needed, 1)}% on your final.",
                        text_color="#92c91c"
                    )
            except ValueError as e:
                result_label.configure(text=str(e) or "Please enter valid numbers.", text_color="#f13636")

        ctk.CTkButton(
            master=frame, text="Calculate", width=100, height=28,
            font=self.font_button, fg_color="#858585", hover_color="#c3c0c0",
            command=calculate
        ).pack(pady=8)