import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.db.models import Min, Q

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Category
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)

    class Meta:  # merged Meta (your second Meta was masking ordering)
        ordering = ['name']  # keeps existing intent
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=['slug']),  # NEW: faster lookups by slug
        ]

    def __str__(self):
        return self.name

    # NEW: Optional convenience
    def get_absolute_url(self):
        return reverse('products:products_by_category', kwargs={'slug': self.slug})

    # ---- helpers ----
    def _generate_unique_slug(self):
        """
        Create a URL-safe slug from name and ensure uniqueness by adding -2, -3, ...
        Only called when slug is empty.
        """
        base = slugify(self.name) or "category"
        maxlen = self._meta.get_field("slug").max_length or 50
        slug = base[:maxlen]

        # If taken, append -2, -3 ... truncating base to keep within maxlen
        counter = 2
        while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            suffix = f"-{counter}"
            slug = f"{base[:maxlen - len(suffix)]}{suffix}"
            counter += 1
        return slug

    # ---- save override ----
    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Products
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='product_images/')  # keep required (no behavior change)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products',
        null=True, blank=True, help_text="Optional: leave blank for uncategorized"
    )

    class Meta:
        ordering = ['name']  # NEW: consistent listing without changing features
        indexes = [
            models.Index(fields=['slug']),                 # NEW
            models.Index(fields=['category']),             # NEW
        ]

    def __str__(self):
        return self.name

    # NEW: keep slug populated if left blank
    def _generate_unique_slug(self):
        base = slugify(self.name) or "product"
        maxlen = self._meta.get_field("slug").max_length or 50
        slug = base[:maxlen]
        counter = 2
        while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            suffix = f"-{counter}"
            slug = f"{base[:maxlen - len(suffix)]}{suffix}"
            counter += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    # NEW: convenience for templates/admin; does not change stored totals
    @property
    def starting_price(self) -> Decimal | None:
        """
        Lowest tier price (or None if no tiers).
        """
        agg = self.quantity_tiers.aggregate(p=Min('base_price'))
        return agg['p']

    # NEW: optional convenience
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})


# ✅ Quantity-based pricing (e.g. 100 = R300, 500 = R750)
class QuantityTier(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="quantity_tiers")
    quantity = models.PositiveIntegerField(help_text="Units in this tier, e.g. 100, 500")
    base_price = models.DecimalField(max_digits=8, decimal_places=2, help_text="Price for this tier")

    class Meta:
        ordering = ['quantity']
        constraints = [
            models.UniqueConstraint(fields=['product', 'quantity'], name='uq_tier_product_quantity'),  # NEW
            models.CheckConstraint(check=Q(quantity__gt=0), name='ck_tier_quantity_gt_0'),             # NEW
            models.CheckConstraint(check=Q(base_price__gte=0), name='ck_tier_price_gte_0'),            # NEW
        ]
        indexes = [
            models.Index(fields=['product', 'quantity']),  # NEW
        ]

    def __str__(self):
        return f"{self.quantity} @ R{self.base_price} for {self.product.name}"


# ✅ Configurable dropdown options (e.g. Finish: Matte +R15)
class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options')
    option_type = models.CharField(max_length=50)  # e.g. Finish, Size, Format
    value = models.CharField(max_length=100)       # e.g. Glossy, Double-sided
    price_modifier = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'option_type', 'value'], name='uq_option_product_type_value'),  # NEW
            models.CheckConstraint(check=Q(price_modifier__gte=0), name='ck_option_price_mod_gte_0'),                 # NEW
        ]
        indexes = [
            models.Index(fields=['product', 'option_type']),  # NEW
        ]

    def __str__(self):
        return f"{self.product.name} - {self.option_type}: {self.value}"


# ✅ Optional add-ons (e.g. Design Help, Express Delivery)
class OptionalService(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='services')
    label = models.CharField(max_length=100, help_text='e.g. "3-Day Design Service"')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_required = models.BooleanField(default=False, help_text="If true, auto-included in orders")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'label'], name='uq_service_product_label'),  # NEW
            models.CheckConstraint(check=Q(price__gte=0), name='ck_service_price_gte_0'),           # NEW
        ]
        indexes = [
            models.Index(fields=['product']),  # NEW
        ]

    def __str__(self):
        return f"{self.label} (+R{self.price})"


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Orders
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Order(models.Model):
    class Status(models.TextChoices):  # NEW: safer than raw strings in code, same values
        RECEIVED = "received", "Received"
        IN_PROD = "in_production", "In Production"
        COMPLETED = "completed", "Completed"
        SHIPPED = "shipped", "Shipped"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    class PaymentStatus(models.TextChoices):  # NEW
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"

    class PaymentMethod(models.TextChoices):  # NEW
        EFT = "eft", "EFT"
        ONLINE = "online", "Online"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True, db_index=True)  # db_index NEW

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

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEIVED)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.EFT)
    proof_of_payment = models.FileField(upload_to='payments/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),        # NEW
            models.Index(fields=['status', 'created_at']),      # NEW
            models.Index(fields=['payment_status', 'created_at']),  # NEW
        ]
        constraints = [
            models.CheckConstraint(check=Q(quantity__gt=0), name='ck_order_qty_gt_0'),                # NEW
            models.CheckConstraint(check=Q(base_price__gte=0), name='ck_order_base_price_gte_0'),     # NEW
            models.CheckConstraint(check=Q(shipping_price__gte=0), name='ck_order_shipping_gte_0'),   # NEW
            models.CheckConstraint(check=Q(total_price__gte=0), name='ck_order_total_gte_0'),         # NEW
        ]

    def __str__(self):
        return f"Order #{str(self.uuid)[:8]} - {self.product.name} - R{self.total_price}"

    # NEW: small helpers (no behavior change)
    @property
    def proof_received(self) -> bool:
        return bool(self.proof_of_payment)

    @property
    def is_cancelable(self) -> bool:
        return self.status == self.Status.RECEIVED
