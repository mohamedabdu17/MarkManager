import customtkinter as ctk


def mark_color(label: ctk.CTkLabel, average: float | None) -> None:
    """Colour a grade label based on the percentage value.
    Mirrors the original markColor() thresholds exactly."""
    if average is None:
        label.configure(text="No Marks Yet", text_color="gray")
        return
    if average >= 90:
        label.configure(text_color="#3d7dcc")   # blue
    elif average >= 80:
        label.configure(text_color="#92c91c")   # yellow-green
    elif average >= 70:
        label.configure(text_color="#4d9e3a")   # green
    elif average >= 60:
        label.configure(text_color="#c98a1c")   # orange
    elif average >= 50:
        label.configure(text_color="#c91c1c")   # red
    else:
        label.configure(text_color="#8b0000")   # dark red


def display_error(frame: ctk.CTkFrame, message: str,
                  font: ctk.CTkFont = None) -> ctk.CTkLabel:
    """Show an error label on a frame. Destroys any previous error first.
    Returns the label so the caller can destroy it later if needed."""
    if hasattr(frame, "_error_label") and frame._error_label is not None:
        frame._error_label.destroy()
    frame._error_label = ctk.CTkLabel(
        master=frame, text=message,
        text_color="#f13636", font=font, wraplength=250, justify="center"
    )
    frame._error_label.pack(pady=(0, 5))
    return frame._error_label


def clear_error(frame: ctk.CTkFrame) -> None:
    """Remove an error label from a frame if one exists."""
    if hasattr(frame, "_error_label") and frame._error_label is not None:
        frame._error_label.destroy()
        frame._error_label = None


def sidebar_title(sidebar: ctk.CTkFrame, font: ctk.CTkFont) -> None:
    """Render the standard 'Options' title at the top of the sidebar."""
    ctk.CTkLabel(master=sidebar, text="Options", font=font).pack(pady=20)


def back_button(parent, image, command) -> ctk.CTkButton:
    """Render a back arrow button placed at the top-left of a frame."""
    btn = ctk.CTkButton(
        master=parent, image=image, text="", width=50, height=30,
        fg_color="#858585", hover_color="#c3c0c0", command=command
    )
    btn.place(x=25, y=30)
    return btn