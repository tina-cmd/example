from django.urls import path
from .views import SendMessageView, InboxView, GetUserByUsername

urlpatterns = [
    path('send/', SendMessageView.as_view(), name='send-message'),
    path('inbox/', InboxView.as_view(), name='inbox'),
    path('users/get_by_username/', GetUserByUsername.as_view(), name='get_user_by_username'),  # This is correct
]
