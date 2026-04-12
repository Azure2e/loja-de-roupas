from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # ==================== LOGIN ====================
    path('login/', 
         auth_views.LoginView.as_view(
             template_name='accounts/login.html',
             redirect_authenticated_user=True,
             success_url=reverse_lazy('core:home')
         ), 
         name='login'),

    # ==================== LOGOUT ====================
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # ==================== CADASTRO ====================
    path('register/', views.register, name='register'),

    # ==================== PERFIL DO USUÁRIO ====================
    path('perfil/', views.perfil, name='perfil'),   # ← CORRIGIDO (agora usa a função perfil)

    # ==================== NOTIFICAÇÕES ====================
    path('notifications/', views.get_notifications, name='get_notifications'),

    # ==================== RESET DE SENHA ====================
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url=reverse_lazy('accounts:password_reset_done')
         ), 
         name='password_reset'),

    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
         name='password_reset_done'),

    path('password-reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), 
         name='password_reset_confirm'),

    path('password-reset/complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
         name='password_reset_complete'),
]