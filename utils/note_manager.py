import streamlit as st
import sqlite3
from sqlite3 import Error
from utils.database import create_connection

def save_note(user_id, title, content):
    """
    Speichert eine neue Notiz in der Datenbank.
    :param user_id: Die ID des Benutzers
    :param title: Der Titel der Notiz
    :param content: Der Inhalt der Notiz
    """
    if title and content:
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)", (user_id, title, content))
                conn.commit()
                st.success("Notiz gespeichert!")
            except Error as e:
                st.error(f"Fehler beim Speichern der Notiz: {e}")
            finally:
                conn.close()
    else:
        st.error("Titel und Inhalt dürfen nicht leer sein.")

def edit_note(note_id, new_title, new_content):
    """
    Bearbeitet eine vorhandene Notiz.
    :param note_id: Die ID der Notiz
    :param new_title: Der neue Titel der Notiz
    :param new_content: Der neue Inhalt der Notiz
    """
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE notes SET title = ?, content = ? WHERE id = ?", (new_title, new_content, note_id))
            conn.commit()
            st.success("Notiz erfolgreich bearbeitet!")
        except Error as e:
            st.error(f"Fehler beim Bearbeiten der Notiz: {e}")
        finally:
            conn.close()

def share_note(note_id, shared_by_user_id, shared_with_username):
    """
    Teilt eine Notiz mit einem anderen Benutzer.
    :param note_id: ID der Notiz
    :param shared_by_user_id: ID des Besitzers der Notiz
    :param shared_with_username: Benutzername des Empfängers
    """
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            # Hole die Benutzer-ID des Empfängers basierend auf dem Benutzernamen
            cursor.execute("SELECT id FROM users WHERE username = ?", (shared_with_username,))
            shared_with_user = cursor.fetchone()
            if shared_with_user:
                shared_with_user_id = shared_with_user[0]
                # Füge die geteilte Notiz in die Datenbank ein
                cursor.execute(
                    "INSERT INTO shared_notes (note_id, shared_by_user_id, shared_with_user_id) VALUES (?, ?, ?)",
                    (note_id, shared_by_user_id, shared_with_user_id),
                )
                conn.commit()
                st.success(f"Notiz erfolgreich mit {shared_with_username} geteilt!")
            else:
                st.error(f"Benutzer '{shared_with_username}' nicht gefunden.")
        except Error as e:
            st.error(f"Fehler beim Teilen der Notiz: {e}")
        finally:
            conn.close()

def load_shared_notes(user_id):
    """
    Lädt die mit dem Benutzer geteilten Notizen.
    :param user_id: Die ID des Benutzers
    :return: Liste der geteilten Notizen
    """
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT notes.id, notes.title, notes.content, users.username
                FROM shared_notes
                JOIN notes ON shared_notes.note_id = notes.id
                JOIN users ON shared_notes.shared_by_user_id = users.id
                WHERE shared_notes.shared_with_user_id = ?
            """, (user_id,))
            shared_notes = cursor.fetchall()
            return shared_notes
        except Error as e:
            st.error(f"Fehler beim Laden der geteilten Notizen: {e}")
        finally:
            conn.close()
    return []

def load_notes(user_id):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, content FROM notes WHERE user_id = ?", (user_id,))
            notes = cursor.fetchall()
            return notes
        except Error as e:
            st.error(f"Fehler beim Laden der Notizen: {e}")
        finally:
            conn.close()
    return []

def delete_note(note_id):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            st.success("Notiz gelöscht!")
        except Error as e:
            st.error(f"Fehler beim Löschen der Notiz: {e}")
        finally:
            conn.close()