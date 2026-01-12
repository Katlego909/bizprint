from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/setup/', views.complete_profile, name='complete_profile'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('validate-discount/', views.validate_discount_code, name='validate_discount'),
]
