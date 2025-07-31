import requests
import os

def brave_search(query, api_key=None, num_results=3):
    if not api_key:
        api_key = os.environ.get("BRAVE_API_KEY")
    if not api_key:
        raise ValueError("Clé API Brave manquante. Définis BRAVE_API_KEY dans ton environnement.")

    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key
    }
    params = {
        "q": query,
        "count": num_results,
        "search_lang": "fr"
    }
    url = "https://api.search.brave.com/res/v1/web/search"

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    results = []
    for entry in data.get("web", {}).get("results", [])[:num_results]:
        results.append({
            "title": entry.get("title"),
            "snippet": entry.get("description"),
            "url": entry.get("url")
        })

    return results