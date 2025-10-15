from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.core.mail import EmailMessage, get_connection
from django.conf import settings

from .models import (
    CompanySettings,
    Civilite,
    LegalForm,
    PaymentMode,
    TaxRate,
    PaymentCondition,
    AutoEntrepreneurParameters,
    InterfaceSettings,
    EmailSettings,
)
from .forms import (
    CompanySettingsForm,
    CiviliteForm,
    LegalFormForm,
    PaymentModeForm,
    TaxRateForm,
    PaymentConditionForm,
    AutoEntrepreneurParametersForm,
    InterfaceSettingsForm,
    EmailSettingsForm,
)

# ===================== HELPERS =====================

def is_admin(user):
    return user.is_authenticated and getattr(user, 'account_type', None) == 'ADMINISTRATOR'

admin_required = user_passes_test(is_admin)

# ===================== HOME CONFIGURATION =====================

@login_required
@admin_required
def configuration_home(request):
    return render(request, 'system_config/configuration_home.html', {
        'page_title': 'Configuration Système',
    })

# ===================== COMPANY SETTINGS (SINGLETON) =====================

@login_required
@admin_required
def company_settings_view(request):
    instance = CompanySettings.get_solo()
    if request.method == 'POST':
        form = CompanySettingsForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, _('Paramètres société enregistrés avec succès.'))
            return redirect('system_config:company_settings')
    else:
        form = CompanySettingsForm(instance=instance)
    return render(request, 'system_config/company_settings.html', {
        'form': form,
        'page_title': 'Informations / Coordonnées Société',
    })

# ===================== LISTS GENERIC =====================

LIST_MODELS = {
    'civilites': (Civilite, CiviliteForm, 'Civilités'),
    'formes-juridiques': (LegalForm, LegalFormForm, 'Formes juridiques'),
    'modes-reglement': (PaymentMode, PaymentModeForm, 'Modes de règlement'),
    'taux-taxes': (TaxRate, TaxRateForm, 'Taux de taxes'),
    'conditions-paiement': (PaymentCondition, PaymentConditionForm, 'Conditions de paiement'),
}

@login_required
@admin_required
def list_generic(request, slug):
    if slug not in LIST_MODELS:
        messages.error(request, _('Liste inconnue.'))
        return redirect('system_config:configuration_home')
    model, form_class, verbose = LIST_MODELS[slug]

    # CREATE / UPDATE
    if request.method == 'POST':
        obj_id = request.POST.get('object_id')
        instance = None
        if obj_id:
            instance = get_object_or_404(model, pk=obj_id)
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            if instance:
                messages.success(request, _('Enregistré avec succès.'))
            else:
                messages.success(request, _('Créé avec succès.'))
            return redirect(request.path)
    else:
        form = form_class()

    # DELETE
    delete_id = request.GET.get('delete')
    if delete_id:
        obj = get_object_or_404(model, pk=delete_id)
        obj.delete()
        messages.success(request, _('Supprimé.'))
        return redirect(request.path.split('?')[0])

    objects = model.objects.all()
    return render(request, 'system_config/list_generic.html', {
        'objects': objects,
        'form': form,
        'verbose': verbose,
        'slug': slug,
        'page_title': f'Liste - {verbose}',
    })

# ===================== PARAMETRES (AUTO ENTREPRENEUR / INTERFACE / EMAIL) =====================

@login_required
@admin_required
def parameters_view(request):
    auto_params, created_auto = AutoEntrepreneurParameters.objects.get_or_create(pk=1)
    interface_params, created_interface = InterfaceSettings.objects.get_or_create(pk=1)
    email_params, created_email = EmailSettings.objects.get_or_create(pk=1)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'auto':
            auto_form = AutoEntrepreneurParametersForm(request.POST, instance=auto_params)
            if auto_form.is_valid():
                auto_form.save()
                messages.success(request, _('Paramètres auto-entrepreneur enregistrés.'))
                return redirect('system_config:parameters')
        else:
            auto_form = AutoEntrepreneurParametersForm(instance=auto_params)
        if form_type == 'interface':
            interface_form = InterfaceSettingsForm(request.POST, request.FILES, instance=interface_params)
            if interface_form.is_valid():
                interface_form.save()
                messages.success(request, _('Interface mise à jour.'))
                return redirect('system_config:parameters')
        else:
            interface_form = InterfaceSettingsForm(instance=interface_params)
        if form_type == 'email':
            email_form = EmailSettingsForm(request.POST, instance=email_params)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, _('Paramètres email enregistrés.'))
                return redirect('system_config:parameters')
        else:
            email_form = EmailSettingsForm(instance=email_params)
    else:
        auto_form = AutoEntrepreneurParametersForm(instance=auto_params)
        interface_form = InterfaceSettingsForm(instance=interface_params)
        email_form = EmailSettingsForm(instance=email_params)

    return render(request, 'system_config/parameters.html', {
        'auto_form': auto_form,
        'interface_form': interface_form,
        'email_form': email_form,
        'page_title': 'Paramètres Système',
    })

@login_required
@admin_required
def test_email_settings(request):
    """Testa a configuração SMTP salva enviando um e-mail de teste."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)
    try:
        email_params = EmailSettings.objects.get(pk=1)
        if not email_params.actif:
            return JsonResponse({'success': False, 'message': "Les paramètres email ne sont pas 'actifs'."}, status=400)

        # Validações básicas antes de tentar enviar
        if email_params.use_tls and email_params.use_ssl:
            return JsonResponse({'success': False, 'message': "N'utilisez pas TLS et SSL en même temps."}, status=400)
        if email_params.port == 587 and not email_params.use_tls:
            return JsonResponse({'success': False, 'message': "Le port 587 requiert TLS (STARTTLS) activé."}, status=400)
        if email_params.port == 465 and not email_params.use_ssl:
            return JsonResponse({'success': False, 'message': "Le port 465 requiert SSL activé."}, status=400)
        if not email_params.username or not email_params.password:
            return JsonResponse({'success': False, 'message': "SMTP AUTH requis: renseignez 'Nom d'utilisateur' et 'Mot de passe' (utilisez un mot de passe d'application si nécessaire)."}, status=400)

        # Construir conexão SMTP direta com os parâmetros salvos
        conn = get_connection(
            backend="django.core.mail.backends.smtp.EmailBackend",
            host=email_params.host,
            port=email_params.port,
            username=email_params.username,
            password=email_params.password,
            use_tls=email_params.use_tls,
            use_ssl=email_params.use_ssl,
            fail_silently=False,
        )

        # Destinatário de teste: email do usuário logado ou email da empresa
        to_email = getattr(request.user, 'email', None)
        if not to_email:
            try:
                to_email = CompanySettings.get_solo().email
            except Exception:
                to_email = None
        if not to_email:
            return JsonResponse({'success': False, 'message': "Aucun destinataire de test disponible (utilisateur/entreprise)."}, status=400)

        from_email = (email_params.from_email or email_params.username or '') or None
        if not from_email:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)

        msg = EmailMessage(
            subject="Test SMTP - Lopes Peinture",
            body="Ceci est un email de test pour valider la configuration SMTP.",
            from_email=from_email,
            to=[to_email],
            connection=conn,
        )
        msg.send(fail_silently=False)
        return JsonResponse({'success': True, 'message': f"Email de test envoyé à {to_email}"})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f"Erreur: {e}"}, status=500)
