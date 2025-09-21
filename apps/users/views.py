from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.candidate.models import Candidate
from apps.candidate.serializers import CandidateSerializer

from .serializers import (
    RegisterSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ["register", "login"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    # 🔹 Acción personalizada para registrar
    @action(
        detail=False,
        methods=["post"],
        url_path="register",
        permission_classes=[AllowAny],
    )
    def register(self, request):
        document_number = request.data.get("document_number")
        if User.objects.filter(dni=document_number).exists():
            return Response(
                {"message": "Este DNI ya fue registrado"}, status=status.HTTP_200_OK
            )
        data = request.data.copy()
        data["dni"] = document_number
        serializer = RegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Crear Candidate asociado al User
        candidate_data = {
            "user": user.id,
            "name": request.data.get("name"),
            "document_type": request.data.get("document_type"),
            "document_number": document_number,
            "country": request.data.get("country"),
            "gender": request.data.get("gender"),
            "birth_date": request.data.get("birth_date"),
            "education_level": request.data.get("education_level"),
            "location": request.data.get("location"),
            "short_bio": request.data.get("short_bio"),
            "experience_years": request.data.get("experience_years"),
            "avaliability": request.data.get("avaliability"),
            "linkedin_url": request.data.get("linkedin_url"),
            "portfolio_url": request.data.get("portfolio_url"),
        }

        candidate_serializer = CandidateSerializer(data=candidate_data)
        candidate_serializer.is_valid(raise_exception=True)
        candidate = candidate_serializer.save()

        return Response(
            {
                "user": UserSerializer(user).data,
                "candidate": CandidateSerializer(candidate).data,
            },
            status=status.HTTP_201_CREATED,
        )

    # 🔹 Acción personalizada para ver perfil
    @action(detail=False, methods=["get"], url_path="profile")
    def profile(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="change-password",
        permission_classes=[IsAuthenticated],
    )
    def change_password(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not current_password or not new_password or not confirm_password:
            return Response(
                {"error": "Debes completar todos los campos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar contraseña actual
        if not user.check_password(current_password):
            return Response(
                {"error": "La contraseña actual es incorrecta"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar coincidencia nueva contraseña
        if new_password != confirm_password:
            return Response(
                {"error": "La nueva contraseña y la confirmación no coinciden"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Cambiar la contraseña
        user.set_password(new_password)
        user.last_password_change = timezone.now()  # 🔹 Actualizamos la fecha

        user.save()

        return Response(
            {"message": "Contraseña actualizada correctamente"},
            status=status.HTTP_200_OK,
        )


# 🔹 Vista separada para login con JWT
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
