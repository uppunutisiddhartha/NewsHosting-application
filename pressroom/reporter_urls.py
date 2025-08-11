from django.urls import path
from .reporters_views import *

urlpatterns = [
    path('reporter/register/', reporter_registration, name='reporter_registration'),
    path('verify-email/<uuid:token>/', verify_email, name='verify_email'),
    path('reporter-admin/pending/', reporter_admin_view, name='reporter_admin_dashboard'),
    path('reporter-admin/handle/<int:reporter_id>/', handle_reporter_status, name='handle_reporter_status'),
    path('reporter/login/', reporter_login, name='reporter_login'),
    path('reporter/dashboard/', reporter_dashboard, name='reporter_dashboard'),
]