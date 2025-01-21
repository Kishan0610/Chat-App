from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView, LoginView
from .models import Message
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

def index(request):
    if request.user.is_authenticated:
        return redirect('chat')  
    return redirect('login')  

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

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
            {"sender": msg.sender.username, "content": msg.content, "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
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
            msg = Message.objects.create(sender=sender, receiver=recipient, content=content)
            return JsonResponse({'status': 'success', 'message': 'Message sent successfully.'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Recipient not found.'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
