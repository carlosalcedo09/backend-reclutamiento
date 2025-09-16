
from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from apps.base.admin import BaseAdmin
from apps.maintenance.models import Skill, Company

class SkillAdmin(BaseAdmin):
    list_display=('name','description','category','edit',)
    search_fields=('name',)
    list_filter= ['category']
    exclude = [ 'state', 'creator_user',]
    list_display_links = ['edit','name']
    
    def edit(self, obj):
        return format_html("<img src={icon_url}>", icon_url=settings.ICON_EDIT_URL)
    
    edit.short_description = '->'


class CompanyAdmin(BaseAdmin):
    list_display=('tax_id','name','legal_name','industry','edit',)
    search_fields=('tax_id','name','legal_name',)
    list_filter= ['industry']
    exclude = [ 'state', 'creator_user',]
    list_display_links = ['edit','tax_id']
    
    def edit(self, obj):
        return format_html("<img src={icon_url}>", icon_url=settings.ICON_EDIT_URL)
    
    edit.short_description = '->'


    

admin.site.register(Skill, SkillAdmin)
admin.site.register(Company, CompanyAdmin)