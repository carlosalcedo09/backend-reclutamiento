from rest_framework import viewsets, permissions
from rest_framework.authentication import TokenAuthentication

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.candidate.models import Candidate, CandidateSkill
from apps.candidate.serializers import CandidateSkillSerializer
from apps.users.models import User


class CandidateSkillViewSet(viewsets.ModelViewSet):
    queryset = CandidateSkill.objects.all()
    serializer_class = CandidateSkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return CandidateSkill.objects.all()
        if hasattr(user, "candidate"):
            return CandidateSkill.objects.filter(candidate=user.candidate)
        return CandidateSkill.objects.none()

    @action(detail=False, methods=["post"], url_path="add-skill")
    def add_skill(self, request):
        user = request.user
        candidate = Candidate.objects.filter(user=user).first() 
        if not candidate:
            return Response(
                {"error": "El usuario no tiene un candidato asociado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(candidate=candidate)  # 👈 fuerza aquí
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
