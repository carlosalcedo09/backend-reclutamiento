from django.db import models
from apps.base.models import BaseModel
from apps.maintenance.models import Skill
from apps.candidate.choices import DocumentTypeChoices, SexoChoices, CountryChoices,EducationNivelChoices
from apps.job.choices import TypeJobChoices
from apps.users.models import User

class Candidate(BaseModel):
    user = models.ForeignKey(User, verbose_name="Cuenta del candidato", null=True, blank=True, on_delete=models.CASCADE, related_name="account_candidate")
    document_type = models.CharField(verbose_name="Tipo de documento", default=None, null=True, blank=True, max_length=30, choices=DocumentTypeChoices.choices)
    document_number = models.CharField('Código', max_length=10)
    country = models.CharField(verbose_name="País de procedencia", null=True, blank=True, default=None, max_length=100, choices=CountryChoices.choices)
    photograph = models.ImageField(verbose_name="Fotografía", upload_to="candidates/photos/", blank=True, null=True)
    name = models.CharField(verbose_name="Nombre Completo", max_length=255)
    gender = models.CharField(verbose_name="Sexo", null=True, blank=True, default=None, max_length=30, choices=SexoChoices.choices)
    birth_date = models.DateField(verbose_name='Fecha de nacimiento', help_text='Fecha de fallecimiento de candidato')
    education_level  = models.CharField(verbose_name='Nivel de educación', max_length=255, blank=True, null=True,choices=EducationNivelChoices.choices)
    location = models.CharField(verbose_name='Dirección', max_length=255, blank=True, null=True)
    short_bio = models.TextField(verbose_name='Breve biografía', blank=True, null=True)

    cv_file = models.FileField(upload_to="candidates/cv/", blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    experience_years= models.CharField( verbose_name="Años de experiencia", blank=True, null=True , default=0)
    has_recommendation = models.BooleanField( verbose_name="¿Recomendación?", blank=True, null=True, default=False)
    avaliability = models.CharField (verbose_name="Disponibilidad", blank=True, null=True,choices=TypeJobChoices.choices )


    class Meta:
        verbose_name='Candidato'
        verbose_name_plural= 'Candidatos'
        ordering = ('created_at',)


    def __str__(self):
        return self.name

class CandidateSkill(BaseModel):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level = models.IntegerField(verbose_name='Nivel de manejo de habilidad', default=1)

    class Meta:
        unique_together = ("candidate", "skill")
        verbose_name='Habilidad'
        verbose_name_plural= 'Habilidades'
        ordering = ('created_at',)

    def __str__(self):
        return f"{self.candidate} - {self.skill} ({self.proficiency_level})"

class Experience(BaseModel):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="experiences")
    company_name = models.CharField( verbose_name="Nombre de Compañia", max_length=255)
    position = models.CharField(verbose_name="Cargo", max_length=255)
    start_date = models.DateField(verbose_name="Fecha de Inicio",blank=True, null=True)
    end_date = models.DateField(verbose_name="Fecha de Fin", blank=True, null=True)  
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name='Experiencia'
        verbose_name_plural= 'Experiencias'
        ordering = ('created_at',)
        

    def __str__(self):
        return f"{self.position} en {self.company_name}"


class Education(BaseModel):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="educations")
    institution = models.CharField(verbose_name="Institución",max_length=255)
    degree = models.CharField(verbose_name="Grado",max_length=255) 
    field_of_study = models.CharField(verbose_name="Campo de estudio", max_length=255, blank=True, null=True)
    start_date = models.DateField(verbose_name="Fecha de Inicio", blank=True, null=True)
    end_date = models.DateField(verbose_name="Fecha de Fin",blank=True, null=True)
    is_study = models.BooleanField(verbose_name="¿Actualmente estudias?",blank=True, null=True)
    description = models.TextField(verbose_name="Breve Descripción",blank=True, null=True)

    def __str__(self):
        return f"{self.degree} en {self.institution}"
