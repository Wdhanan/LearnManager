import streamlit as st
import sqlite3
from sqlite3 import Error
from utils.database import create_connection

# Custom CSS für einheitliches Design
st.markdown(
    """
    <style>
    .stTextInput>div>div>input {
        border-radius: 8px;
        padding: 0.5rem;
        border: 1px solid #4A90E2;
        width: 100%;
    }
    .stButton>button {
        background-color: #4A90E2;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #FFA500;
    }
    .stHeader {
        color: #4A90E2;
        text-align: center;
    }
    .stSuccess {
        background-color: #E6F4EA;
        color: #2E7D32;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #2E7D32;
    }
    .stError {
        background-color: #FFEBEE;
        color: #C62828;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #C62828;
    }
    .centered-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 1rem;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .divider {
        border-top: 2px solid #4A90E2;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def register():
    st.header("Registrierung")
    with st.container():
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        with st.container():
            st.write("Bitte gib deine Daten ein, um dich zu registrieren.")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
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
                                st.session_state["show_login"] = True
                            except Error as e:
                                st.error(f"Fehler bei der Registrierung: {e}")
                            finally:
                                conn.close()
                    else:
                        st.error("Benutzername und Passwort dürfen nicht leer sein.")

def login():
    st.header("Login")
    with st.container():
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        with st.container():
            st.write("Bitte gib deine Anmeldedaten ein.")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
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
                                    st.rerun()  # Lade die Seite neu, um die Navigation zu aktualisieren
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
            cursor.execute("SELECT username FROM users")  # Nur Benutzernamen abfragen
            users = cursor.fetchall()
            return [user[0] for user in users]  # Extrahiere die Benutzernamen
        except Error as e:
            st.error(f"Fehler beim Laden der Benutzer: {e}")
        finally:
            conn.close()
    return []