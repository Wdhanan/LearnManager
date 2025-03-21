import sqlite3
from sqlite3 import Error
from utils.database import create_connection
from datetime import datetime
import streamlit as st

def save_stats(user_id, note_id, score):
    """
    Speichert die Statistik für eine Quiz-Session.
    :param user_id: Die ID des Benutzers
    :param note_id: Die ID der Notiz
    :param score: Die erreichte Punktzahl
    """
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO stats (user_id, note_id, score, timestamp) VALUES (?, ?, ?, ?)",
                (user_id, note_id, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
        except Error as e:
            st.error(f"Fehler beim Speichern der Statistik: {e}")
        finally:
            conn.close()

def load_stats(user_id):
    """
    Lädt die Statistiken für einen Benutzer.
    :param user_id: Die ID des Benutzers
    :return: Eine Liste von Statistiken (Notiz-Titel, Punktzahl, Datum)
    """
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT notes.title, stats.score, stats.timestamp
                FROM stats
                JOIN notes ON stats.note_id = notes.id
                WHERE stats.user_id = ?
                ORDER BY stats.timestamp DESC
            """, (user_id,))
            stats = cursor.fetchall()
            return stats
        except Error as e:
            st.error(f"Fehler beim Laden der Statistiken: {e}")
        finally:
            conn.close()
    return []