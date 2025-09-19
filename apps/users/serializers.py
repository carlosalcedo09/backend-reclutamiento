from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "dni", "is_active", "created_at"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "dni", "password"]
        extra_kwargs = {
            "email": {"required": True, "allow_blank": False}
        }

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("El campo Email es obligatorio")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            dni=validated_data.get("document_number", ""),
        )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)  # tokens (refresh + access)

        # Datos adicionales del usuario
        data.update({
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "dni": self.user.dni,
        })

        return data
