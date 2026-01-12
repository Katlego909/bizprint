from django.contrib import admin
from .models import Product, QuantityTier, ProductOption, OptionalService, Order, Category, ShippingMethod
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
        'created_at', 'artwork_preview', 'payment_preview',
        'whatsapp_actions'
    ]

    def whatsapp_actions(self, obj):
        if not obj.phone:
            return "No phone number"
        
        # Basic sanitization for SA numbers
        phone = obj.phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if phone.startswith("0"):
            phone = "27" + phone[1:]
            
        from urllib.parse import quote

        def make_btn(label, status_header, specific_msg, color="#25D366"):
            text_lines = [
                f"Hi {obj.full_name or 'Customer'}, this is BizPrint.",
                "",
                f"Regarding Order #{str(obj.uuid)[:8]}:",
                "",
                f"• Product: {obj.product.name}",
                f"• Qty: {obj.quantity}",
                f"• Total: R{obj.total_price}",
                f"• Email: {obj.email}",
                f"• Payment: {obj.get_payment_status_display()}",
                "",
                "--------------------------------",
                f"{status_header}",
                "--------------------------------",
                specific_msg
            ]
            full_msg = "\n".join(text_lines)
            url = f"https://wa.me/{phone}?text={quote(full_msg)}"
            return f'<a class="button" href="{url}" target="_blank" style="background-color:{color}; color:white; padding:5px 10px; border-radius:5px; text-decoration:none; margin-right:5px; display:inline-block; margin-bottom:5px;">{label}</a>'

        # 1. Proof Message
        proof_msg = "Here is the proof for your order.\nPlease reply with APPROVED so we can proceed to print."
        
        # 2. In Production Message
        prod_msg = "Your artwork has been approved!\nYour order is now being printed. We will notify you when it is ready."

        # 3. Ready/Shipped Message
        ready_msg = "Good news! Your order is READY.\nYou can collect it during our office hours, or we will dispatch it shortly if you chose delivery."

        # 4. Payment Reminder
        pay_msg = "We haven't received your payment yet.\nPlease send proof of payment so we can start your order."

        buttons = [
            make_btn("Send Proof", "ACTION REQUIRED", proof_msg),
            make_btn("In Production", "STATUS UPDATE", prod_msg, "#3498db"),
            make_btn("Ready / Shipped", "ORDER COMPLETE", ready_msg, "#9b59b6"),
            make_btn("Payment Reminder", "PAYMENT REQUIRED", pay_msg, "#e67e22"),
        ]

        return format_html("".join(buttons))
    
    whatsapp_actions.short_description = "WhatsApp Actions"
    whatsapp_actions.allow_tags = True

    fieldsets = (
        (None, {
            'fields': (
                'uuid', 'whatsapp_actions', 'user', 'product', 'quantity', 'base_price',
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

# ==========================
# Shipping Method Admin
# ==========================

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'description']
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ['price']
    search_fields = ['name', 'description']