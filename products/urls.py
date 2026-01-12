from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),

    path('categories/<slug:slug>/', views.products_by_category, name='products_by_category'),
    path('categories/', views.all_categories, name='all_categories'),
    
    # Order flow
    path('order/success/<uuid:order_id>/', views.order_success, name='order_success'),
    path('order/<uuid:order_id>/invoice/', views.order_invoice, name='order_invoice'),
    path('order/<uuid:order_id>/invoice/download/', views.download_invoice_pdf, name='download_invoice_pdf'),
    path('order/<uuid:order_id>/reupload/', views.reupload_artwork, name='reupload_artwork'),
    
    # Tracking & dashboard
    path('track/', views.track_order_form, name='track_order'),
    path('track/result/', views.track_order_result, name='track_order_result'),
    path('my-orders/', views.my_orders, name='my_orders'),

    path('cancel-order/<uuid:order_id>/', views.cancel_order, name='cancel_order'),

    path('upload-payment/<uuid:order_id>/', views.upload_payment_proof, name='upload_payment_proof'),

    path('contact/', views.contact_support, name='contact_support'),
]
