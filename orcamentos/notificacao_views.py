# ============ SISTEMA DE NOTIFICAÇÕES ============
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone


@login_required
def get_user_notifications(request):
	"""API endpoint para buscar notificações do usuário"""
	from .models import Notificacao
	
	# Buscar notificações não lidas do usuário
	notificacoes = Notificacao.objects.filter(
		usuario=request.user,
		lida=False
	).order_by('-created_at')[:10]
	
	# Contar total de não lidas
	total_nao_lidas = Notificacao.objects.filter(
		usuario=request.user,
		lida=False
	).count()
	
	# Preparar dados para JSON
	notifications_data = []
	for notif in notificacoes:
		notifications_data.append({
			'id': notif.id,
			'tipo': notif.tipo,
			'titulo': notif.titulo,
			'mensagem': notif.mensagem,
			'url_acao': notif.url_acao or '#',
			'created_at': notif.created_at.strftime('%d/%m/%Y %H:%M'),
			'icon': get_notification_icon(notif.tipo)
		})
	
	return JsonResponse({
		'notifications': notifications_data,
		'total_unread': total_nao_lidas
	})


@login_required
def mark_notification_read(request, notification_id):
	"""Marcar notificação como lida"""
	from .models import Notificacao
	
	if request.method == 'POST':
		try:
			notificacao = Notificacao.objects.get(
				id=notification_id,
				usuario=request.user
			)
			notificacao.lida = True
			notificacao.read_at = timezone.now()
			notificacao.save()
			
			return JsonResponse({'success': True})
		except Notificacao.DoesNotExist:
			return JsonResponse({'success': False, 'error': 'Notification not found'})
	
	return JsonResponse({'success': False, 'error': 'Method not allowed'})


@login_required
def mark_all_notifications_read(request):
	"""Marcar todas as notificações como lidas"""
	from .models import Notificacao
	
	if request.method == 'POST':
		Notificacao.objects.filter(
			usuario=request.user,
			lida=False
		).update(
			lida=True,
			read_at=timezone.now()
		)
		
		return JsonResponse({'success': True})
	
	return JsonResponse({'success': False, 'error': 'Method not allowed'})


def get_notification_icon(tipo):
	"""Retorna o ícone apropriado para cada tipo de notificação"""
	icons = {
		'nova_solicitacao': 'fas fa-plus-circle text-blue-500',
		'orcamento_elaborado': 'fas fa-file-invoice-dollar text-green-500',
		'orcamento_enviado': 'fas fa-paper-plane text-blue-500',
		'orcamento_aceito': 'fas fa-check-circle text-green-500',
		'orcamento_recusado': 'fas fa-times-circle text-red-500',
		'projeto_criado': 'fas fa-project-diagram text-purple-500',
	}
	return icons.get(tipo, 'fas fa-bell text-gray-500')