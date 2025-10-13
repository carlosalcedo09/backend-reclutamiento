from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from apps.base.admin import BaseAdmin
from apps.candidate.models import (
    Candidate,
    Certificates,
    Experience,
    Education,
    CandidateSkill,
)
from unfold.admin import TabularInline


class SkillInline(TabularInline):
    model = CandidateSkill
    extra = 0
    exclude = ["created_at", "state", "creator_user"]
    readonly_fields = ()
    show_change_link = True


class ExperienceInline(TabularInline):
    model = Experience
    extra = 0
    exclude = ["created_at", "state", "creator_user"]
    readonly_fields = ()
    show_change_link = True


class EducationInline(TabularInline):
    model = Education
    extra = 0
    exclude = ["created_at", "state", "creator_user"]
    readonly_fields = ()
    show_change_link = True


class CertificatesInline(TabularInline):
    model = Certificates
    extra = 0
    exclude = ["created_at", "state", "creator_user"]
    readonly_fields = ()
    show_change_link = True


class CandidateAdmin(BaseAdmin):
    list_display = (
        "image",
        "document_number",
        "name",
        "gender",
        "birth_date",
        "education_level",
        "edit",
    )
    search_fields = (
        "document_number",
        "full_name",
    )
    exclude = [
        "state",
        "creator_user",
    ]
    list_display_links = ["edit", "image"]
    inlines = [SkillInline, ExperienceInline, EducationInline, CertificatesInline]
    fieldsets = [
        (
            "Información personal",
            {
                "fields": [
                    "document_type",
                    "document_number",
                    "photograph",
                    "name",
                    "gender",
                    "birth_date",
                    "country",
                    "experience_years",
                    "user",
                ],
            },
        ),
        (
            "Información laboral",
            {
                "fields": [
                    "education_level",
                    "has_recommendation",
                    "availability",
                    "short_bio",
                    "cv_file",
                    "linkedin_url",
                    "portfolio_url",
                ],
            },
        ),
    ]

    def save_related(self, request, form, formsets, change):
        """
        Este método se ejecuta DESPUÉS de guardar los inlines.
        Ideal para actualizar datos derivados del conjunto.
        """
        super().save_related(request, form, formsets, change)
        candidate = form.instance
        candidate.update_experience_years()
        
    def edit(self, obj):
        return format_html("<img src={icon_url}>", icon_url=settings.ICON_EDIT_URL)

    edit.short_description = "->"

    def image(self, obj):
        if obj.photograph:
            logo_url = obj.photograph.url
            return format_html('<img src="{}" width="80" height="80" />', logo_url)
        return "No image"

    image.short_description = "Fotografía"


admin.site.register(Candidate, CandidateAdmin)
