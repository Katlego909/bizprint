import os
from django.conf import settings

def send_whatsapp_message(to_number, body):
    """
    Sends a WhatsApp message via Twilio.
    Requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_WHATSAPP_NUMBER in settings.
    """
    # 1. Sanitize Number (Ensure it starts with +27 for SA)
    to_number = to_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if to_number.startswith("0"):
        to_number = "+27" + to_number[1:]
    elif not to_number.startswith("+"):
        to_number = "+" + to_number

    # 2. Check if Twilio is configured (Prevent crash if keys are missing)
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    from_number = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886') # Twilio Sandbox Default

    if not account_sid or not auth_token:
        print(f"⚠️ [Mock WhatsApp] To: {to_number} | Body: {body}")
        return

    # 3. Send Message
    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_=from_number,
            body=body,
            to=f"whatsapp:{to_number}"
        )
        print(f"✅ WhatsApp sent to {to_number}: {message.sid}")
    except Exception as e:
        print(f"❌ Failed to send WhatsApp: {e}")
