import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Charge les variables d'environnement du fichier .env

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

def search_brave(query: str, count: int = 5) -> list[dict]:
    """
    Effectue une recherche web via l'API Brave et retourne une liste de résultats.
    Chaque résultat contient : title, url, snippet.
    """
    if not BRAVE_API_KEY:
        raise ValueError("Clé API Brave manquante dans les variables d'environnement.")

    headers = {
        "Accept": "application/json",
        "X-API-KEY": BRAVE_API_KEY
    }
    params = {"q": query, "size": count}

    response = requests.get(BRAVE_SEARCH_URL, headers=headers, params=params)
    response.raise_for_status()  # Lᵉve une exception HTTP en cas d'erreur

    data = response.json()
    results = [
        {
            "title": item.get("title", "Sans titre"),
            "url": item.get("url", ""),
            "snippet": item.get("description", "")
        }
        for item in data.get("web", [])
    ]
    return results

def search_web(query: str) -> str:
    """
    Recherche web et formate les résultats pour un retour textuel lisible.
    """
    try:
        results = search_brave(query)
        if not results:
            return "J’ai rien trouvé... Essaie avec d’autres mots ?"

        # Limite aux 3 premiers résultats
        lines = [f"Voici ce que j’ai trouvé :"]
        for i, res in enumerate(results[:3], start=1):
            lines.append(f"{i}. {res['title']} - {res['url']}")

        return "\n".join(lines)

    except Exception as e:
        return f"Oups… J’ai eu un souci en cherchant. Détails : {e}"
