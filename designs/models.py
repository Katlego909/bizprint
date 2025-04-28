from django.db import models
from django.contrib.auth.models import User

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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='design_requests')
    image = models.ImageField(upload_to='design_images/', blank=True, null=True)
    packages = models.ManyToManyField(DesignPackage)
    additional_instructions = models.TextField(blank=True)
    uploaded_files = models.FileField(upload_to='design_uploads/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    proof_of_payment = models.FileField(upload_to='design_payments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(p.price for p in self.packages.all())

    def __str__(self):
        return f"Design Request #{self.id} by {self.user.username}"