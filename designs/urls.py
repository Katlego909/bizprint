from django.urls import path
from . import views

app_name = 'designs'

urlpatterns = [
    path('', views.design_list, name='design_list'),
    path('request/', views.design_request_create, name='design_request_create'),
    path('my-requests/', views.my_design_requests, name='my_design_requests'),
    path('upload-proof/<int:request_id>/', views.upload_proof_of_payment, name='upload_proof_of_payment'),
    path('quote/<str:quote_token>/', views.design_request_quote, name='design_request_quote'),
    path('quote/<str:quote_token>/download/', views.download_design_quote_pdf, name='download_quote_pdf'),
    path('invoice/<int:request_id>/', views.design_request_invoice, name='design_request_invoice'),
]
