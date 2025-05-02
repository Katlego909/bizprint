from django.db import models
from django.contrib.auth.models import User

import uuid


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Category
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)

    class Meta:
        ordering = ['name']

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"    

    def __str__(self):
        return self.name

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Products
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='product_images/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    
    def __str__(self):
        return self.name

# ✅ Quantity-based pricing (e.g. 100 = R300, 500 = R750)

class QuantityTier(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="quantity_tiers")
    quantity = models.PositiveIntegerField()
    base_price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ['quantity']

    def __str__(self):
        return f"{self.quantity} @ R{self.base_price} for {self.product.name}"

# ✅ Configurable dropdown options (e.g. Finish: Matte +R15)

class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options')
    option_type = models.CharField(max_length=50)  # e.g. Finish, Size, Format
    value = models.CharField(max_length=100)       # e.g. Glossy, Double-sided
    price_modifier = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.product.name} - {self.option_type}: {self.value}"

# ✅ Optional add-ons (e.g. Design Help, Express Delivery)

class OptionalService(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='services')
    label = models.CharField(max_length=100)  # e.g. "3-Day Design Service"
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_required = models.BooleanField(default=False)  # e.g. Delivery might be required

    def __str__(self):
        return f"{self.label} (+R{self.price})"
        
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Orders
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Order(models.Model):
    STATUS_CHOICES = [
        ("received", "Received"),
        ("in_production", "In Production"),
        ("completed", "Completed"),
        ("shipped", "Shipped"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('eft', 'EFT'),
        ('online', 'Online'),
    ]

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        blank=True,
        null=True
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)

    # Snapshot of user contact info at time of order
    full_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    options = models.JSONField()
    services = models.JSONField(blank=True, null=True)
    file = models.FileField(upload_to='orders/')

    shipping_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)  # ✅ Shipping field added

    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="received")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='eft')
    proof_of_payment = models.FileField(upload_to='payments/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{str(self.uuid)[:8]} - {self.product.name} - R{self.total_price}"

