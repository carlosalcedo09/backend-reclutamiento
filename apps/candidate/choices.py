from django.db.models import TextChoices,IntegerChoices 


class DocumentTypeChoices(TextChoices):
    DNI = "Dni", "Dni"
    CE = "Carnet extranjeria", "Carnet extranjeria"
    PASSPORT = "Pasaporte", "Pasaporte"
    EMPTY = "", ""


class SexoChoices(TextChoices):
    M = "Masculino", "Masculino"
    F = "Femenino", "Femenino"


class CountryChoices(TextChoices):
    PERU = "Perú", "Perú"
    CHILE = "Chile", "Chile"
    ECUADOR = "Ecuador", "Ecuador"
    ARGENTINA = "Argentina", "Argentina"
    ESPAÑA = "España", "España"
    GUAYAQUIL = "Guayaquil", "Guayaquil"
    COLOMBIA = "Colombia", "Colombia"
    BOLIVIA = "Bolivia", "Bolivia"


class EducationNivelChoices(TextChoices):
    BC = "Bachiller", "Bachiller"
    ES = "Especialidad", "Especialidad"
    DI = "Diplomado", "Diplomado"
    MA = "Maestría", "Maestría"
    DO = "Doctorado", "Doctorado"
    LI = "Licenciado", "Licenciado"
    TC = "Tecnico", "Tecnico"


class ProficiencyChoices(IntegerChoices):
    Basic = 1, "Básico"
    Intermediate = 2, "Intermedio"
    Advanced = 3, "Avanzado"
