from django.db import models
from apps.base.models import BaseModel
from apps.maintenance.models import Company, Skill
from apps.job.choices import (
    StatusInterviewChoices,
    TypeJobChoices,
    StatusChoices,
    ResultChoices,
    ModeChoices,
)
from apps.candidate.models import Candidate
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Q, Avg


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
    description = models.TextField(verbose_name="Descripción de oferta")
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
    status_interview = models.CharField(
        verbose_name="Estado de la entrevista",
        max_length=255,
        null=True,
        blank=True,
        choices=StatusInterviewChoices.choices,
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


class TimeMetrics(models.Model):
    job_application_batch = models.ForeignKey(
        JobApplications,
        on_delete=models.CASCADE,
        related_name="time_metrics",
        verbose_name="Postulación / Lote",
        null=True,
        blank=True,
    )
    request_id = models.CharField(
        "Identificador de la ejecución", max_length=64, unique=True, db_index=True
    )
    candidate_count = models.PositiveIntegerField("CVs procesados", default=0)

    started_at = models.DateTimeField("Inicio de la evaluación", null=True, blank=True)
    finished_at = models.DateTimeField("Fin de la evaluación", null=True, blank=True)

    processing_time_seconds = models.DecimalField(
        "Tiempo total (s)", max_digits=10, decimal_places=4
    )
    processing_time_per_candidate = models.DecimalField(
        "Tiempo promedio por CV (s)", max_digits=10, decimal_places=4
    )

    candidate_processing_times = models.JSONField(
        "Duración por CV",
        help_text="Lista de objetos {id, name, processing_time_seconds}",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Métrica de tiempo"
        verbose_name_plural = "Métricas de tiempo"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.request_id} ({self.processing_time_seconds}s)"

    def processing_time_minutes(self):
        return (
            float(self.processing_time_seconds) / 60
            if self.processing_time_seconds
            else 0.0
        )


class ApplicationsAiAnalysis(BaseModel):
    jobApplications = models.ForeignKey(
        JobApplications,
        verbose_name="Postulación",
        on_delete=models.CASCADE,
        related_name="analysis",
    )

    # Puntajes principales
    job_match_score = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    semantic_score = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    structural_score = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    overall_score = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )

    # Evaluación de equidad
    fairness_structural_score = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    fairness_overall_score = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    fairness_overall_delta = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )

    # JSON con detalle de breakdown
    structural_breakdown = models.JSONField(null=True, blank=True)
    fairness_groups = models.JSONField(null=True, blank=True)

    # Resultado final
    status = models.CharField(
        verbose_name="Resultado",
        max_length=255,
        null=True,
        blank=True,
        choices=ResultChoices.choices,
        default=ResultChoices.EA,
    )
    observation = models.CharField(
        verbose_name="Observaciones", max_length=500, null=True, blank=True
    )

    processing_start_time = models.TimeField(
        verbose_name="Hora de inicio de evaluación", null=True, blank=True
    )
    processing_end_time = models.TimeField(
        verbose_name="Hora de fin de evaluación", null=True, blank=True
    )
    processing_time_minutes = models.DecimalField(
        verbose_name="Duración de evaluación (segundos)",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Análisis de Postulación"
        verbose_name_plural = "Análisis de Postulaciones"
        ordering = ("created_at",)


class EvaluationSummary(models.Model):
    job_offer = models.ForeignKey(
        "JobOffers", on_delete=models.CASCADE, related_name="evaluation_summaries"
    )
    fecha = models.DateField()
    criterio = models.CharField(max_length=100)
    grupo_protegido = models.CharField(max_length=100)
    total_cvs_gp = models.PositiveIntegerField()
    cvs_preseleccionados_gp = models.PositiveIntegerField()
    tasa_seleccion_gp = models.FloatField()
    grupo_referente = models.CharField(max_length=100)
    total_cvs_gr = models.PositiveIntegerField()
    cvs_preseleccionados_gr = models.PositiveIntegerField()
    tasa_seleccion_gr = models.FloatField()
    spd = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Resumen de selección"
        verbose_name_plural = "Resumenes de selección"

    def __str__(self):
        return f"{self.criterio} ({self.fecha})"


class AccuracyMetrics(models.Model):
    interview_date = models.DateField(
        verbose_name="Fecha de evaluación",
        default=timezone.now,
        db_index=True
    )

    job_applications = models.ManyToManyField(
        "JobApplications",
        verbose_name="Postulaciones del día",
        related_name="accuracy_metrics",
        blank=True,
    )

    total_cvs = models.PositiveIntegerField(
        verbose_name="N° CVs evaluados", default=0
    )
    total_cvs_selected = models.PositiveIntegerField(
        verbose_name="N° CVs seleccionados (IA o reclutador)", default=0
    )
    total_cvs_passed_ef = models.PositiveIntegerField(
        verbose_name="N° CVs que pasan a entrevista final (EF)", default=0
    )

    selection_accuracy = models.DecimalField(
        verbose_name="Exactitud de selección (%)",
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Exactitud de Selección"
        verbose_name_plural = "Exactitudes de Selección"
        ordering = ["-interview_date"]

    def __str__(self):
        return f"{self.interview_date} - Exactitud: {self.selection_accuracy or 0}%"

    def calculate_metrics(self):

        apps = self.job_applications.all()

        self.total_cvs = apps.count()

        self.total_cvs_selected = apps.filter(
            analysis__status="Aprobado"
        ).distinct().count()

        self.total_cvs_passed_ef = apps.filter(
            status_interview__in=["Pasa entrevista", "Contratado"]
        ).distinct().count()

        avg_score = (
            apps.filter(analysis__overall_score__isnull=False)
            .aggregate(avg=Avg("analysis__overall_score"))
            .get("avg")
        )
        self.average_score = avg_score or 0

        if self.total_cvs_selected > 0:
            self.selection_accuracy = round(
                (self.total_cvs_passed_ef / self.total_cvs_selected) * 100, 3
            )
        else:
            self.selection_accuracy = 0

        self.save()
        return self.selection_accuracy