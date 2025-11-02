import os
import json
import re
import requests  # <— cette ligne est parfaitement correcte

# Récupération de la clé API OpenRouter depuis Render (variable d’environnement)
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

# Modèle IA utilisé (Claude 3 Haiku = rapide, stable, peu coûteux)
MODEL = "anthropic/claude-3-haiku"

def interpret_prompt(prompt: str) -> dict:
    """
    Envoie le texte utilisateur à OpenRouter et récupère
    un JSON structuré décrivant la conception mécanique.
    """

    if not OPENROUTER_KEY:
        raise ValueError("Clé OpenRouter manquante sur Render.")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Tu es un ingénieur mécanique expert. "
                    "Analyse la demande utilisateur et fournis un JSON structuré avec les clés suivantes : "
                    "type (chape ou porte-a-faux), load_mass_kg, duty_hours, material, "
                    "diameter_mm, rope_diameter_mm, et commentaire. "
                    "Ne renvoie rien d'autre que ce JSON."
                )
            },
            {"role": "user", "content": prompt}
        ]
    }

    # Requête HTTP vers OpenRouter
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )

    if response.status_code != 200:
        raise RuntimeError(f"Erreur API OpenRouter : {response.text}")

    content = response.json()["choices"][0]["message"]["content"]

    # Extraction du JSON depuis la réponse IA
    try:
        json_str = re.search(r"\{.*\}", content, re.S).group()
        return json.loads(json_str)
    except Exception:
        return {"reponse_brute": content}
