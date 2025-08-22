from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Quotation, QuotationItem, QuotationTemplate


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1
    fields = ['product_service', 'description', 'quantity', 'unit_price', 'line_total']
    readonly_fields = ['line_total']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('quotation')


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = [
        'quotation_number', 'client_name', 'quotation_date', 'valid_until', 
        'status_badge', 'grand_total_formatted', 'user_name', 'created_at'
    ]
    list_filter = [
        'status', 'quotation_date', 'valid_until', 'created_at', 
        'user__company_profile__company_name'
    ]
    search_fields = [
        'quotation_number', 'client__name', 'client__email', 
        'client__phone', 'notes', 'terms'
    ]
    readonly_fields = [
        'quotation_number', 'created_at', 'updated_at', 'subtotal', 
        'grand_total', 'user_name', 'client_details'
    ]
    date_hierarchy = 'quotation_date'
    ordering = ['-created_at']
    inlines = [QuotationItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('quotation_number', 'user_name', 'quotation_date', 'valid_until', 'status')
        }),
        ('Client Information', {
            'fields': ('client', 'client_details')
        }),
        ('Template', {
            'fields': ('template',),
            'classes': ('collapse',)
        }),
        ('Financial Information', {
            'fields': ('subtotal', 'total_tax', 'total_discount', 'shipping_fee', 'other_charges', 'grand_total')
        }),
        ('Additional Information', {
            'fields': ('terms', 'notes', 'custom_fields'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def client_name(self, obj):
        return obj.client.name if obj.client else 'No Client'
    client_name.short_description = 'Client'
    client_name.admin_order_field = 'client__name'
    
    def user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email
    user_name.short_description = 'Created By'
    user_name.admin_order_field = 'user__first_name'
    
    def status_badge(self, obj):
        colors = {
            'draft': '#e3f2fd',
            'sent': '#fff3e0',
            'accepted': '#e8f5e8',
            'declined': '#ffebee',
            'expired': '#f3e5f5'
        }
        color = colors.get(obj.status, '#f8f9fa')
        return format_html(
            '<span style="background-color: {}; color: #333; padding: 4px 8px; '
            'border-radius: 12px; font-size: 12px; font-weight: 600;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def grand_total_formatted(self, obj):
        return format_html('<strong>₦{:,.2f}</strong>', obj.grand_total)
    grand_total_formatted.short_description = 'Total Amount'
    grand_total_formatted.admin_order_field = 'grand_total'
    
    def client_details(self, obj):
        if obj.client:
            details = []
            if obj.client.email:
                details.append(f'Email: {obj.client.email}')
            if obj.client.phone:
                details.append(f'Phone: {obj.client.phone}')
            if obj.client.address:
                details.append(f'Address: {obj.client.address}')
            return mark_safe('<br>'.join(details))
        return 'No client details'
    client_details.short_description = 'Client Details'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'client', 'user', 'template', 'user__company_profile'
        ).prefetch_related('items')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only for new quotations
            obj.user = request.user
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.user == request.user
    
    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.user == request.user
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing quotation
            return self.readonly_fields + ('quotation_number', 'user')
        return self.readonly_fields


@admin.register(QuotationItem)
class QuotationItemAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'quotation_number', 'product_service', 'description', 
        'quantity', 'unit_price', 'line_total_formatted'
    ]
    list_filter = ['quotation__status', 'quotation__quotation_date']
    search_fields = [
        'product_service', 'description', 'quotation__quotation_number',
        'quotation__client__name'
    ]
    readonly_fields = ['line_total']
    ordering = ['-quotation__created_at']
    
    def quotation_number(self, obj):
        return obj.quotation.quotation_number
    quotation_number.short_description = 'Quotation Number'
    quotation_number.admin_order_field = 'quotation__quotation_number'
    
    def line_total_formatted(self, obj):
        return format_html('<strong>₦{:,.2f}</strong>', obj.line_total)
    line_total_formatted.short_description = 'Line Total'
    line_total_formatted.admin_order_field = 'line_total'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'quotation', 'quotation__client'
        )
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.quotation.user == request.user
    
    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.quotation.user == request.user


@admin.register(QuotationTemplate)
class QuotationTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user_name', 'is_default', 'document_title', 
        'number_prefix', 'created_at'
    ]
    list_filter = ['is_default', 'created_at', 'user__company_profile__company_name']
    search_fields = ['name', 'description', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'user_name', 'color_preview']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'user_name', 'is_default')
        }),
        ('Document Settings', {
            'fields': ('document_title', 'number_prefix')
        }),
        ('Color Scheme', {
            'fields': ('primary_color', 'secondary_color', 'text_color', 'accent_color', 'color_preview'),
            'classes': ('collapse',)
        }),
        ('Display Options', {
            'fields': ('show_company_logo', 'show_company_details', 'show_bank_details', 'show_signature'),
            'classes': ('collapse',)
        }),
        ('Content', {
            'fields': ('default_terms', 'footer_text'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email
    user_name.short_description = 'Created By'
    user_name.admin_order_field = 'user__first_name'
    
    def color_preview(self, obj):
        if obj.primary_color and obj.secondary_color:
            return format_html(
                '<div style="display: flex; gap: 10px; align-items: center;">'
                '<div style="width: 30px; height: 30px; background-color: {}; border-radius: 5px; border: 1px solid #ddd;"></div>'
                '<span>Primary</span>'
                '<div style="width: 30px; height: 30px; background-color: {}; border-radius: 5px; border: 1px solid #ddd;"></div>'
                '<span>Secondary</span>'
                '<div style="width: 30px; height: 30px; background-color: {}; border-radius: 5px; border: 1px solid #ddd;"></div>'
                '<span>Text</span>'
                '<div style="width: 30px; height: 30px; background-color: {}; border-radius: 5px; border: 1px solid #ddd;"></div>'
                '<span>Accent</span>'
                '</div>',
                obj.primary_color, obj.secondary_color, obj.text_color, obj.accent_color
            )
        return 'No colors set'
    color_preview.short_description = 'Color Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'user__company_profile'
        )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only for new templates
            obj.user = request.user
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.user == request.user
    
    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.user == request.user


# Customize admin site
admin.site.site_header = "Business App Administration"
admin.site.site_title = "Business App Admin"
admin.site.index_title = "Welcome to Business App Administration"

# Add custom admin actions
@admin.action(description="Mark selected quotations as sent")
def mark_as_sent(modeladmin, request, queryset):
    updated = queryset.update(status='sent')
    modeladmin.message_user(request, f'{updated} quotation(s) marked as sent.')

@admin.action(description="Mark selected quotations as accepted")
def mark_as_accepted(modeladmin, request, queryset):
    updated = queryset.update(status='accepted')
    modeladmin.message_user(request, f'{updated} quotation(s) marked as accepted.')

@admin.action(description="Mark selected quotations as declined")
def mark_as_declined(modeladmin, request, queryset):
    updated = queryset.update(status='declined')
    modeladmin.message_user(request, f'{updated} quotation(s) marked as declined.')

# Add actions to QuotationAdmin
QuotationAdmin.actions = [mark_as_sent, mark_as_accepted, mark_as_declined]
