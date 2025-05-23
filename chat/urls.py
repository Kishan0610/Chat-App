from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomLogoutView, CustomLoginView, CustomPasswordResetView, signup, activate
from django.contrib import messages

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', signup, name='signup'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('chat/', views.chat_view, name='chat'),
    path('send-message/', views.send_message, name='send_message'),
    path('messages/<str:recipient_username>/', views.fetch_messages, name='fetch_messages'),
    path("create-group/", views.create_group, name="create-group"),
    path("add-member/", views.add_member, name="add-member"),
    path("send-group-message/", views.send_group_message, name="send-group-message"),
    path("group-messages/<int:group_id>/", views.fetch_group_messages, name="fetch-group-messages"),
    # Password reset URLs
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]