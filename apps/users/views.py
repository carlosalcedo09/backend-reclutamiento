from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.candidate.models import Candidate
from apps.candidate.serializers import CandidateSerializer
from django.core.mail import send_mail
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from django.utils.crypto import get_random_string
from datetime import timedelta
from apps.users.models import PasswordResetToken
from django.conf import settings
from datetime import timedelta
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        print(self.action)
        if self.action in ["register", "login", "recovery_password", "reset_password_confirm"]:
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

    @action(detail=False,methods=["post"],url_path="recovery-password", permission_classes=[AllowAny],)
    def recovery_password(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "El correo electrónico es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {
                    "message": "Si el correo está registrado, se enviará un enlace para restablecer la contraseña."
                },
                status=status.HTTP_200_OK,
            )

        token = get_random_string(64)
        expires_at = timezone.now() + timedelta(hours=1)

        PasswordResetToken.objects.update_or_create(
            user=user,
            defaults={"token": token, "expires_at": expires_at},
        )

        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        subject = "Recupera tu contraseña"
        html_content = f"""
            <div style="font-family: Arial, sans-serif; color: #333;">
                <h2>Hola {user.username},</h2>
                <p>Recibiste este correo porque solicitaste restablecer tu contraseña.</p>
                <p>Puedes hacerlo usando el siguiente enlace:</p>
                <p>
                    <a href="{reset_link}" style="background-color:#003b99; color:white; padding:10px 20px; text-decoration:none; border-radius:4px;">
                        Restablecer contraseña
                    </a>
                </p>
                <p>Este enlace expirará en 1 hora.</p>
                <hr/>
                <p style="font-size:12px; color:#888;">
                    Si no solicitaste este cambio, puedes ignorar este mensaje.
                </p>
            </div>
        """
        try:
            message = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=email,
                subject=subject,
                html_content=html_content,
            )
            sg = SendGridAPIClient(settings.API_KEY_SMTP)
            sg.send(message)
        except Exception as e:
            print("❌ Error enviando email:", str(e))
            return Response(
                {"error": "Error al enviar el correo de recuperación."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "message": "Si el correo está registrado, se enviará un enlace para restablecer la contraseña."
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="confirm-password",)
    def reset_password_confirm(self, request):
        """
        Restablecer la contraseña usando el token recibido por correo.
        """
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not token or not new_password:
            return Response(
                {"error": "Token y nueva contraseña son requeridos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reset_token = PasswordResetToken.objects.filter(token=token).first()
        if not reset_token or not reset_token.is_valid():
            return Response(
                {"error": "Token inválido o expirado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = reset_token.user
        user.set_password(new_password)
        user.save()

        reset_token.delete()  # invalidar token

        return Response(
            {"message": "Contraseña restablecida correctamente."},
            status=status.HTTP_200_OK,
        )


# 🔹 Vista separada para login con JWT
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
