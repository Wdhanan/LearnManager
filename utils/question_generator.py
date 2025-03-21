import os
import json
import logging
import re
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
from utils.note_manager import load_notes
from utils.stats_manager import save_stats

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()

# Configuration API
api_key = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# Verzeichnis für Fragen
QUESTIONS_DIR = "data/questions"
os.makedirs(QUESTIONS_DIR, exist_ok=True)

def generate_questions(note_title, note_content):
    """
    Generiert Fragen basierend auf dem Inhalt der Notizen mithilfe der DeepSeek-API.
    :param note_title: Titel der Notiz
    :param note_content: Inhalt der Notiz
    :return: Eine Liste von generierten Fragen
    """
    try:
        prompt = (
            f"Generiere Fragen basierend auf dem folgenden Text. Die Fragen sollten offen sein und aktives Lernen fördern.\n"
            f"Für jede Frage gib ein JSON-Objekt mit zwei Schlüsseln zurück: 'frage' für die Frage und 'antwort' für die korrekte Antwort.\n"
            f"Text: {note_content}\n"
            f"Gib nur das JSON zurück, nichts anderes."
        )

        # Sende die Anfrage an die API
        response = client.chat.completions.create(
            extra_body={},
            model="deepseek/deepseek-chat",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )

        # Überprüfe die Antwort
        logging.info("API-Antwort: %s", response)
        generated_text = response.choices[0].message.content.strip()
        if generated_text.startswith("```json") and generated_text.endswith("```"):
            generated_text = generated_text.strip("```json").strip("```")
        if not generated_text:
            raise ValueError("Leere Antwort von der API erhalten.")

        # Lade das JSON
        try:
            questions = json.loads(generated_text)
        except json.JSONDecodeError as json_err:
            logging.error("Fehler beim Parsen des JSON: %s", json_err)
            raise ValueError("Die API-Antwort ist kein gültiges JSON.")

        # Speichere die Fragen in einer JSON-Datei
        json_file_path = os.path.join(QUESTIONS_DIR, f"{note_title}.json")
        with open(json_file_path, "w") as file:
            json.dump(questions, file, indent=4, ensure_ascii=False)
        logging.info("Fragen gespeichert in: %s", json_file_path)
        return questions

    except Exception as e:
        logging.error("Fehler bei der Generierung der Fragen: %s", e)
        return []

def load_questions(note_title):
    """
    Lädt die gespeicherten Fragen für eine bestimmte Notiz.
    :param note_title: Titel der Notiz
    :return: Liste der Fragen
    """
    json_file_path = os.path.join(QUESTIONS_DIR, f"{note_title}.json")
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as file:
            return json.load(file)
    return []

def evaluate_answer(question, user_answer, correct_answer):
    """
    Bewertet die Antwort des Benutzers mithilfe der DeepSeek-API.
    :param question: Die gestellte Frage
    :param user_answer: Die Antwort des Benutzers
    :param correct_answer: Die korrekte Antwort
    :return: Ein Dictionary mit der Bewertung
    """
    try:
        prompt = (
            f"Du bist ein Lehrer, der die Antwort eines Schülers bewertet.\n"
            f"Frage: {question}\n"
            f"Korrekte Antwort: {correct_answer}\n"
            f"Antwort des Schülers: {user_answer}\n\n"
            f"Bewertungsregeln:\n"
            f"- Kurze Antworten mit den wesentlichen Elementen verdienen eine hohe Punktzahl.\n"
            f"- Wenn die Schlüsselwörter vorhanden sind, sollte die Punktzahl hoch sein (4 oder 5).\n"
            f"- Die Form der Antwort ist weniger wichtig als der Inhalt.\n"
            f"- Präzise Antworten sind genauso gut wie detaillierte Antworten.\n\n"
            f"Gib NUR ein gültiges JSON im folgenden Format zurück: {{\"score\": X}}, wobei X eine Zahl zwischen 0 und 5 ist.\n"
            f"Verwende doppelte Anführungszeichen für den Schlüssel \"score\"."
        )

        response = client.chat.completions.create(
            extra_body={},
            model="deepseek/deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
        )

        if not response or not response.choices:
            raise ValueError("Die API hat keine gültige Antwort zurückgegeben.")

        raw_content = response.choices[0].message.content
        if not raw_content:
            raise ValueError("Die API-Antwort ist leer.")

        # Bereinige das JSON
        cleaned_content = raw_content.strip().strip("```json").strip("```")
        cleaned_content = cleaned_content.replace("'", '"')

        try:
            evaluation = json.loads(cleaned_content)
        except json.JSONDecodeError:
            # Versuche, die Punktzahl direkt zu extrahieren
            score_match = re.search(r'score["\']?\s*:\s*(\d+)', cleaned_content)
            if score_match:
                return {"score": int(score_match.group(1))}
            raise

        if "score" not in evaluation:
            raise ValueError("Das JSON enthält nicht den Schlüssel 'score'.")

        return {"score": evaluation["score"]}

    except Exception as e:
        logging.exception("Fehler bei der Bewertung der Antwort: %s", e)
        return {"score": 0}

def quiz_mode(user_id):
    st.header("Quiz-Modus")
    notes = load_notes(user_id)
    if notes:
        note_titles = [note[1] for note in notes]
        selected_note = st.selectbox("Wähle eine Notiz", note_titles, key="quiz_select_note")
        
        # Zurücksetzen der Fragen und Antworten, wenn eine neue Notiz ausgewählt wird
        if "selected_note" not in st.session_state or st.session_state["selected_note"] != selected_note:
            st.session_state["selected_note"] = selected_note
            st.session_state["questions"] = None
            st.session_state["answers"] = {}

        if st.button("Fragen generieren", key="generate_questions_button"):
            note_content = next(note[2] for note in notes if note[1] == selected_note)
            questions = generate_questions(selected_note, note_content)
            
            if questions:
                st.session_state["questions"] = questions  # Speichere die Fragen im session_state
                st.session_state["answers"] = {}  # Initialisiere die Antworten

        if "questions" in st.session_state and st.session_state["questions"]:
            st.write("Generierte Fragen:")
            questions = st.session_state["questions"]
            all_answered = True  # Überprüft, ob alle Fragen beantwortet wurden
            total_score = 0  # Gesamtpunktzahl für das Quiz

            for i, question in enumerate(questions, start=1):
                st.write(f"**Frage {i}:** {question['frage']}")
                
                # Antwortfeld mit session_state verknüpfen
                answer_key = f"user_answer_{i}"
                if answer_key not in st.session_state:
                    st.session_state[answer_key] = ""  # Initialisiere die Antwort
                
                # Textfeld für die Antwort
                user_answer = st.text_input(
                    f"Deine Antwort auf Frage {i}",
                    value=st.session_state[answer_key],  # Verwende den gespeicherten Wert
                    key=f"input_{answer_key}"  # Eindeutiger Schlüssel für das Widget
                )
                
                # Wenn der Benutzer eine Antwort eingibt, speichere sie im session_state
                if user_answer:
                    st.session_state[answer_key] = user_answer
                else:
                    all_answered = False  # Es gibt noch unbeantwortete Fragen

            # Button zum Anzeigen der Bewertung
            if all_answered and st.button("Quiz abschließen", key="finish_quiz_button"):
                st.write("### Bewertung:")
                for i, question in enumerate(questions, start=1):
                    answer_key = f"user_answer_{i}"
                    user_answer = st.session_state[answer_key]
                    evaluation = evaluate_answer(question['frage'], user_answer, question['antwort'])
                    st.write(f"**Frage {i}:** {question['frage']}")
                    st.write(f"Deine Antwort: {user_answer}")
                    st.write(f"Bewertung: {evaluation['score']}/5")
                    total_score += evaluation["score"]  # Addiere die Punktzahl zur Gesamtpunktzahl

                # Gesamtpunktzahl anzeigen
                st.write(f"### Gesamtpunktzahl: {total_score}/{len(questions) * 5}")
                # Statistik speichern
                note_id = next(note[0] for note in notes if note[1] == selected_note)
                save_stats(st.session_state["user_id"], note_id, total_score)

                # Antworten zurücksetzen
                for i in range(1, len(questions) + 1):
                    answer_key = f"user_answer_{i}"
                    st.session_state[answer_key] = ""  # Leere die Antworten

                # Optional: Fragen zurücksetzen
                st.session_state["questions"] = None
                st.success("Quiz abgeschlossen! Die Antworten wurden zurückgesetzt.")
    else:
        st.warning("Keine Notizen gefunden. Bitte erstelle zuerst eine Notiz.")