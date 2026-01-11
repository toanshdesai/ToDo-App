# TODO App - Desktop Task Manager

A clean, professional TODO application for macOS with priorities, due dates, subtasks, and drag-and-drop reordering.

## Features

- ✅ Add, complete, and delete tasks
- 🎯 Priority levels (High, Medium, Low)
- 📅 Due dates for tasks
- 📋 Subtasks for organizing complex work
- 🎨 Dark mode with professional GitHub-inspired colors
- 🖱️ Drag-and-drop to reorder tasks
- 📊 Sort by priority or due date
- 💾 Auto-saves all changes to JSON

## Quick Start

### For Users: Run the App

**Option 1: Download & Run (No Python needed)**
1. Download `TODO.app.zip` from Releases
2. Extract the ZIP file
3. Double-click `TODO.app` to run

**Option 2: Build from Source (If you have Python)**
```bash
cd /path/to/ToDoApp
chmod +x build.sh
./build.sh
open dist/TODO.app
```

### For Developers: Run from Source

```bash
# Clone or download the repo
cd ToDoApp

# Install dependencies (optional - only needed to run from source)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the app directly
python3 desktop_app.py
```

##  Build Your Own .app Bundle

### Prerequisites
- Python 3.7+
- pip

### Build Instructions

```bash
# 1. Navigate to the project directory
cd /path/to/ToDoApp

# 2. Install PyInstaller (one-time)
pip install pyinstaller>=6.0.0

# 3. Build the app
chmod +x build.sh
./build.sh

# Or manually:
pyinstaller TODO.spec
```

### Result
- **Location**: `dist/TODO.app`
- **Size**: ~30-40 MB (includes Python runtime)
- **Share**: Zip and distribute to other macOS users

```bash
# Create a shareable ZIP
zip -r TODO.app.zip dist/TODO.app
```

## Usage

### Adding Tasks
1. Type in the "Add a new task..." field
2. Click "Add" or press Enter
3. A dialog opens - enter task details:
   - Task title
   - Priority (High/Medium/Low)
   - Due date (optional)

### Task Management
- **Complete**: Select a task and click "✓ Complete" or press Enter
- **Edit**: Double-click a task to edit it
- **Add Subtask**: Select a task and click "+ Subtask"
- **Delete**: Select a task and click "✕ Delete"
- **Reorder**: Click and drag tasks (only works in "Original" sort mode)

### Sorting
- **Original**: Manual order (drag-and-drop enabled)
- **🎯 Priority**: Sort by High → Medium → Low
- **📅 Due Date**: Sort by earliest date first

##  Data Storage

- Tasks are saved in `tasks.json` in the app folder
- Each task includes: title, priority, due date, completion status
- Subtasks are stored within parent tasks
- Changes auto-save on every action

### Backup Your Tasks
```bash
# Copy tasks to backup
cp tasks.json tasks.json.backup

# Restore from backup
cp tasks.json.backup tasks.json
```

## ️ Keyboard Shortcuts

- `Enter` - Add a new task (when in input field)
- `Enter` - Toggle task completion (when task is selected)
- `Double-Click` - Edit task
- `Ctrl+Q` - Quit application (on any screen)

## Requirements

### To Run the App
- macOS 10.12+
- That's it!

### To Build from Source
- Python 3.7+
- PyInstaller 6.0+
- Tkinter (included with Python)

## Files

- `desktop_app.py` - Main application
- `dialogs.py` - Dialog windows (confirmation, info)
- `task_dialogs.py` - Task editing dialog
- `tasks.json` - Your task data
- `TODO.spec` - PyInstaller configuration
- `build.sh` - Build script

## Troubleshooting

### App won't open
- Make sure you're on macOS 10.12 or later
- Try right-clicking the app and selecting "Open"

### App is slow on first launch
- First run can take a few seconds as the app initializes
- Subsequent launches are faster

### Can't edit or save tasks
- Check that `tasks.json` is not read-only
- Make sure the app folder has write permissions

### Need to rebuild after changes
```bash
# Clean old build
rm -rf build dist

# Rebuild
./build.sh
```
