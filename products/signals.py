from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order
from .utils import send_whatsapp_message

@receiver(pre_save, sender=Order)
def track_order_status_change(sender, instance, **kwargs):
    """
    Check if the status has changed before saving.
    """
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            instance._old_payment_status = old_instance.payment_status
        except Order.DoesNotExist:
            pass

@receiver(post_save, sender=Order)
def send_order_notifications(sender, instance, created, **kwargs):
    """
    Send WhatsApp notifications on creation or status change.
    """
    # 1. New Order Notification
    if created:
        msg = (
            f"🎉 Hi {instance.full_name}, thanks for your order at BizPrint!\n\n"
            f"Order #{str(instance.uuid)[:8]}\n"
            f"📦 {instance.product.name}\n"
            f"💰 Total: R{instance.total_price}\n\n"
            f"We will notify you once production starts."
        )
        send_whatsapp_message(instance.phone, msg)
        return

    # 2. Status Change Notification
    if hasattr(instance, '_old_status') and instance._old_status != instance.status:
        new_status = instance.get_status_display()
        
        msg = (
            f"📢 Update on Order #{str(instance.uuid)[:8]}\n\n"
            f"Current Status: *{new_status}*\n\n"
        )

        if instance.status == Order.Status.IN_PROD:
            msg += "🎨 Your artwork is approved and printing has started!"
        elif instance.status == Order.Status.COMPLETED:
            msg += "✅ Your order is complete and ready for collection/shipping."
        elif instance.status == Order.Status.SHIPPED:
            msg += "🚚 Your order is on its way!"
        
        send_whatsapp_message(instance.phone, msg)

    # 3. Payment Received Notification
    if hasattr(instance, '_old_payment_status') and instance._old_payment_status != instance.payment_status:
        if instance.payment_status == Order.PaymentStatus.PAID:
            msg = (
                f"💰 Payment Received for Order #{str(instance.uuid)[:8]}.\n"
                f"Thank you! We are now processing your order."
            )
            send_whatsapp_message(instance.phone, msg)
