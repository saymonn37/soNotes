# 📌 SoNotes – Smart & Draggable Notes Organizer

🚀 **SoNotes** is a **powerful note-taking application** built with Python and Tkinter, featuring **draggable tabs, reorderable lists, and persistent storage**. Easily create, organize, and manage notes in multiple tabs with an intuitive, user-friendly interface.

---

## 🎯 Features

✅ **Tabbed Interface** – Organize notes into different tabs for better management.  
✅ **Drag & Drop Tabs** – Rearrange tabs easily by dragging them.  
✅ **Reorder Notes** – Move notes within a tab using drag & drop.  
✅ **Persistent Storage** – Automatically saves notes and restores them on restart.  
✅ **Note Editing** – Easily add, edit, move, and delete notes with a smooth workflow.  
✅ **Custom Dialogs** – Interactive prompts for input and confirmations.  
✅ **Keyboard Shortcuts** – Quickly perform actions like select all, undo, and redo.  

---

## 🛠️ Installation & Setup

### **Requirements**
Ensure you have **Python 3.x** installed. Required libraries:
- `tkinter` (built-in with Python)
- `pickle` (built-in with Python)

### **Installation**
1. **Clone the Repository**  
   ```bash
   git clone https://github.com/saymonn37/soNotes.git
   cd SoNotes
   ```

2. **Run the Application**  
   ```bash
   python3 so_notes.py
   ```

---

## 🚀 How It Works

1. **Create & Manage Tabs**  
   - Add, rename, delete, and reorder tabs with a simple drag-and-drop action.

2. **Add & Edit Notes**  
   - Add new notes by entering a title.
   - Double-click a note to **view and edit** its content.

3. **Move & Delete Notes**  
   - Move notes between tabs with an intuitive selection system.
   - Delete unwanted notes with a confirmation prompt.

4. **Reordering**  
   - Drag & drop notes inside a tab for a custom order.

5. **Keyboard Shortcuts**
   - `Ctrl + A` → Select all text  
   - `Ctrl + Z` → Undo  
   - `Ctrl + Y` or `Ctrl + Shift + Z` → Redo  

---

## 🖥️ UI Overview

The application consists of:

- **Menu Bar**: Options for managing tabs and notes.
- **Tabbed Interface**: Organize notes efficiently.
- **Draggable Listbox**: Allows easy reordering of notes.
- **Text Editor**: Provides a clean, distraction-free space for writing.

---

## 📜 Technical Details

| File                 | Description |
|----------------------|-------------|
| `sonotes.py`        | Main application file with Tkinter UI. |
| `notes.dat`         | Saves all notes persistently. |
| `window_geometry.dat` | Saves the last window position & size. |

### **Key Components**
- **Draggable Tabs** – Allows users to reorder tabs dynamically.
- **Draggable Listbox** – Enables reordering of notes within tabs.
- **Custom Dialogs** – Provides a seamless way to confirm actions.

---

## 🔧 Troubleshooting

| Issue | Solution |
|------|---------|
| Application not opening | Ensure Python 3 is installed. Run `python3 sonotes.py`. |
| Notes not saving | Check if `notes.dat` exists in the project folder. |
| Window position reset | Make sure `window_geometry.dat` is writable. |

---

## 🏗️ Future Improvements

- **Cloud Sync** – Sync notes across devices.
- **Markdown Support** – Enhance note formatting.
- **Dark Mode** – Aesthetic improvement for low-light environments.

---

## 📝 License

This project is open-source under the **MIT License**.

## 👥 Author

Developed by [Saymonn](https://github.com/saymonn37). Contributions and feedback are welcome! 🚀
