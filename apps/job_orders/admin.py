from django.contrib import admin
from .models import JobOrder, JobOrderComment, JobOrderLayout

@admin.register(JobOrder)
class JobOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'created_by', 'approved_by', 'created_at', 'approved_at')
    list_filter = ('status', 'created_by', 'approved_by', 'created_at', 'approved_at')
    search_fields = ('title', 'organization', 'created_by__username', 'approved_by__username')
    actions = ['mark_as_approved', 'mark_as_rejected']

    def mark_as_approved(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} job orders marked as approved.")
    mark_as_approved.short_description = "Mark selected job orders as approved"

    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} job orders marked as rejected.")
    mark_as_rejected.short_description = "Mark selected job orders as rejected"

@admin.register(JobOrderComment)
class JobOrderCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'job_order', 'user', 'created_at')
    search_fields = ('job_order__title', 'user__username', 'comment')
    list_filter = ('created_at',)

@admin.register(JobOrderLayout)
class JobOrderLayoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'organization', 'created_at')
    search_fields = ('name', 'user__username', 'organization')
    list_filter = ('created_at',)
