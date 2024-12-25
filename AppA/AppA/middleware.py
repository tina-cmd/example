from cryptography.fernet import Fernet
from django.http import JsonResponse
from rest_framework.response import Response
from django.conf import settings

# Initialize the encryption key globally
cipher = Fernet(settings.ENCRYPTION_KEY)

class EncryptRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only encrypt POST/PUT/PATCH requests, where data is present
        if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'data'):
            if 'content' in request.data:
                content = request.data['content']
                encrypted_content = cipher.encrypt(content.encode()).decode()
                request.data['content'] = encrypted_content

        # Call the next middleware or the view
        response = self.get_response(request)
        return response


class DecryptResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Call the view or the next middleware
        response = self.get_response(request)

        # Ensure the response is either a DRF Response or JsonResponse
        if isinstance(response, (Response, JsonResponse)):
            if isinstance(response.data, dict) and 'content' in response.data:
                encrypted_content = response.data['content']
                try:
                    decrypted_content = cipher.decrypt(encrypted_content.encode()).decode()
                    response.data['content'] = decrypted_content
                except Exception as e:
                    response.data['content'] = "Decryption error"  # Handle decryption failure

        return response
