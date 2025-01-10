from typing import List
from reprlib import repr

from .note import Note
from .storage import Storage
from .exc import NoteNotFound


class Notebook:
    def __init__(self, storage: Storage):
        self.__storage = storage
        self.__notes = self.__storage.load()

    @property
    def notes(self):
        return self.__notes
    
    @property
    def last_note_id(self):
        if len(self):
            return max(note.id for note in self.__notes)
        else:
            return 0

    def add_note(self, note: Note) -> None:
        self.__notes.append(note)
        self.__storage.save(self.__notes)


    def update_note(self, note: Note) -> None:
        for n in self:
            if n.id == note.id:
                n.text = note.text
        self.__storage.save(self.__notes)
        # TODO: Raise error if note not found


    def delete_note(self, note_id: int) -> None:
        for note in self:
            if note.id == note_id:
                self.__notes.remove(note)
        self.__storage.save(self.__notes)
        # TODO: Raise error if note not found

    def get_notes(self) -> List[Note]:
        return self.notes

    def get_note(self, note_id: int) -> Note:
        return self[note_id]
    
    def __getitem__(self, note_id: int):
        for note in self.__notes:
            if note.id == note_id:
                return note
        raise NoteNotFound(msg=f'Note with {note_id=} note found.')

    def __iter__(self):
        notes = self.__notes.copy()
        for note in notes:
            yield note

    def __str__(self):
        return f"Notebook: {repr(self.__notes)}"
    
    def __len__(self):
        return len(self.__notes)
    
