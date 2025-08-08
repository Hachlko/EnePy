import os
import json

MEMORY_FILE = "data/ene_memory.json"

def clean_memory_file():
    if not os.path.exists(MEMORY_FILE):
        print("Fichier mémoire inexistant, rien à nettoyer.")
        return

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("Fichier mémoire corrompu (JSON invalide), suppression.")
            os.remove(MEMORY_FILE)
            return

    if isinstance(data, list):
        print("Mémoire est une liste au lieu d'un dictionnaire, nettoyage en cours...")
        # Soit on supprime le fichier
        os.remove(MEMORY_FILE)
        print("Fichier mémoire supprimé. Une nouvelle mémoire sera créée à la prochaine sauvegarde.")
    elif isinstance(data, dict):
        print("Mémoire correcte, aucun nettoyage nécessaire.")
    else:
        print("Mémoire a un format inconnu, suppression pour repartir à zéro.")
        os.remove(MEMORY_FILE)

if __name__ == "__main__":
    clean_memory_file()
