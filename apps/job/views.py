from rest_framework import viewsets
from apps.job.models import JobOffers, JobApplications
from apps.candidate.models import Candidate
from apps.job.serializers import JobApplicationsFullSerializer, JobOffersSerializer, JobApplicationsSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, serializers

from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, BasePermission

class ReadOnlyOrIsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:  
            return True
        return request.user and request.user.is_authenticated

class JobOffersViewSet(viewsets.ModelViewSet):
    serializer_class = JobOffersSerializer
    permission_classes = [ReadOnlyOrIsAuthenticated]

    def get_queryset(self):
        return JobOffers.objects.filter(is_active=True)

class JobApplicationsViewSet(viewsets.ModelViewSet):
    queryset = JobApplications.objects.all()
    serializer_class = JobApplicationsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            candidate = Candidate.objects.get(user=self.request.user)
        except Candidate.DoesNotExist:
            return JobApplications.objects.none()  
        return JobApplications.objects.filter(candidate=candidate)
    
    @action(detail=False, methods=["get"], url_path="my-applications")
    def my_applications(self, request):
        """
        📌 Devuelve las postulaciones del candidato logueado con:
        - Información detallada de la oferta
        - Estado de postulación
        - Análisis de IA (si existe)
        """
        candidate = Candidate.objects.filter(user=request.user).first()
        if not candidate:
            return Response({"detail": "No se encontró candidato asociado."}, status=status.HTTP_404_NOT_FOUND)

        apps = JobApplications.objects.filter(candidate=candidate).prefetch_related("analysis", "joboffers__company")
        serializer = JobApplicationsFullSerializer(apps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)