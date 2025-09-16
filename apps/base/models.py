from django.db import models
import uuid

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField('Registrado el', auto_now_add=True)
    updated_at = models.DateTimeField('Ultima actualización', auto_now=True)
    creator_user = models.ForeignKey('users.User', verbose_name='Usuario creador', on_delete=models.CASCADE, null=True, blank=True)
    state = models.BooleanField('Activo?', default=True)

    class Meta:
        abstract = True
        verbose_name = 'Modelo Base'
        verbose_name_plural = 'Modelos Base'
        ordering = ['-created_at']

