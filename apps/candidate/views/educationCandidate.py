from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.candidate.models import Candidate, Education, Experience
from apps.candidate.serializers import EducationSerializer, ExperienceSerializer

class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Education.objects.all()
        if hasattr(user, "candidate"):
            return Education.objects.filter(candidate=user.candidate)
        return Education.objects.none()

    @action(detail=False, methods=["post"], url_path="add-education")
    def add_education(self, request):
        user = request.user
        candidate = Candidate.objects.filter(user=user).first()
        if not candidate:
            return Response(
                {"error": "El usuario no tiene un candidato asociado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(candidate=candidate)  # 👈 forzamos el candidato aquí
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
