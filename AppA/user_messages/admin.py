from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Message

# Register the Message model so it appears in the Django admin
admin.site.register(Message)
