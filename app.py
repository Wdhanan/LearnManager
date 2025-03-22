import streamlit as st
from dotenv import load_dotenv
from utils.auth import register, login, logout, load_all_users
from utils.note_manager import load_shared_notes, save_note, load_notes, delete_note, share_note, edit_note
from utils.question_generator import quiz_mode
from utils.stats_manager import load_stats
import os

# Umgebungsvariablen laden
load_dotenv()

# Farben für die Anwendung
PRIMARY_COLOR = "#4A90E2"  # Blau
SECONDARY_COLOR = "#F5F5F5"  # Hellgrau
TERTIARY_COLOR = "#333333"  # Dunkelgrau
ACCENT_COLOR = "#FFA500"  # Orange

# Custom CSS für einheitliches Design
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {SECONDARY_COLOR};
        color: {TERTIARY_COLOR};
    }}
    .stButton>button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
    }}
    .stButton>button:hover {{
        background-color: {ACCENT_COLOR};
    }}
    .stHeader {{
        color: {PRIMARY_COLOR};
    }}
    .stSidebar {{
        background-color: {PRIMARY_COLOR};
        color: white;
    }}
    .stExpander {{
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    .divider {{
        border-top: 2px solid {PRIMARY_COLOR};
        margin: 1rem 0;
    }}
    .note-grid {{
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 1rem;
    }}
    .note-list {{
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    .note-form {{
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Titel der Anwendung
st.title("📚 LernManager")
st.write("Willkommen beim LernManager! Eine Anwendung, um deine Vorlesungen aktiv zu lernen.")

# Zustandsvariablen initialisieren
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "api_key_configured" not in st.session_state:
    st.session_state["api_key_configured"] = os.getenv("DEEPSEEK_API_KEY") is not None
if "deepseek_api_key" not in st.session_state:
    st.session_state["deepseek_api_key"] = os.getenv("DEEPSEEK_API_KEY", "")
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False  # Standardmäßig ist der Dunkelmodus deaktiviert

# Dunkelmodus anwenden (nur auf den Hauptinhalt)
if st.session_state["dark_mode"]:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Seitenleiste für Navigation
st.sidebar.title("Navigation")
if not st.session_state["api_key_configured"]:
    page = st.sidebar.radio(
        "Wähle eine Seite",
        ["API-Key konfigurieren"],
        key="auth_navigation"
    )
else:
    if not st.session_state["logged_in"]:
        page = st.sidebar.radio(
            "Wähle eine Seite",
            ["Login", "Registrierung", "API-Key bearbeiten"],
            key="auth_navigation"
        )
    else:
        page = st.sidebar.radio(
            "Wähle eine Seite",
            ["Dashboard", "Notizen", "Rätsel", "Statistiken", "Profil", "Einstellungen", "Über die Anwendung"],
            key="main_navigation"
        )

# Hauptinhalt basierend auf der ausgewählten Seite
if page == "API-Key konfigurieren" or page == "API-Key bearbeiten":
    st.header("API-Key konfigurieren")
    with st.container():
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        with st.container():
            st.write("""
                Um den LernManager zu nutzen, benötigst du einen DeepSeek API-Key. 
                Gehe auf [OpenRouter](https://openrouter.ai), erstelle ein kostenloses Konto und generiere einen API-Key für DeepSeek.
                Gib den Key unten ein, um fortzufahren.
            """)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                api_key = st.text_input("Gib deinen DeepSeek API-Key ein", value=st.session_state["deepseek_api_key"], key="api_key_input")
                if st.button("API-Key speichern", key="save_api_key_button"):
                    if api_key:
                        with open(".env", "w") as env_file:
                            env_file.write(f"DEEPSEEK_API_KEY={api_key}")
                        st.session_state["api_key_configured"] = True
                        st.session_state["deepseek_api_key"] = api_key
                        st.success("API-Key erfolgreich gespeichert!")
                        load_dotenv(override=True)
                    else:
                        st.error("Bitte gib einen gültigen API-Key ein.")

elif not st.session_state["logged_in"]:
    if page == "Login":
        login()
    elif page == "Registrierung":
        register()
else:
    if page == "Dashboard":
        st.header("Dashboard")
        st.write("Hier siehst du eine Übersicht deiner Aktivitäten.")
        notes = load_notes(st.session_state["user_id"])
        stats = load_stats(st.session_state["user_id"])

        # Anzahl der Notizen
        num_notes = len(notes) if notes else 0
        st.write(f"**Anzahl der Notizen:** {num_notes}")

        # Anzahl der Quizze
        num_quizzes = len(stats) if stats else 0
        st.write(f"**Anzahl der durchgeführten Rätsel:** {num_quizzes}")

        # Durchschnittliche Punktzahl
        if stats:
            total_score = sum(stat[1] for stat in stats)
            average_score = total_score / num_quizzes
            st.write(f"**Durchschnittliche Punktzahl:** {average_score:.2f}/25")
        else:
            st.write("**Durchschnittliche Punktzahl:** Noch keine Rätsel durchgeführt.")

    elif page == "Notizen":
        st.header("📝 Notizen")
        with st.container():
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.write("### Erstelle oder bearbeite Notizen")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write("#### Erstellte Notizen")
                notes = load_notes(st.session_state["user_id"])
                shared_notes = load_shared_notes(st.session_state["user_id"])
                all_notes = notes + shared_notes
                if all_notes:
                    selected_note = st.selectbox("Wähle eine Notiz", [note[1] for note in all_notes], key="note_selection")
                    selected_note_id = next(note[0] for note in all_notes if note[1] == selected_note)
                    col1_1, col1_2 = st.columns(2)
                    with col1_1:
                        if st.button("✏️ Bearbeiten", key="edit_note_button"):
                            st.session_state["edit_note_id"] = selected_note_id
                    with col1_2:
                        if st.button("🗑️ Löschen", key="delete_note_button"):
                            delete_note(selected_note_id)
                            st.rerun()
                else:
                    st.warning("Keine Notizen gefunden.")

            with col2:
                st.write("#### Notiz erstellen/bearbeiten")
                if "edit_note_id" in st.session_state:
                    note_to_edit = next(note for note in all_notes if note[0] == st.session_state["edit_note_id"])
                    title = st.text_input("Titel", value=note_to_edit[1], key="edit_title")
                    content = st.text_area("Inhalt", value=note_to_edit[2], key="edit_content")
                else:
                    title = st.text_input("Titel", key="new_title")
                    content = st.text_area("Inhalt", key="new_content")

                col2_1, col2_2 = st.columns(2)
                with col2_1:
                    if st.button("Speichern", key="save_note_button"):
                        if "edit_note_id" in st.session_state:
                            edit_note(st.session_state["edit_note_id"], title, content)
                            del st.session_state["edit_note_id"]
                        else:
                            save_note(st.session_state["user_id"], title, content)
                        st.rerun()
                with col2_2:
                    if st.button("Abbrechen", key="cancel_note_button"):
                        if "edit_note_id" in st.session_state:
                            del st.session_state["edit_note_id"]
                        st.rerun()

                st.write("#### Notiz teilen")
                # Alle Benutzer laden und den aktuellen Benutzer herausfiltern
                all_users = load_all_users()
                if all_users:
                    if notes:  # Überprüfen, ob Notizen vorhanden sind
                        shared_with_username = st.selectbox(
                            f"Notiz mit Benutzer teilen (Notiz {selected_note})",  # Verwende den Titel der ausgewählten Notiz
                            all_users,  # Zeige nur Benutzernamen an
                            key=f"share_note_{selected_note_id}"  # Verwende die ID der ausgewählten Notiz
                        )
                        if st.button(f"Notiz {selected_note} teilen", key=f"share_button_{selected_note_id}"):
                            if shared_with_username != st.session_state["username"]:
                                share_note(selected_note_id, st.session_state["user_id"], shared_with_username)
                            else:
                                st.error("Du kannst keine Notiz mit dir selbst teilen.")
                    else:
                        st.warning("Keine Notizen gefunden. Bitte erstelle zuerst eine Notiz.")
                else:
                    st.warning("Keine anderen Benutzer gefunden.")

    elif page == "Rätsel":
        quiz_mode(st.session_state["user_id"])

    elif page == "Statistiken":
        st.header("Statistiken")
        stats = load_stats(st.session_state["user_id"])
        if stats:
            st.write("Deine detaillierten Statistiken:")
            st.write("### Rätsel-Ergebnisse")
            for stat in stats:
                st.write(f"**Notiz:** {stat[0]}, **Punktzahl:** {stat[1]}/25, **Datum:** {stat[2]}")

            best_score = max(stats, key=lambda x: x[1])
            worst_score = min(stats, key=lambda x: x[1])
            st.write("### Bestes Ergebnis:")
            st.write(f"**Notiz:** {best_score[0]}, **Punktzahl:** {best_score[1]}/25, **Datum:** {best_score[2]}")
            st.write("### Schlechtestes Ergebnis:")
            st.write(f"**Notiz:** {worst_score[0]}, **Punktzahl:** {worst_score[1]}/25, **Datum:** {worst_score[2]}")

            st.write("### Entwicklung der Punktzahl über die Zeit")
            dates = [stat[2] for stat in stats]
            scores = [stat[1] for stat in stats]
            st.line_chart({"Punktzahl": scores}, use_container_width=True)
        else:
            st.warning("Keine Statistiken gefunden. Bitte führe zuerst ein Rätsel durch.")

    elif page == "Profil":
        st.header("Profil")
        st.write(f"Eingeloggt als: {st.session_state['username']}")
        if st.button("Ausloggen", key="logout_button"):
            logout()

    elif page == "Einstellungen":
        st.header("Einstellungen")
        st.write("Konfiguriere die Anwendungseinstellungen.")

        dark_mode = st.checkbox(
            "Dunkelmodus aktivieren",
            value=st.session_state["dark_mode"],
            key="dark_mode_checkbox"
        )
        if dark_mode != st.session_state["dark_mode"]:
            st.session_state["dark_mode"] = dark_mode
            st.rerun()

    elif page == "Über die Anwendung":
        st.header("Über die Anwendung")
        st.write("""
            ## LernManager – Dein Assistent für aktives Lernen
            Der LernManager ist eine Webanwendung, die dir hilft, effektiver zu lernen. 
            Mit dieser Anwendung kannst du:
            - **Notizen erstellen und verwalten**
            - **Fragen basierend auf deinen Notizen generieren**
            - **Deine Lernfortschritte verfolgen**

            ### Wie funktioniert es?
            1. **Notizen erstellen**: Gib deine Lerninhalte ein.
            2. **Fragen generieren**: Die Anwendung generiert automatisch Fragen basierend auf deinen Notizen.
            3. **Rätsel-Modus**: Beantworte die Fragen und überprüfe dein Wissen.
            4. **Statistiken**: Verfolge deine Fortschritte und verbessere dich.

            ### DeepSeek API-Key
            Um Fragen zu generieren, benötigst du einen DeepSeek API-Key. 
            Du kannst diesen kostenlos auf [OpenRouter](https://openrouter.ai) erstellen.
        """)