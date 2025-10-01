from django.db import models
from apps.base.models import BaseModel
from apps.maintenance.models import Company, Skill
from apps.job.choices import TypeJobChoices, StatusChoices, ResultChoices, ModeChoices
from apps.candidate.models import Candidate
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.signals import pre_save
from django.dispatch import receiver


class JobPositions(BaseModel):
    name = models.CharField(
        verbose_name="Nombre de puesto", max_length=255, null=True, blank=True
    )
    description = models.TextField(verbose_name="Descripción de puesto")

    class Meta:
        verbose_name = "Posición"
        verbose_name_plural = "Posiciones"
        ordering = ("created_at",)

    def __str__(self):
        return self.name


class JobOffers(BaseModel):
    title = models.CharField(verbose_name="Nombre de oferta laboral", max_length=255)
    description = models.TextField(verbose_name="Descripción de oferta", max_length=255)
    job_position = models.ForeignKey(
        JobPositions,
        verbose_name="Posición",
        on_delete=models.CASCADE,
        related_name="jobpositions_joboffers",
    )
    company = models.ForeignKey(
        Company,
        verbose_name="Empresa",
        on_delete=models.CASCADE,
        related_name="company_joboffers",
    )
    location = models.CharField(
        verbose_name="Lugar", max_length=255, null=True, blank=True
    )
    start_date = models.DateField(verbose_name="Fecha de inicio", null=True, blank=True)
    end_date = models.DateField(
        verbose_name="Fecha de finalización", null=True, blank=True
    )
    is_active = models.BooleanField(verbose_name="¿Activo?", null=True, blank=True)
    employment_type = models.CharField(
        verbose_name="Tipo de trabajo",
        max_length=50,
        null=True,
        blank=True,
        choices=TypeJobChoices.choices,
    )
    salary_min = models.DecimalField(
        verbose_name="Salario mínimo",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    salary_max = models.DecimalField(
        verbose_name="Salario máximo",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    mode = models.CharField(
        verbose_name="Modalidad",
        max_length=50,
        null=True,
        blank=True,
        choices=ModeChoices.choices,
    )
    is_urgent = models.BooleanField(verbose_name="Es uregente?", null=True, blank=True)

    class Meta:
        verbose_name = "Oferta Laboral"
        verbose_name_plural = "Ofertas Laborales"
        ordering = ("created_at",)

    def __str__(self):
        return self.title


class JobSkill(BaseModel):
    jobOffers = models.ForeignKey(
        JobOffers, on_delete=models.CASCADE, related_name="skills_joboffert"
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, verbose_name="Habilidad")

    class Meta:
        verbose_name = "Habilidad para puesto"
        verbose_name_plural = "Habilidades para puesto"
        ordering = ("created_at",)


class JobRequirements(BaseModel):
    jobOffers = models.ForeignKey(
        JobOffers, on_delete=models.CASCADE, related_name="requirements_joboffert"
    )
    description = models.CharField(
        verbose_name="Description de requisitos", max_length=255
    )

    class Meta:
        verbose_name = "Requisito de puesto"
        verbose_name_plural = "Requisitos de puesto"
        ordering = ("created_at",)

    def __str__(self):
        return self.description


class JobBenefits(BaseModel):
    jobOffers = models.ForeignKey(
        JobOffers, on_delete=models.CASCADE, related_name="benefits_joboffert"
    )
    description = models.CharField(
        verbose_name="Description de beneficios", max_length=255
    )

    class Meta:
        verbose_name = "Beneficio de puesto"
        verbose_name_plural = "Beneficios de puesto"
        ordering = ("created_at",)

    def __str__(self):
        return self.description


class JobApplications(BaseModel):
    candidate = models.ForeignKey(
        Candidate,
        verbose_name="Candidato",
        on_delete=models.CASCADE,
        related_name="jobapplication_candidate",
    )
    joboffers = models.ForeignKey(
        JobOffers,
        verbose_name="Oferta laboral",
        on_delete=models.CASCADE,
        related_name="jobapplication_joboffers",
    )
    status = models.CharField(
        verbose_name="Estado",
        max_length=255,
        null=True,
        blank=True,
        choices=StatusChoices.choices,
    )
    candidate_snapshot = models.JSONField(
        verbose_name="Datos del candidato al momento de la postulación",
        blank=True,
        null=True,
        encoder=DjangoJSONEncoder,
        editable=False,
    )

    has_snapshot = models.BooleanField(
        verbose_name="Información del usuario almacenada",
        default=False,
    )

    class Meta:
        verbose_name = "Postulacion"
        verbose_name_plural = "Postulaciones"
        ordering = ("created_at",)

    def save(self, *args, **kwargs):
        if not self.candidate_snapshot:
            candidate = self.candidate
            snapshot = {
                "name": candidate.name,
                "email": candidate.user.email if candidate.user else None,
                "document_type": candidate.document_type,
                "document_number": candidate.document_number,
                "country": candidate.country,
                "photograph": (
                    candidate.photograph.url if candidate.photograph else None
                ),
                "gender": candidate.gender,
                "birth_date": str(candidate.birth_date),
                "education_level": candidate.education_level,
                "location": candidate.location,
                "short_bio": candidate.short_bio,
                "cv_file": candidate.cv_file.url if candidate.cv_file else None,
                "linkedin_url": candidate.linkedin_url,
                "portfolio_url": candidate.portfolio_url,
                "has_recommendation": candidate.has_recommendation,
                "availability": candidate.availability,
                "skills": [
                    {"skill": s.skill.name, "proficiency_level": s.proficiency_level}
                    for s in candidate.skills.all()
                ],
                "experiences": [
                    {
                        "company_name": e.company_name,
                        "position": e.position,
                        "start_date": str(e.start_date) if e.start_date else None,
                        "end_date": str(e.end_date) if e.end_date else None,
                        "description": e.description,
                    }
                    for e in candidate.experiences.all()
                ],
                "educations": [
                    {
                        "institution": edu.institution,
                        "degree": edu.degree,
                        "field_of_study": edu.field_of_study,
                        "start_date": str(edu.start_date) if edu.start_date else None,
                        "end_date": str(edu.end_date) if edu.end_date else None,
                        "is_study": edu.is_study,
                        "description": edu.description,
                    }
                    for edu in candidate.educations.all()
                ],
            }
            self.candidate_snapshot = snapshot
            self.has_snapshot = True

        super().save(*args, **kwargs)


class AplicationsAiAnalysis(BaseModel):
    jobApplications = models.ForeignKey(
        JobApplications,
        verbose_name="Posición",
        on_delete=models.CASCADE,
        related_name="analysis",
    )
    match_score = models.DecimalField(
        verbose_name="Resultado de evaluación",
        max_digits=5,
        decimal_places=5,
        null=True,
        blank=True,
    )
    status = models.CharField(
        verbose_name="Resultado de evaluación",
        max_length=255,
        null=True,
        blank=True,
        choices=ResultChoices.choices,
    )
    observation = models.CharField(
        verbose_name="Observaciones", max_length=500, null=True, blank=True
    )

    class Meta:
        verbose_name = "Análisis de Postulación"
        verbose_name_plural = "Análisis de Postulación"
        ordering = ("created_at",)
