# urls.py
from django.urls import path
from .views import * 


urlpatterns = [
    path('', index, name='index'),
     path('user/',user, name='user'),
   path('send-otp/',send_email_otp, name='send_email_otp'),
    path('verify-otp/',verify_email_otp, name='verify_email_otp'),
]
