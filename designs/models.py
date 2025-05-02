from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import uuid

class DesignPackage(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='design_images/', blank=True, null=True)

    def __str__(self):
        return self.title

class DesignRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('paid', 'Paid')
    ]

    # Allow guests (user null) or authenticated users
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='design_requests',
        null=True,
        blank=True
    )
    email = models.EmailField(
        blank=True,
        help_text="Required if you are not logged in"
    )
    quote_token = models.CharField(
        max_length=32,
        unique=True,
        null=True,
        blank=True,
        help_text="Unique token for guest quote access"
    )

    image = models.ImageField(
        upload_to='design_images/',
        blank=True,
        null=True
    )
    packages = models.ManyToManyField(DesignPackage)
    additional_instructions = models.TextField(blank=True)
    uploaded_files = models.FileField(
        upload_to='design_uploads/',
        blank=True,
        null=True
    )
    proof_of_payment = models.FileField(
        upload_to='design_payments/',
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        user_part = self.user.username if self.user else self.email or "Guest"
        return f"Design Request #{self.id} by {user_part}"

    def clean(self):
        # Ensure a user or an email is provided
        if not self.user and not self.email:
            raise ValidationError("A logged‑in user or an email address is required.")

    def save(self, *args, **kwargs):
        # Generate a unique token for guest access if missing
        if not self.quote_token:
            self.quote_token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return sum(p.price for p in self.packages.all())