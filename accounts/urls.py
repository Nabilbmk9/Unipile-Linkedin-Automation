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
    path("prospection/<int:pk>/launch/", views.launch_prospection_view, name="launch_prospection"),
    path("prospection/<int:pk>/confirmation/", views.confirm_prospection_view, name="confirm_prospection"),
    path("prospection/<int:pk>/detail/", views.prospection_detail_view, name="prospection_detail"),
]
