import sqlite3

DB_NAME = "ingredients.db"

def get_connection():
    """Return a new connection to the main database."""
    return sqlite3.connect(DB_NAME)