from pydantic import BaseModel
from typing import Literal, Optional

class PulleySpec(BaseModel):
    type: Literal["chape", "porte-a-faux"] = "chape"
    load_mass_kg: float = 500.0
    duty_hours: Optional[float] = None
    material: Optional[str] = "S355"
    diameter_mm: float = 120.0
    rope_diameter_mm: float = 10.0
    width_mm: Optional[float] = None  # par défaut 2×rope_diameter
