from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet

# Secure key for encryption (store securely in production)
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    encrypted_content = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Encrypt content before saving
        if self.content:
            self.encrypted_content = cipher.encrypt(self.content.encode()).decode()
        super().save(*args, **kwargs)

    def decrypt_content(self):
        if self.encrypted_content:
            return cipher.decrypt(self.encrypted_content.encode()).decode()
        else:
            return ""
