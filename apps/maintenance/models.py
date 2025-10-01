from django.db import models
from apps.base.models import BaseModel
from apps.maintenance.choices import CategoryChoices, SizeChoices

class Skill(BaseModel):
    name = models.CharField(verbose_name="Nombre de Habilidad", max_length=100, unique=True)
    description = models.CharField(verbose_name="Descripción de Habilidad", max_length=300, unique=True,null=True, blank=True)
    category = models.CharField(verbose_name="Categoria de Habilidad", max_length=20, choices=CategoryChoices.choices, default="technical")

    class Meta:
        verbose_name='Habilidad'
        verbose_name_plural= 'Habilidades'
        ordering = ('created_at',)

    def __str__(self):
        return self.name


class Company (BaseModel):
    name = models.CharField(verbose_name="Nombre de Compañia", max_length=100, unique=True)
    legal_name = models.CharField(verbose_name="Nombre de Legal de la Compañia", max_length=100, unique=True)
    tax_id =models.CharField(verbose_name="RUC", max_length=20, unique=True)
    industry = models.CharField(verbose_name="Industria", max_length=20, unique=True)
    address =  models.CharField(verbose_name="Dirección", max_length=20, unique=True)
    phone =models.CharField(verbose_name="Número telefónico", max_length=10, unique=True)
    email= models.EmailField(verbose_name="Correo electrónico", max_length=100, unique=True)
    size = models.CharField(verbose_name="Tamaño de la empresa", max_length=20, choices=SizeChoices.choices)

    class Meta:
        verbose_name='Empresa'
        verbose_name_plural= 'Empresas'
        ordering = ('created_at',)

    def __str__(self):
        return self.name