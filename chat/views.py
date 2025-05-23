from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView, LoginView, PasswordResetView
from .models import Message, Group, GroupMessage
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from .models import EmailVerification

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
        'placeholder': 'Email'
    }))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    
class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives with both text and HTML versions
        """
        subject = render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())  # Remove any line breaks
        body = render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(
            subject, body, from_email, [to_email]
        )

        if html_email_template_name is not None:
            html_email = render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    html_email_template_name = 'password_reset_email.html'
    success_url = '/password-reset/done/'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            messages.error(self.request, "No account exists with this email address.")
            return self.form_invalid(form)
        return super().form_valid(form)

def index(request):
    if request.user.is_authenticated:
        return redirect('chat')
    else:
        return render(request, 'index.html') 

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User can't login until verified
            user.save()
            
            # Create and send verification email
            verification = EmailVerification.create_verification(user)
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            message = render_to_string('acc_activate_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': verification.token,
            })
            send_mail(mail_subject, message, 'noreply@yourdomain.com', [user.email])
            
            return render(request, 'registration/verification_sent.html')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None:
        verification = EmailVerification.objects.filter(user=user, token=token).first()
        if verification and not verification.is_verified:
            verification.is_verified = True
            verification.save()
            user.is_active = True
            user.save()
            return render(request, 'registration/verification_success.html')
    
    return render(request, 'registration/verification_invalid.html')

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def form_invalid(self, form):
        form.add_error(None, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    http_method_names = ['get', 'post']


@login_required
def chat_view(request):
    users = User.objects.exclude(username=request.user.username)
    return render(request, 'chat.html', {'users': users})

@login_required
def fetch_messages(request, recipient_username):
    sender = request.user
    try:
        recipient = User.objects.get(username=recipient_username)
        messages = Message.objects.filter(sender=sender, receiver=recipient) | Message.objects.filter(sender=recipient, receiver=sender)
        messages = messages.order_by('timestamp')

        message_list = [
            {"sender": msg.sender.username, "content": msg.content, "timestamp": msg.timestamp.isoformat()}  # Send ISO timestamp
            for msg in messages
        ]
        return JsonResponse({"messages": message_list}, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "Recipient not found"}, status=404)

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sender = request.user
        recipient_username = data.get('recipient')
        content = data.get('message')

        try:
            recipient = User.objects.get(username=recipient_username)
            Message.objects.create(sender=sender, receiver=recipient, content=content)
            return JsonResponse({'status': 'success', 'message': 'Message sent successfully.'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Recipient not found.'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

@login_required
def create_group(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if Group.objects.filter(name=name).exists():
            return JsonResponse({"error": "Group name already exists"}, status=400)
        group = Group.objects.create(name=name, creator=request.user)
        group.members.add(request.user)
        return JsonResponse({"message": "Group created successfully", "group_id": group.id})

@login_required
def add_member(request):
    if request.method == "POST":
        group_id = request.POST.get("group_id")
        username = request.POST.get("username")
        try:
            group = Group.objects.get(id=group_id, creator=request.user)
            user = User.objects.get(username=username)
            group.members.add(user)
            return JsonResponse({"message": "User added successfully"})
        except Group.DoesNotExist:
            return JsonResponse({"error": "Group not found"}, status=404)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

@login_required
def send_group_message(request):
    if request.method == "POST":
        group_id = request.POST.get("group_id")
        content = request.POST.get("content")
        group = Group.objects.get(id=group_id)
        if request.user in group.members.all():
            message = GroupMessage.objects.create(group=group, sender=request.user, content=content)
            return JsonResponse({"message": "Message sent", "message_id": message.id})
        return JsonResponse({"error": "You are not in this group"}, status=403)
    

@login_required
def fetch_group_messages(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
        if request.user not in group.members.all():
            return JsonResponse({"error": "Not a member of this group"}, status=403)

        messages = GroupMessage.objects.filter(group=group).order_by("timestamp")
        message_list = [{"sender": msg.sender.username, "content": msg.content, "timestamp": msg.timestamp.isoformat()} for msg in messages]

        return JsonResponse({"messages": message_list}, status=200)
    except Group.DoesNotExist:
        return JsonResponse({"error": "Group not found"}, status=404)
