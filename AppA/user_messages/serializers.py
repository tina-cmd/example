from rest_framework import serializers
from .models import Message
from django.contrib.auth.models import User

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    recipient = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    # Add a custom field to include the sender's username in the response
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['sender', 'sender_username', 'recipient', 'content', 'encrypted_content', 'timestamp']

    def to_representation(self, instance):
        # Get the default serialized data first
        data = super().to_representation(instance)
        
        # Attempt to decrypt content before returning it
        try:
            decrypted_content = instance.decrypt_content()
            data['content'] = decrypted_content
        except Exception as e:
            # Handle decryption errors gracefully
            data['content'] = "Error decrypting content"  # Default message if decryption fails
            print(f"Decryption error: {e}")  # Log for debugging

        return data
