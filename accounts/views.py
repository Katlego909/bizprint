from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from .forms import UserRegistrationForm, CustomerProfileForm, ProfileUpdateForm, NewsletterSignupForm
from .models import CustomerProfile, NewsletterSubscriber
from accounts.utils import send_newsletter_discount_email
from .analytics import get_user_analytics

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('products:home')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.first_name = form.cleaned_data['full_name']
            user.save()
            login(request, user)
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(f"{reverse('accounts:complete_profile')}?next={next_url}")
            return redirect('accounts:complete_profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def complete_profile(request):
    next_url = request.GET.get('next')
    try:
        profile = request.user.profile  # This will raise AttributeError if not created yet
        if next_url:
            return redirect(next_url)
        return redirect('products:product_list')  # Already has profile, skip setup
    except CustomerProfile.DoesNotExist:
        pass

    if request.method == 'POST':
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            if next_url:
                return redirect(next_url)
            return redirect('products:product_list')
    else:
        form = CustomerProfileForm()
    return render(request, 'accounts/complete_profile.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

@login_required
def dashboard_view(request):
    # Fetch recent orders (limit 5)
    recent_orders = request.user.orders.all().order_by('-created_at')[:5]
    
    # Fetch recent design requests (limit 5)
    # Note: We need to make sure the related_name 'design_requests' is set on the DesignRequest model
    # Based on previous context, it is: related_name='design_requests'
    recent_designs = request.user.design_requests.all().order_by('-created_at')[:5]
    
    # Get analytics data
    analytics = get_user_analytics(request.user)

    context = {
        'recent_orders': recent_orders,
        'recent_designs': recent_designs,
        'analytics': analytics,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/edit_profile.html', {'form': form})    

# Email Subscription View

def subscribe_newsletter(request):
    if request.method == 'POST':
        form = NewsletterSignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if created:
                send_newsletter_discount_email(subscriber)
                messages.success(request, "Thanks for signing up! Check your email for your 10% discount code.")
            else:
                messages.info(request, "You're already subscribed.")
        else:
            messages.error(request, "Please enter a valid email.")

    # send them back to where they submitted from; fall back to home
    referer = request.META.get("HTTP_REFERER") or reverse('products:home')
    return redirect(referer)

def validate_discount_code(request):
    """AJAX endpoint to validate discount codes in real-time"""
    code = request.GET.get('code', '').strip().upper()
    
    if not code:
        return JsonResponse({'valid': False})
    
    try:
        subscriber = NewsletterSubscriber.objects.get(discount_code=code)
        return JsonResponse({'valid': True, 'discount': 10})
    except NewsletterSubscriber.DoesNotExist:
        return JsonResponse({'valid': False})

@login_required
def analytics_view(request):
    """Dedicated analytics dashboard with detailed charts and insights"""
    analytics = get_user_analytics(request.user)
    
    context = {
        'analytics': analytics,
    }
    return render(request, 'accounts/analytics.html', context)

@login_required
def loyalty_program_view(request):
    """View loyalty points and tier information"""
    profile = request.user.profile
    transactions = request.user.loyalty_transactions.all()[:20]
    
    # Calculate potential rewards
    points_value = profile.loyalty_points * Decimal('0.10')  # R0.10 per point
    
    context = {
        'profile': profile,
        'transactions': transactions,
        'points_value': points_value,
    }
    return render(request, 'accounts/loyalty.html', context)

@login_required
def referral_program_view(request):
    """View referral program information and track referrals"""
    profile = request.user.profile
    
    # Get user's referrals
    from .models import Referral
    referrals = Referral.objects.filter(referrer=request.user)
    completed_referrals = referrals.filter(is_completed=True).count()
    pending_referrals = referrals.filter(is_completed=False).count()
    
    # Calculate potential earnings
    potential_earnings = pending_referrals * 50  # R50 per referral
    
    context = {
        'profile': profile,
        'referrals': referrals,
        'completed_referrals': completed_referrals,
        'pending_referrals': pending_referrals,
        'potential_earnings': potential_earnings,
    }
    return render(request, 'accounts/referral.html', context)
