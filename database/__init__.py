from pathlib import Path
from database.connection import get_connection

def init_db() -> None:
    """Run schema.sql on startup. Safe to call every launch — IF NOT EXISTS
    means existing tables and data are never touched."""
    schema = Path(__file__).parent / "schema.sql"
    with get_connection() as conn:
        conn.executescript(schema.read_text())