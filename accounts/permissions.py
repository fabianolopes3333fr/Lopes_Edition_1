from django.db.models import Q
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from projects.models import Project
from profiles.models import UserProfile

User = get_user_model()

# Define as permissões customizadas para cada modelo
CUSTOM_PERMISSIONS = {
    User: {
        "view_own_profile": "Peut voir son propre profil",
        "edit_own_profile": "Peut modifier son propre profil",
        "view_all_profiles": "Peut voir tous les profils",
        "edit_all_profiles": "Peut modifier tous les profils",
        "delete_profiles": "Peut supprimer des profils",
    },
    Project: {
        "view_own_projects": "Peut voir ses propres projets",
        "edit_own_projects": "Peut modifier ses propres projets",
        "view_all_projects": "Peut voir tous les projets",
        "edit_all_projects": "Peut modifier tous les projets",
        "delete_projects": "Peut supprimer des projets",
        "manage_project_status": "Peut gérer le statut des projets",
    },
    UserProfile: {
        "manage_collaborators": "Peut gérer les collaborateurs",
        "view_statistics": "Peut voir les statistiques",
    },
}


def create_custom_permissions():
    """Cria todas as permissões customizadas definidas"""
    for model, permissions in CUSTOM_PERMISSIONS.items():
        content_type = ContentType.objects.get_for_model(model)
        for codename, name in permissions.items():
            Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type,
            )
