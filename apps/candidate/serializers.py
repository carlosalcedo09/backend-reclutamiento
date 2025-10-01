from apps.candidate.models import (
    Candidate,
    CandidateSkill,
    Certificates,
    Education,
    Experience,
)
from rest_framework import serializers


class CandidateSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.name", read_only=True)
    proficiency_label = serializers.SerializerMethodField()

    class Meta:
        model = CandidateSkill
        fields = ["id", "skill", "skill_name", "proficiency_level", "proficiency_label"]

    def get_proficiency_label(self, obj):
        return obj.get_proficiency_level_display()


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = [
            "id",
            "company_name",
            "position",
            "start_date",
            "end_date",
            "description",
        ]


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            "id",
            "institution",
            "degree",
            "field_of_study",
            "start_date",
            "end_date",
            "is_study",
            "description",
        ]


class CertificatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificates
        fields = [
            "id",
            "name",
            "code",
            "institution",
            "date_obtained",
            "expiration_date",
            "certificate_file",
        ]


class CandidateSerializer(serializers.ModelSerializer):
    skills = CandidateSkillSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    educations = EducationSerializer(many=True, read_only=True)
    certificates = CertificatesSerializer(many=True, read_only=True)

    class Meta:
        model = Candidate
        fields = [
            "id",
            "name",
            "document_type",
            "document_number",
            "photograph",
            "country",
            "gender",
            "birth_date",
            "education_level",
            "location",
            "short_bio",
            "cv_file",
            "linkedin_url",
            "portfolio_url",
            "experience_years",
            "has_recommendation",
            "availability",
            "skills",
            "experiences",
            "educations",
            "certificates",
        ]


