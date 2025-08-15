from django.urls import path
from .cluster_views import *

urlpatterns = [
    path('superadmin/', superadmin, name='superadmin'),
    path('cluster/login/', cluster_admin_login, name='cluster_admin_login'),
    path('cluster/dashboard/', cluster_admin_dashboard, name='cluster_admin_dashboard'),
]
