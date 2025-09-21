# candidates/views.py
from rest_framework import viewsets, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.candidate.models import Candidate
from apps.candidate.serializers import CandidateSerializer


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]

    # Opcional: filtrar solo el candidato del usuario logueado
    def get_queryset(self):
        user = self.request.user
        return Candidate.objects.filter(user=user)

    @action(detail=False, methods=["patch"], url_path="update-profile")
    def update_profile(self, request):
        # Retorna el candidato del usuario logueado y permite patch
        candidate = self.get_queryset().first()
        serializer = CandidateSerializer(candidate, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
