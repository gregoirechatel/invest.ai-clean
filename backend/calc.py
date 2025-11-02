from backend.rules import Spec
import math

YIELD = {
    "S235": 235e6,
    "S355": 355e6,
    "42CrMo4": 900e6,
    "Al-6082": 250e6,
    "PA6": 70e6,
}

def compute_mechanics(spec: Spec) -> dict:
    """
    Calculs simplifiés :
    - effort (N)
    - moment fléchissant (N·m)
    - diamètre d’axe minimal (mm)
    - facteur de sécurité
    """
    g = 9.81
    F = spec.load_mass_kg * g
    L = 0.03 if spec.type == "porte-a-faux" else 0.015
    M = F * L
    Re = YIELD[spec.material]
    d_min = ((32 * M) / (math.pi * Re / 2)) ** (1/3) * 1000
    safety = (Re / (16 * M / (math.pi * (d_min/1000)**3)))

    return {
        "charge_N": round(F, 2),
        "moment_Nm": round(M, 2),
        "axe_min_mm": round(d_min, 2),
        "facteur_securite": round(safety, 2)
    }
