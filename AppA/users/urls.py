from django.urls import path
from .views import RegisterView, LoginView, GetUserByUsernameView  # Import the updated view

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/get_by_username/', GetUserByUsernameView.as_view(), name='get-user-by-username'),  # Updated to CBV
]
