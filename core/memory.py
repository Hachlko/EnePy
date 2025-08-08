import json
import os
from datetime import datetime

MEMORY_FILE = "data/ene_memory.json"

def load_memory() -> dict:
    """Charge la mémoire depuis le fichier JSON,
    convertit la liste en dict si besoin."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    new_data = {}
                    for entry in data:
                        ts = entry.get("timestamp") or datetime.now().isoformat(timespec='seconds')
                        user = entry.get("user", "")
                        ene = entry.get("ene", "")
                        new_data[ts] = {"user": user, "ene": ene}
                    return new_data
                elif isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass
    return {}

def save_memory(memory: dict) -> None:
    """Sauvegarde la mémoire dans le fichier JSON."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def get_recent_memories(memory: dict, max_entries=7) -> str:
    """Retourne les derniers échanges sous forme de texte lisible."""
    if not memory:
        return "Aucune conversation passée trouvée..."

    try:
        sorted_entries = sorted(memory.items(), reverse=True)
    except Exception as e:
        return f"[ERROR] Problème tri mémoire : {e}"

    recent = sorted_entries[:max_entries]

    lines = []
    for timestamp, entry in recent:
        user = entry.get("user", "")
        ene = entry.get("ene", "")
        lines.append(f"[{timestamp}] Toi : {user}")
        lines.append(f"[{timestamp}] Ene : {ene}")

    return "\n".join(lines)

def add_conversation_entry(memory: dict, user_text: str, ene_text: str) -> None:
    """Ajoute une nouvelle entrée en évitant les doublons récents."""
    # Vérifie dans les 3 derniers messages s'il y a un doublon exact
    recent_entries = list(memory.items())[-3:]
    for _, entry in recent_entries:
        if entry.get("user") == user_text and entry.get("ene") == ene_text:
            return  # Doublon détecté, on n'ajoute pas

    timestamp = datetime.now().isoformat(timespec='seconds')
    memory[timestamp] = {
        "user": user_text,
        "ene": ene_text
    }

def clean_memory(memory: dict) -> dict:
    """Nettoie la mémoire en supprimant les doublons (même user/ene) en gardant le premier."""
    seen = set()
    cleaned = {}

    for timestamp, entry in sorted(memory.items()):
        key = (entry.get("user"), entry.get("ene"))
        if key not in seen:
            seen.add(key)
            cleaned[timestamp] = entry

    return cleaned
