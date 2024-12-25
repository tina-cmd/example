from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.conf import settings  # Import settings to use ENCRYPTION_KEY

class Message(models.Model):
    sender = models.ForeignKey(User, related_name="appA_sent_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="appA_received_messages", on_delete=models.CASCADE)
    content = models.TextField()  # This stores the plain text message
    encrypted_content = models.TextField(blank=True, null=True)  # For the encrypted content
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set the time when the message is sent

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username} at {self.timestamp}"

    def save(self, *args, **kwargs):
        if self.content:
            # Use the key from settings (loaded from .env)
            cipher = Fernet(settings.ENCRYPTION_KEY)
            self.encrypted_content = cipher.encrypt(self.content.encode()).decode()
        super().save(*args, **kwargs)

    def decrypt_content(self):
        if self.encrypted_content:
            try:
                # Use the key from settings (loaded from .env)
                cipher = Fernet(settings.ENCRYPTION_KEY)
                return cipher.decrypt(self.encrypted_content.encode()).decode()
            except Exception as e:
                # Handle decryption errors gracefully
                return f"Decryption failed: {str(e)}"
        return "No content"
