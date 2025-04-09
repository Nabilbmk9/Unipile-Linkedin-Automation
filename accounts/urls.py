# accounts/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('connect-linkedin/', views.connect_linkedin, name='connect_linkedin'),
    path('unipile-callback/', views.unipile_callback, name='unipile_callback'),
    path("prospection/new/", views.new_prospection_view, name="new_prospection"),
    path("prospection/<int:pk>/toggle/", views.toggle_prospection, name="toggle_prospection"),
]
