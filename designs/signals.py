from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import DesignRequest
from decimal import Decimal


@receiver(pre_save, sender=DesignRequest)
def track_status_change(sender, instance, **kwargs):
    """
    Track status changes before saving to trigger appropriate emails
    """
    if instance.pk:
        try:
            previous = DesignRequest.objects.get(pk=instance.pk)
            instance._previous_status = previous.status
        except DesignRequest.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=DesignRequest)
def send_status_change_email(sender, instance, created, **kwargs):
    """
    Send email notifications when design request status changes
    """
    # Get email address
    email = instance.email if instance.email else (instance.user.email if instance.user else None)
    
    if not email:
        return
    
    # Prepare context data
    subtotal = instance.total_price
    vat = subtotal * Decimal('0.15')
    total = subtotal + vat
    turnaround_days = instance.get_estimated_turnaround_days()
    
    context = {
        'design_request': instance,
        'total': total,
        'turnaround_days': turnaround_days,
    }
    
    # Determine which email to send based on status change
    email_sent = False
    
    # New request created (status = pending)
    if created and instance.status == 'pending':
        subject = f'Your Design Quote #{instance.id} is Ready - BizPrint'
        html_message = render_to_string('emails/quote_ready.html', context)
        email_sent = True
    
    # Status changed from pending to paid
    elif hasattr(instance, '_previous_status') and instance._previous_status == 'pending' and instance.status == 'paid':
        subject = f'Payment Confirmed - Design #{instance.id} - BizPrint'
        html_message = render_to_string('emails/payment_confirmed.html', context)
        email_sent = True
    
    # Status changed to in_progress
    elif hasattr(instance, '_previous_status') and instance._previous_status != 'in_progress' and instance.status == 'in_progress':
        subject = f'Your Design is In Progress - #{instance.id} - BizPrint'
        html_message = render_to_string('emails/design_in_progress.html', context)
        email_sent = True
    
    # Status changed to completed
    elif hasattr(instance, '_previous_status') and instance._previous_status != 'completed' and instance.status == 'completed':
        subject = f'🎉 Your Design is Ready! - #{instance.id} - BizPrint'
        html_message = render_to_string('emails/design_completed.html', context)
        email_sent = True
    
    # Send the email if a status change was detected
    if email_sent:
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't break the save operation
            print(f"Failed to send email: {e}")
