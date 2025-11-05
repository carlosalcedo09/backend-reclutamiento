from django.contrib import admin
from unfold.admin import ModelAdmin 

class UnfoldSubAdmin( ModelAdmin):
    pass

class UnfoldRootSubAdmin( ModelAdmin):
    pass

class BaseAdmin(ModelAdmin):
    list_per_page = 20
    exclude = ('state', )


    def save_model(self, request, obj, form, change):
        if hasattr(obj, "creator_user"):
            if not change or not obj.creator_user:
                obj.creator_user = request.user
        super().save_model(request, obj, form, change)
    
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for formset in formsets:
            instances = formset.save(commit=False)
            for instance in instances:
                if hasattr(instance, "creator_user"):
                    if not instance.creator_user:
                        instance.creator_user = request.user
                instance.save()
        

    class Media:
        js = ('admin/js/hide_view.js',)

