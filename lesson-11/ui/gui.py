from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk

from core import Notebook, Note, JsonFile


class GUIApp:
    def __init__(self):
        self.storage = JsonFile(file_path="notes.json")
        self.notebook = Notebook(storage=self.storage)

        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("Note Application")
        self.root.geometry("600x400")

        # Create UI Components
        self.__setup_ui()

    def __setup_ui(self):
        # Create a Treeview for displaying notes
        self.tree = ttk.Treeview(self.root, columns=("ID", "Text", "Created Date"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Text", text="Text")
        self.tree.heading("Created Date", text="Created Date")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Add buttons for actions
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(btn_frame, text="Add Note", command=self.__add_note).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Update Note", command=self.__update_note).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Note", command=self.__delete_note).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="View Note", command=self.__view_note).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh Notes", command=self.__refresh_notes).pack(side=tk.LEFT, padx=5)

        # Load initial data
        self.__refresh_notes()

    def __refresh_notes(self):
        # Clear the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Populate the Treeview with notes
        for note in self.notebook:
            self.tree.insert("", "end", values=(note.id, note.text[:50], note.created_date.strftime("%Y-%m-%d %H:%M:%S")))

    def __add_note(self):
        text = simpledialog.askstring("Add Note", "Enter note text:")
        if text:
            note = Note(
                id=self.notebook.last_note_id + 1,
                text=text,
                created_date=datetime.now()
            )
            self.notebook.add_note(note)
            messagebox.showinfo("Success", "Note added successfully.")
            self.__refresh_notes()

    def __update_note(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a note to update.")
            return

        note_id = int(self.tree.item(selected_item[0], "values")[0])
        note = self.notebook.get_note(note_id)
        if note:
            new_text = simpledialog.askstring("Update Note", "Enter updated note text:", initialvalue=note.text)
            if new_text:
                updated_note = Note(
                    id=note.id,
                    text=new_text,
                    created_date=datetime.now()
                )
                self.notebook.update_note(updated_note)
                messagebox.showinfo("Success", "Note updated successfully.")
                self.__refresh_notes()
        else:
            messagebox.showerror("Error", "Selected note not found.")

    def __delete_note(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a note to delete.")
            return

        note_id = int(self.tree.item(selected_item[0], "values")[0])
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete note {note_id}?"):
            self.notebook.delete_note(note_id)
            messagebox.showinfo("Success", "Note deleted successfully.")
            self.__refresh_notes()

    def __view_note(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a note to view.")
            return

        note_id = int(self.tree.item(selected_item[0], "values")[0])
        note = self.notebook.get_note(note_id)
        if note:
            messagebox.showinfo("View Note", f"ID: {note.id}\nText: {note.text}\nCreated Date: {note.created_date}")
        else:
            messagebox.showerror("Error", "Selected note not found.")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = GUIApp()
    app.run()
