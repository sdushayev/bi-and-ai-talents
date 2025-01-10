
import os
import json
import csv
import sqlite3

from abc import ABC, abstractmethod
from typing import List

try:
    import pyodbc
except ModuleNotFoundError:
    pyodbc = None

from .note import Note


class Storage(ABC):
    @abstractmethod
    def save(self, notes: List[Note]) -> None:
        pass

    @abstractmethod
    def load(self) -> List[Note]:
        pass

    @property
    @abstractmethod
    def info(self) -> dict:
        pass


class JsonFile(Storage):
    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)

    def save(self, notes: List[Note]) -> None:
        notes = [note.as_dict() for note in notes]
        with open(self.file_path, "wt") as f:
            json.dump(notes, f, indent=4)

    def load(self) -> List[Note]:
        with open(self.file_path, "rt") as f:
            raw_notes = json.load(f)
        return [Note.from_dict(note) for note in raw_notes]

    @property
    def info(self):
        return {'file_path': self.file_path}


class CsvFile(Storage):
    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w'):
                pass

    def save(self, notes: List[Note]) -> None:
        with open(self.file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(Note.fields)
            for note in notes:
                writer.writerow(note.as_tuple())

    def load(self) -> List[Note]:

        notes = []
        with open(self.file_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                notes.append(Note.from_dict(row))
        return notes

    @property
    def info(self):
        return {'file_path': self.file_path}
    

class SqliteDB(Storage):
    def __init__(self, db_path: str, table_name: str = None):
        self.db_path = db_path
        self.table_name = table_name or 'notes1'
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id TEXT PRIMARY KEY,
                    text TEXT,
                    created_at TEXT
                )
            """)
            conn.commit()

    def save(self, notes: List[Note]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany(f"""
                INSERT OR REPLACE INTO {self.table_name} (id, text, created_at)
                VALUES (?, ?, ?)
            """, [note.as_tuple() for note in notes])
            conn.commit()

    def load(self) -> List[Note]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name}")
            rows = cursor.fetchall()
        return [Note.from_tuple(row) for row in rows]

    @property
    def info(self):
        return {'db_path': self.db_path, 'table_name': self.table_name}
    

class SqlServerDB(Storage):
    def __init__(self, server_name: str, database: str, table: str = 'notes', login: str = None, password: str = None):
        if pyodbc is None:
            raise ModuleNotFoundError('`pyodbc` must be installed in order to interact with sql server')
        self.server_name = server_name
        self.database = database
        self.table = table
        self.login = login
        self.password = password
        self.connection_string = self._build_connection_string()
        self._initialize_db()

    def _build_connection_string(self) -> str:
        if self.login and self.password:
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server_name};DATABASE={self.database};UID={self.login};PWD={self.password}"
        else:
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server_name};DATABASE={self.database};Trusted_Connection=yes;"

    def _initialize_db(self):
        with pyodbc.connect(self.connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{self.table}' AND xtype='U')
                CREATE TABLE {self.table} (
                    id NVARCHAR(50) PRIMARY KEY,
                    text NVARCHAR(MAX),
                    created_at DATETIME
                )
            """)
            conn.commit()

    def save(self, notes: List[Note]) -> None:
        with pyodbc.connect(self.connection_string) as conn:
            cursor = conn.cursor()
            for note in notes:
                cursor.execute(f"""
                    MERGE {self.table} AS target
                    USING (VALUES (?, ?, ?)) AS source (id, text, created_at)
                    ON target.id = source.id
                    WHEN MATCHED THEN
                        UPDATE SET text = source.text
                    WHEN NOT MATCHED THEN
                        INSERT (id, text, created_at)
                        VALUES (source.id, source.text, source.created_at);
                """, note.as_tuple())
            conn.commit()

    def load(self) -> List[Note]:
        with pyodbc.connect(self.connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table}")
            rows = cursor.fetchall()
        return [Note.from_tuple(row) for row in rows]

    @property
    def info(self):
        return {
            'server_name': self.server_name,
            'database': self.database,
            'table': self.table,
            'login': self.login if self.login else 'Trusted_Connection'
        }
