import base64
from datetime import date, datetime
import requests
import os
from apps.job.choices import ResultChoices

API_URL = "http://localhost:8000/api/evaluate"

def base64_pdf(file_field) -> str | None:
    """
    Convierte un FileField de Django (PDF) a base64.
    Si el archivo no existe, retorna None.
    """
    if not file_field or not getattr(file_field, "path", None):
        return None

    path = file_field.path
    if not os.path.exists(path):
        return None

    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def calculate_experience_years(candidate):
    """
    Calcula los años totales de experiencia laboral de un candidato.
    Si no hay end_date, se asume la fecha actual.
    Si no hay experiencias válidas, retorna 0.0 años.
    """
    total_days = 0
    today = date.today()

    for exp in candidate.experiences.all():
        if not exp.start_date:
            continue  # ignorar experiencias sin fecha de inicio

        # Si no hay fecha de fin, asumimos que sigue vigente
        end = exp.end_date or today

        # Evitar valores inconsistentes (end < start)
        if end < exp.start_date:
            continue

        # Diferencia en días
        delta = (end - exp.start_date).days
        total_days += delta

    # Convertir días a años (365 días ≈ 1 año)
    total_years = total_days / 365 if total_days > 0 else 0.0

    # Si solo hay una experiencia sin end_date y muy reciente (< 1 año),
    # podemos asumir al menos 1 año de experiencia básica
    if total_years < 1 and candidate.experiences.exists():
        return 1.0

    return round(total_years, 1)


def decide_status(score: float) -> str:
    if score >= 75:
        return ResultChoices.AP  # Aprobado, recomendado
    elif score >= 55:
        return ResultChoices.AP  # Aprobado, competitivo
    else:
        return ResultChoices.RC  # Rechazado
    
def parse_time_str(value):
    """Convierte string a objeto time soportando varios formatos."""
    if not value:
        return None
    value = str(value).strip()

    # Lista de formatos posibles
    formats = ["%H:%M:%S", "%H:%M", "%H:%M:%S.%f", "%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue

    print(f"⚠️ No se pudo parsear la hora: '{value}'")
    return None