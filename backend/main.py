from fastapi import FastAPI, Response
from backend.rules import PulleySpec
from backend.cad_pulley import build_pulley, export_step_bytes, export_stl_bytes
import requests
import os

# ==========================================================
# ⚙️ Configuration
# ==========================================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "anthropic/claude-3-haiku"

app = FastAPI()

# ==========================================================
# 1️⃣ Page d'accueil
# ==========================================================
@app.get("/")
def home():
    """Affiche la page d'accueil HTML"""
    return Response(
        content=open("templates/index.html", encoding="utf-8").read(),
        media_type="text/html",
    )

# ==========================================================
# 2️⃣ Appel IA : interprétation du texte en JSON mécanique
# ==========================================================
@app.post("/ia")
def analyse_ia(payload: dict):
    """Appelle OpenRouter avec la clé API stockée dans les variables d'environnement"""
    prompt = payload.get("text", "")
    if not OPENROUTER_API_KEY:
        return {"error": "Clé API manquante. Définis OPENROUTER_API_KEY dans tes variables d'environnement."}

    url = "https://api.openrouter.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Tu es un ingénieur mécanique. "
                    "Analyse la demande et rends un JSON clair des caractéristiques d'une poulie demandée."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
    }

    try:
        r = requests.post(url, headers=headers, json=body, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", {})
    except Exception as e:
        return {"error": str(e)}

# ==========================================================
# 3️⃣ Génération de la poulie 3D au format STEP
# ==========================================================
@app.post("/cad/pulley")
def cad_build_pulley(spec: PulleySpec):
    """Construit une poulie 3D et renvoie le fichier STEP"""
    try:
        part = build_pulley(
            diameter_mm=spec.diameter_mm,
            rope_mm=spec.rope_diameter_mm,
            width_mm=spec.width_mm or (2.0 * spec.rope_diameter_mm),
        )
        step_bytes = export_step_bytes(part)
        return Response(
            content=step_bytes,
            media_type="model/step",
            headers={"Content-Disposition": "attachment; filename=pulley.step"},
        )
    except Exception as e:
        return {"error": str(e)}

# ==========================================================
# 4️⃣ Génération de la poulie 3D au format STL
# ==========================================================
@app.post("/cad/pulley/stl")
def cad_build_pulley_stl(spec: PulleySpec):
    """Construit une poulie 3D et renvoie le fichier STL"""
    try:
        part = build_pulley(
            diameter_mm=spec.diameter_mm,
            rope_mm=spec.rope_diameter_mm,
            width_mm=spec.width_mm or (2.0 * spec.rope_diameter_mm),
        )
        stl_bytes = export_stl_bytes(part)
        return Response(
            content=stl_bytes,
            media_type="model/stl",
            headers={"Content-Disposition": "attachment; filename=pulley.stl"},
        )
    except Exception as e:
        return {"error": str(e)}
