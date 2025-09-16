from django.db import models
from apps.base.models import BaseModel
from apps.maintenance.models import Company, Skill
from apps.job.choices import TypeJobChoices, StatusChoices, ResultChoices
from apps.candidate.models import Candidate


class JobPositions (BaseModel):
    name  = models.CharField(verbose_name="Nombre de puesto", max_length=255, null=True, blank=True)
    description = models.TextField(verbose_name="Descripción de puesto")

    class Meta:
        verbose_name='Posición'
        verbose_name_plural= 'Posiciones'
        ordering = ('created_at',)


    def __str__(self):
        return self.name
    

class JobOffers(BaseModel):
    title = models.CharField(verbose_name="Nombre de oferta laboral", max_length=255)
    description = models.TextField(verbose_name="Descripción de oferta", max_length=255)
    job_position = models.ForeignKey(JobPositions, verbose_name='Posición', on_delete=models.CASCADE, related_name="jobpositions_joboffers")
    company =  models.ForeignKey(Company, verbose_name='Empresa', on_delete=models.CASCADE, related_name="company_joboffers")
    location = models.CharField(verbose_name="Lugar", max_length=255, null=True, blank=True)
    start_date= models.DateField(verbose_name="Fecha de inicio", null=True, blank=True)
    end_date = models.DateField(verbose_name="Fecha de finalización", null=True, blank=True)
    is_active = models.BooleanField(verbose_name="¿Activo?", null=True, blank=True)
    employment_type = models.CharField(verbose_name="Modalidad de trabajo", max_length=50, null=True, blank=True, choices=TypeJobChoices.choices)
    salary_min = models.DecimalField(verbose_name="Salario mínimo", max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(verbose_name="Salario máximo", max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name='Oferta Laboral'
        verbose_name_plural= 'Ofertas Laborales'
        ordering = ('created_at',)


    def __str__(self):
        return self.title


class JobSkill(BaseModel):
    jobOffers = models.ForeignKey(JobOffers, on_delete=models.CASCADE, related_name="skills_joboffert")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, verbose_name="Habilidad")

    class Meta:
        verbose_name='Habilidad para puesto'
        verbose_name_plural= 'Habilidades para puesto'
        ordering = ('created_at',)


class JobRequirements(BaseModel):
    jobOffers = models.ForeignKey(JobOffers, on_delete=models.CASCADE, related_name="requirements_joboffert")
    description =  models.CharField(verbose_name="Description de requisitos", max_length=255)

    class Meta:
        verbose_name='Requisito de puesto'
        verbose_name_plural= 'Requisitos de puesto'
        ordering = ('created_at',)

    def __str__(self):
        return self.description


class JobApplications(BaseModel):
    candidate = models.ForeignKey(Candidate, verbose_name='Candidato', on_delete=models.CASCADE, related_name="jobapplication_candidate")
    joboffers = models.ForeignKey(JobOffers, verbose_name='Oferta laboral', on_delete=models.CASCADE, related_name= "jobapplication_joboffers")
    status = models.CharField(verbose_name="Estado", max_length=255, null=True, blank=True, choices=StatusChoices.choices)

    class Meta:
        verbose_name='Postulacion'
        verbose_name_plural= 'Postulaciones'
        ordering = ('created_at',)



class AplicationsAiAnalysis(BaseModel):
    jobApplications = models.ForeignKey(JobApplications, verbose_name='Posición', on_delete=models.CASCADE, related_name="analysis")
    match_score = models.DecimalField( verbose_name="Resultado de evaluación", max_digits=5,  decimal_places=5, null=True, blank=True )
    status = models.CharField(verbose_name="Resultado de evaluación", max_length=255, null=True, blank=True, choices=ResultChoices.choices)
    observation = models.CharField(verbose_name="Observaciones", max_length=500, null=True, blank=True)

    class Meta:
        verbose_name='Análisis de Postulación'
        verbose_name_plural= 'Análisis de Postulación'
        ordering = ('created_at',)