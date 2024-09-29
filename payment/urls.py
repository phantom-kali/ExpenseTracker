
from django.urls import path
from . import views

urlpatterns = [
    path('api/process-mpesa-sms/', views.process_mpesa_sms, name='process_mpesa_sms'),
    path('submit_mpesa_sms/', views.submit_mpesa_sms, name='submit_mpesa_sms')
]