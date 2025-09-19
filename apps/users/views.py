from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

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
    @action(detail=False, methods=["post"], url_path="register", permission_classes=[AllowAny])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Crear Candidate asociado al User
        candidate_data = {
            "user": user.id,
            "name": request.data.get("name"),
            "document_type": request.data.get("dni"),
            "document_number": request.data.get("document_number"),
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
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# 🔹 Vista separada para login con JWT
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
