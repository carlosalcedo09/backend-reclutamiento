from django.db.models import TextChoices


class CategoryChoices(TextChoices):
        Technical = 'Técnica', 'Técnica'
        Soft = 'Blanda', 'Blanda'
        Language= 'Idioma', 'Idioma'
        Ofimatic = 'Ofimática', 'Ofimática'

class SizeChoices(TextChoices):
        Small = 'Pequeña', 'Pequeña'
        Median = 'Mediana', 'Mediana'
        Big = 'Grande', 'Grande'

        