from django.urls import path
from . import views
from . import social_views
from . import settings_views

app_name = "accounts"

urlpatterns = [
    # ==================== AUTENTICAÇÃO ====================
    # Registro
    path("register/", views.RegisterView.as_view(), name="register"),
    # Login
    path("login/", views.user_login, name="login"),
    # Logout (suporta GET e POST)
    path("logout/", views.user_logout, name="logout"),

    # ==================== LOGIN SOCIAL ====================
    # Callbacks e redirecionamentos para login social
    path(
        "social/success/",
        social_views.social_login_success,
        name="social_login_success",
    ),
    path(
        "social/error/",
        social_views.social_login_error,
        name="social_login_error",
    ),
    path(
        "social/connections/",
        social_views.social_account_connections,
        name="social_connections",
    ),
    path(
        "social/disconnect/<str:provider>/",
        social_views.disconnect_social_account,
        name="disconnect_social",
    ),
    # AJAX endpoints para login social
    path(
        "ajax/social-status/",
        social_views.ajax_social_login_status,
        name="ajax_social_status",
    ),

    # ==================== PARÂMETROS E CONFIGURAÇÕES ====================
    # Página principal de parâmetros
    path("parametros/", settings_views.parametros, name="parametros"),
    path("settings/", settings_views.account_settings, name="settings"),  # Alias

    # AJAX endpoints para parâmetros
    path("ajax/update-preferences/", settings_views.update_preferences, name="update_preferences"),
    path("ajax/toggle-2fa/", settings_views.toggle_2fa, name="toggle_2fa"),
    path("ajax/export-data/", settings_views.export_data, name="export_data"),
    path("ajax/delete-account/", settings_views.delete_account, name="delete_account"),

    # ==================== RESET SENHA ==================
    # Fluxo de reset de senha
    path("password_reset/", views.password_reset, name="password_reset"),
    path(
        "password_reset/done/",
        views.password_reset_done,
        name="password_reset_done",
    ),
    path(
        "password_reset/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path("password_reset/complete/", views.password_reset_complete, name="password_reset_complete"),
    path("password_change/", views.password_change, name="password_change"),

    # ==================== DASHBOARD ====================
    # Dashboard principal
    path("dashboard/", views.dashboard, name="dashboard"),
    # Perfil básico (redirecionará para profiles app)

    # ==================== AJAX ENDPOINTS ====================
    # Logout via AJAX
    path("ajax/logout/", views.ajax_logout, name="ajax_logout"),
    # Verificação de disponibilidade de email
    path("ajax/check-email/", views.check_email_availability, name="check_email"),
    # ==================== REDIRECTS ÚTEIS ====================
    # Redirect para dashboard (URL amigável)
    path("", views.dashboard, name="index"),
]
