# ============ VIEWS AJAX ============
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from orcamentos.models import Orcamento


@staff_member_required
def buscar_clientes_ajax(request):
	"""Busca clientes via AJAX para uso nas faturas"""
	from django.contrib.auth import get_user_model
	User = get_user_model()
	
	query = request.GET.get('q', '')
	
	if len(query) < 2:
		return JsonResponse({'clientes': []})
	
	clientes = User.objects.filter(
		is_active=True,
		is_staff=False
	).filter(
		Q(first_name__icontains=query) |
		Q(last_name__icontains=query) |
		Q(email__icontains=query) |
		Q(username__icontains=query)
	)[:10]
	
	clientes_data = []
	for cliente in clientes:
		nome_completo = f"{cliente.first_name} {cliente.last_name}".strip()
		if not nome_completo:
			nome_completo = cliente.username
		
		clientes_data.append({
			'id': cliente.id,
			'nome_completo': nome_completo,
			'email': cliente.email,
			'username': cliente.username,
			'first_name': cliente.first_name,
			'last_name': cliente.last_name
		})
	
	return JsonResponse({'clientes': clientes_data})


@staff_member_required
def buscar_produtos_ajax(request):
	"""Busca produtos via AJAX para uso nos orçamentos"""
	query = request.GET.get('q', '')
	
	if len(query) < 2:
		return JsonResponse({'produtos': []})
	
	try:
		from .models import Produto
		produtos = Produto.objects.filter(
			ativo=True
		).filter(
			Q(referencia__icontains=query) |
			Q(descricao__icontains=query)
		)[:10]
		
		produtos_data = []
		for produto in produtos:
			produtos_data.append({
				'id': produto.id,
				'referencia': produto.referencia,
				'nome': produto.descricao,
				'descricao': produto.descricao,
				'preco_venda': float(produto.preco_venda_ttc),  # Preço TTC (COM IVA) - preço final para o cliente
				'preco_venda_ht': float(produto.preco_venda_ht),  # Preço HT (para referência)
				'preco_venda_ttc': float(produto.preco_venda_ttc),  # Preço TTC (preço final)
				'preco_compra_ht': float(produto.preco_compra),
				'unidade': produto.unidade,
				'taxa_tva': produto.taxa_tva,  # Taxa de IVA do produto
				'atividade': getattr(produto, 'atividade', 'marchandise'),  # Adicionar atividade
				'categoria': '',
				'fornecedor': produto.fornecedor.nome if produto.fornecedor else ''
			})
		
		return JsonResponse({'produtos': produtos_data})
	
	except Exception as e:
		import logging
		logger = logging.getLogger(__name__)
		logger.error(f"Erro na busca de produtos: {str(e)}")
		return JsonResponse({'produtos': [], 'error': str(e)})


@staff_member_required
def ajax_orcamento_items(request, numero):
	"""Retorna os itens de um orçamento via AJAX para edição"""
	try:
		orcamento = get_object_or_404(Orcamento, numero=numero)
		
		items = []
		for item in orcamento.itens.all():
			items.append({
				'referencia': item.referencia or '',
				'descricao': item.descricao,
				'unidade': item.unidade,
				'atividade': item.atividade,
				'quantidade': float(item.quantidade),
				'preco_unitario_ht': float(item.preco_unitario_ht),
				'remise_percentual': float(item.remise_percentual),
				'taxa_tva': item.taxa_tva,
			})
		
		return JsonResponse({
			'success': True,
			'items': items,
			'count': len(items)
		})
	
	except Exception as e:
		return JsonResponse({
			'success': False,
			'error': str(e),
			'items': []
		})