from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.core.exceptions import ValidationError
import re
from django.conf import settings
from apps.users.models import (
    User
)

from django.shortcuts import render

from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django import forms

from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _


class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'
        widgets = {
            'permissions': FilteredSelectMultiple(verbose_name=_('Permissions'), is_stacked=False),
        }

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)

        permisos = self.fields['permissions'].queryset

        permisos_traducidos = []
        for permiso in permisos:
            model_class = permiso.content_type.model_class()

            if model_class:
                verbose_name = model_class._meta.verbose_name
            else:
                verbose_name = permiso.content_type.model

            if permiso.codename.startswith('add_'):
                name = _('%(verbose_name)s | Puede agregar %(verbose_name)s') % {'verbose_name': verbose_name}
            elif permiso.codename.startswith('change_'):
                name = _('%(verbose_name)s | Puede cambiar %(verbose_name)s') % {'verbose_name': verbose_name}
            elif permiso.codename.startswith('delete_'):
                name = _('%(verbose_name)s | Puede eliminar %(verbose_name)s') % {'verbose_name': verbose_name}
            elif permiso.codename.startswith('view_'):
                name = _('%(verbose_name)s | Puede ver %(verbose_name)s') % {'verbose_name': verbose_name}
            else:
                name = permiso.name

            permisos_traducidos.append((permiso.id, name))

        self.fields['permissions'].choices = permisos_traducidos



class CustomGroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    search_fields = ('name',)

class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        widgets = {
            'user_permissions': FilteredSelectMultiple(verbose_name=_('Permissions'), is_stacked=False),
            'password': forms.TextInput(attrs={'type': 'text'})  # Esto hace que la contraseña sea visible
        }

    def __init__(self, *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get("password")
        errors = []

        if password:
            if len(password) < 8:
                errors.append("La contraseña debe tener al menos 8 caracteres.")
            if not re.search(r'[A-Z]', password):
                errors.append("La contraseña debe contener al menos una letra mayúscula.")
            if not re.search(r'[a-z]', password):
                errors.append("La contraseña debe contener al menos una letra minúscula.")
            if not re.search(r'[0-9]', password):
                errors.append("La contraseña debe contener al menos un número.")
            if not re.search(r'[@$!%*?&]', password):
                errors.append("La contraseña debe contener al menos un carácter especial (@, $, !, %, *, ?, &).")
        
        if errors:
            raise ValidationError(errors)

        return password

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'dni', 'user_permissions']

class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm  
    list_display = ('username', 'first_name', 'last_name', 'dni', 'edit')
    list_display_links = ('edit',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    search_fields = ('username', 'first_name', 'last_name', 'dni')
    exclude = ('state', 'creator_user')
    filter_horizontal = ('groups', 'user_permissions')
    fieldsets = [
        ('Información personal', {
            'fields': ['first_name', 'last_name', 'email', 'dni']
        }),
        ('Información de inicio de sesión', {
            'fields': ['username', 'password'],
            'classes': ['collapse'],
        }),
        ('Registro', {
            'fields': ['created_at', 'last_login', 'updated_at'],
            'classes': ['collapse'],
        }),
        ('Permisos', {
            'fields': ['is_active', 'is_superuser', 'groups', 'user_permissions'],
            'classes': ['collapse'],
        }),
    ]

    def save_model(self, request, obj, form, change):
        if not change or not obj.creator_user:
            obj.creator_user = request.user
            obj.is_staff = True
        if form.cleaned_data.get('password'):
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

    def edit(self, obj):
        return format_html("<img src={icon_url}>", icon_url=settings.ICON_EDIT_URL)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj and obj.pk:  
            readonly_fields.append('password')
        return readonly_fields

    edit.short_description = '->'

    class Media:
        js = ['admin/js/hide_view.js']
        
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)