from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserRegistrationForm, CustomerProfileForm, ProfileUpdateForm, NewsletterSignupForm
from .models import CustomerProfile, NewsletterSubscriber
from accounts.utils import send_newsletter_discount_email

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.first_name = form.cleaned_data['full_name']
            user.save()
            login(request, user)
            return redirect('accounts:complete_profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def complete_profile(request):
    try:
        profile = request.user.profile  # This will raise AttributeError if not created yet
        return redirect('products:product_list')  # Already has profile, skip setup
    except CustomerProfile.DoesNotExist:
        pass

    if request.method == 'POST':
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('products:product_list')
    else:
        form = CustomerProfileForm()
    return render(request, 'accounts/complete_profile.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

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
    return redirect('products:home')