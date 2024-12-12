from django.shortcuts import get_object_or_404  # <-- Add this import
from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Message
from .serializers import MessageSerializer
from rest_framework import status
from rest_framework.decorators import api_view

@api_view(['POST'])
def send_message(request):
    """
    Send a message from the authenticated user to the recipient.
    """
    try:
        # Extract the recipient ID and content from the request body
        recipient_id = request.data.get('recipient')
        content = request.data.get('content')

        if not recipient_id or not content:
            return Response({"detail": "Recipient and content are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the authenticated user (sender)
        sender = request.user

        # Try to find the recipient by their ID
        recipient = User.objects.get(id=recipient_id)

        # Create and save the message
        message = Message(sender=sender, recipient=recipient, content=content)
        message.save()

        # Return a success response
        return Response({"message": "Message sent successfully"}, status=status.HTTP_201_CREATED)

    except User.DoesNotExist:
        # If the recipient does not exist
        return Response({"detail": "Recipient not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # For any other exceptions
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Secure key for encryption (store securely in production)
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        sender = request.user  # Get the authenticated user

        # Ensure the recipient ID is provided
        recipient_id = data.get('recipient')
        if not recipient_id:
            return Response({"detail": "Recipient is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Look up the recipient by ID
        try:
            recipient = User.objects.get(id=recipient_id)  # Use ID here
        except User.DoesNotExist:
            return Response({"detail": "Recipient not found."}, status=status.HTTP_404_NOT_FOUND)

        # Proceed with creating the message
        message = Message(sender=sender, recipient=recipient, content=data.get('content'))
        message.save()

        return Response({"message": "Message sent successfully"}, status=status.HTTP_201_CREATED)


class InboxView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get all messages where the authenticated user is the recipient
            messages = Message.objects.filter(recipient=request.user)
            
            if not messages.exists():
                return Response({"detail": "No messages found."}, status=status.HTTP_404_NOT_FOUND)

            # Serialize the messages and include decrypted content
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)  # Return the serialized messages
        except Exception as e:
            # Log the error for debugging
            print(f"Error fetching messages: {e}")
            return Response({"detail": "An error occurred while loading the inbox."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class GetUserByUsername(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        if not username:
            return Response({"detail": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
            return Response({"id": user.id, "username": user.username}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
