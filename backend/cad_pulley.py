import cadquery as cq
from io import BytesIO

def build_pulley(diameter_mm: float, rope_mm: float, width_mm: float = None):
    """
    Construit une poulie simple avec gorge en V.
    Compatible CadQuery 2.4+ (OpenCascade 7.8).
    """
    # Définitions des paramètres
    W = width_mm or (2.0 * rope_mm)
    R = diameter_mm / 2.0
    depth = rope_mm * 0.5
    v_angle = 60  # angle de la gorge

    # --- 1️⃣ Créer le corps de la poulie ---
    part = (
        cq.Workplane("XY")
        .circle(R)
        .extrude(W)
    )

    # --- 2️⃣ Créer la gorge (coupe en V) ---
    # On crée un petit triangle et on le revolve à 360°
    triangle = (
        cq.Workplane("XZ")
        .workplane(offset=W / 2.0)
        .polyline([
            (0, 0),
            (depth, depth / 2),
            (depth, -depth / 2),
        ])
        .close()
        .revolve(360)
    )

    # On soustrait la gorge au cylindre
    part = part.cut(triangle)

    return part


def export_step_bytes(shape: cq.Workplane) -> bytes:
    """Exporte la pièce en format STEP (retourne les bytes)."""
    buffer = BytesIO()
    cq.exporters.export(shape, buffer, exportType="STEP")
    return buffer.getvalue()


def export_stl_bytes(shape: cq.Workplane) -> bytes:
    """Exporte la pièce en format STL (retourne les bytes)."""
    buffer = BytesIO()
    cq.exporters.export(shape, buffer, exportType="STL")
    return buffer.getvalue()
