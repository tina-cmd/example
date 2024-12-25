from django.shortcuts import render

def index(request):
    return render(request, 'AppA/index.html')  # Include the app name in the template path


# views.py in AppA
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User

@api_view(['GET'])
def get_user_by_username(request):
    username = request.query_params.get('username')
    try:
        user = User.objects.get(username=username)
        return Response({"id": user.id, "username": user.username})
    except User.DoesNotExist:
        return Response({"detail": "No User matches the given query"}, status=404)
