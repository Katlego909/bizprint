from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
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
    phone = models.CharField(max_length=20, blank=True, help_text="Contact number for WhatsApp updates")
    full_name = models.CharField(max_length=150, blank=True, help_text="Client name")
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True, db_index=True)
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
    
    # Design Brief Fields
    brand_colors = models.CharField(
        max_length=200,
        blank=True,
        help_text="Main brand colors (e.g., #FF5733, Blue, Red)"
    )
    target_audience = models.TextField(
        blank=True,
        help_text="Who is your target audience?"
    )
    design_preferences = models.TextField(
        blank=True,
        help_text="Any specific design style preferences?"
    )
    inspiration_links = models.TextField(
        blank=True,
        help_text="Links to designs you like (one per line)"
    )
    timeline_preference = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('rush', 'Rush (1-2 days)'),
            ('standard', 'Standard (3-5 days)'),
            ('flexible', 'Flexible (1-2 weeks)'),
        ],
        help_text="When do you need this completed?"
    )
    
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
    
    def get_rush_fee(self):
        """
        Calculate rush fee - 50% surcharge for rush timeline
        """
        if self.timeline_preference == 'rush':
            base_price = self.total_price
            return base_price * Decimal('0.50')  # 50% rush fee
        return Decimal('0.00')
    
    def get_subtotal_with_rush(self):
        """
        Get subtotal including rush fee if applicable
        """
        return self.total_price + self.get_rush_fee()
    
    def get_estimated_turnaround_days(self):
        """
        Calculate estimated turnaround time based on timeline preference and package count
        """
        # Base turnaround on timeline preference
        if self.timeline_preference == 'rush':
            base_days = 2
        elif self.timeline_preference == 'standard':
            base_days = 4
        elif self.timeline_preference == 'flexible':
            base_days = 10
        else:
            # Default to standard if not specified
            base_days = 5
        
        # Adjust based on number of packages (complexity)
        package_count = self.packages.count()
        if package_count > 3:
            base_days += 2
        elif package_count > 1:
            base_days += 1
        
        return base_days