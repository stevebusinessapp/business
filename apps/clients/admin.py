from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "email", "phone", "contact_person", "created_by", "created_at")
    search_fields = ("name", "email", "phone", "company__name")
    list_filter = ("company",)
    readonly_fields = ("created_at", "updated_at")
