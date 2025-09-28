import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Profile
from .forms import ProfileForm

logger = logging.getLogger(__name__)


# ==================== PROFILE VIEWS ====================
@login_required
def profile_detail(request):
    """✅ CORRIGIDO: Visualizar perfil do usuário"""
    user = request.user

    # Criar ou obter perfil
    try:
        profile = user.profile
        logger.info(f"Perfil encontrado para {user.email}")
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)
        messages.info(request, "Profil créé automatiquement.")
        logger.info(f"Perfil criado para {user.email}")

    # Calcular dados de completude
    completion_data = {
        "percentage": profile.completion_percentage,
        "is_complete": profile.is_complete,
        "missing_fields": _get_missing_fields(profile),
    }

    # ✅ LOG para debug
    logger.info(
        f"Profile detail para {user.email}: completude={completion_data['percentage']}%"
    )

    context = {
        "user": user,
        "profile": profile,
        "groups": user.groups.all(),
        "completion": completion_data,
    }

    return render(request, "profiles/detail.html", context)


@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def profile_edit(request):
    """Editar perfil - VERSÃO LIMPA"""
    user = request.user
    profile = user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            try:
                saved_profile = form.save()
                messages.success(
                    request,
                    f"✅ Profil mis à jour avec succès! Complétude: {saved_profile.completion_percentage}%",
                )
                return redirect("profiles:detail")

            except Exception as e:
                messages.error(request, f"Erreur lors de la sauvegarde: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        form = ProfileForm(instance=profile)

    context = {
        "form": form,
        "user": user,
        "profile": profile,
        "completion_percentage": profile.completion_percentage,
    }

    return render(request, "profiles/edit.html", context)


@login_required
@require_http_methods(["GET"])
def ajax_profile_completion_status(request):
    """✅ CORRIGIDO: Verificar status de completude do perfil via AJAX"""
    user = request.user

    try:
        profile = user.profile
        completion_data = {
            "is_complete": profile.is_complete,
            "completion_percentage": profile.completion_percentage,
            "missing_fields": _get_missing_fields(profile),
            "message": "Profil complet" if profile.is_complete else "Profil incomplet",
        }
    except Profile.DoesNotExist:
        completion_data = {
            "is_complete": False,
            "completion_percentage": 0,
            "missing_fields": ["phone", "address", "city", "postal_code"],
            "message": "Profil non créé",
        }

    return JsonResponse(completion_data)


@login_required
@require_http_methods(["POST"])
def ajax_upload_avatar(request):
    """✅ NOVO: Upload de avatar via AJAX"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Profil non trouvé"}, status=404
        )

    if "avatar" not in request.FILES:
        return JsonResponse(
            {"success": False, "error": "Aucun fichier fourni"}, status=400
        )

    avatar_file = request.FILES["avatar"]

    # Validações
    if avatar_file.size > 2097152:  # 2MB
        return JsonResponse(
            {"success": False, "error": "Fichier trop volumineux (max 2MB)"}, status=400
        )

    allowed_types = ["image/jpeg", "image/png", "image/gif"]
    if avatar_file.content_type not in allowed_types:
        return JsonResponse(
            {"success": False, "error": "Type de fichier non autorisé"}, status=400
        )

    try:
        # Deletar avatar antigo
        if profile.avatar:
            profile.delete_old_avatar()

        # Salvar novo avatar
        profile.avatar = avatar_file
        profile.save()

        return JsonResponse(
            {
                "success": True,
                "avatar_url": profile.avatar.url,
                "message": "Avatar mis à jour avec succès",
            }
        )

    except Exception as e:
        logger.error(f"Erro ao fazer upload de avatar para {request.user.email}: {e}")
        return JsonResponse(
            {"success": False, "error": "Erreur lors du téléchargement"}, status=500
        )


@login_required
def test_profile_save(request):
    """✅ TESTE: View para testar salvamento direto"""
    if request.method == "POST":
        try:
            profile = request.user.profile

            # ✅ SAVE DIRETO SEM FORM
            profile.phone = "+33 1 23 45 67 89"
            profile.city = "Test City"
            profile.address = "Test Address"
            profile.postal_code = "75001"
            profile.save()

            # Verificar se salvou
            profile.refresh_from_db()

            return JsonResponse(
                {
                    "success": True,
                    "phone": profile.phone,
                    "city": profile.city,
                    "message": "Save direto funcionou!",
                }
            )

        except Exception as e:
            logger.error(f"Erro no teste de save: {e}", exc_info=True)
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"error": "Método não permitido"})


# ==================== UTILITY FUNCTIONS ====================
def _get_missing_fields(profile):
    """✅ NOVO: Obter campos faltantes do perfil"""
    missing = []

    if not (profile.phone and profile.phone.strip()):
        missing.append("phone")
    if not (profile.address and profile.address.strip()):
        missing.append("address")
    if not (profile.city and profile.city.strip()):
        missing.append("city")
    if not (profile.postal_code and profile.postal_code.strip()):
        missing.append("postal_code")
    if not profile.avatar:
        missing.append("avatar")

    return missing


def calculate_profile_completion(profile):
    """✅ MANTIDO: Função para compatibilidade (usar profile.completion_percentage)"""
    return profile.completion_percentage
