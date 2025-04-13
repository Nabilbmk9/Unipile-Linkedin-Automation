# accounts/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # URLs pour la réinitialisation du mot de passe
    path('password-reset/', 
        views.CustomPasswordResetView.as_view(), 
        name='password_reset'
    ),
    path('password-reset/done/', 
        views.CustomPasswordResetDoneView.as_view(), 
        name='password_reset_done'
    ),
    path('password-reset-confirm/<uidb64>/<token>/', 
        views.CustomPasswordResetConfirmView.as_view(), 
        name='password_reset_confirm'
    ),
    path('password-reset-complete/', 
        views.CustomPasswordResetCompleteView.as_view(), 
        name='password_reset_complete'
    ),
    
    # URLs LinkedIn et prospection
    path('unipile-callback/', views.unipile_callback, name='unipile_callback'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('new-prospection/', views.new_prospection_view, name='new_prospection'),
    path('delete-prospection/<int:session_id>/', views.delete_prospection_view, name='delete_prospection'),
    path('connect-linkedin/', views.connect_linkedin, name='connect_linkedin'),
    path('prospection/<int:pk>/toggle/', views.toggle_prospection, name='toggle_prospection'),
    path('prospection/<int:pk>/launch/', views.launch_prospection_view, name='launch_prospection'),
    path('prospection/<int:pk>/confirmation/', views.confirm_prospection_view, name='confirm_prospection'),
    path('prospection/<int:pk>/detail/', views.prospection_detail_view, name='prospection_detail'),
]
