from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.translation import gettext_lazy as _

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
