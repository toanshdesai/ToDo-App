#!/usr/bin/env python3
"""Desktop TODO application using Tkinter with light/dark theme support."""

import sys
import json
import shutil
import tempfile
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
from typing import Dict, List, Optional

from dialogs import ConfirmDialog, InfoDialog, WarningDialog
from task_dialogs import TaskEditDialog


TASKS_FILENAME = "tasks.json"


class TaskManager:
    """Manages task persistence."""

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = Path(__file__).parent / TASKS_FILENAME
        self.path = path

    def load(self) -> List[Dict]:
        """Load tasks from JSON file."""
        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise json.JSONDecodeError("root is not a list", doc="", pos=0)
                return data
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            bak = self.path.with_suffix(self.path.suffix + f".bak.{int(time.time())}")
            try:
                shutil.copy2(str(self.path), str(bak))
            except Exception:
                pass
            return []

    def save(self, tasks: List[Dict]) -> None:
        """Save tasks to JSON file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tf:
            json.dump(tasks, tf, indent=2, ensure_ascii=False)
            temp_name = tf.name
        shutil.move(temp_name, str(self.path))

    @staticmethod
    def next_id(tasks: List[Dict]) -> int:
        if not tasks:
            return 1
        return max(int(t.get("id", 0)) for t in tasks) + 1


class TodoApp:
    """Desktop TODO application using Tkinter."""

    def __init__(self, root):
        self.root = root
        self.root.title("TODO - Task Manager")
        self.root.geometry("600x600")
        self.root.minsize(500, 450)

        self.task_manager = TaskManager()
        self.tasks = self.task_manager.load()
        self.dark_mode = True  # Always use dark mode

        # Drag and drop state
        self.drag_start_index = None

        # Map listbox index to (task_index, subtask_index) - subtask_index is None for parent tasks
        self.index_map = []

        # Sorting state
        self.sort_mode = "none"  # none, priority, due_date

        self.setup_styles()
        self.create_widgets()
        self.update_task_list()

        # Bind Ctrl+Q to quit
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        # Bind Enter in input field
        self.task_input.bind("<Return>", lambda e: self.add_task())

    def setup_styles(self):
        """Setup color scheme for dark mode (only theme)."""
        # Dark theme with GitHub-inspired colors for excellent contrast
        self.bg_color = "#0D1117"  # GitHub dark background
        self.fg_color = "#E6EDF3"  # GitHub light text
        self.accent_color = "#58A6FF"  # GitHub blue accent
        self.button_bg = "#238636"  # GitHub green button
        self.button_fg = "#FFFFFF"
        self.input_bg = "#0D1117"  # Same as background
        self.input_fg = "#E6EDF3"
        self.list_bg = "#010409"  # Darker than background
        self.list_fg = "#E6EDF3"
        self.border_color = "#30363D"
        self.delete_btn = "#DA3633"  # GitHub red
        self.clear_btn = "#6E40AA"  # GitHub purple

        # Priority colors
        self.priority_colors = {
            "high": "#DA3633",    # Red
            "medium": "#D29922",  # Yellow/Orange
            "low": "#238636",     # Green
        }

        # Priority symbols
        self.priority_symbols = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢",
        }

        # Apply colors to root
        self.root.configure(bg=self.bg_color)

    def _make_button(self, parent, text, bg, fg, command, padx=12, pady=6):
        """Create a Canvas-based button to bypass macOS color filtering.

        macOS applies grayscale filters to focused Tkinter windows with standard widgets.
        Using Canvas widgets bypasses this issue as they render pixels directly.
        """
        # Container frame
        btn_frame = tk.Frame(parent, bg=parent.cget('bg'))

        # Calculate button dimensions based on text and padding
        # Rough estimate: 7 pixels per character for Calibri 10 bold
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

        # Draw button background (rectangle)
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

        # Hover effect
        def on_enter(e):
            canvas.config(cursor="hand2")
            # Slightly lighter shade for hover
            hover_bg = self._shade_color(bg, 15)
            canvas.itemconfig(rect, fill=hover_bg)

        def on_leave(e):
            canvas.config(cursor="")
            canvas.itemconfig(rect, fill=bg)

        def on_click(e):
            # Visual feedback
            pressed_bg = self._shade_color(bg, -10)
            canvas.itemconfig(rect, fill=pressed_bg)
            canvas.after(100, lambda: canvas.itemconfig(rect, fill=bg))
            command()

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        canvas.bind("<Button-1>", on_click)

        return btn_frame


    def _shade_color(self, hex_color, percent):
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

    def create_widgets(self):
        """Create the UI widgets."""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Title
        title_label = tk.Label(
            main_frame,
            text="My Tasks",
            font=("Calibri", 18, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        title_label.pack(pady=(0, 10))

        # Input frame
        input_frame = tk.Frame(main_frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        self.task_input = tk.Entry(
            input_frame,
            font=("Calibri", 11),
            bg=self.input_bg,
            fg=self.input_fg,
            insertbackground=self.input_fg,
            relief=tk.RAISED,
            bd=1,
            highlightthickness=2,
            highlightcolor=self.accent_color,
            highlightbackground=self.border_color
        )
        self.task_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        self.placeholder = "Add a new task..."
        self.task_input.insert(0, self.placeholder)
        self.task_input.config(fg="#6E7681")  # GitHub gray for placeholder
        self.task_input.bind("<FocusIn>", self.on_input_focus_in)
        self.task_input.bind("<FocusOut>", self.on_input_focus_out)

        add_btn = self._make_button(input_frame, "Add", self.button_bg, "#FFFFFF", self.add_task, padx=20, pady=8)
        add_btn.pack(side=tk.LEFT)

        # Task list frame with themed scrollbar
        list_frame = tk.Frame(main_frame, bg=self.bg_color)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create themed scrollbar
        scrollbar = tk.Scrollbar(
            list_frame,
            bg=self.list_bg,
            troughcolor=self.bg_color,
            activebackground=self.border_color,
            highlightthickness=0,
            bd=0,
            width=8
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.task_listbox = tk.Listbox(
            list_frame,
            font=("Calibri", 24),
            bg=self.list_bg,
            fg=self.list_fg,
            selectmode=tk.SINGLE,
            relief=tk.RAISED,
            bd=0,
            highlightthickness=0,
            activestyle="none",
            selectbackground=self.accent_color,
            selectforeground="#010409",
            yscrollcommand=scrollbar.set
        )
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.task_listbox.yview)

        # Bind selection, Enter key, and double-click for editing
        self.task_listbox.bind("<<ListboxSelect>>", self.on_task_select)
        self.task_listbox.bind("<Return>", lambda e: self.toggle_task())
        self.task_listbox.bind("<Double-Button-1>", lambda e: self.edit_task())

        # Bind drag and drop for reordering
        self.task_listbox.bind("<ButtonPress-1>", self.on_drag_start)
        self.task_listbox.bind("<B1-Motion>", self.on_drag_motion)
        self.task_listbox.bind("<ButtonRelease-1>", self.on_drag_release)

        # Action buttons frame
        action_frame = tk.Frame(main_frame, bg=self.bg_color)
        action_frame.pack(fill=tk.X, pady=(0, 10))

        complete_btn = self._make_button(action_frame, "✓ Complete", self.button_bg, "#FFFFFF", self.toggle_task)
        complete_btn.pack(side=tk.LEFT, padx=(0, 5))

        subtask_btn = self._make_button(action_frame, "+ Subtask", self.accent_color, "#FFFFFF", self.add_subtask)
        subtask_btn.pack(side=tk.LEFT, padx=5)

        delete_btn = self._make_button(action_frame, "✕ Delete", self.delete_btn, "#FFFFFF", self.delete_task)
        delete_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = self._make_button(action_frame, "⊟ Clear All", self.clear_btn, "#FFFFFF", self.clear_all)
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Sort controls frame
        sort_frame = tk.Frame(main_frame, bg=self.bg_color)
        sort_frame.pack(fill=tk.X, pady=(0, 10))

        sort_label = tk.Label(
            sort_frame,
            text="Sort:",
            font=("Calibri", 10),
            bg=self.bg_color,
            fg=self.fg_color
        )
        sort_label.pack(side=tk.LEFT, padx=(0, 8))

        sort_none_btn = self._make_button(sort_frame, "Original", self.border_color, "#FFFFFF", lambda: self.set_sort_mode("none"), padx=12, pady=4)
        sort_none_btn.pack(side=tk.LEFT, padx=2)

        sort_priority_btn = self._make_button(sort_frame, "🎯 Priority", "#6E40AA", "#FFFFFF", lambda: self.set_sort_mode("priority"), padx=12, pady=4)
        sort_priority_btn.pack(side=tk.LEFT, padx=2)

        sort_date_btn = self._make_button(sort_frame, "📅 Due Date", "#58A6FF", "#FFFFFF", lambda: self.set_sort_mode("due_date"), padx=12, pady=4)
        sort_date_btn.pack(side=tk.LEFT, padx=2)

        # Stats frame
        stats_frame = tk.Frame(main_frame, bg=self.bg_color)
        stats_frame.pack(fill=tk.X)

        self.stats_label = tk.Label(
            stats_frame,
            text="",
            font=("Calibri", 13),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.stats_label.pack(anchor=tk.W)

    def on_input_focus_in(self, event):
        """Handle input field focus - clear placeholder if present."""
        if self.task_input.get() == self.placeholder:
            self.task_input.delete(0, tk.END)
            self.task_input.config(fg=self.input_fg)  # Change to normal text color

    def on_input_focus_out(self, event):
        """Handle input field blur - restore placeholder if empty."""
        if self.task_input.get() == "":
            self.task_input.insert(0, self.placeholder)
            self.task_input.config(fg="#6E7681")  # GitHub gray placeholder color

    def on_task_select(self, event):
        """Handle task selection."""
        pass  # Can be used for future features

    def add_task(self):
        """Add a new task with optional priority and due date."""
        initial_title = self.task_input.get().strip()
        if initial_title == self.placeholder:
            initial_title = ""

        # Open dialog for task details
        dialog = TaskEditDialog(
            self.root,
            title="Add Task",
            initial_title=initial_title
        )
        result = dialog.get_result()

        if result:
            task = {
                "id": TaskManager.next_id(self.tasks),
                "title": result["title"],
                "completed": False,
                "priority": result.get("priority", ""),
                "due_date": result.get("due_date", "")
            }
            self.tasks.append(task)
            self.task_manager.save(self.tasks)
            self.task_input.delete(0, tk.END)
            self.task_input.insert(0, self.placeholder)
            self.task_input.config(fg="#6E7681")  # GitHub gray
            self.update_task_list()
            self.root.focus()  # Remove focus from input field to show placeholder cleanly

    def toggle_task(self):
        """Toggle selected task completion."""
        selection = self.task_listbox.curselection()
        if not selection:
            InfoDialog(self.root, "No Selection", "Please select a task to complete.")
            return

        list_index = selection[0]
        if list_index >= len(self.index_map):
            return

        task_idx, subtask_idx = self.index_map[list_index]

        if subtask_idx is None:
            # Toggle parent task
            self.tasks[task_idx]["completed"] = not self.tasks[task_idx].get("completed", False)
        else:
            # Toggle subtask
            if "subtasks" not in self.tasks[task_idx]:
                self.tasks[task_idx]["subtasks"] = []
            self.tasks[task_idx]["subtasks"][subtask_idx]["completed"] = \
                not self.tasks[task_idx]["subtasks"][subtask_idx].get("completed", False)

        self.task_manager.save(self.tasks)
        self.update_task_list()
        self.task_listbox.selection_set(list_index)

    def delete_task(self):
        """Delete selected task."""
        selection = self.task_listbox.curselection()
        if not selection:
            InfoDialog(self.root, "No Selection", "Please select a task to delete.")
            return

        list_index = selection[0]
        if list_index >= len(self.index_map):
            return

        task_idx, subtask_idx = self.index_map[list_index]

        if subtask_idx is None:
            # Delete parent task
            del self.tasks[task_idx]
        else:
            # Delete subtask
            if "subtasks" in self.tasks[task_idx]:
                del self.tasks[task_idx]["subtasks"][subtask_idx]

        self.task_manager.save(self.tasks)
        self.update_task_list()

    def edit_task(self):
        """Edit selected task with priority and due date."""
        selection = self.task_listbox.curselection()
        if not selection:
            InfoDialog(self.root, "No Selection", "Please select a task to edit.")
            return

        list_index = selection[0]
        if list_index >= len(self.index_map):
            return

        task_idx, subtask_idx = self.index_map[list_index]

        if subtask_idx is None:
            # Edit parent task
            task = self.tasks[task_idx]
            current_title = task.get("title", "")
            current_priority = task.get("priority", "")
            current_due_date = task.get("due_date", "")
            dialog_title = "Edit Task"
        else:
            # Edit subtask
            subtask = self.tasks[task_idx]["subtasks"][subtask_idx]
            current_title = subtask.get("title", "")
            current_priority = subtask.get("priority", "")
            current_due_date = subtask.get("due_date", "")
            dialog_title = "Edit Subtask"

        # Open dialog for editing
        dialog = TaskEditDialog(
            self.root,
            title=dialog_title,
            initial_title=current_title,
            initial_priority=current_priority,
            initial_due_date=current_due_date
        )
        result = dialog.get_result()

        # Update task if user didn't cancel
        if result:
            if subtask_idx is None:
                self.tasks[task_idx]["title"] = result["title"]
                self.tasks[task_idx]["priority"] = result.get("priority", "")
                self.tasks[task_idx]["due_date"] = result.get("due_date", "")
            else:
                self.tasks[task_idx]["subtasks"][subtask_idx]["title"] = result["title"]
                self.tasks[task_idx]["subtasks"][subtask_idx]["priority"] = result.get("priority", "")
                self.tasks[task_idx]["subtasks"][subtask_idx]["due_date"] = result.get("due_date", "")

            self.task_manager.save(self.tasks)
            self.update_task_list()
            # Reselect the edited item
            self.task_listbox.selection_set(list_index)

    def add_subtask(self):
        """Add a subtask to the selected parent task."""
        selection = self.task_listbox.curselection()
        if not selection:
            InfoDialog(self.root, "No Selection", "Please select a parent task to add a subtask.")
            return

        list_index = selection[0]
        if list_index >= len(self.index_map):
            return

        task_idx, subtask_idx = self.index_map[list_index]

        # If a subtask is selected, use its parent
        # task_idx already points to the parent

        # Open dialog for subtask details
        dialog = TaskEditDialog(
            self.root,
            title="Add Subtask"
        )
        result = dialog.get_result()

        if result:
            # Initialize subtasks list if it doesn't exist
            if "subtasks" not in self.tasks[task_idx]:
                self.tasks[task_idx]["subtasks"] = []

            # Add the subtask
            subtask = {
                "title": result["title"],
                "completed": False,
                "priority": result.get("priority", ""),
                "due_date": result.get("due_date", "")
            }
            self.tasks[task_idx]["subtasks"].append(subtask)

            self.task_manager.save(self.tasks)
            self.update_task_list()

    def clear_all(self):
        """Clear all tasks after confirmation."""
        if not self.tasks:
            InfoDialog(self.root, "No Tasks", "There are no tasks to clear.")
            return

        def on_confirm(result):
            if result:
                self.tasks = []
                self.task_manager.save(self.tasks)
                self.update_task_list()

        ConfirmDialog(self.root, "Clear All", "Delete all tasks? This cannot be undone.", on_confirm)

    def on_drag_start(self, event):
        """Handle start of drag operation."""
        # Disable drag-and-drop when sorted
        if self.sort_mode != "none":
            self.drag_start_index = None
            return

        # Get the index of the item under the mouse
        index = self.task_listbox.nearest(event.y)
        if index >= 0 and index < len(self.index_map):
            # Only allow dragging parent tasks, not subtasks
            task_idx, subtask_idx = self.index_map[index]
            if subtask_idx is None:
                self.drag_start_index = index
                self.task_listbox.selection_clear(0, tk.END)
                self.task_listbox.selection_set(index)
            else:
                self.drag_start_index = None

    def on_drag_motion(self, event):
        """Handle drag motion - highlight target position."""
        if self.drag_start_index is None:
            return

        # Get current index under mouse
        current_index = self.task_listbox.nearest(event.y)
        if current_index >= 0:
            # Visual feedback: select the target position
            self.task_listbox.selection_clear(0, tk.END)
            self.task_listbox.selection_set(current_index)

    def on_drag_release(self, event):
        """Handle drop - reorder tasks."""
        if self.drag_start_index is None:
            return

        # Get drop listbox index
        drop_list_index = self.task_listbox.nearest(event.y)

        # Only reorder if dropping in a different position
        if drop_list_index >= 0 and drop_list_index < len(self.index_map) and drop_list_index != self.drag_start_index:
            # Get the actual task indices from index_map
            start_task_idx, _ = self.index_map[self.drag_start_index]
            drop_task_idx, drop_subtask_idx = self.index_map[drop_list_index]

            # Only allow dropping on parent tasks
            if drop_subtask_idx is None:
                # Remove task from old position
                task = self.tasks.pop(start_task_idx)

                # Adjust drop index if moving down
                if drop_task_idx > start_task_idx:
                    drop_task_idx -= 1

                # Insert at new position
                self.tasks.insert(drop_task_idx, task)

                # Save and update display
                self.task_manager.save(self.tasks)
                self.update_task_list()

                # Find the new listbox index for the moved task and select it
                for i, (t_idx, s_idx) in enumerate(self.index_map):
                    if t_idx == drop_task_idx and s_idx is None:
                        self.task_listbox.selection_set(i)
                        break

        # Reset drag state
        self.drag_start_index = None

    def set_sort_mode(self, mode):
        """Set the sort mode and refresh display."""
        self.sort_mode = mode
        self.update_task_list()

    def get_sorted_task_indices(self):
        """Get list of task indices sorted according to current sort mode."""
        if self.sort_mode == "none":
            return list(range(len(self.tasks)))

        # Create list of (original_index, task) tuples
        indexed_tasks = list(enumerate(self.tasks))

        if self.sort_mode == "priority":
            # Priority order: high > medium > low > none
            priority_order = {"high": 0, "medium": 1, "low": 2, "": 3}

            def priority_key(item):
                idx, task = item
                priority = task.get("priority", "")
                return priority_order.get(priority, 3)

            indexed_tasks.sort(key=priority_key)

        elif self.sort_mode == "due_date":
            # Sort by due date (earliest first), tasks without dates go last
            def date_key(item):
                idx, task = item
                due_date = task.get("due_date", "")
                if not due_date:
                    return "9999-99-99"  # Put tasks without dates at the end
                return due_date

            indexed_tasks.sort(key=date_key)

        # Return the sorted indices
        return [idx for idx, task in indexed_tasks]

    def update_task_list(self):
        """Update the task list display with priority and due dates."""
        self.task_listbox.delete(0, tk.END)
        self.index_map = []

        # Get sorted task indices
        sorted_indices = self.get_sorted_task_indices()

        for task_idx in sorted_indices:
            task = self.tasks[task_idx]
            status = "✓" if task.get("completed") else " "

            # Add priority symbol if present
            priority = task.get("priority", "")
            priority_symbol = self.priority_symbols.get(priority, "")
            if priority_symbol:
                priority_symbol += " "

            # Add due date if present
            due_date = task.get("due_date", "")
            due_date_str = f" 📅 {due_date}" if due_date else ""

            task_str = f"{priority_symbol}[{status}] {task.get('title')}{due_date_str}"
            self.task_listbox.insert(tk.END, task_str)
            self.index_map.append((task_idx, None))  # Parent task

            # Display subtasks if they exist
            if "subtasks" in task and task["subtasks"]:
                for subtask_idx, subtask in enumerate(task["subtasks"]):
                    sub_status = "✓" if subtask.get("completed") else " "

                    # Add priority symbol for subtask
                    sub_priority = subtask.get("priority", "")
                    sub_priority_symbol = self.priority_symbols.get(sub_priority, "")
                    if sub_priority_symbol:
                        sub_priority_symbol += " "

                    # Add due date for subtask
                    sub_due_date = subtask.get("due_date", "")
                    sub_due_date_str = f" 📅 {sub_due_date}" if sub_due_date else ""

                    sub_str = f"    └─ {sub_priority_symbol}[{sub_status}] {subtask.get('title')}{sub_due_date_str}"
                    self.task_listbox.insert(tk.END, sub_str)
                    self.index_map.append((task_idx, subtask_idx))  # Subtask

        # Update stats
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.get("completed", False))
        remaining = total - completed

        stats_text = f"Total: {total} | Completed: {completed} | Remaining: {remaining}"
        self.stats_label.config(text=stats_text)

    def toggle_theme(self):
        """Theme toggle disabled - dark mode only."""
        pass  # Dark mode is the only theme


def main():
    """Main entry point."""
    root = tk.Tk()

    # Set window icon
    try:
        icon_path = Path(__file__).parent / "TODO.iconset" / "icon_256x256.png"
        if icon_path.exists():
            icon = tk.PhotoImage(file=str(icon_path))
            root.iconphoto(True, icon)
    except Exception:
        # If icon loading fails, continue without it
        pass

    # macOS-specific: Force appearance mode to prevent color desaturation on focus
    if sys.platform == "darwin":
        try:
            # Try to set NSAppearance to darkAqua to prevent macOS from applying filters
            from tkinter import _tkinter
            root.tk.call('tk::unsupported::MacWindowStyle', 'style', root, 'darkAqua')
        except Exception:
            pass

        # Alternative approach: Try setting color space
        try:
            root.tk.call('::tk::mac::useThemedToplevel', '0')
        except Exception:
            pass

    # Use a theme that respects custom colors; 'clam' is cross-platform and avoids macOS native overrides.
    try:
        style = ttk.Style(root)
        style.theme_use('clam')
    except Exception:
        # If theme change isn't available, continue without failing.
        pass

    app = TodoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

