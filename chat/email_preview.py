# email_preview.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.utils.html import strip_tags

def preview_password_reset_email():
    user = User.objects.first() 
    context = {
        'user': user,
        'protocol': 'http',
        'domain': 'localhost:8000',
        'uid': 'MQ', 
        'token': 'abcdefg-123456',
        'site_name': 'Chat Application',
    }
    
    # Render HTML email
    html_content = render_to_string('password_reset_email.html', context)
    text_content = strip_tags(html_content)
    
    # Create and send email
    email = EmailMultiAlternatives(
        subject="🔑 Password Reset Request",
        body=text_content,
        from_email="061002kishan@example.com",
        to=[user.email],
    )
    email.attach_alternative(html_content, "text/html")
    
    # Save to file for preview instead of sending
    with open('password_reset_email_preview.html', 'w') as f:
        f.write(html_content)
    print("Email preview saved to password_reset_email_preview.html")

if __name__ == "__main__":
    preview_password_reset_email()