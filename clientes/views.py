from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Cliente, AdresseLivraison, AdresseTransporteur, AdresseChantier, TarifTVAClient
from .forms import (
    ClienteForm, AdresseLivraisonFormSet, AdresseTransporteurFormSet,
    AdresseChantierFormSet, TarifTVAClientFormSet
)


@login_required
def lista_clientes(request):
    """Lista todos os clientes com filtros e paginação"""
    clientes = Cliente.objects.all()

    # Adicionar filtro por origem (dashboard, auto-registro, devis público)
    origem_filter = request.GET.get('origem')

    # Filtros
    search = request.GET.get('search')
    status_filter = request.GET.get('status')

    if search:
        clientes = clientes.filter(
            Q(code__icontains=search) |
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(raison_sociale__icontains=search) |
            Q(email__icontains=search)
        )

    if status_filter:
        clientes = clientes.filter(status=status_filter)

    if origem_filter:
        clientes = clientes.filter(origem=origem_filter)

    # Ordenação com clientes criados via dashboard primeiro
    clientes = clientes.order_by('origem', 'nom', 'prenom')

    # Paginação
    paginator = Paginator(clientes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'origem_filter': origem_filter,
        'status_choices': Cliente.STATUS_CHOICES,
        'origem_choices': Cliente.ORIGEM_CHOICES,
    }

    return render(request, 'clientes/lista_clientes.html', context)


@login_required
def criar_cliente(request):
    """Criar um novo cliente"""
    if request.method == 'POST':
        form = ClienteForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    cliente = form.save()
                    messages.success(request, f'Cliente {cliente.nom_complet} criado com sucesso!')
                    return redirect('clientes:editar_cliente', pk=cliente.pk)
            except Exception as e:
                messages.error(request, f'Erro ao salvar cliente: {str(e)}')
                print(f"Erro ao salvar cliente: {e}")  # Debug
        else:
            messages.error(request, 'Erro no formulário. Verifique os dados.')
            # Mostrar erros específicos para debug
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            print(f"Erros no formulário: {form.errors}")  # Debug
    else:
        form = ClienteForm()

    context = {
        'form': form,
        'action': 'Criar',
    }

    return render(request, 'clientes/form_cliente.html', context)


@login_required
def editar_cliente(request, pk):
    """Editar cliente com todas as abas"""
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)

        # Inicializar formsets com tratamento de erro melhorado
        formsets_data = {}
        formsets_valid = True
        formset_errors = []

        try:
            # Criar formsets com dados do POST
            livraison_formset = AdresseLivraisonFormSet(
                request.POST, instance=cliente, prefix='livraison'
            )
            transporteur_formset = AdresseTransporteurFormSet(
                request.POST, instance=cliente, prefix='transporteur'
            )
            chantier_formset = AdresseChantierFormSet(
                request.POST, instance=cliente, prefix='chantier'
            )
            tva_formset = TarifTVAClientFormSet(
                request.POST, instance=cliente, prefix='tva'
            )

            formsets_data = {
                'livraison': livraison_formset,
                'transporteur': transporteur_formset,
                'chantier': chantier_formset,
                'tva': tva_formset
            }

            # Validar cada formset individualmente
            for formset_name, formset in formsets_data.items():
                if not formset.is_valid():
                    formsets_valid = False
                    # Filtrar apenas erros de forms preenchidos (ignorar forms vazios)
                    errors_filtered = []
                    for form_errors in formset.errors:
                        if form_errors:  # Só adicionar se há erros reais
                            errors_filtered.append(form_errors)

                    if errors_filtered:  # Só reportar se há erros em forms preenchidos
                        formset_errors.append(f'{formset_name}: {errors_filtered}')

        except Exception as e:
            messages.error(request, f'Erro ao processar formulários relacionados: {str(e)}')
            formsets_valid = False

        # Validar formulário principal
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Salvar cliente principal
                    cliente = form.save()

                    # Salvar formsets válidos
                    for formset_name, formset in formsets_data.items():
                        try:
                            if formset.is_valid():
                                # Salvar apenas instances com dados preenchidos
                                instances = formset.save(commit=False)
                                for instance in instances:
                                    # Verificar se a instance tem dados essenciais preenchidos
                                    if hasattr(instance, 'nom') and instance.nom:
                                        instance.save()
                                formset.save_m2m()

                        except Exception as e:
                            formset_errors.append(f'{formset_name}: Erro ao salvar - {str(e)}')

                    if formset_errors:
                        messages.warning(
                            request,
                            f'Cliente salvo com problemas nos formulários relacionados: {"; ".join(formset_errors)}'
                        )
                    else:
                        messages.success(request, f'Cliente {cliente.nom_complet} atualizado com sucesso!')

                    return redirect('clientes:editar_cliente', pk=cliente.pk)

            except Exception as e:
                messages.error(request, f'Erro ao salvar: {str(e)}')
                print(f"Erro detalhado ao salvar: {e}")
        else:
            messages.error(request, 'Erro no formulário principal.')
            # Mostrar erros específicos do form principal
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    else:
        # GET request - inicializar forms vazios
        form = ClienteForm(instance=cliente)
        try:
            formsets_data = {
                'livraison': AdresseLivraisonFormSet(instance=cliente, prefix='livraison'),
                'transporteur': AdresseTransporteurFormSet(instance=cliente, prefix='transporteur'),
                'chantier': AdresseChantierFormSet(instance=cliente, prefix='chantier'),
                'tva': TarifTVAClientFormSet(instance=cliente, prefix='tva')
            }
        except Exception as e:
            messages.error(request, f'Erro ao carregar formulários: {str(e)}')
            formsets_data = {
                'livraison': None,
                'transporteur': None,
                'chantier': None,
                'tva': None
            }

    context = {
        'cliente': cliente,
        'form': form,
        'livraison_formset': formsets_data.get('livraison'),
        'transporteur_formset': formsets_data.get('transporteur'),
        'chantier_formset': formsets_data.get('chantier'),
        'tva_formset': formsets_data.get('tva'),
        'action': 'Editar',
    }

    return render(request, 'clientes/editar_cliente.html', context)


@login_required
def detalhe_cliente(request, pk):
    """Visualizar detalhes do cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)

    context = {
        'cliente': cliente,
    }

    return render(request, 'clientes/detalhe_cliente.html', context)


@login_required
def deletar_cliente(request, pk):
    """Deletar cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        nome = cliente.nom_complet
        cliente.delete()
        messages.success(request, f'Cliente {nome} deletado com sucesso!')
        return redirect('clientes:lista_clientes')

    context = {
        'cliente': cliente,
    }

    return render(request, 'clientes/deletar_cliente.html', context)


@login_required
def copiar_endereco_principal(request):
    """AJAX para copiar endereço principal"""
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')

        try:
            cliente = Cliente.objects.get(pk=cliente_id)
            data = {
                'success': True,
                'adresse': cliente.adresse,
                'code_postal': cliente.code_postal,
                'ville': cliente.ville,
                'pays': cliente.pays,
            }
        except Cliente.DoesNotExist:
            data = {'success': False, 'error': 'Cliente não encontrado'}

        return JsonResponse(data)

    return JsonResponse({'success': False, 'error': 'Método não permitido'})


@login_required
def converter_prospect_cliente(request, pk):
    """Converter prospect em cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)

    if cliente.status == 'prospect':
        cliente.status = 'client'
        cliente.save()
        messages.success(request, f'{cliente.nom_complet} convertido de prospect para cliente!')
    else:
        messages.info(request, f'{cliente.nom_complet} já é um cliente.')

    return redirect('clientes:detalhe_cliente', pk=pk)
