import streamlit as st
import sqlite3
from sqlite3 import Error
from utils.database import create_connection

def register():
    st.header("Registrierung")
    username = st.text_input("Benutzername", key="register_username")
    password = st.text_input("Passwort", type="password", key="register_password")
    if st.button("Registrieren", key="register_button"):
        if username and password:
            conn = create_connection()
            if conn is not None:
                try:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    conn.commit()
                    st.success("Registrierung erfolgreich! Bitte melde dich jetzt an.")
                    # Zurück zur Login-Seite
                    st.session_state["show_login"] = True
                except Error as e:
                    st.error(f"Fehler bei der Registrierung: {e}")
                finally:
                    conn.close()
        else:
            st.error("Benutzername und Passwort dürfen nicht leer sein.")

def login():
    st.header("Login")
    username = st.text_input("Benutzername", key="login_username")
    password = st.text_input("Passwort", type="password", key="login_password")
    if st.button("Einloggen", key="login_button"):
        if username and password:
            conn = create_connection()
            if conn is not None:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
                    user = cursor.fetchone()
                    if user:
                        st.session_state["logged_in"] = True
                        st.session_state["user_id"] = user[0]
                        st.session_state["username"] = username
                        st.success("Erfolgreich eingeloggt!")
                        # Aktualisiere die Navigation zur Hauptseite
                        st.rerun()   # Lade die Seite neu, um die Navigation zu aktualisieren
                    else:
                        st.error("Ungültige Anmeldedaten.")
                except Error as e:
                    st.error(f"Fehler beim Login: {e}")
                finally:
                    conn.close()
        else:
            st.error("Benutzername und Passwort dürfen nicht leer sein.")

def logout():
    if "logged_in" in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None
        st.session_state["username"] = None
        st.rerun()
        st.success("Erfolgreich ausgeloggt.")

def load_all_users():
    """
    Lädt alle registrierten Benutzer aus der Datenbank.
    :return: Liste der Benutzernamen
    """
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users")
            users = cursor.fetchall()
            return [user[0] for user in users]  # Extrahiere die Benutzernamen
        except Error as e:
            st.error(f"Fehler beim Laden der Benutzer: {e}")
        finally:
            conn.close()
    return []