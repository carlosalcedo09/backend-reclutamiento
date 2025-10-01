import base64
from datetime import date
import requests

API_URL = "http://localhost:8000/api/evaluate"

def base64_pdf(path: str | None) -> str | None:
    if not path:
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def calculate_experience_years(candidate):
    total_days = 0
    today = date.today()

    for exp in candidate.experiences.all():
        if exp.start_date:
            end = exp.end_date or today
            delta = end - exp.start_date
            total_days += delta.days

    # Convertir días a años (aprox 365 días por año)
    total_years = total_days / 365
    return round(total_years, 1)  # por ejemplo 3.5 años