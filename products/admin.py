from django.contrib import admin
from .models import Product, QuantityTier, ProductOption, OptionalService, Order, Category
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

# ==========================
# Inlines for Product Admin
# ==========================

class QuantityInline(admin.TabularInline):
    model = QuantityTier
    extra = 1

class OptionInline(admin.TabularInline):
    model = ProductOption
    extra = 1

class ServiceInline(admin.TabularInline):
    model = OptionalService
    extra = 1

# ==========================
# Product Admin
# ==========================

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ['name']
    prepopulated_fields = {"slug": ("name",)}
    inlines = [QuantityInline, OptionInline, ServiceInline]

admin.site.register(QuantityTier)
admin.site.register(ProductOption)
admin.site.register(OptionalService)

# ==========================
# Order Admin
# ==========================

@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    list_display = [
        'short_uuid', 'product', 'quantity', 'user_display',
        'total_price', 'status', 'payment_status', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['uuid', 'product__name', 'user__username']
    readonly_fields = [
        'uuid', 'options', 'services', 'total_price',
        'created_at', 'artwork_preview', 'payment_preview'
    ]
    fieldsets = (
        (None, {
            'fields': (
                'uuid', 'user', 'product', 'quantity', 'base_price',
                'options', 'services', 'total_price'
            )
        }),
        ("Customer Info", {
            'fields': ('full_name', 'email', 'phone', 'address')
        }),
        ("Files", {
            'fields': ('file', 'artwork_preview', 'proof_of_payment', 'payment_preview')
        }),
        ("Status", {
            'fields': ('status', 'payment_status', 'payment_method')
        }),
        ("Timestamps", {
            'fields': ('created_at',)
        }),
    )

    def short_uuid(self, obj):
        return str(obj.uuid)[:8]
    short_uuid.short_description = 'Ref'

    def user_display(self, obj):
        return obj.user.username if obj.user else 'Anonymous'
    user_display.short_description = 'Customer'

    def artwork_preview(self, obj):
        if obj.file:
            if any(ext in obj.file.name.lower() for ext in ['.jpg', '.jpeg', '.png']):
                return format_html(f'<img src="{obj.file.url}" style="max-height:100px;" />')
            return format_html(f'<a href="{obj.file.url}" target="_blank">Download</a>')
        return "No file"
    artwork_preview.short_description = "Artwork Preview"

    def payment_preview(self, obj):
        if obj.proof_of_payment:
            if any(ext in obj.proof_of_payment.name.lower() for ext in ['.jpg', '.jpeg', '.png']):
                return format_html(f'<img src="{obj.proof_of_payment.url}" style="max-height:100px;" />')
            return format_html(f'<a href="{obj.proof_of_payment.url}" target="_blank">Download</a>')
        return "No proof"
    payment_preview.short_description = "Payment Preview"

admin.site.register(Category, ImportExportModelAdmin)