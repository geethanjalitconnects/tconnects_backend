import random
from django.core.mail import send_mail
from django.conf import settings


def generate_otp():
    """Generate a random 6-digit OTP"""
    return str(random.randint(100000, 999999))


def send_otp_email(email, code):
    """Send OTP via email"""
    subject = "Your TConnect Login OTP"
    message = f"""
Hello,

Your One-Time Password (OTP) for logging into TConnect is: {code}

This OTP is valid for 10 minutes.

If you didn't request this OTP, please ignore this email.

Best regards,
TConnect Team
    """.strip()
    
    try:
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,  # Raise exceptions so we can catch them
        )
        
        print(f"✅ send_mail returned: {result}")
        return result
        
    except Exception as e:
        print(f"❌ send_mail raised exception: {type(e).__name__}: {str(e)}")
        raise  # Re-raise so the view can handle it