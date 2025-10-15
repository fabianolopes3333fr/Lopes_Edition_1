from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .models import User
from .decorators import account_type_required
from . import forms as account_forms
from utils.emails.sistema_email import send_password_reset_email, send_account_status_email, send_email_changed_notification, send_account_deleted_email

# Novo: enviar verificação de e-mail via allauth
try:
    from allauth.account.utils import send_email_confirmation
    from allauth.account.models import EmailAddress
except Exception:
    send_email_confirmation = None
    EmailAddress = None


@login_required
@account_type_required("ADMINISTRATOR")
def users_list(request):
    """
    Lista de usuários com busca e filtros básicos.
    Acesso: apenas ADMINISTRATOR (account_type).
    """
    q = request.GET.get("q", "").strip()
    account_type = request.GET.get("type", "")
    status = request.GET.get("status", "")

    users = User.objects.all().order_by("-date_joined")

    if q:
        users = users.filter(
            Q(email__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(username__icontains=q)
        )

    if account_type:
        users = users.filter(account_type=account_type)

    if status == "active":
        users = users.filter(is_active=True)
    elif status == "inactive":
        users = users.filter(is_active=False)

    # Estatísticas baseadas no conjunto filtrado atual
    total_count = users.count()
    active_count = users.filter(is_active=True).count()
    admins_count = users.filter(account_type="ADMINISTRATOR").count()
    clients_count = users.filter(account_type="CLIENT").count()

    context = {
        "page_title": "Utilisateurs",
        "users": users.prefetch_related("groups"),
        "query": q,
        "filter_type": account_type,
        "filter_status": status,
        "total_count": total_count,
        "active_count": active_count,
        "admins_count": admins_count,
        "clients_count": clients_count,
    }
    return render(request, "accounts/users/list.html", context)


@login_required
@account_type_required("ADMINISTRATOR")
def user_create(request):
    """Criação de usuário por administrador."""
    if request.method == "POST":
        form = account_forms.AdminUserForm(request.POST, request=request)
        if form.is_valid():
            user = form.save(commit=True)

            # Forçar verificação: definir inativo até confirmar o email
            if user.is_active:
                user.is_active = False
                user.save(update_fields=["is_active"])

            # Enviar email automático para definição de senha
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse("accounts:password_reset_confirm", kwargs={"uidb64": uid, "token": token})
            )
            send_password_reset_email(user, reset_url, request)

            # Garantir EmailAddress do allauth
            try:
                if EmailAddress is not None and user.email:
                    EmailAddress.objects.get_or_create(
                        user=user,
                        email=user.email,
                        defaults={"primary": True, "verified": False},
                    )
            except Exception:
                pass

            # Enviar email de verificação de conta (allauth)
            try:
                if send_email_confirmation is not None:
                    send_email_confirmation(request, user)
            except Exception:
                pass

            messages.success(
                request,
                f"Utilisateur {user.get_full_name() or user.email} créé. Des emails de vérification et de définition de mot de passe ont été envoyés."
            )
            return redirect("accounts:users_list")
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = account_forms.AdminUserForm(request=request)

    return render(request, "accounts/users/form.html", {"form": form, "is_create": True, "page_title": "Nouveau utilisateur"})


@login_required
@account_type_required("ADMINISTRATOR")
def user_edit(request, user_id):
    """Edição de usuário por administrador."""
    user_obj = get_object_or_404(User, pk=user_id)
    old_email = user_obj.email

    if request.method == "POST":
        form = account_forms.AdminUserForm(request.POST, instance=user_obj, request=request)
        if form.is_valid():
            user = form.save(commit=True)
            # Notificar mudança de email (se houver)
            try:
                if old_email and user.email and old_email != user.email:
                    send_email_changed_notification(old_email, user.email, request)
            except Exception:
                pass
            messages.success(request, f"Utilisateur {user.get_full_name() or user.email} mis à jour avec succès.")
            return redirect("accounts:users_list")
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = account_forms.AdminUserForm(instance=user_obj, request=request)

    return render(request, "accounts/users/form.html", {"form": form, "is_create": False, "page_title": "Modifier utilisateur", "user_obj": user_obj})


@login_required
@account_type_required("ADMINISTRATOR")
def user_toggle_active(request, user_id):
    """Ativa/Desativa um usuário. Impede desativar a si mesmo."""
    user_obj = get_object_or_404(User, pk=user_id)

    if user_obj.pk == request.user.pk:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect("accounts:users_list")

    # Não permitir alterar superuser sem ser superuser
    if user_obj.is_superuser and not request.user.is_superuser:
        messages.error(request, "Action refusée: droits de superutilisateur requis.")
        return redirect("accounts:users_list")

    user_obj.is_active = not user_obj.is_active
    user_obj.save(update_fields=["is_active"])

    # Notificar usuário sobre mudança de status (falha silenciosa)
    try:
        send_account_status_email(user_obj, user_obj.is_active, request)
    except Exception:
        pass

    status_txt = "activé" if user_obj.is_active else "désactivé"
    messages.success(request, f"Utilisateur {user_obj.email} {status_txt}.")
    return redirect("accounts:users_list")


@login_required
@account_type_required("ADMINISTRATOR")
def user_send_reset(request, user_id):
    """Envia email de reset de senha para o usuário selecionado."""
    user_obj = get_object_or_404(User, pk=user_id)

    # Gerar token e URL
    token = default_token_generator.make_token(user_obj)
    uid = urlsafe_base64_encode(force_bytes(user_obj.pk))
    reset_url = request.build_absolute_uri(
        reverse("accounts:password_reset_confirm", kwargs={"uidb64": uid, "token": token})
    )

    send_password_reset_email(user_obj, reset_url, request)
    messages.success(request, f"Email de réinitialisation enviado à {user_obj.email}.")
    return redirect("accounts:users_list")


@login_required
@account_type_required("ADMINISTRATOR")
def user_delete(request, user_id):
    """Remove um usuário (somente não-superuser, e não pode remover a si próprio)."""
    user_obj = get_object_or_404(User, pk=user_id)

    if user_obj.pk == request.user.pk:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect("accounts:users_list")

    if user_obj.is_superuser and not request.user.is_superuser:
        messages.error(request, "Action refusée: droits de superutilisateur requis.")
        return redirect("accounts:users_list")

    email = user_obj.email
    user_obj.delete()

    # Notificar usuário sobre exclusão da conta (falha silenciosa)
    try:
        if email:
            send_account_deleted_email(email, request)
    except Exception:
        pass

    messages.success(request, f"Utilisateur {email} supprimé.")
    return redirect("accounts:users_list")
