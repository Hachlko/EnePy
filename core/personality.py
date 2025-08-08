import json
import os
from random import sample

CONFIG_FILE = "data/ene_config.json"
PERSONALITY_FILE = "data/ene_personality.json"

def load_config():
    config_path = "config.json"  # ou un autre chemin si tu as configuré différemment
    if not os.path.exists(config_path):
        print(f"⚠️ Fichier {config_path} introuvable, chargement de la config par défaut.")
        return {"mode": "ene"}

    with open(config_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Le fichier {config_path} est vide ou mal formé. Chargement config par défaut.")
            return {"mode": "ene"}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def load_personality(mode="ene") -> list[str]:
    if not os.path.exists(PERSONALITY_FILE):
        return []

    with open(PERSONALITY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    traits = []

    if mode == "takane":
        takane_all = data.get("takane_traits", [])
        # Prendre un échantillon aléatoire pour éviter que ce soit toujours les mêmes
        traits = sample(takane_all, k=min(6, len(takane_all)))
        return traits

    # Mode Ene : on mélange groupe par groupe + extras
    grouped = data.get("grouped_traits", {})
    for category, group_traits in grouped.items():
        if group_traits:
            traits.append(sample(group_traits, k=1)[0])  # 1 par groupe

    extras = data.get("ene_traits", [])
    if extras:
        traits += sample(extras, k=2)  # Traits bonus pour varier encore plus

    return traits

def format_traits(traits: list[str]) -> str:
    if not traits:
        return "Je n’ai trouvé aucun trait de personnalité !"
    return f"Ene, voici un rappel de ta personnalité actuelle : {', '.join(traits)}."
