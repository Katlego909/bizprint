# accounts/models.py
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    # Loyalty Program
    loyalty_points = models.PositiveIntegerField(default=0, help_text="Points earned from purchases")
    loyalty_tier = models.CharField(
        max_length=20,
        choices=[
            ('bronze', 'Bronze'),
            ('silver', 'Silver'),
            ('gold', 'Gold'),
            ('platinum', 'Platinum'),
        ],
        default='bronze'
    )
    
    # Referral Program
    referral_code = models.CharField(max_length=12, unique=True, null=True, blank=True, help_text="User's unique referral code")
    referred_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='referrals',
        help_text="User who referred this person"
    )
    referral_earnings = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Total earnings from referrals"
    )

    def __str__(self):
        return self.user.get_full_name()
    
    def save(self, *args, **kwargs):
        # Generate referral code if not exists
        if not self.referral_code:
            self.referral_code = f"REF-{str(uuid.uuid4())[:8].upper()}"
        # Update loyalty tier based on points
        self.update_loyalty_tier()
        super().save(*args, **kwargs)
    
    def update_loyalty_tier(self):
        """Update loyalty tier based on points"""
        if self.loyalty_points >= 5000:
            self.loyalty_tier = 'platinum'
        elif self.loyalty_points >= 2500:
            self.loyalty_tier = 'gold'
        elif self.loyalty_points >= 1000:
            self.loyalty_tier = 'silver'
        else:
            self.loyalty_tier = 'bronze'
    
    def add_loyalty_points(self, points):
        """Add loyalty points and update tier"""
        self.loyalty_points += points
        self.save()
    
    @property
    def loyalty_discount_percentage(self):
        """Get discount percentage based on tier"""
        tier_discounts = {
            'bronze': 0,
            'silver': 5,
            'gold': 10,
            'platinum': 15,
        }
        return tier_discounts.get(self.loyalty_tier, 0)
    
    @property
    def points_to_next_tier(self):
        """Calculate points needed for next tier"""
        tier_thresholds = {
            'bronze': 1000,
            'silver': 2500,
            'gold': 5000,
            'platinum': None,
        }
        next_threshold = tier_thresholds.get(self.loyalty_tier)
        if next_threshold is None:
            return 0  # Already at max tier
        return max(0, next_threshold - self.loyalty_points)

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

# Referral Tracking
class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referred_from')
    referral_code_used = models.CharField(max_length=12)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False, help_text="True when referred user makes first purchase")
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=50.00, help_text="Reward for referrer")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_user.username}"

# Loyalty Points History
class LoyaltyTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loyalty_transactions')
    points = models.IntegerField(help_text="Points earned (positive) or redeemed (negative)")
    description = models.CharField(max_length=200)
    order_reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        action = "earned" if self.points > 0 else "redeemed"
        return f"{self.user.username} {action} {abs(self.points)} points"
