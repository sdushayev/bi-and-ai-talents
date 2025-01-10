import configparser
import os
from pathlib import Path

from core.storage import Storage, JsonFile, CsvFile, SqliteDB, SqlServerDB

DEBUG = False

class Settings:

    def __init__(self):
        parser = configparser.ConfigParser()
        parser.read(Path(__file__).resolve().parent / 'config.ini')
        mode = 'dev' if DEBUG else 'prod'
        self.source_type = parser[mode].get('source_type')
        self.source_file = parser[mode].get('source_file')
        if self.source_type == 'file':
            _, ext = os.path.splitext(self.source_file)
            self.ext = ext[1:]
        self.server = parser[mode].get('server')
        self.database = parser[mode].get('database')
        self.table = parser[mode].get('table')
        self.login = parser[mode].get('login')
        self.password = parser[mode].get('password')

    @property
    def storage(self) -> Storage:
        if self.source_type == 'file':
            if self.ext == 'json':
                return JsonFile(self.source_file)
            elif self.ext == 'csv':
                return CsvFile(self.source_file)
            elif self.ext in ('db', 'sqlite', 'sqlite3'):
                return SqliteDB(self.source_file, self.table)
            else:
                raise ValueError(f'Not supported file format: {self.source_file!r}')
        elif self.source_type == 'mssql':
            return SqlServerDB(self.server, self.database, self.table, self.login, self.password)
        else:
            raise ValueError(f'Not supported source type: {self.source_type!r}')
        


            
