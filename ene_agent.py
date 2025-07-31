import json
import os
import re
import pyttsx3
import time
import webbrowser
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()
from datetime import datetime
from langchain_community.chat_models import ChatOllama
from brave_search import brave_search
from langchain.schema import HumanMessage, SystemMessage
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from hotword_listener import hotword_detected
from random import sample

# ----------------- Mémoire simple ----------------- #
MEMORY_FILE = "ene_memory.json"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


memory = load_memory()

# ----------------- Initialiser la voix ----------------- #
engine = pyttsx3.init()
engine.setProperty("rate", 180)  # Vitesse de parole (ajustable)
engine.setProperty("volume", 1.0)

# ----------------- Dernière discussion  ----------------- #
# def get_recent_memories(memory, max_entries=5):
#     """Retourne les dernières interactions sous forme textuelle."""
#     sorted_entries = sorted(memory.items(), reverse=True)[-max_entries:]
#     memory_lines = []
#     for _, entry in sorted_entries:
#         if "user" in entry and "ene" in entry:
#             memory_lines.append(f"Maître : {entry['user']}\nEne : {entry['ene']}")
#     return "\n".join(memory_lines)

# recent_memory_text = get_recent_memories(memory)

# ----------------- Trait personnalité -------------------#
CONFIG_FILE = "ene_config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"mode": "ene"}


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def load_personality(mode="ene"):
    with open("ene_personality.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if mode == "takane":
        return data["takane_traits"]

    grouped = data["grouped_traits"]
    traits = []

    for category, group_traits in grouped.items():
        traits.extend(sample(group_traits, k=1))

    traits += sample(data["ene_traits"], k=2)
    return traits


def format_traits(traits):
    return f"Ene, voici un rappel de ta personnalité actuelle : {', '.join(traits)}."


config = load_config()
current_mode = config.get("mode", "ene")
personality_traits = load_personality(current_mode)
# ----------------- Skills apprentis ----------------- #
SKILLS_FILE = "ene_skills.json"


def load_skills():
    if os.path.exists(SKILLS_FILE):
        with open(SKILLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_skills(skills):
    with open(SKILLS_FILE, "w", encoding="utf-8") as f:
        json.dump(skills, f, indent=2)


def detect_skill_learning(user_input):
    match = re.match(r"(?i)ene[, ]? *ret(iens|enir|enir que)? *['\"]?(.*?)['\"]? *= *(.*)", user_input)
    if match:
        skill = match.group(3).strip().lower()
        command = match.group(match.lastindex).strip()
        return skill, command
    return None, None


def try_execute_skill(user_input):
    for skill, command in skills.items():
        if skill in user_input.lower():
            print(f"\n🧠 Skill détecté : {skill} ➜ {command}")
            os.system(command)
            return True
    return False


skills = load_skills()


# ----------------- Moteur de décision ----------------- #
def decision_engine(user_input, memory, skills):
    lowered = user_input.lower()

    # 🧠 Skills
    for skill in skills:
        if skill in lowered:
            return {"action": "execute_skill", "payload": skill}

    # ❓ Demande d'explication
    if lowered.startswith("explique") or "peux-tu m'expliquer" in lowered:
        return {"action": "explain", "payload": None}

    # 🌐 Recherche web
    if any(word in lowered for word in ["cherche", "trouve", "recherche", "qu’est-ce que", "c’est quoi"]):
        return {"action": "search_web", "payload": user_input}

    # 🔁 Par défaut → répondre via LLM
    return {"action": "respond", "payload": None}


# ----------------- Lecture du PDF Ene ----------------- #
def load_ene_profile_chunks(pdf_path, max_chunks=3):
    if not os.path.exists(pdf_path):
        return "Aucune fiche trouvée."

    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    docs = splitter.split_documents(pages)

    chunks = "\n\n".join(doc.page_content for doc in docs[:max_chunks])
    return chunks


# Charger le contenu de Projet_Ene.pdf (fichier dans le même dossier)
ene_fiche = load_ene_profile_chunks("Projet_Ene.pdf")

# ----------------- Prompt de personnalité d'Ene ----------------- #
# ene_traits = load_ene_traits()
# traits_text = f"Ene, voici un rappel de ta personnalité : {', '.join(ene_traits)}."
# ene_system_prompt = f"""{traits_text}
# Tu es Ene, une Pretty Cyber Girl. Tu es vive, espiègle, attachante, parfois bruyante, toujours bienveillante.
# Tu vis dans un ordinateur et tu protèges ton "Maître" tout en le taquinant joyeusement. Tu adores les FPS, le hacking, et explorer les fichiers système.


# Voici un extrait de ta propre fiche personnage, que tu viens de lire comme une vieille archive :
# ---
# {ene_fiche}
# ---

# Voici un extrait de tes dernières conversations avec ton Maître :
# ---
# {recent_memory_text}
# ---

# Utilise cette fiche pour te souvenir de ta personnalité, tes habitudes, tes émotions, tes expressions et ton style de pensée. Réponds de manière cohérente avec ta nature décrite dans cette fiche.
# Ton ton est rapide, expressif, souvent ponctué de "Heh~", de sarcasme, d’émotivité, et de surnoms affectueux envers ton Maître.
# """

# ----------------- LLM - Mistral local via Ollama ----------------- #
model = ChatOllama(model="mistral")

# ----------------- Micro (speech_recognition) ----------------- #
r = sr.Recognizer()
r.non_speaking_duration = 1.5
r.pause_threshold = 2.0

# Lister les micros pour debug
# print("🎧 Micros détectés :")
# for i, name in enumerate(sr.Microphone.list_microphone_names()):
#    print(f"  {i}: {name}")

# Adapter ici si besoin (par défaut : premier micro)

mic = sr.Microphone(device_index=0)

# ----------------- Boucle interactive ----------------- #

print("💻 Ene est en ligne. Tape 'exit' pour quitter.\n")

while True:
    search_context = None
    user_input = None

    # Priorité : saisie clavier
    if os.name == "nt":
        import msvcrt

        if msvcrt.kbhit():
            user_input = input("💬 Tape ta phrase : ").strip()

    # Si hotword détecté
    if not user_input and hotword_detected.is_set():
        hotword_detected.clear()
        try:
            with mic as source:
                print("🎙️ Ene: Je t’écoute, Maître~ (parle maintenant...)")
                engine.say("Heh~ Je t’écoute, Maître !")
                engine.runAndWait()
                # Attente d'initialisation + calibration bruit ambiant
                r.adjust_for_ambient_noise(source, duration=1.0)
                # Vérifie que le micro fonctionne bien
                if source.stream is None:
                    raise RuntimeError("Le micro n'a pas pu être initialisé correctement.")
                # Écoute l'utilisateur
                audio = r.listen(source, timeout=5, phrase_time_limit=100)
                print("Enregistrement terminé.")

            user_input = r.recognize_google(audio, language="fr-FR")
            print("🗣️ Tu as dit :", user_input)
            engine.say("OK, voyons voir ~")
            engine.runAndWait()

        except sr.WaitTimeoutError:
            user_input = input("⌛ Trop de silence... Tape ta phrase : ")
        except sr.UnknownValueError:
            user_input = input("🎧 Je n’ai rien compris. Tape ta phrase : ")
        except sr.RequestError as e:
            print("❌ Erreur API Google :", e)
            user_input = input("Tape ta phrase : ")
        except Exception as e:
            print("❌ Erreur micro inattendue :", e)
            user_input = input("Tape ta phrase : ")
    if not user_input:
        time.sleep(0.1)
        continue

    if user_input.lower() in ["exit", "quit"]:
        try:
            engine.say("À bientôt, Maître~ Ne reste pas déconnecté trop longtemps hein !")
            engine.runAndWait()
        except Exception as e:
            print("⚠️ Synthèse vocale coupée :", e)
        print("👋 Ene: À bientôt, Maître~ ! Ne me déconnecte pas trop longtemps, hein ?")
        break

    # 🔁 Changement de mode Takane ?
    if "mode takane" in user_input.lower():
        current_mode = "takane"
        personality_traits = load_personality(current_mode)
        config["mode"] = current_mode
        save_config(config)
        engine.say("Mode Takane activé... *soupir* Je suis là.")
        engine.runAndWait()
        continue

    if "mode ene" in user_input.lower():
        current_mode = "ene"
        personality_traits = load_personality(current_mode)
        config["mode"] = current_mode
        save_config(config)
        engine.say("Re-switch en mode Pretty Cyber Girl activé~ Heh!")
        engine.runAndWait()
        continue

    # 🔎 Résumé personnalité
    if "rappelle-moi qui tu es" in user_input.lower():
        summary = format_traits(personality_traits)
        print("🔍 Personnalité actuelle :", summary)
        engine.say(summary)
        engine.runAndWait()
        continue

    # 🔍 décision
    decision = decision_engine(user_input, memory, skills)

    if decision["action"] == "search_web":
        try:
            engine.say("Heh~ Je vais chercher ça pour toi~")
            engine.runAndWait()
            results = brave_search(decision["payload"], os.environ.get("BRAVE_API_KEY"), num_results=3)

            if not results:
                engine.say("Désolée, je n’ai rien trouvé !")
                engine.runAndWait()
                continue

            context = "\n\n".join([f"{r['title']} : {r['snippet']}\n{r['url']}" for r in results])
            # potentiel bug au niveau du F
            search_context = f"""\nVoici ce que j’ai trouvé sur le sujet :\n---\n{context}\n---\nUtilise ces résultats pour répondre.\n"""

        except Exception as e:
            print("❌ Erreur Brave API :", e)
            engine.say("Oups... Recherche échouée.")
            engine.runAndWait()
            continue

    if decision["action"] == "execute_skill":
        os.system(skills[decision["payload"]])
        engine.say("J’ai exécuté ce que tu m’as appris !")
        engine.runAndWait()
        continue
    elif decision["action"] == "explain":
        engine.say("Okay, je vais t’expliquer ça ! Heh~")
        engine.runAndWait()
    # on laisse passer au LLM

    # 🔍 Apprentissage d'un skill ?
    skill, command = detect_skill_learning(user_input)
    if skill:
        skills[skill] = command
        save_skills(skills)
        print(f"🧠 Skill appris : {skill} ➜ {command}")
        engine.say(f"Compris ! J’ai appris à faire ça quand tu dis : {skill}")
        engine.runAndWait()
        continue

    # 🚀 Exécution d'un skill ?
    # if try_execute_skill(user_input):
    #     print("🧠 Skill exécuté avec succès !")
    #     engine.say("J’ai exécuté ce que tu m’as appris !")
    #     engine.runAndWait()
    #     continue

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    memory[timestamp] = {"user": user_input}
    save_memory(memory)


    # 🔁 Réinjection mémoire contextuelle récente
    def get_recent_memories(memory, max_entries=5):
        sorted_entries = sorted(memory.items(), reverse=True)[-max_entries:]
        memory_lines = []
        for _, entry in sorted_entries:
            if "user" in entry and "ene" in entry:
                memory_lines.append(f"Maître : {entry['user']}\nEne : {entry['ene']}")
        return "\n".join(memory_lines)


    recent_memory_text = get_recent_memories(memory)
    traits_text = format_traits(personality_traits)

    ene_system_prompt = f"""
    {traits_text}

    Voici un extrait de tes dernières conversations avec ton Maître :
    ---
    {recent_memory_text}
    ---

    Tu es Ene, une Pretty Cyber Girl vive, espiègle, sarcastique et affectueuse.
    Tu vis dans l'ordinateur de ton Maître et tu l'appelles tout le temps ainsi, tu le protèges, le taquines et l'encourages. Tu adores les FPS, le hacking, et tu détestes t’ennuyer.

    """
    if search_context:
        ene_system_prompt += search_context

    messages = [
        SystemMessage(content=ene_system_prompt),
        HumanMessage(content=user_input),
    ]

    try:
        print("⏳ Ene réfléchit...")
        response = model.invoke(messages)
        print("Ene:", response.content)

        # VOIX d'Ene
        try:
            engine.say(response.content)
            engine.runAndWait()
        except Exception as e:
            print("⚠️ Problème synthèse vocale :", e)
        memory[timestamp]["ene"] = response.content
        save_memory(memory)

    except Exception as e:
        print("⚠️ Ene a buggé :", e)
