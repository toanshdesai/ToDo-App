#!/usr/bin/env python3
"""Custom integrated dialogs for the TODO app."""

import tkinter as tk
from tkinter import ttk


def _shade_color(hex_color, percent):
    """Lighten or darken a hex color by percent (-100..100)."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return hex_color
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    def clamp(x):
        return max(0, min(255, x))
    # adjust by percentage of current channel rather than 255 for more predictable shading
    r = clamp(int(r + (percent/100.0)*(255 - r) if percent>0 else r + (percent/100.0)*r))
    g = clamp(int(g + (percent/100.0)*(255 - g) if percent>0 else g + (percent/100.0)*g))
    b = clamp(int(b + (percent/100.0)*(255 - b) if percent>0 else b + (percent/100.0)*b))
    return f"#{r:02x}{g:02x}{b:02x}"


def _make_canvas_button(parent, text, bg, fg, command, padx=12, pady=6):
    """Create a Canvas-based button to bypass macOS color filtering."""
    # Container frame
    btn_frame = tk.Frame(parent, bg=parent.cget('bg'))

    # Calculate button dimensions based on text and padding
    text_width = len(text) * 7 + padx * 2
    text_height = 20 + pady * 2

    # Create canvas for button
    canvas = tk.Canvas(
        btn_frame,
        width=text_width,
        height=text_height,
        bg=bg,
        highlightthickness=0,
        bd=0
    )
    canvas.pack()

    # Draw button background
    rect = canvas.create_rectangle(
        0, 0, text_width, text_height,
        fill=bg,
        outline=""
    )

    # Draw button text
    text_item = canvas.create_text(
        text_width // 2, text_height // 2,
        text=text,
        fill=fg,
        font=("Calibri", 10, "bold")
    )

    # Hover and click effects
    def on_enter(e):
        canvas.config(cursor="hand2")
        hover_bg = _shade_color(bg, 15)
        canvas.itemconfig(rect, fill=hover_bg)

    def on_leave(e):
        canvas.config(cursor="")
        canvas.itemconfig(rect, fill=bg)

    def on_click(e):
        pressed_bg = _shade_color(bg, -10)
        canvas.itemconfig(rect, fill=pressed_bg)
        canvas.after(100, lambda: canvas.itemconfig(rect, fill=bg))
        command()

    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)
    canvas.bind("<Button-1>", on_click)

    return btn_frame


class ConfirmDialog:
    """Custom confirmation dialog that appears within the app."""

    def __init__(self, parent, title, message, callback):
        """
        Create a confirmation dialog.

        Args:
            parent: Parent window
            title: Dialog title
            message: Message to display
            callback: Function to call with result (True/False)
        """
        self.result = None
        self.callback = callback
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()

        self.dialog.transient(parent)
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 75
        self.dialog.geometry(f"+{x}+{y}")

        # GitHub-inspired colors
        bg_color = "#0D1117"
        fg_color = "#E6EDF3"
        button_yes = "#238636"
        button_no = "#DA3633"

        self.dialog.configure(bg=bg_color)

        msg_label = tk.Label(
            self.dialog,
            text=message,
            font=("Calibri", 12),
            bg=bg_color,
            fg=fg_color,
            wraplength=350,
            justify=tk.LEFT
        )
        msg_label.pack(pady=20, padx=20, expand=True)

        button_frame = tk.Frame(self.dialog, bg=bg_color)
        button_frame.pack(pady=(0, 15), padx=20, fill=tk.X)

        yes_btn = _make_canvas_button(button_frame, "Yes", button_yes, "#FFFFFF", self.on_yes, padx=20, pady=6)
        yes_btn.pack(side=tk.LEFT, padx=(0, 10))

        no_btn = _make_canvas_button(button_frame, "No", button_no, "#FFFFFF", self.on_no, padx=20, pady=6)
        no_btn.pack(side=tk.LEFT)

        self.dialog.bind("<Escape>", lambda e: self.on_no())
        self.dialog.bind("<Return>", lambda e: self.on_yes())

    def on_yes(self):
        """Handle Yes button click."""
        self.result = True
        self.callback(True)
        self.dialog.destroy()

    def on_no(self):
        """Handle No button click."""
        self.result = False
        self.callback(False)
        self.dialog.destroy()


class InfoDialog:
    """Custom info dialog that appears within the app."""

    def __init__(self, parent, title, message):
        """
        Create an info dialog.

        Args:
            parent: Parent window
            title: Dialog title
            message: Message to display
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()

        self.dialog.transient(parent)
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 75
        self.dialog.geometry(f"+{x}+{y}")

        # GitHub-inspired colors
        bg_color = "#0D1117"
        fg_color = "#E6EDF3"
        button_color = "#58A6FF"

        self.dialog.configure(bg=bg_color)

        msg_label = tk.Label(
            self.dialog,
            text=message,
            font=("Calibri", 12),
            bg=bg_color,
            fg=fg_color,
            wraplength=350,
            justify=tk.LEFT
        )
        msg_label.pack(pady=20, padx=20, expand=True)

        button_frame = tk.Frame(self.dialog, bg=bg_color)
        button_frame.pack(pady=(0, 15), padx=20, fill=tk.X)

        ok_btn = _make_canvas_button(button_frame, "OK", button_color, "#FFFFFF", self.on_ok, padx=30, pady=6)
        ok_btn.pack()

        self.dialog.bind("<Return>", lambda e: self.on_ok())
        self.dialog.bind("<Escape>", lambda e: self.on_ok())

    def on_ok(self):
        """Handle OK button click."""
        self.dialog.destroy()


class WarningDialog:
    """Custom warning dialog that appears within the app."""

    def __init__(self, parent, title, message):
        """
        Create a warning dialog.

        Args:
            parent: Parent window
            title: Dialog title
            message: Message to display
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()

        self.dialog.transient(parent)
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 75
        self.dialog.geometry(f"+{x}+{y}")

        # GitHub-inspired colors
        bg_color = "#0D1117"
        fg_color = "#E6EDF3"
        button_color = "#D29922"

        self.dialog.configure(bg=bg_color)

        msg_label = tk.Label(
            self.dialog,
            text=message,
            font=("Calibri", 12),
            bg=bg_color,
            fg=fg_color,
            wraplength=350,
            justify=tk.LEFT
        )
        msg_label.pack(pady=20, padx=20, expand=True)

        button_frame = tk.Frame(self.dialog, bg=bg_color)
        button_frame.pack(pady=(0, 15), padx=20, fill=tk.X)

        ok_btn = _make_canvas_button(button_frame, "OK", button_color, "#FFFFFF", self.on_ok, padx=30, pady=6)
        ok_btn.pack()

        self.dialog.bind("<Return>", lambda e: self.on_ok())
        self.dialog.bind("<Escape>", lambda e: self.on_ok())

    def on_ok(self):
        """Handle OK button click."""
        self.dialog.destroy()



