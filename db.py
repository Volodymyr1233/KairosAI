from peewee import *
from pathlib import Path

database_path = str(Path(__file__).resolve().parent / "baza.db")

db = SqliteDatabase(database_path)
db.connect()
