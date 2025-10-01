from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.candidate.models import Candidate, Certificates
from apps.candidate.serializers import CertificatesSerializer
import rest_framework.status as status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied


class CertificatesViewSet(viewsets.ModelViewSet):
    queryset = Certificates.objects.all()
    serializer_class = CertificatesSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Certificates.objects.all()
        if hasattr(user, "candidate"):
            return Certificates.objects.filter(candidate=user.candidate)
        return Certificates.objects.none()
    
    @action(detail=False, methods=["post"], url_path="add-certificate")
    def add_certificate(self, request):
        user = request.user
        candidate = Candidate.objects.filter(user=user).first()
        if not candidate:
            return Response(
                {"error": "El usuario no tiene un candidato asociado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(candidate=candidate)  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["post"], url_path="update-certificate")
    def update_certificate(self, request):
        user = self.request.user
        cert_id = request.data.get("id")
        if not cert_id:
            return Response(
                {"error": "Se requiere el id del certificado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cert = Certificates.objects.get(id=cert_id)
        except Certificates.DoesNotExist:
            return Response(
                {"error": "Certificado no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ✅ obtener el candidate correcto desde el related_name
        candidate = Candidate.objects.filter(user=user).first()

        # Validación de permisos
        if not user.is_superuser and cert.candidate != candidate:
            raise PermissionDenied("No tienes permiso para editar este certificado")

        serializer = self.get_serializer(cert, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
