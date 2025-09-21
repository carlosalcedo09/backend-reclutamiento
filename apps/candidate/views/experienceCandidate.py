from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.candidate.models import Candidate, Experience
from apps.candidate.serializers import ExperienceSerializer

class ExperienceViewSet(viewsets.ModelViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Experience.objects.all()
        if hasattr(user, "candidate"):
            return Experience.objects.filter(candidate=user.candidate)
        return Experience.objects.none()

    @action(detail=False, methods=["post"], url_path="add-experience")
    def add_experience(self, request):
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
