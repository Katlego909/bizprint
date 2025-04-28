# accounts/models.py
import uuid
from django.db import models
from django.contrib.auth.models import User

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return self.user.get_full_name()

# Newsletter Subscription
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    discount_code = models.CharField(max_length=20, unique=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.discount_code:
            self.discount_code = f"BIZ-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email