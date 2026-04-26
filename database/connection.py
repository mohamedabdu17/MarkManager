import sqlite3
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = Path(os.getenv("DB_PATH", "markmanager.db"))

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts: row["name"]
    conn.execute("PRAGMA foreign_keys = ON")  # enforce ON DELETE CASCADE etc.
    return conn