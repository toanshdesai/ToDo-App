#!/usr/bin/env python3
"""Custom dialogs for task creation and editing with priority and due date."""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta


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
    r = clamp(int(r + (percent/100.0)*(255 - r) if percent>0 else r + (percent/100.0)*r))
    g = clamp(int(g + (percent/100.0)*(255 - g) if percent>0 else g + (percent/100.0)*g))
    b = clamp(int(b + (percent/100.0)*(255 - b) if percent>0 else b + (percent/100.0)*b))
    return f"#{r:02x}{g:02x}{b:02x}"


def _make_canvas_button(parent, text, bg, fg, command, padx=12, pady=6):
    """Create a Canvas-based button to bypass macOS color filtering."""
    btn_frame = tk.Frame(parent, bg=parent.cget('bg'))

    # Better text width estimation - use 8 pixels per char minimum + extra padding
    text_width = max(len(text) * 8 + padx * 2, 80)  # Minimum 80px width
    text_height = 20 + pady * 2

    canvas = tk.Canvas(
        btn_frame,
        width=text_width,
        height=text_height,
        bg=bg,
        highlightthickness=0,
        bd=0
    )
    canvas.pack()

    rect = canvas.create_rectangle(
        0, 0, text_width, text_height,
        fill=bg,
        outline=""
    )

    text_item = canvas.create_text(
        text_width // 2, text_height // 2,
        text=text,
        fill=fg,
        font=("Calibri", 10, "bold")
    )

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


class TaskEditDialog:
    """Dialog for creating or editing a task with priority and due date."""

    def __init__(self, parent, title="Add Task", initial_title="", initial_priority="", initial_due_date=""):
        """
        Create a task edit dialog.

        Args:
            parent: Parent window
            title: Dialog title
            initial_title: Initial task title
            initial_priority: Initial priority (low, medium, high, or "")
            initial_due_date: Initial due date (YYYY-MM-DD format or "")
        """
        self.result = None
        self.parent = parent

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("550x300")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()

        self.dialog.transient(parent)
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 275
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 150
        self.dialog.geometry(f"+{x}+{y}")

        # GitHub-inspired colors
        bg_color = "#0D1117"
        fg_color = "#E6EDF3"
        input_bg = "#010409"
        border_color = "#30363D"
        button_ok = "#238636"
        button_cancel = "#6E7681"

        self.dialog.configure(bg=bg_color)

        # Title input
        title_label = tk.Label(
            self.dialog,
            text="Task Title:",
            font=("Calibri", 11, "bold"),
            bg=bg_color,
            fg=fg_color
        )
        title_label.pack(pady=(20, 5), padx=20, anchor=tk.W)

        self.title_entry = tk.Entry(
            self.dialog,
            font=("Calibri", 12),
            bg=input_bg,
            fg=fg_color,
            insertbackground=fg_color,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightcolor="#58A6FF",
            highlightbackground=border_color
        )
        self.title_entry.pack(fill=tk.X, padx=20, pady=(0, 15))
        self.title_entry.insert(0, initial_title)
        self.title_entry.focus()

        # Priority selection
        priority_label = tk.Label(
            self.dialog,
            text="Priority:",
            font=("Calibri", 11, "bold"),
            bg=bg_color,
            fg=fg_color
        )
        priority_label.pack(pady=(0, 5), padx=20, anchor=tk.W)

        priority_frame = tk.Frame(self.dialog, bg=bg_color)
        priority_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        self.priority_var = tk.StringVar(value=initial_priority if initial_priority else "none")

        priorities = [
            ("None", "none", "#6E7681"),
            ("Low", "low", "#238636"),
            ("Medium", "medium", "#D29922"),
            ("High", "high", "#DA3633")
        ]

        for label, value, color in priorities:
            rb = tk.Radiobutton(
                priority_frame,
                text=label,
                variable=self.priority_var,
                value=value,
                font=("Calibri", 10),
                bg=bg_color,
                fg=color,
                selectcolor=bg_color,
                activebackground=bg_color,
                activeforeground=color,
                cursor="hand2"
            )
            rb.pack(side=tk.LEFT, padx=(0, 15))

        # Due date input
        date_label = tk.Label(
            self.dialog,
            text="Due Date (optional):",
            font=("Calibri", 11, "bold"),
            bg=bg_color,
            fg=fg_color
        )
        date_label.pack(pady=(0, 5), padx=20, anchor=tk.W)

        date_input_frame = tk.Frame(self.dialog, bg=bg_color)
        date_input_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        self.date_entry = tk.Entry(
            date_input_frame,
            font=("Calibri", 11),
            bg=input_bg,
            fg=fg_color,
            insertbackground=fg_color,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightcolor="#58A6FF",
            highlightbackground=border_color,
            width=15
        )
        self.date_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.date_entry.insert(0, initial_due_date)

        # Quick date buttons (Canvas-based for proper color rendering)
        today_btn = _make_canvas_button(date_input_frame, "Today", border_color, fg_color, self.set_today, padx=8, pady=3)
        today_btn.pack(side=tk.LEFT, padx=2)

        tomorrow_btn = _make_canvas_button(date_input_frame, "Tomorrow", border_color, fg_color, self.set_tomorrow, padx=8, pady=3)
        tomorrow_btn.pack(side=tk.LEFT, padx=2)

        clear_btn = _make_canvas_button(date_input_frame, "Clear", border_color, fg_color, lambda: self.date_entry.delete(0, tk.END), padx=8, pady=3)
        clear_btn.pack(side=tk.LEFT, padx=2)

        # Format hint
        hint_label = tk.Label(
            self.dialog,
            text="Format: YYYY-MM-DD (e.g., 2026-01-15)",
            font=("Calibri", 8),
            bg=bg_color,
            fg="#6E7681"
        )
        hint_label.pack(pady=(0, 15), padx=20, anchor=tk.W)

        # Buttons (Canvas-based for proper color rendering)
        button_frame = tk.Frame(self.dialog, bg=bg_color)
        button_frame.pack(pady=(0, 20), padx=20, fill=tk.X)

        ok_btn = _make_canvas_button(button_frame, "OK", button_ok, "#FFFFFF", self.on_ok, padx=30, pady=8)
        ok_btn.pack(side=tk.LEFT, padx=(0, 10))

        cancel_btn = _make_canvas_button(button_frame, "Cancel", button_cancel, "#FFFFFF", self.on_cancel, padx=30, pady=8)
        cancel_btn.pack(side=tk.LEFT)

        self.dialog.bind("<Return>", lambda e: self.on_ok())
        self.dialog.bind("<Escape>", lambda e: self.on_cancel())

    def set_today(self):
        """Set due date to today."""
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, today)

    def set_tomorrow(self):
        """Set due date to tomorrow."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, tomorrow)

    def on_ok(self):
        """Handle OK button click."""
        title = self.title_entry.get().strip()
        priority = self.priority_var.get()
        due_date = self.date_entry.get().strip()

        # Validate due date format if provided
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                # Invalid date format
                from dialogs import WarningDialog
                WarningDialog(self.dialog, "Invalid Date", "Please use format: YYYY-MM-DD")
                return

        if title:
            self.result = {
                "title": title,
                "priority": priority if priority != "none" else "",
                "due_date": due_date
            }
            self.dialog.destroy()

    def on_cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.dialog.destroy()

    def get_result(self):
        """Wait for dialog to close and return result."""
        self.dialog.wait_window()
        return self.result
