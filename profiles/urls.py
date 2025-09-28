# filepath: c:\Users\fabia\OneDrive\todos os projetos\Projetos\site_lopes_peinture\profiles\urls.py
from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    # ==================== PERFIL ====================
    # Visualizar perfil
    path("", views.profile_detail, name="detail"),
    path("detail/", views.profile_detail, name="detail"),
    # Editar perfil
    path("edit/", views.profile_edit, name="edit"),
    # ==================== AJAX ENDPOINTS ====================
    # Status de completude do perfil
    path(
        "ajax/completion-status/",
        views.ajax_profile_completion_status,
        name="completion_status",
    ),
    # ✅ NOVO: Upload de avatar via AJAX
    path("ajax/upload-avatar/", views.ajax_upload_avatar, name="upload_avatar"),
    # Teste de salvamento de perfil
    path("test-save/", views.test_profile_save, name="test_save"),
]
