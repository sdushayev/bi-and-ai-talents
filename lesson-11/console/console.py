import sys
from datetime import datetime

from core import Notebook, Note
from core.exc import NoteNotFound
from .settings import Settings

try:
    from tabulate import tabulate
except ModuleNotFoundError:
    import warnings
    warnings.warn("`tabulate` is not installed. Run `pip install tabulate` for pretty printing.")
    tabulate = None


class ConsoleApp:
    def __init__(self, config: Settings = None):
        if config is None:
            config = Settings()

        storage = config.storage
        
        for k, v in storage.info.items():
            print(f"{k}: {v}")
        print()

        self.__notebook = Notebook(storage=storage)

    def run(self):
        options = {
            "1": self.__show_notes,
            "2": self.__show_note,
            "3": self.__add_note,
            "4": self.__update_note,
            "5": self.__delete_note,
            "m": self.__show_menu,
            "q": sys.exit,
        }

        self.__show_menu()
        while True:
            option = input("Choose option: ").lower()
            
            cmd = options.get(option)
            if cmd:
                cmd()
                print()
            else:
                print('Invalid option')


    def __show_notes(self):
        if len(self.__notebook) == 0:
            print('No notes yet.')
            return
        
        if tabulate:
            print(
                tabulate(
                    [note.as_dict(shorten=True) for note in self.__notebook],
                    tablefmt="rounded_grid",
                    headers="keys",
                )
            )
        else:
            for note in self.__notebook:
                note.display()

    def __show_note(self):
        try:
            note_id = self.__get_note_id()
            note = self.__notebook[note_id]
        except NoteNotFound as exc:
            print(exc.msg)
            return
        if tabulate:
            print(tabulate([note.as_dict()], tablefmt='rounded_grid', headers='keys'))
        else:
            note.display()

    def __add_note(self):
        text = input('Note text: ')
        note_id = self.__notebook.last_note_id + 1
        created_date = datetime.now()
        new_note = Note(id=note_id, text=text, created_date=created_date)
        self.__notebook.add_note(new_note)
        print(f'New note created with {note_id=}.')

    def __update_note(self):
        note_id = self.__get_note_id()
        text = input('Note text: ')
        note = Note(id=note_id, text=text, created_date=datetime.now())
        self.__notebook.update_note(note)
        print(f"Note with {note_id=} updated.")

    def __delete_note(self):
        note_id = self.__get_note_id()
        self.__notebook.delete_note(note_id=note_id)
        print(f"Note with {note_id=} deleted.")

    def __show_menu(self):
        menu = """CHOOSE OPTION
    1: SHOW ALL NOTES
    2: SHOW NOTE DETAILS
    3: CREATE NOTE
    4: UPDATE NOTE
    5: DELETE NOTE
    M: SHOW MENU AGAIN
    Q: QUIT THE APPLICATION
"""
        print(menu)

    @staticmethod
    def __get_note_id():
        while True:
            try:
                return int(input("Enter note id: "))
            except ValueError:
                print("Invalid input. Please enter a valid number.")



if __name__ == "__main__":
    app = ConsoleApp()
    app.run()
