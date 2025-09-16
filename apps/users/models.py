from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def _create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El campo Email es obligatorio')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(username, email, password, **extra_fields)
    

class User(AbstractUser):
    
    username = models.CharField('Username', max_length=10, unique=True)
    email = models.EmailField('Email', max_length=50, blank=True, null=True, unique = True) #unique = True
    dni = models.CharField('DNI', max_length=8, blank=True, null=True, unique=True)

    is_active = models.BooleanField('¿Usuario Activo?', default=True)
    
    last_login = models.DateTimeField("Último inicio", default=timezone.now, null=True)
    created_at = models.DateTimeField("Fecha de registro", auto_now_add=True, null=True)
    updated_at = models.DateTimeField("Última de modificación", auto_now=True, null=True)
    creator_user = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='Usuario creador', null=True, blank=True)

    objects = UserManager()

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.username}'