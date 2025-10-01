from django.db.models import TextChoices


class TypeJobChoices(TextChoices):
    PT = "Part-Time", "Part-Time"
    FT = "Full-Time", "Full-Time"


class ModeChoices(TextChoices):
    R = "Remoto", "Remoto"
    P = "Presencial", "Presencial"
    H = "Híbrido", "Híbrido"


class StatusChoices(TextChoices):
    ENV = "Enviado", "Enviado"
    EVAL = "En evaluación", "En evaluación"
    PRO = "Procesado", "Procesado"


class ResultChoices(TextChoices):
    DS = "Desconocido", "Desconocido"
    NC = "No contratado", "No contratado"
    CN = "Contratado", "Contratado"
    RC = "Rechazado", "Rechazado"
    AP = "Aprobado", "Aprobado"
    EV = "Evaluado", "Evaluado"
    EA = "En evaluación", "En evaluación"