from django.db.models import TextChoices


class DocumentTypeChoices(TextChoices):
    DNI = 'Dni', 'Dni'
    CE = 'Carnet extranjeria', 'Carnet extranjeria'
    PASSPORT = 'Pasaporte', 'Pasaporte'
    EMPTY = '', ''


class SexoChoices(TextChoices):
    M = 'Masculino', 'Masculino'
    F = 'Femenino', 'Femenino'

class CountryChoices(TextChoices):
    PERU = 'Perú' , 'Perú'
    CHILE = 'Chile' , 'Chile'
    ECUADOR = 'Ecuador' , 'Ecuador'

class EducationNivelChoices(TextChoices):
    SE = 'Secundaria' , 'Secundaria'
    TE = 'Tecnico', 'Tecnico'
    LI = 'Licenciatura','Licenciatura'
    MA = 'Maestría', 'Maestría'
    DO = "Doctorado", "Doctorado"