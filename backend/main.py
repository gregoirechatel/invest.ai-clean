from fastapi import FastAPI, Response
from backend.rules import PulleySpec
from backend.cad_pulley import build_pulley, export_step_bytes, export_stl_bytes
import requests
import os

app = FastAPI()

# ==========================================================
# 1️⃣ Accueil
# ==========================================================
@app.get("/")
def home():
    """Affiche la page d'accueil HTML"""
    return Response(
        content=open("templates/index.html", encoding="utf-8").read(),
        media_type="text/html",
    )

# ==========================================================
# 2️⃣ Appel IA
# ==========================================================
@app.post("/ia")
def analyse_ia(payload: dict):
    """Appelle l'API OpenRouter avec la clé définie dans les variables d'environnement GitHub/Render"""
    prompt = payload.get("text", "")
    api_key = os.getenv("OPENROUTER_API_KEY")  # 🔑 clé chargée automatiquement par GitHub/Render
    url = "https://api.openrouter.ai/v1/chat/completions"

    if not api_key:
        return {"error": "Clé API OpenRouter manquante (variable d'environnement OPENROUTER_API_KEY non trouvée)"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = {
        "model": "anthropic/claude-3-haiku",
        "messages": [
            {
                "role": "system",
                "content": "Tu es un ingénieur mécanique. Rends un JSON clair des caractéristiques d'une poulie demandée.",
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
# 3️⃣ Génération de la poulie STEP
# ==========================================================
@app.post("/cad/pulley")
def cad_build_pulley(spec: PulleySpec):
    """Construit une poulie 3D STEP"""
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

# ==========================================================
# 4️⃣ Génération de la poulie STL
# ==========================================================
@app.post("/cad/pulley/stl")
def cad_build_pulley_stl(spec: PulleySpec):
    """Construit une poulie 3D STL"""
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
