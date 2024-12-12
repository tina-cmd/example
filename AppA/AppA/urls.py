from django.contrib import admin
from django.urls import path, include
from .views import index,get_user_by_username
from user_messages import views as message_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),  # This includes all the auth-related URLs from the users app
    path('api/messages/', include('user_messages.urls')),  # This includes all the message-related URLs from the user_messages app
    path('', index, name='home'),
    path('users/get_by_username/', get_user_by_username, name='get_user_by_username'),
    # path('chat/', include('appA.routing.websocket_urlpatterns')),

]
