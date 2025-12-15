from django.contrib import admin
from django.utils.html import format_html
from .models import DesignPackage, DesignRequest
from import_export.admin import ImportExportModelAdmin


@admin.register(DesignPackage)
class DesignPackageAdmin(ImportExportModelAdmin):
    list_display = ('title', 'price')

@admin.register(DesignRequest)
class DesignRequestAdmin(ImportExportModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'whatsapp_actions')
    list_filter = ('status',)
    search_fields = ('user__email', 'user__username', 'quote_token')
    readonly_fields = ('uuid', 'quote_token')

    def whatsapp_actions(self, obj):
        phone = obj.phone
        if not phone and obj.user and hasattr(obj.user, 'profile'):
            phone = obj.user.profile.phone
            
        if not phone:
            return "No phone number"
        
        # Basic sanitization for SA numbers
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if phone.startswith("0"):
            phone = "27" + phone[1:]
            
        from urllib.parse import quote

        def make_btn(label, status_header, specific_msg, color="#25D366"):
            # Determine name
            name = obj.full_name or (obj.user.first_name if obj.user else "Customer")
            
            text_lines = [
                f"Hi {name}, this is BizPrint.",
                "",
                f"Regarding Design Request #{obj.id}:",
                "",
                f"• Status: {obj.get_status_display()}",
                f"• Total: R{obj.total_price}",
                "",
                "--------------------------------",
                f"{status_header}",
                "--------------------------------",
                specific_msg
            ]
            full_msg = "\n".join(text_lines)
            url = f"https://wa.me/{phone}?text={quote(full_msg)}"
            return f'<a class="button" href="{url}" target="_blank" style="background-color:{color}; color:white; padding:5px 10px; border-radius:5px; text-decoration:none; margin-right:5px; display:inline-block; margin-bottom:5px;">{label}</a>'

        # 1. Quote Ready
        quote_url = f"https://bizprint.co.za/designs/quote/{obj.quote_token}/" # Placeholder URL
        quote_msg = f"Your design quote is ready!\nYou can view and accept it here:\n{quote_url}"
        
        # 2. Payment Reminder
        pay_msg = "We haven't received your payment yet.\nPlease send proof of payment so we can start your design."

        # 3. First Draft / Proof
        draft_msg = "Here is the first draft of your design.\nPlease let us know if you have any changes or if we can proceed."

        # 4. Final Files
        final_msg = "Your design is complete! We have emailed the final high-quality files to you."

        buttons = [
            make_btn("Send Quote", "QUOTE READY", quote_msg),
            make_btn("Payment Reminder", "PAYMENT REQUIRED", pay_msg, "#e67e22"),
            make_btn("Send Draft", "ACTION REQUIRED", draft_msg, "#3498db"),
            make_btn("Design Complete", "COMPLETED", final_msg, "#9b59b6"),
        ]

        return format_html("".join(buttons))
    
    whatsapp_actions.short_description = "WhatsApp Actions"
    whatsapp_actions.allow_tags = True
