import streamlit as st
from dotenv import load_dotenv
from utils.auth import register, login, logout, load_all_users
from utils.note_manager import load_shared_notes, save_note, load_notes, delete_note, share_note
from utils.question_generator import quiz_mode
from utils.stats_manager import load_stats
import os

# Umgebungsvariablen laden
load_dotenv()

# Titel der Anwendung
st.title("📚 LernManager")
st.write("Willkommen beim LernManager! Eine Anwendung, um seine Vorlesungen aktiv zu lernen.")

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

# Dunkelmodus anwenden
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
if not st.session_state["api_key_configured"]:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Wähle eine Seite",
        ["API-Key konfigurieren"],
        key="auth_navigation"
    )
else:
    st.sidebar.title("Navigation")
    if not st.session_state["logged_in"]:
        page = st.sidebar.radio(
            "Wähle eine Seite",
            ["Login", "Registrierung", "API-Key bearbeiten"],
            key="auth_navigation"
        )
    else:
        page = st.sidebar.radio(
            "Wähle eine Seite",
            ["Dashboard", "Notizen", "Quiz", "Statistiken", "Profil", "Einstellungen", "Über die Anwendung"],
            key="main_navigation"
        )

# Hauptinhalt basierend auf der ausgewählten Seite
if page == "API-Key konfigurieren" or page == "API-Key bearbeiten":
    st.header("API-Key konfigurieren")
    st.write("""
        Um den LernManager zu nutzen, benötigst du einen DeepSeek API-Key. 
        Gehe auf [OpenRouter](https://openrouter.ai), erstelle ein kostenloses Konto und generiere einen API-Key für DeepSeek.
        Gib den Key unten ein, um fortzufahren.
    """)
    api_key = st.text_input("Gib deinen DeepSeek API-Key ein", value=st.session_state["deepseek_api_key"], key="api_key_input")
    if st.button("API-Key speichern", key="save_api_key_button"):
        if api_key:
            with open(".env", "w") as env_file:
                env_file.write(f"DEEPSEEK_API_KEY={api_key}")
            st.session_state["api_key_configured"] = True
            st.session_state["deepseek_api_key"] = api_key
            st.success("API-Key erfolgreich gespeichert!")
            # Lade die Umgebungsvariablen neu, um den neuen API-Key zu verwenden
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
        # Lade die Notizen und Statistiken des Benutzers
        notes = load_notes(st.session_state["user_id"])
        stats = load_stats(st.session_state["user_id"])

        # Anzahl der Notizen
        num_notes = len(notes) if notes else 0
        st.write(f"**Anzahl der Notizen:** {num_notes}")

        # Anzahl der Quizze
        num_quizzes = len(stats) if stats else 0
        st.write(f"**Anzahl der durchgeführten Quizze:** {num_quizzes}")

        # Durchschnittliche Punktzahl
        if stats:
            total_score = sum(stat[1] for stat in stats)
            average_score = total_score / num_quizzes
            st.write(f"**Durchschnittliche Punktzahl:** {average_score:.2f}/25")
        else:
            st.write("**Durchschnittliche Punktzahl:** Noch keine Quizze durchgeführt.")


    elif page == "Notizen":
        save_note(st.session_state["user_id"])
        notes = load_notes(st.session_state["user_id"])
        shared_notes = load_shared_notes(st.session_state["user_id"])

        if notes or shared_notes:
            st.write("Deine Notizen:")
            for note in notes:
                st.subheader(note[1])
                st.write(note[2])
                if st.button(f"Notiz löschen {note[0]}", key=f"delete_note_{note[0]}"):
                    delete_note(note[0])

                # Liste der Benutzer zum Teilen der Notiz
                all_users = load_all_users()
                if all_users:
                    shared_with_username = st.selectbox(
                        f"Notiz mit Benutzer teilen (Notiz {note[0]})",
                        all_users,
                        key=f"share_note_{note[0]}"
                    )
                    if st.button(f"Notiz {note[0]} teilen", key=f"share_button_{note[0]}"):
                        if shared_with_username != st.session_state["username"]:  # Verhindere, dass man sich selbst teilt
                            share_note(note[0], st.session_state["user_id"], shared_with_username)
                        else:
                            st.error("Du kannst keine Notiz mit dir selbst teilen.")
                else:
                    st.warning("Keine anderen Benutzer gefunden.")

            st.write("Mit dir geteilte Notizen:")
            for shared_note in shared_notes:
                st.subheader(f"{shared_note[1]} (geteilt von {shared_note[3]})")
                st.write(shared_note[2])
        else:
            st.warning("Keine Notizen gefunden. Bitte erstelle zuerst eine Notiz.")

    elif page == "Quiz":
        quiz_mode(st.session_state["user_id"])

    elif page == "Statistiken":
        st.header("Statistiken")
        stats = load_stats(st.session_state["user_id"])
        if stats:
            st.write("Deine detaillierten Statistiken:")

            # Tabelle mit allen Quiz-Ergebnissen
            st.write("### Quiz-Ergebnisse")
            for stat in stats:
                st.write(f"**Notiz:** {stat[0]}, **Punktzahl:** {stat[1]}/25, **Datum:** {stat[2]}")

            # Bestes und schlechtestes Ergebnis
            best_score = max(stats, key=lambda x: x[1])
            worst_score = min(stats, key=lambda x: x[1])
            st.write("### Bestes Ergebnis:")
            st.write(f"**Notiz:** {best_score[0]}, **Punktzahl:** {best_score[1]}/25, **Datum:** {best_score[2]}")
            st.write("### Schlechtestes Ergebnis:")
            st.write(f"**Notiz:** {worst_score[0]}, **Punktzahl:** {worst_score[1]}/25, **Datum:** {worst_score[2]}")

            # Entwicklung der Punktzahl über die Zeit (optional)
            st.write("### Entwicklung der Punktzahl über die Zeit")
            dates = [stat[2] for stat in stats]
            scores = [stat[1] for stat in stats]
            st.line_chart({"Punktzahl": scores}, use_container_width=True)
        else:
            st.warning("Keine Statistiken gefunden. Bitte führe zuerst ein Quiz durch.")

    elif page == "Profil":
        st.header("Profil")
        st.write(f"Eingeloggt als: {st.session_state['username']}")
        if st.button("Ausloggen", key="logout_button"):
            logout()

    elif page == "Einstellungen":
        st.header("Einstellungen")
        st.write("Konfiguriere die Anwendungseinstellungen.")

        # Dunkelmodus aktivieren/deaktivieren
        dark_mode = st.checkbox(
            "Dunkelmodus aktivieren",
            value=st.session_state["dark_mode"],
            key="dark_mode_checkbox"
        )
        if dark_mode != st.session_state["dark_mode"]:
            st.session_state["dark_mode"] = dark_mode
            st.rerun()  # Seite neu laden, um den Dunkelmodus anzuwenden

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
            3. **Quiz-Modus**: Beantworte die Fragen und überprüfe dein Wissen.
            4. **Statistiken**: Verfolge deine Fortschritte und verbessere dich.

            ### DeepSeek API-Key
            Um Fragen zu generieren, benötigst du einen DeepSeek API-Key. 
            Du kannst diesen kostenlos auf [OpenRouter](https://openrouter.ai) erstellen.
        """)