import json
from core.voice import VoiceEngine, listen_hotword_then_transcribe
from core.config import load_config
from core.memory import load_memory, save_memory
from core.search import search_brave
from core.decision import decision_engine
from core.assistant import EneAssistant

def load_personality_traits(path="data/ene_personality.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("ene_traits", [])

def search_web(query: str) -> str:
    try:
        results = search_brave(query)
        if not results:
            return "J’ai rien trouvé... Essaie avec d’autres mots ?"
        lines = ["Voici ce que j’ai trouvé :"]
        for i, res in enumerate(results[:3], start=1):
            lines.append(f"{i}. {res['title']} - {res['url']}")
        return "\n".join(lines)
    except Exception as e:
        return f"Oups… J’ai eu un souci en cherchant. Détails : {e}"

def remove_duplicate_paragraphs(text: str) -> str:
    seen = set()
    result = []
    for paragraph in text.strip().split("\n\n"):
        p = paragraph.strip()
        if p and p not in seen:
            result.append(p)
            seen.add(p)
    return "\n\n".join(result)

def main():
    config = load_config("data/ene_config.json")
    mode = config.get("mode", "ene")

    traits = load_personality_traits()
    memory = load_memory()
    voice_engine = VoiceEngine()
    assistant = EneAssistant()

    print(f"💻 Ene est en ligne en mode '{mode}'.\n")

    while True:
        user_mode = input("Tape 'v' pour voix, 't' pour texte, ou 'quit' pour sortir: ").strip().lower()

        if user_mode == 'quit':
            print("👋 Ene: À bientôt, Maître~ ! Ne me déconnecte pas trop longtemps, hein ?")
            break

        if user_mode not in ('v', 't'):
            print("Mode invalide, tape 'v', 't' ou 'quit'.")
            continue

        if user_mode == 'v':
            print("Dis ene puis ta phrase...")
            user_input = listen_hotword_then_transcribe(voice_engine)
            if not user_input:
                print("Je n'ai rien entendu, réessaie.")
                continue
        else:  # mode texte
            user_input = input("Écris ta question : ").strip()
            if not user_input:
                continue

        print("⏳ Ene réfléchit...")

        # Décision sur l’action à prendre
        decision = decision_engine(user_input, skills={})

        if decision["action"] == "search_web":
            response = search_web(decision["payload"])
        elif decision["action"] == "execute_skill":
            response = f"Exécution du skill: {decision['payload']}"
        else:
            response = assistant.generate_response(user_input, traits, memory)

        print(f"Ene : {response}")
        voice_engine.say(response)

        # Sauvegarde mémoire
        save_memory(memory)

if __name__ == "__main__":
    main()
