from django.db.models import TextChoices


class CategoryChoices(TextChoices):
        Technical = 'Técnica', 'Técnica'
        Soft = 'Blanda', 'Blanda'
        Language= 'Idioma', 

class SizeChoices(TextChoices):
        Small = 'Pequeña', 'Pequeña'
        Median = 'Mediana', 'Mediana'
        Big = 'Grande', 'Grande'

        