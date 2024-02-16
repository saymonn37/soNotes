#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import pickle
import os

class DraggableListbox(tk.Listbox):
    """A custom Listbox that allows dragging and dropping items."""
    def __init__(self, master, app, **kw):
        super().__init__(master, **kw)
        self.app = app
        self.bind('<Button-1>', self._on_click)
        self.bind('<B1-Motion>', self._on_drag)
        self.drag_start_index = None

    def _on_click(self, event):
        """Handle mouse click event to determine the start index of drag."""
        self.drag_start_index = self.nearest(event.y)

    def _on_drag(self, event):
        """Handle mouse drag event to reorder items."""
        drag_to_index = self.nearest(event.y)
        if drag_to_index != self.drag_start_index:
            self._reorder_items(self.drag_start_index, drag_to_index)
            self.drag_start_index = drag_to_index

    def _reorder_items(self, start_index, end_index):
        """Reorder items within the listbox."""
        item = self.get(start_index)
        self.delete(start_index)
        self.insert(end_index, item)
        self.selection_set(end_index)
        self.app.update_notes_order()

class CustomDialog(tk.Toplevel):
    """A custom dialog window for confirmation messages."""
    def __init__(self, parent, title, message, on_confirm):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.title(title)
        self.message = message
        self.on_confirm = on_confirm

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
        self.create_widgets()
        self.deiconify()

    def create_widgets(self):
        """Create widgets for the dialog window."""
        tk.Label(self, text=self.message, wraplength=250).pack(padx=20, pady=20)
        tk.Button(self, text="OK", command=self.confirm).pack(side=tk.LEFT, padx=(20, 10), pady=20)
        tk.Button(self, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=(10, 20), pady=20)

    def confirm(self):
        """Callback function when 'OK' button is clicked."""
        self.on_confirm()
        self.destroy()

    def cancel(self):
        """Callback function when 'Cancel' button is clicked."""
        self.destroy()

class CustomInputDialog(tk.Toplevel):
    """A custom input dialog window."""
    def __init__(self, parent, title, prompt, on_confirm, options=None):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.title(title)
        self.prompt = prompt
        self.on_confirm = on_confirm
        self.options = options
        self.result = None

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
        self.create_widgets()
        self.deiconify()

    def create_widgets(self):
        """Create widgets for the input dialog window."""
        tk.Label(self, text=self.prompt).pack(padx=10, pady=10)
        if self.options:
            self.combobox = ttk.Combobox(self, values=self.options)
            self.combobox.pack(padx=10, pady=10)
            self.combobox.bind("<<ComboboxSelected>>", lambda event: self.confirm())
        else:
            self.entry = tk.Entry(self)
            self.entry.pack(padx=10, pady=10)
            self.entry.focus_set()
            self.bind("<Return>", self.confirm)
        tk.Button(self, text="OK", command=self.confirm).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(self, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=10, pady=10)

    def confirm(self, event=None):
        """Callback function when 'OK' button is clicked."""
        if self.options:
            self.result = self.combobox.get()
        else:
            self.result = self.entry.get()
        if self.result:
            self.on_confirm(self.result)
        self.destroy()

    def cancel(self, event=None):
        """Callback function when 'Cancel' button is clicked."""
        self.destroy()

class SoNotes:
    """Main application class with smooth tab dragging."""
    def __init__(self, root):
        self.root = root
        self.root.title("So Notes")
        self.data_file = 'notes.dat'

        self.tabs = {}
        self.current_tab = None
        self.dragging_tab = False
        self.dragged_tab_index = None
        self.drag_over_tab_index = None 

        self.tab_control = ttk.Notebook(root)
        self.tab_control.pack(expand=1, fill="both")
        self.tab_control.bind("<ButtonPress-1>", self.start_tab_drag)
        self.tab_control.bind("<B1-Motion>", self.drag_tab)
        self.tab_control.bind("<ButtonRelease-1>", self.stop_tab_drag)

        self.create_menu()
        self.load_state()

    def start_tab_drag(self, event):
        try:
            self.dragged_tab_index = self.tab_control.index("@%d,%d" % (event.x, event.y))
            self.drag_over_tab_index = self.dragged_tab_index
        except tk.TclError:
            self.dragged_tab_index = 0
        self.dragging_tab = True

    def drag_tab(self, event):
        """Handle dragging of a tab with a visual indicator."""
        if not self.dragging_tab:
            return
        try:
            tab_index = self.tab_control.index("@%d,%d" % (event.x, event.y))
            if tab_index != self.dragged_tab_index:
                self.drag_over_tab_index = tab_index
        except tk.TclError:
            pass

    def stop_tab_drag(self, event):
        """Stop dragging a tab and move it to the new location."""
        if self.dragging_tab and self.drag_over_tab_index is not None and self.drag_over_tab_index != "end":
            self.tab_control.insert(self.drag_over_tab_index, self.dragged_tab_index)
        self.dragging_tab = False
        self.drag_over_tab_index = None

    # Methods for creating menu items
    def create_menu(self):
        """Create menu items."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        tabs_menu = tk.Menu(menu_bar, tearoff=0)
        tabs_menu.add_command(label="New Tab", command=self.new_tab)
        tabs_menu.add_command(label="Delete Tab", command=self.delete_tab)
        tabs_menu.add_command(label="Edit Tab Name", command=self.edit_tab_name)
        tabs_menu.add_separator()
        tabs_menu.add_command(label="Exit", command=self.on_closing)
        menu_bar.add_cascade(label="Tabs", menu=tabs_menu)

        note_menu = tk.Menu(menu_bar, tearoff=0)
        note_menu.add_command(label="Add Note", command=self.add_note)
        note_menu.add_command(label="Edit Note Name", command=self.edit_note_name)
        note_menu.add_command(label="Move Note", command=self.move_note_menu)
        note_menu.add_command(label="Delete Note", command=self.delete_note_menu)
        menu_bar.add_cascade(label="Notes", menu=note_menu)

    # Methods for handling note movement
    def move_note_menu(self):
        """Open a dialog to move a note to another tab."""
        tab = self.tab_control.tab(self.tab_control.select(), "text")
        listbox = self.tabs[tab]['listbox']
        title_index = listbox.curselection()
        if title_index:
            title = listbox.get(title_index[0])
            def on_tab_select(target_tab):
                if target_tab and target_tab != tab:
                    self.move_note(tab, target_tab, title)
            tab_names = [self.tab_control.tab(tab_id, "text") for tab_id in self.tab_control.tabs()]
            CustomInputDialog(self.root, "Move Note", "Select target tab:", on_tab_select, options=tab_names)

    def move_note(self, source_tab, target_tab, note_title):
        """Move a note from one tab to another."""
        if note_title in self.tabs[source_tab]['notes']:
            note_content = self.tabs[source_tab]['notes'].pop(note_title)
            self.tabs[target_tab]['notes'][note_title] = note_content
            source_listbox = self.tabs[source_tab]['listbox']
            target_listbox = self.tabs[target_tab]['listbox']
            source_listbox.delete(source_listbox.get(0, "end").index(note_title))
            target_listbox.insert(tk.END, note_title)
            self.save_state()
        else:
            print(f"Error: Note '{note_title}' does not exist in '{source_tab}' tab.")

    # Methods for handling keyboard shortcuts
    def bind_shortcuts(self, text_widget):
        """Bind keyboard shortcuts."""
        text_widget.bind('<Control-a>', self.select_all)
        text_widget.bind('<Control-z>', self.undo)
        text_widget.bind('<Control-y>', self.redo)
        text_widget.bind('<Control-Shift-Z>', self.redo)

    def select_all(self, event):
        """Select all text."""
        event.widget.tag_add("sel", "1.0", "end")
        return 'break'

    def undo(self, event):
        """Undo action."""
        event.widget.event_generate("<<Undo>>")
        return 'break'

    def redo(self, event):
        """Redo action."""
        event.widget.event_generate("<<Redo>>")
        return 'break'

    # Methods for managing tabs
    def new_tab(self):
        """Create a new tab."""
        def on_confirm(result):
            if result:
                self.tabs[result] = {'notes': {}}
                self.create_tab(result, {})
                self.save_state()
        CustomInputDialog(self.root, "New Tab", "Tab Name:", on_confirm)

    def delete_tab(self):
        """Delete the current tab."""
        index = self.tab_control.index(self.tab_control.select())
        name = self.tab_control.tab(index, "text")
        def on_confirm():
            del self.tabs[name]
            self.tab_control.forget(index)
            self.save_state()
        CustomDialog(self.root, "Delete Tab", f"Are you sure you want to delete '{name}'?", on_confirm)

    def edit_tab_name(self):
        """Edit the name of the current tab."""
        index = self.tab_control.index(self.tab_control.select())
        old_name = self.tab_control.tab(index, "text")
        def on_confirm(result):
            if result and result != old_name:
                self.tabs[result] = self.tabs.pop(old_name)
                self.tab_control.tab(index, text=result)
                self.save_state()
        CustomInputDialog(self.root, "Edit Tab Name", "New Tab Name:", on_confirm)

    # Methods for managing notes
    def edit_note_name(self):
        """Edit the name of a note."""
        tab = self.tab_control.tab(self.tab_control.select(), "text")
        listbox = self.tabs[tab]['listbox']
        title_index = listbox.curselection()
        if title_index:
            title_index = title_index[0]
            current_name = listbox.get(title_index)
            def on_confirm(result):
                if result and result != current_name:
                    listbox.delete(title_index)
                    listbox.insert(title_index, result)
                    self.tabs[tab]['notes'][result] = self.tabs[tab]['notes'].pop(current_name)
                    self.save_state()
            CustomInputDialog(self.root, "Edit Note Name", "Edit Note Name:", on_confirm)

    def add_note(self):
        """Add a new note."""
        tab = self.tab_control.tab(self.tab_control.select(), "text")

        def on_title_confirm(title):
            if title:
                note_content = ""
                def save_note():
                    nonlocal note_content
                    note_content = text_area.get("1.0", "end-1c")
                    if note_content:
                        self.tabs[tab]['listbox'].insert(tk.END, title)
                        self.tabs[tab]['notes'][title] = note_content
                        self.save_state()
                    top.destroy()

                top = tk.Toplevel(self.root)
                top.title("Add Note")
                top.geometry("+%d+%d" % (self.root.winfo_rootx()+50, self.root.winfo_rooty()+50))
                text_area = tk.Text(top, height=30, width=100, undo=True)
                self.bind_shortcuts(text_area)
                text_area.pack(expand=1, fill="both")
                save_button = tk.Button(top, text="Save", command=save_note)
                save_button.pack()
                top.transient(self.root)
                top.grab_set()
                top.wait_window(top)

        CustomInputDialog(self.root, "Add Note", "Note Title:", on_title_confirm)

    def view_note(self, event):
        """View the content of a note."""
        listbox = event.widget
        if listbox.curselection():
            title = listbox.get(listbox.curselection()[0])
            tab = self.tab_control.tab(self.tab_control.select(), "text")
            if title in self.tabs[tab]['notes']:
                note_content = self.tabs[tab]['notes'][title]
    
                top = tk.Toplevel()
                top.title(title)
                text_area = tk.Text(top, height=30, width=100, undo=True)
                self.bind_shortcuts(text_area)
                text_area.pack(expand=1, fill="both")
                text_area.insert(tk.END, note_content)
    
                button_frame = tk.Frame(top)
                button_frame.pack(fill="x")
    
                copy_button = tk.Button(button_frame, text="Copy to Clipboard", command=lambda: self.copy_to_clipboard(text_area))
                copy_button.pack(side="left")
    
                save_button = tk.Button(button_frame, text="Save changes", command=lambda: self.save_note_changes(tab, title, text_area))
                save_button.pack(side="left")
    
                delete_button = tk.Button(button_frame, text="Delete", command=lambda: self.delete_note(tab, title, listbox))
                delete_button.pack(side="left")
            else:
                tk.messagebox.showerror("Error", f"Note '{title}' does not exist.")
        else:
            tk.messagebox.showerror("Error", "No note selected.")

    def save_note_changes(self, tab, title, text_area):
        """Save changes made to a note."""
        new_note_content = text_area.get("1.0", "end-1c")

        def confirm_save():
            self.tabs[tab]['notes'][title] = new_note_content
            self.save_state()

        CustomDialog(self.root, "Save Note Changes",
                     f"Save changes to '{title}'?",
                     confirm_save)

    def delete_note_menu(self):
        """Open a confirmation dialog to delete a note."""
        tab = self.tab_control.tab(self.tab_control.select(), "text")
        listbox = self.tabs[tab]['listbox']
        title_index = listbox.curselection()
        if title_index:
            title_index = title_index[0]
            current_name = listbox.get(title_index)
            def on_confirm():
                self.delete_note(tab, current_name, listbox)
            CustomDialog(self.root, "Delete Note", f"Are you sure you want to delete '{current_name}'?", on_confirm)

    def delete_note(self, tab, title, listbox):
        """Delete a note."""
        del self.tabs[tab]['notes'][title]
        listbox.delete(listbox.curselection())
        self.save_state()

    def copy_to_clipboard(self, text_area):
        """Copy note content to clipboard."""
        note_content = text_area.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(note_content)

    def update_notes_order(self):
        """Update the order of notes in the active tab."""
        tab_name = self.tab_control.tab(self.tab_control.select(), "text")
        if tab_name in self.tabs:
            listbox = self.tabs[tab_name]['listbox']
            notes_order = list(listbox.get(0, tk.END))
            self.tabs[tab_name]['notes'] = {title: self.tabs[tab_name]['notes'][title] for title in notes_order}
            self.save_state()

    def create_tab(self, tab_name, notes):
        """Create a new tab."""
        tab = ttk.Frame(self.tab_control)
        self.tab_control.add(tab, text=tab_name)
        listbox = DraggableListbox(tab, app=self)
        listbox.pack(expand=1, fill="both")
        listbox.bind("<Double-1>", self.view_note)
        for title in notes.keys():
            listbox.insert(tk.END, title)
        self.tabs[tab_name] = {'tab': tab, 'listbox': listbox, 'notes': notes}

    def save_state(self):
        """Save the current state of the application."""
        save_data = {tab_name: self.tabs[tab_name]['notes'] for tab_name in self.tabs}
        tabs_order = [self.tab_control.tab(tab_id, "text") for tab_id in self.tab_control.tabs()]
        current_tab_index = self.get_current_tab_index()  # Get the index of the current tab
        with open(self.data_file, 'wb') as file:
            pickle.dump((save_data, tabs_order, current_tab_index), file)  # Save the index of the current tab
        self.save_window_geometry()

    def load_state(self):
        """Load the saved state of the application."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'rb') as file:
                loaded_data = pickle.load(file)
                if isinstance(loaded_data, tuple) and len(loaded_data) == 3:
                    saved_data, saved_tabs_order, last_active_tab_index = loaded_data
                elif isinstance(loaded_data, tuple) and len(loaded_data) == 2:
                    saved_data, saved_tabs_order = loaded_data
                    last_active_tab_index = 0
                else:
                    saved_data = {}
                    saved_tabs_order = []
                    last_active_tab_index = 0
    
                for tab_name in saved_tabs_order:
                    if tab_name in saved_data:
                        self.create_tab(tab_name, saved_data[tab_name])
                if self.tab_control.tabs():
                    if last_active_tab_index >= 0 and last_active_tab_index < len(saved_tabs_order):
                        self.set_current_tab_by_index(last_active_tab_index)  # Set the current tab
        self.load_window_geometry()
    
    def set_current_tab_by_index(self, index):
        """Set the current tab by index."""
        if self.tab_control.tabs():
            self.tab_control.select(index)  # Select tab by index
    

    def get_current_tab_index(self):
        """Get the index of the current tab."""
        if self.tab_control.select():
            return self.tab_control.index("current")
        else:
            return -1  # Return a default value or handle this case based on your application's logic

    def load_window_geometry(self):
        """Load the window geometry."""
        try:
            with open('window_geometry.dat', 'r') as file:
                geometry = file.read()
                if geometry:
                    self.window_geometry = geometry
                    self.root.geometry(geometry)
        except FileNotFoundError:
            pass

    def save_window_geometry(self):
        """Save the window geometry."""
        if self.root.state() == 'normal':
            self.window_geometry = self.root.geometry()
            with open('window_geometry.dat', 'w') as file:
                file.write(self.window_geometry)

    def on_closing(self):
        """Handle closing event."""
        self.save_state()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SoNotes(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()