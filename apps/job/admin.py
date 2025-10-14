from datetime import date
import uuid
from django.urls import reverse
from django.contrib import admin, messages
from django.utils.html import format_html
from django.conf import settings
from unfold.decorators import display
from apps.base.admin import BaseAdmin
from unfold.admin import TabularInline
from apps.job.models import (
    AccuracyMetrics,
    EvaluationSummary,
    JobPositions,
    JobOffers,
    JobRequirements,
    JobSkill,
    JobApplications,
    ApplicationsAiAnalysis,
    JobBenefits,
    TimeMetrics,
)
from apps.job.choices import StatusChoices
from django.template.response import TemplateResponse
from django.utils import timezone
import json
import requests
from django.db.models import Prefetch
from django.db.models.functions import TruncDate

from apps.job.utils.utils import (
    base64_pdf,
    calculate_experience_years,
    decide_status,
    parse_time_str,
)
from collections import Counter


class JobBenefitsInline(TabularInline):
    model = JobBenefits
    extra = 0
    exclude = ["created_at", "state", "creator_user"]
    readonly_fields = ()
    show_change_link = True


class JobSkillInline(TabularInline):
    model = JobSkill
    extra = 0
    exclude = ["created_at", "state", "creator_user"]
    readonly_fields = ()
    show_change_link = True


class JobRequirementsInline(TabularInline):
    model = JobRequirements
    extra = 0
    exclude = ["created_at", "state", "creator_user"]
    readonly_fields = ()
    show_change_link = True


class JobOffersAdmin(BaseAdmin):
    list_display = (
        "title",
        "job_position",
        "company",
        "employment_type",
        "is_active",
        "evaluate_link",
        "edit",
    )
    search_fields = ("title",)
    exclude = ["state", "creator_user"]
    list_display_links = ["edit", "title"]
    inlines = [JobSkillInline, JobRequirementsInline, JobBenefitsInline]

    def edit(self, obj):
        return format_html("<img src='{}'>", settings.ICON_EDIT_URL)

    edit.short_description = "->"

    def evaluate_link(self, obj):
        list_url = reverse("admin:job_jobapplications_changelist")
        return format_html(
            '<a style="border-radius: 6px; padding:0.5rem; background: #7acdf059; color: #01c9ea; font-size: 12px" href="{}?joboffers__id__exact={}"> VISUALIZAR</a>',
            list_url,
            obj.pk,
        )

    evaluate_link.short_description = "Postulaciones"


class JobPositionsAdmin(BaseAdmin):
    list_display = (
        "name",
        "description",
        "edit",
    )
    search_fields = ("name",)
    exclude = ["state", "creator_user", "candidate_snapshot"]
    list_display_links = ["edit", "name"]

    def edit(self, obj):
        return format_html("<img src={icon_url}>", icon_url=settings.ICON_EDIT_URL)

    edit.short_description = "->"


class AplicationsAiAnalysisInline(TabularInline):
    model = ApplicationsAiAnalysis
    extra = 0
    exclude = [
        "created_at",
        "state",
        "creator_user",
        "job_match_score",
        "structural_breakdown",
        "fairness_groups",
        "semantic_score",
        "structural_score",
        "fairness_overall_delta",
    ]
    readonly_fields = ()
    show_change_link = True


class EvaluationSummaryAdmin(BaseAdmin):
    model = EvaluationSummary
    list_filter = ("criterio",)
    list_display = (
        "fecha",
        "criterio",
        "grupo_protegido",
        "total_cvs_gp",
        "cvs_preseleccionados_gp",
        "tasa_seleccion_gp",
        "grupo_referente",
        "total_cvs_gr",
        "cvs_preseleccionados_gr",
        "tasa_seleccion_gr",
        "spd",
    )


class AccuracyMetricsAdmin(BaseAdmin):
    model = AccuracyMetrics


class JobApplicationsAdmin(BaseAdmin):
    list_display = (
        "created_at",
        "get_candidate_name",
        "joboffers",
        "show_status_customized_color",
        "status_interview",
        "edit",
    )
    search_fields = (
        "joboffers__title",
        "candidate__name",
    )
    list_filter = ("joboffers", "status")
    exclude = ["state", "creator_user"]
    list_display_links = ["edit", "created_at", "get_candidate_name"]
    inlines = [AplicationsAiAnalysisInline]

    change_list_template = "admin/job/jobapplications_changelist.html"
    actions = ["evaluate_all"]

    def edit(self, obj):
        return format_html("<img src='{}'>", settings.ICON_EDIT_URL)

    edit.short_description = "->"

    @display(
        description="Estado de la evaluación",
        ordering="status",
        label={
            "ENV": "warning",
            "EVAL": "success",
            "PRO": "dark",
        },
    )
    def show_status_customized_color(self, obj):
        return obj.status

    def get_candidate_name(self, obj):
        return obj.candidate.name

    get_candidate_name.short_description = "Candidato"

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "evaluate-offer/<str:offer_id>/",
                self.admin_site.admin_view(self.evaluate_offer),
                name="jobapplications_evaluate_offer",
            ),
        ]
        return custom_urls + urls

    # EVALUACION
    def evaluate_offer(self, request, offer_id):
        offer = JobOffers.objects.get(pk=offer_id)
        applications = (
            JobApplications.objects.filter(joboffers=offer)
            .select_related("candidate")
            .prefetch_related("analysis")
        )

        payload = {
            "job_title": offer.title,
            "job_description": offer.description,
            "job_position": offer.job_position.name if offer.job_position else None,
            "job_position_description": (
                offer.job_position.description if offer.job_position else None
            ),
            "company": offer.company.name if offer.company else None,
            "location": offer.location,
            "start_date": str(offer.start_date) if offer.start_date else None,
            "end_date": str(offer.end_date) if offer.end_date else None,
            "is_active": offer.is_active,
            "employment_type": offer.employment_type,
            "salary_min": float(offer.salary_min) if offer.salary_min else None,
            "salary_max": float(offer.salary_max) if offer.salary_max else None,
            "mode": offer.mode,
            "is_urgent": offer.is_urgent,
            "candidates": [],
        }

        errors = []

        for app in applications:
            try:
                candidate = app.candidate
                if not candidate:
                    raise ValueError("Candidato no asociado a la postulación")

                created_at_str = app.created_at.isoformat() if app.created_at else None
                # === SKILLS ===
                ofimatic_map = {1: "Básico", 2: "Intermedio", 3: "Avanzado"}
                skills_detail = [
                    {
                        "name": cs.skill.name,
                        "category": cs.skill.category,
                        "level": ofimatic_map.get(cs.proficiency_level, None),
                    }
                    for cs in candidate.skills.all()
                    if cs.skill.category in ["Técnica", "Blanda"]
                ]

                languages_detail = [
                    {
                        "name": cs.skill.name,
                        "level": ofimatic_map.get(cs.proficiency_level, None),
                    }
                    for cs in candidate.skills.all()
                    if cs.skill.category == "Idioma"
                ]

                ofimatic_detail = [
                    {
                        "name": cs.skill.name,
                        "level": ofimatic_map.get(cs.proficiency_level, None),
                    }
                    for cs in candidate.skills.all()
                    if cs.skill.category == "Ofimática"
                ]

                # === EXPERIENCIAS ===
                experiences = [
                    exp.description or f"{exp.position} en {exp.company_name}"
                    for exp in candidate.experiences.all()
                ]
                # university_name = (
                #     candidate.educations.first().institution
                #     if candidate.educations.exists()
                #     else None
                # )

                # # 👇 Depuración
                # print(f"   Universidad enviada → {university_name}\n")
                # === ARMADO DE CANDIDATO ===
                payload["candidates"].append(
                    {
                        "id": str(candidate.id),
                        "name": candidate.name,
                        "short_bio": candidate.short_bio,
                        "experience": experiences,
                        "education_level": candidate.education_level,
                        "skills": skills_detail,
                        "experience_years": calculate_experience_years(candidate),
                        "certifications_count": candidate.certificates.count(),
                        "languages": languages_detail,
                        "ofimatic": ofimatic_detail,
                        "cv_pdf_base64": base64_pdf(candidate.cv_file),
                        "university_name": (
                            candidate.educations.first().institution
                            if candidate.educations.exists()
                            else None
                        ),
                        "age": (
                            (timezone.now().year - candidate.birth_date.year)
                            if candidate.birth_date
                            else None
                        ),
                        "availability": candidate.availability,
                        "created_at": created_at_str,
                    }
                )

            except Exception as e:
                print(
                    f"⚠️ Error con candidato {getattr(app.candidate, 'name', 'Desconocido')}: {e}"
                )
                errors.append(
                    {
                        "application_id": str(app.id),
                        "candidate_name": getattr(app.candidate, "name", "Sin nombre"),
                        "error": str(e),
                    }
                )
                continue

        # === ENVÍO A FASTAPI ===
        try:
            response = requests.post(
                "http://127.0.0.1:8001/api/evaluate",
                json=payload,
                timeout=180,
            )
            response.raise_for_status()
            result = response.json()

            selection_summary = result.get("selection_summary", [])

            # === GUARDAR RESULTADOS ===
            for c in result.get("candidates", []):
                app = applications.get(candidate__id=c["id"])
                score = c.get("fairness_overall_score", 0)
                status = decide_status(score)

                ApplicationsAiAnalysis.objects.create(
                    jobApplications=app,
                    job_match_score=c.get("job_match_score"),
                    semantic_score=c.get("semantic_score"),
                    structural_score=c.get("structural_score"),
                    overall_score=score,
                    fairness_structural_score=c.get("fairness_structural_score"),
                    fairness_overall_score=c.get("fairness_overall_score"),
                    fairness_overall_delta=c.get("fairness_overall_delta"),
                    structural_breakdown=c.get("structural_breakdown"),
                    fairness_groups=c.get("fairness_groups"),
                    status=status,
                    observation=c.get("decision_label"),
                    processing_start_time=parse_time_str(
                        c.get("processing_start_time")
                    ),
                    processing_end_time=parse_time_str(c.get("processing_end_time")),
                    processing_time_minutes=round(
                        float(c.get("processing_time_seconds", 0)), 2
                    ),
                )
                app.status = status
                app.save(update_fields=["status"])

            # === GUARDAR SELECTION SUMMARY ===
            if selection_summary:
                EvaluationSummary.objects.filter(job_offer=offer).delete()
                for summary in selection_summary:
                    EvaluationSummary.objects.create(
                        job_offer=offer,
                        fecha=summary.get("fecha"),
                        criterio=summary.get("criterio"),
                        grupo_protegido=summary.get("grupo_protegido"),
                        total_cvs_gp=summary.get("total_cvs_gp", 0),
                        cvs_preseleccionados_gp=summary.get(
                            "cvs_preseleccionados_gp", 0
                        ),
                        tasa_seleccion_gp=summary.get("tasa_seleccion_gp", 0),
                        grupo_referente=summary.get("grupo_referente"),
                        total_cvs_gr=summary.get("total_cvs_gr", 0),
                        cvs_preseleccionados_gr=summary.get(
                            "cvs_preseleccionados_gr", 0
                        ),
                        tasa_seleccion_gr=summary.get("tasa_seleccion_gr", 0),
                        spd=summary.get("spd") or 0,
                    )

            # === GUARDAR MÉTRICAS DE EXACTITUD ===
            dates = (
                JobApplications.objects.filter(joboffers=offer)
                .annotate(post_date=TruncDate("created_at"))
                .values_list("post_date", flat=True)
                .distinct()
            )

            for d in dates:
                apps_by_date = JobApplications.objects.filter(
                    joboffers=offer, created_at__date=d
                )
                if not apps_by_date.exists():
                    continue

                metric, _ = AccuracyMetrics.objects.get_or_create(interview_date=d)
                metric.job_applications.set(apps_by_date)
                metric.calculate_metrics()

                print(
                    f"📊 Exactitud para {d}: {metric.selection_accuracy}% "
                    f"({apps_by_date.count()} CVs)"
                )
            applications = (
                JobApplications.objects.filter(joboffers=offer)
                .select_related("candidate")
                .prefetch_related(
                    Prefetch(
                        "analysis",
                        queryset=ApplicationsAiAnalysis.objects.order_by("-created_at"),
                    )
                )
            )

            self.message_user(
                request,
                f"{applications.count()} postulaciones evaluadas con éxito.",
                messages.SUCCESS,
            )

        except requests.RequestException as e:
            print(f"❌ Error en la petición a IA: {e}")
            result = {}

        context = {
            "offer": offer,
            "applications": [
                {
                    "application": app,
                    "analysis": app.analysis.first() if app.analysis.exists() else None,
                }
                for app in applications
            ],
        }

        return TemplateResponse(
            request, "admin/job/jobapplications_evaluate_result.html", context
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["has_evaluate_button"] = False
        extra_context["current_offer_id"] = request.GET.get(
            "joboffers__id__exact", None
        )
        return super().changelist_view(request, extra_context)


admin.site.register(JobPositions, JobPositionsAdmin)
admin.site.register(JobOffers, JobOffersAdmin)
admin.site.register(JobApplications, JobApplicationsAdmin)
admin.site.register(EvaluationSummary, EvaluationSummaryAdmin)
admin.site.register(AccuracyMetrics, AccuracyMetricsAdmin)
