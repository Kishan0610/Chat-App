from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomLogoutView, CustomLoginView

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('chat/', views.chat_view, name='chat'),
    path('send-message/', views.send_message, name='send_message'),
    path('messages/<str:recipient_username>/', views.fetch_messages, name='fetch_messages'),
    path("create-group/", views.create_group, name="create-group"),
    path("add-member/", views.add_member, name="add-member"),
    path("send-group-message/", views.send_group_message, name="send-group-message"),
    path("group-messages/<int:group_id>/", views.fetch_group_messages, name="fetch-group-messages"),
]
