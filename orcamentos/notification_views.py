from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import Notificacao

@login_required
def listar_notificacoes(request):
    """Lista todas as notificações do usuário"""
    notificacoes = Notificacao.objects.filter(usuario=request.user).order_by('-created_at')

    # Paginação
    paginator = Paginator(notificacoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'page_title': 'Mes Notifications',
    }
    return render(request, 'orcamentos/notifications/listar.html', context)

@login_required
@require_http_methods(["POST"])
def marcar_notificacao_lida(request, notificacao_id):
    """Marcar uma notificação como lida via AJAX"""
    try:
        notificacao = get_object_or_404(
            Notificacao,
            id=notificacao_id,
            usuario=request.user
        )
        notificacao.marcar_como_lida()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def marcar_todas_lidas(request):
    """Marcar todas as notificações como lidas"""
    try:
        Notificacao.objects.filter(
            usuario=request.user,
            lida=False
        ).update(lida=True, read_at=timezone.now())

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_notificacoes_nao_lidas(request):
    """Retorna o número de notificações não lidas via AJAX"""
    count = Notificacao.objects.filter(
        usuario=request.user,
        lida=False
    ).count()

    notificacoes_recentes = Notificacao.objects.filter(
        usuario=request.user,
        lida=False
    ).order_by('-created_at')[:5]

    notificacoes_data = []
    for notif in notificacoes_recentes:
        notificacoes_data.append({
            'id': notif.id,
            'titulo': notif.titulo,
            'mensagem': notif.mensagem,
            'tipo': notif.tipo,
            'url_acao': notif.url_acao,
            'created_at': notif.created_at.strftime('%d/%m/%Y %H:%M')
        })

    return JsonResponse({
        'count': count,
        'notificacoes': notificacoes_data
    })
