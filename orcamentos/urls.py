from django.urls import path
from . import views
from . import produtos_views
from . import acompte_views
from . import notificacao_views
from . import views_faturas
from . import views_uploader
from . import views_via_publica
from . import views_projetos
from . import views_solicitacoes
from . import views_orfao
from . import views_busca_ajax
from . import notification_views  # Added: HTML notifications views

app_name = 'orcamentos'

urlpatterns = [
    # ============ URLs PÚBLICAS (SEM LOGIN) ============
    path('solicitar/', views_via_publica.solicitar_orcamento_publico, name='solicitar_publico'),
    path('sucesso/<str:numero>/', views_via_publica.sucesso_solicitacao, name='sucesso_solicitacao'),
    path('publico/<uuid:uuid>/', views_via_publica.orcamento_publico_detail, name='orcamento_publico_detail'),
    path('publico/<uuid:uuid>/aceitar/', views_via_publica.orcamento_publico_aceitar, name='orcamento_publico_aceitar'),
    path('publico/<uuid:uuid>/recusar/', views_via_publica.orcamento_publico_recusar, name='orcamento_publico_recusar'),
    # Novo endpoint público para PDF
    path('publico/<uuid:uuid>/pdf/', views_via_publica.orcamento_publico_pdf, name='orcamento_publico_pdf'),

    # ============ URLs PARA CLIENTES ============
    path('projets/', views_projetos.cliente_projetos, name='cliente_projetos'),
    path('projets/nouveau/', views_projetos.cliente_criar_projeto, name='cliente_criar_projeto'),
    path('projets/<uuid:uuid>/', views_projetos.cliente_projeto_detail, name='cliente_projeto_detail'),
    path('projets/<uuid:uuid>/editer/', views_projetos.cliente_editar_projeto, name='cliente_editar_projeto'),
    path('projets/<uuid:uuid>/supprimer/', views_projetos.cliente_excluir_projeto, name='cliente_excluir_projeto'),
    path('projets/<uuid:uuid>/solicitar-orcamento/', views_projetos.cliente_solicitar_orcamento_projeto, name='cliente_solicitar_orcamento'),

    # URLs AJAX para clientes
    path('projets/<uuid:uuid>/upload-anexo/', views_uploader.upload_anexo_projeto, name='upload_anexo_projeto'),
    path('projets/<uuid:uuid>/anexos/<int:anexo_id>/delete/', views_uploader.excluir_anexo_projeto, name='excluir_anexo_projeto'),

    # ============ URLs ADMINISTRATIVAS ============
    path('admin/dashboard/', views_solicitacoes.admin_dashboard, name='admin_dashboard'),
    path('admin/solicitacoes/', views_solicitacoes.admin_solicitacoes, name='admin_solicitacoes'),
    path('admin/solicitacoes/<str:numero>/', views_solicitacoes.admin_solicitacao_detail, name='admin_solicitacao_detail'),
    path('admin/solicitacoes/<str:numero>/criar-orcamento/', views_solicitacoes.admin_elaborar_orcamento, name='admin_criar_orcamento'),

    # URLs para elaboração de orçamentos
    path('admin/elaborar/<str:numero>/', views_solicitacoes.admin_elaborar_orcamento, name='admin_elaborar_orcamento'),
    path('admin/clientes/<int:cliente_id>/criar-orcamento/', views.admin_criar_orcamento_cliente, name='admin_criar_orcamento_cliente'),

    # URLs para gestão de orçamentos órfãos
    path('admin/orcamentos-orfaos/', views_orfao.admin_orcamentos_orfaos, name='admin_orcamentos_orfaos'),
    path('admin/vincular-orcamentos-orfaos/', views_orfao.admin_vincular_orcamentos_orfaos, name='admin_vincular_orcamentos_orfaos'),

    # ============ URLs ADMINISTRATIVAS DE PROJETOS ============
    path('admin/projetos/', views_projetos.admin_projetos_list, name='admin_projetos_list'),
    path('admin/projetos/<uuid:uuid>/', views_projetos.admin_projeto_detail, name='admin_projeto_detail'),
    path('admin/projetos/<uuid:uuid>/change-status/', views_projetos.admin_projeto_change_status, name='admin_projeto_change_status'),
    path('admin/projetos/<uuid:uuid>/criar-orcamento/', views_projetos.admin_criar_orcamento_projeto, name='admin_criar_orcamento_projeto'),

    # ============ URLs PARA PRODUTOS ============
    path('admin/produtos/', produtos_views.lista_produtos, name='lista_produtos'),
    path('admin/produtos/criar/', produtos_views.criar_produto, name='criar_produto'),
    path('admin/produtos/<int:produto_id>/editar/', produtos_views.editar_produto, name='editar_produto'),
    path('admin/produtos/<int:produto_id>/excluir/', produtos_views.excluir_produto, name='excluir_produto'),

    # ============ URLs PARA FORNECEDORES ============
    path('admin/fornecedores/', produtos_views.lista_fornecedores, name='lista_fornecedores'),
    path('admin/fornecedores/criar/', produtos_views.criar_fornecedor, name='criar_fornecedor'),
    path('admin/fornecedores/<int:fornecedor_id>/editar/', produtos_views.editar_fornecedor, name='editar_fornecedor'),
	
	# URLs para orçamentos dos clientes
    path('mes-devis/', views.cliente_orcamentos, name='cliente_orcamentos'),
    path('devis/<str:numero>/', views.cliente_devis_detail, name='cliente_devis_detail'),
    path('devis/<str:numero>/accepter/', views.cliente_devis_accepter, name='cliente_aceitar_orcamento'),
    path('devis/<str:numero>/refuser/', views.cliente_devis_refuser, name='cliente_recusar_orcamento'),
    path('devis/<str:numero>/pdf/', views.cliente_devis_pdf, name='cliente_devis_pdf'),
	
	# URLs para gestão de orçamentos
	path('admin/orcamentos/', views.admin_orcamentos, name='admin_orcamentos'),
	path('admin/orcamentos/<str:numero>/', views.admin_orcamento_detail, name='admin_orcamento_detail'),
	path('admin/orcamentos/<str:numero>/editar/', views.admin_editar_orcamento, name='admin_editar_orcamento'),
	path('admin/orcamentos/<str:numero>/enviar/', views.admin_enviar_orcamento, name='admin_enviar_orcamento'),
	path('admin/orcamentos/<str:numero>/pdf/', views.admin_orcamento_pdf, name='admin_orcamento_pdf'),
	path('admin/orcamentos/<str:numero>/pdf-html/', views.admin_orcamento_pdf_html, name='admin_orcamento_pdf_html'),
	
	# ============ URLs PARA ACOMPTES ============
	
	path('admin/orcamentos/<str:numero>/acomptes/', views.admin_orcamento_acomptes, name='admin_orcamento_acomptes'),
	path('admin/orcamentos/<str:numero>/acomptes/criar/', views.admin_criar_acompte, name='admin_criar_acompte'),
	path('admin/acomptes/<int:acompte_id>/editar/', views.admin_editar_acompte, name='admin_editar_acompte'),
	path('admin/acomptes/<int:acompte_id>/marcar-pago/', acompte_views.admin_marcar_acompte_pago,
	     name='admin_marcar_acompte_pago'),
	path('admin/acomptes/<int:acompte_id>/gerar-fatura/', views.admin_gerar_fatura_acompte,
	     name='admin_gerar_fatura_acompte'),
	path('admin/acomptes/<int:acompte_id>/deletar/', views.admin_deletar_acompte, name='admin_deletar_acompte'),
	
	# URLs para faturas dos clientes
    path('mes-factures/', views_faturas.cliente_faturas, name='cliente_faturas'),
    path('factures/<str:numero>/', views_faturas.cliente_fatura_detail, name='cliente_fatura_detail'),
    path('factures/<str:numero>/pdf/', views_faturas.cliente_fatura_pdf, name='cliente_fatura_pdf'),

    # ============ URLs PARA FATURAS ============
    path('admin/faturas/', views_faturas.admin_faturas_list, name='admin_faturas_list'),
    path('admin/faturas/nova/', views_faturas.admin_criar_fatura, name='admin_criar_fatura'),
    path('admin/faturas/nova/orcamento/<str:orcamento_numero>/', views_faturas.admin_criar_fatura_from_orcamento, name='admin_criar_fatura_from_orcamento'),
    path('admin/faturas/<str:numero>/', views_faturas.admin_fatura_detail, name='admin_fatura_detail'),
    path('admin/faturas/<str:numero>/editar/', views_faturas.admin_editar_fatura, name='admin_editar_fatura'),
    path('admin/faturas/<str:numero>/deletar/', views_faturas.admin_deletar_fatura, name='admin_deletar_fatura'),
    path('admin/faturas/<str:numero>/marcar-paga/', views_faturas.admin_marcar_fatura_paga, name='admin_marcar_fatura_paga'),
    path('admin/faturas/<str:numero>/pdf/', views_faturas.admin_fatura_pdf, name='admin_fatura_pdf'),

    # ============ URLs AJAX ============
    path('ajax/buscar-clientes/', views_busca_ajax.buscar_clientes_ajax, name='buscar_clientes_ajax'),
    path('ajax/buscar-produtos/', views_busca_ajax.buscar_produtos_ajax, name='buscar_produtos_ajax'),
    path('ajax/orcamento-items/<str:numero>/', views_busca_ajax.ajax_orcamento_items, name='ajax_orcamento_items'),

    # ============ URLs DE NOTIFICAÇÕES (API) ============
    path('api/notifications/', notificacao_views.get_user_notifications, name='get_user_notifications'),
    path('api/notifications/<int:notification_id>/read/', notificacao_views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/mark-all-read/', notificacao_views.mark_all_notifications_read, name='mark_all_notifications_read'),

    # ============ URLs DE NOTIFICAÇÕES (HTML) ============
    path('notifications/', notification_views.listar_notificacoes, name='notifications_list'),
    path('notifications/<int:notificacao_id>/read/', notification_views.marcar_notificacao_lida, name='notification_mark_read'),
    path('notifications/mark-all-read/', notification_views.marcar_todas_lidas, name='notifications_mark_all_read'),

    # ============ AGENDAMENTOS (RENDEZ-VOUS) ============
    path('devis/<str:numero>/agendar/', views.cliente_devis_agendar, name='cliente_devis_agendar'),
    path('admin/agendamentos/<int:agendamento_id>/confirmar/', views.admin_confirmar_agendamento, name='admin_confirmar_agendamento'),
    path('admin/agendamentos/<int:agendamento_id>/recusar/', views.admin_recusar_agendamento, name='admin_recusar_agendamento'),
]
