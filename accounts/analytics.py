# accounts/analytics.py
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from collections import defaultdict

def get_user_analytics(user):
    """
    Generate comprehensive analytics for a user
    """
    from products.models import Order
    from designs.models import DesignRequest
    
    # Get all user orders
    orders = Order.objects.filter(user=user)
    # Only count spending for paid AND completed/delivered orders
    completed_paid_orders = orders.filter(
        payment_status='paid',
        status__in=['completed', 'delivered']
    )
    
    # Overall statistics
    total_orders = orders.count()
    total_spent = completed_paid_orders.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
    avg_order_value = completed_paid_orders.aggregate(avg=Avg('total_price'))['avg'] or Decimal('0.00')
    
    # Orders by status
    orders_by_status = orders.values('status').annotate(count=Count('id'))
    status_breakdown = {item['status']: item['count'] for item in orders_by_status}
    
    # Monthly spending (last 12 months) - only completed & paid orders
    twelve_months_ago = timezone.now() - timedelta(days=365)
    monthly_spending = completed_paid_orders.filter(
        created_at__gte=twelve_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('total_price'),
        count=Count('id')
    ).order_by('month')
    
    # Format monthly data
    monthly_data = {
        'labels': [item['month'].strftime('%b %Y') for item in monthly_spending],
        'spending': [float(item['total']) for item in monthly_spending],
        'orders': [item['count'] for item in monthly_spending]
    }
    
    # Popular products - only from completed & paid orders
    popular_products = completed_paid_orders.values(
        'product__name'
    ).annotate(
        count=Count('id'),
        total_spent=Sum('total_price')
    ).order_by('-count')[:5]
    
    # Design requests
    design_requests = DesignRequest.objects.filter(user=user)
    total_design_requests = design_requests.count()
    # Only count design spending for paid design requests
    paid_design_requests = design_requests.filter(status='paid')
    design_spending = paid_design_requests.aggregate(
        total=Sum(F('packages__price'))
    )['total'] or Decimal('0.00')
    
    # Recent activity
    recent_orders = orders.order_by('-created_at')[:5]
    
    # Savings from discounts - only from completed & paid orders
    total_discounts = completed_paid_orders.aggregate(total=Sum('discount_amount'))['total'] or Decimal('0.00')
    
    return {
        'total_orders': total_orders,
        'total_spent': total_spent,
        'avg_order_value': avg_order_value,
        'status_breakdown': status_breakdown,
        'monthly_data': monthly_data,
        'popular_products': list(popular_products),
        'total_design_requests': total_design_requests,
        'design_spending': design_spending,
        'recent_orders': recent_orders,
        'total_discounts': total_discounts,
        'total_all_spending': total_spent + design_spending,
    }


def get_platform_analytics():
    """
    Generate platform-wide analytics (for admin/reporting)
    """
    from products.models import Order, Product
    from designs.models import DesignRequest
    from accounts.models import NewsletterSubscriber
    from django.contrib.auth.models import User
    
    # Overall metrics
    total_users = User.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(
        payment_status='paid'
    ).aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
    
    # Recent growth (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_users = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    new_orders = Order.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Product performance
    top_products = Order.objects.values(
        'product__name'
    ).annotate(
        total_orders=Count('id'),
        revenue=Sum('total_price')
    ).order_by('-total_orders')[:10]
    
    # Newsletter stats
    newsletter_subs = NewsletterSubscriber.objects.count()
    
    return {
        'total_users': total_users,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'new_users_30d': new_users,
        'new_orders_30d': new_orders,
        'top_products': list(top_products),
        'newsletter_subscribers': newsletter_subs,
    }
