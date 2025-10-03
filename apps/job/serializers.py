from apps.job.models import ApplicationsAiAnalysis, JobOffers, JobRequirements, JobSkill, JobBenefits, JobApplications
from rest_framework import serializers
from apps.candidate.models import Candidate

class JobBenefitsSerializer(serializers.ModelSerializer):
      class Meta:
        model = JobBenefits
        fields = ["id","description" ]

class JobSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.name", read_only=True)

    class Meta:
        model = JobSkill
        fields = ["id","skill_name"]

class JobRequerimentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRequirements
        fields = ["id","description" ]

class JobOffersSerializer(serializers.ModelSerializer):
    skills = JobSkillSerializer(source="skills_joboffert", many=True, read_only=True)
    requeriments = JobRequerimentsSerializer(source="requirements_joboffert", many=True, read_only=True)
    benefits = JobBenefitsSerializer(source="benefits_joboffert", many=True, read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)


    class Meta:
        model = JobOffers
        fields = [
            "id",
            "title",
            "description",
            "company_name",
            "location",
            "start_date",
            "end_date",
            "employment_type",
            "salary_min",
            "salary_max",
            "mode",
            "is_urgent",
            "skills",
            "benefits",
            "requeriments",
        ]


class JobApplicationsSerializer(serializers.ModelSerializer):
    joboffers_id = serializers.UUIDField(write_only=True)  # Se envía en POST
    joboffers = serializers.SerializerMethodField(read_only=True)  # Mostrar info de la oferta

    class Meta:
        model = JobApplications
        fields = ["candidate", "status", "joboffers", "joboffers_id"]
        read_only_fields = ["candidate", "joboffers"]

    def get_joboffers(self, obj):
        from .serializers import JobOffersSerializer
        return JobOffersSerializer(obj.joboffers).data

    def create(self, validated_data):
        joboffers_id = validated_data.pop("joboffers_id")
        joboffers = JobOffers.objects.get(id=joboffers_id)
        candidate = Candidate.objects.get(user=self.context["request"].user)

        if JobApplications.objects.filter(candidate=candidate, joboffers=joboffers).exists():
            raise serializers.ValidationError("Ya tienes una postulación para esta oferta.")

        return JobApplications.objects.create(
            candidate=candidate,
            joboffers=joboffers,
            **validated_data
        )
        
class JobOffersNestedSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = JobOffers
        fields = [
            "id",
            "title",
            "description",
            "location",
            "employment_type",
            "mode",
            "salary_min",
            "salary_max",
            "company_name",
        ]

class AplicationsAiAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationsAiAnalysis
        fields = ["match_score", "status", "observation"]

class JobApplicationsFullSerializer(serializers.ModelSerializer):
    joboffers = JobOffersNestedSerializer(read_only=True)
    analysis = AplicationsAiAnalysisSerializer(many=True, read_only=True)

    class Meta:
        model = JobApplications
        fields = [
            "id",
            "status",
            "created_at",
            "joboffers",
            "analysis",
        ]