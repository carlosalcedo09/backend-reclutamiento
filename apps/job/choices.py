from django.db.models import TextChoices

class TypeJobChoices(TextChoices):
    PT = "Part-Time", "Part-Time"
    FT = "Full-Time", "Full-Time"

class StatusChoices(TextChoices):
    ENV = "Enviado", "Enviado"
    EVAL = "En evaluación", "En evaluación"
    PRO = "Procesado", "Procesado"

class ResultChoices(TextChoices):
    AP= "Apto", "Apto"
    NA= "No apto", "No apto"
