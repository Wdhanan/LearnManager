import sqlite3
from sqlite3 import Error

def create_connection():
    """Erstelle eine Verbindung zur SQLite-Datenbank."""
    conn = None
    try:
        conn = sqlite3.connect("data/lernmanager.db")
        return conn
    except Error as e:
        print(e)
    return conn

def create_tables():
    """Erstelle die notwendigen Tabellen in der Datenbank."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            # Tabelle für Benutzer
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            # Tabelle für Notizen
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
             # Tabelle für geteilte Notizen
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shared_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER NOT NULL,
                    shared_by_user_id INTEGER NOT NULL,
                    shared_with_user_id INTEGER NOT NULL,
                    FOREIGN KEY (note_id) REFERENCES notes (id),
                    FOREIGN KEY (shared_by_user_id) REFERENCES users (id),
                    FOREIGN KEY (shared_with_user_id) REFERENCES users (id)
                )
            """)

            # Tabelle für Statistiken
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    note_id INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (note_id) REFERENCES notes (id)
                )
            """)
            conn.commit()
        except Error as e:
            print(e)
        finally:
            conn.close()

if __name__ == "__main__":
    create_tables()