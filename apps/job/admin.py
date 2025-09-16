from django.urls import reverse
from django.contrib import admin, messages
from django.utils.html import format_html
from django.conf import settings
from unfold.decorators import display
from apps.base.admin import BaseAdmin
from unfold.admin import TabularInline
from apps.job.models import JobPositions, JobOffers, JobRequirements, JobSkill, JobApplications, AplicationsAiAnalysis
from apps.job.choices import  StatusChoices
from django.template.response import TemplateResponse

class JobSkillInline(TabularInline):
    model = JobSkill
    extra = 0  
    exclude =['created_at','state','creator_user']
    readonly_fields = ()
    show_change_link = True 

class JobRequirementsInline(TabularInline):
    model = JobRequirements
    extra = 0  
    exclude =['created_at','state','creator_user']
    readonly_fields = ()
    show_change_link = True 

class JobOffersAdmin(BaseAdmin):
    list_display = ('title', 'job_position', 'company', 'employment_type', 'is_active', 'evaluate_link', 'edit',)
    search_fields = ('title',)
    exclude = ['state', 'creator_user']
    list_display_links = ['edit', 'title']
    inlines = [JobSkillInline, JobRequirementsInline]

    def edit(self, obj):
        return format_html("<img src='{}'>", settings.ICON_EDIT_URL)
    edit.short_description = '->'

    def evaluate_link(self, obj):
        list_url = reverse("admin:job_jobapplications_changelist")
        return format_html(
            '<a style="border-radius: 6px; padding:0.5rem; background: #7acdf059; color: #01c9ea; font-size: 12px" href="{}?joboffers__id__exact={}"> VISUALIZAR</a>',
            list_url,
            obj.pk,
        )
    evaluate_link.short_description = "Postulaciones"



class JobPositionsAdmin(BaseAdmin):
    list_display=('name','description','edit',)
    search_fields=('name',)
    exclude = [ 'state', 'creator_user',]
    list_display_links = ['edit','name']
    
    def edit(self, obj):
        return format_html("<img src={icon_url}>", icon_url=settings.ICON_EDIT_URL)
    
    edit.short_description = '->'



class AplicationsAiAnalysisInline(TabularInline):
    model = AplicationsAiAnalysis
    extra = 0  
    exclude =['created_at','state','creator_user']
    readonly_fields = ()
    show_change_link = True 

class JobApplicationsAdmin(BaseAdmin):
    list_display = ('get_candidate_name', 'joboffers', 'show_status_customized_color', 'edit',)
    search_fields = ('joboffers__title', 'candidate__name',)
    list_filter = ('joboffers', 'status')
    exclude = ['state', 'creator_user']
    list_display_links = ['edit', 'get_candidate_name']
    inlines = [AplicationsAiAnalysisInline]

    change_list_template = "admin/job/jobapplications_changelist.html"
    actions = ["evaluate_all"]

    def edit(self, obj):
        return format_html("<img src='{}'>", settings.ICON_EDIT_URL)
    edit.short_description = '->'

    @display(
        description="Estado",
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
    get_candidate_name.short_description = 'Candidato'

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

    def evaluate_offer(self, request, offer_id):
        offer = JobOffers.objects.get(pk=offer_id)
        applications = JobApplications.objects.filter(
            joboffers=offer
        ).select_related("candidate").prefetch_related("analysis")

        for application in applications:
            if not AplicationsAiAnalysis.objects.filter(jobApplications=application).exists():
                AplicationsAiAnalysis.objects.create(
                    jobApplications=application,
                    match_score=0.85,
                    status="apto",
                    observation="Evaluado automáticamente desde modal"
                )

        self.message_user(
            request,
            f"{applications.count()} postulaciones evaluadas con éxito.",
            messages.SUCCESS
        )

        context = {
            "offer": offer,
            "applications": applications,
        }

        return TemplateResponse(
            request,
            "admin/job/jobapplications_evaluate_result.html",
            context
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["has_evaluate_button"] = False
        extra_context["current_offer_id"] = request.GET.get("joboffers__id__exact", None)
        return super().changelist_view(request, extra_context)
    
admin.site.register(JobPositions, JobPositionsAdmin)
admin.site.register(JobOffers, JobOffersAdmin)
admin.site.register(JobApplications, JobApplicationsAdmin)