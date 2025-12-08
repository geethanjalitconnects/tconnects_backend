import random
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP

def generate_otp():
    return f"{random.randint(100000,999999)}"

def send_otp_email(email, code):
    subject = "Your verification code"
    message = f"Your OTP code is {code}. It will expire in 10 minutes."
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
    except Exception:
        # Avoid raising raw exceptions up to the view; log and re-raise so
        # the caller can handle the failure gracefully.
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Failed to send OTP email to %s", email)
        raise
