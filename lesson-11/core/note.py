from __future__ import annotations

from typing import Dict, Union
from reprlib import repr
from datetime import datetime


class Note:
    fields = ['id', 'text', 'created_date']
    
    def __init__(self, id: int, text: str, created_date: Union[datetime, str]):
        self.__id = id
        self.text = text
        if isinstance(created_date, str):
            created_date = datetime.fromisoformat(created_date)
        self.__created_date = created_date

    @classmethod
    def from_dict(cls, values: dict[str, str]):
        note_id = values['id']
        text = values['text']
        created_date = values['created_date']
        return cls(note_id, text, created_date)

    @classmethod
    def from_tuple(cls, values: tuple[str, str, str]):
        note_id, text, created_date = values
        return cls(note_id, text, created_date)


    @property
    def id(self):
        return self.__id

    @property
    def created_date(self):
        return self.__created_date

    def as_dict(self, shorten: bool = False) -> Dict:
        return {
            'id': self.id,
            'text': repr(self.text) if shorten else self.text,
            'created_date': self.created_date.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def as_tuple(self, shorten: bool = False) -> Dict:
        return (
            self.id,
            repr(self.text) if shorten else self.text,
            self.created_date.strftime("%Y-%m-%d %H:%M:%S")
        )
    

    
    def __str__(self):
        return f"Note(id={self.id}, text={repr(self.text)}, created_date={self.created_date!r})"

    def display(self, shorten: bool = False):
        text = repr(self.text) if shorten else self.text
        print(
            f"| ID: {self.id:<4} | Text: {text:<30} | Datetime: {self.created_date} |"
        )

