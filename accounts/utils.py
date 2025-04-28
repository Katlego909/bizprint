from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal

def send_order_confirmation_email(order):
    subject = f"Your BizPrint Order #{str(order.uuid)[:8]} Confirmation"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [order.email]

    shipping_raw = getattr(order, "shipping_price", Decimal("0.00"))
    shipping = shipping_raw if isinstance(shipping_raw, Decimal) else Decimal(str(shipping_raw))

    pre_vat_total = (order.total_price - shipping) / Decimal("1.15")
    vat = pre_vat_total * Decimal("0.15")

    context = {
        "order": order,
        "shipping": shipping,
        "subtotal": pre_vat_total,
        "vat": vat,
    }

    html_body = render_to_string("emails/order_confirmation.html", context)
    email = EmailMultiAlternatives(subject, '', from_email, to_email)
    email.attach_alternative(html_body, "text/html")
    email.send()


def send_payment_received_email(order):
    subject = f"Payment Received for Order #{str(order.uuid)[:8]}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [order.email]

    context = {"order": order}
    html_body = render_to_string("emails/payment_received.html", context)
    email = EmailMultiAlternatives(subject, '', from_email, to_email)
    email.attach_alternative(html_body, "text/html")
    email.send()


def send_order_status_update_email(order):
    subject = f"Order #{str(order.uuid)[:8]} Status Update"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [order.email]

    context = {"order": order}
    html_body = render_to_string("emails/status_update.html", context)
    email = EmailMultiAlternatives(subject, '', from_email, to_email)
    email.attach_alternative(html_body, "text/html")
    email.send()

# Newsletter Subscription 

def send_newsletter_discount_email(subscriber):
    subject = "🎉 Welcome to BizPrint – Here's Your 10% Discount Code!"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [subscriber.email]

    context = {
        "discount_code": subscriber.discount_code,
        "email": subscriber.email,
    }

    html_body = render_to_string("emails/newsletter_discount.html", context)

    email = EmailMultiAlternatives(subject, '', from_email, to_email)
    email.attach_alternative(html_body, "text/html")
    email.send()