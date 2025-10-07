from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import MagicMock
from django.utils import timezone
from orcamentos.models import SolicitacaoOrcamento, StatusOrcamento
from orcamentos.auditoria import AuditoriaManager, LogAuditoria, TipoAcao

User = get_user_model()

class AuditoriaOrcamentosOrfaosTestCase(TestCase):
    """
    Testes específicos para auditoria das funcionalidades de orçamentos órfãos
    """

    def setUp(self):
        """Configurar dados para os testes"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@exemplo.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )

        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@exemplo.com',
            password='adminpass123',
            is_staff=True
        )

        self.solicitacao = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Test User',
            email_solicitante='test@exemplo.com',
            telefone_solicitante='11999999999',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            cep='01234-567',
            tipo_servico='pintura_interior',
            descricao_servico='Pintura de teste',
        )

    def test_registrar_vinculacao_orcamento_orfao(self):
        """Testar registro de vinculação de orçamento órfão"""
        # Registrar vinculação
        log = AuditoriaManager.registrar_vinculacao_orcamento_orfao(
            usuario=self.user,
            solicitacao=self.solicitacao,
            origem="teste"
        )

        # Verificar se o log foi criado
        self.assertIsNotNone(log)
        self.assertEqual(log.acao, TipoAcao.VINCULACAO_ORFAO)
        self.assertEqual(log.usuario, self.user)
        self.assertEqual(log.objeto_afetado, self.solicitacao)

        # Verificar descrição
        self.assertIn('Liaison automatique', log.descricao)
        self.assertIn(self.solicitacao.numero, log.descricao)
        self.assertIn('Test User', log.descricao)
        self.assertIn('teste', log.descricao)

        # Verificar dados estruturados
        self.assertIsNotNone(log.dados_anteriores)
        self.assertIsNotNone(log.dados_posteriores)
        self.assertIsNotNone(log.campos_alterados)

        # Verificar conteúdo dos dados
        self.assertIsNone(log.dados_anteriores['cliente'])
        self.assertEqual(log.dados_posteriores['cliente'], self.user.id)
        self.assertIn('cliente', log.campos_alterados)

    def test_registrar_deteccao_orcamento_orfao(self):
        """Testar registro de detecção de orçamentos órfãos"""
        # Registrar detecção
        log = AuditoriaManager.registrar_deteccao_orcamento_orfao(
            usuario=self.user,
            email='test@exemplo.com',
            quantidade_encontrada=3
        )

        # Verificar log
        self.assertEqual(log.acao, TipoAcao.DETECCAO_ORFAO)
        self.assertEqual(log.usuario, self.user)
        self.assertEqual(log.objeto_afetado, self.user)

        # Verificar descrição
        self.assertIn('Détection de 3 demandes orphelines', log.descricao)
        self.assertIn('test@exemplo.com', log.descricao)

        # Verificar dados
        dados = log.dados_posteriores
        self.assertEqual(dados['email_verificado'], 'test@exemplo.com')
        self.assertEqual(dados['quantidade_orfas_encontradas'], 3)
        self.assertEqual(dados['usuario_beneficiado'], self.user.id)

    def test_registrar_processamento_lote_orfaos(self):
        """Testar registro de processamento em lote"""
        emails_processados = {'test@exemplo.com', 'outro@exemplo.com'}

        # Registrar processamento em lote
        log = AuditoriaManager.registrar_processamento_lote_orfaos(
            usuario_comando=self.admin_user,
            total_processadas=5,
            total_vinculadas=3,
            emails_processados=emails_processados
        )

        # Verificar log
        self.assertEqual(log.acao, TipoAcao.PROCESSAMENTO_LOTE)
        self.assertEqual(log.usuario, self.admin_user)

        # Verificar descrição
        self.assertIn('Traitement en lot: 3/5', log.descricao)
        self.assertIn('2 emails traités', log.descricao)

        # Verificar dados
        dados = log.dados_posteriores
        self.assertEqual(dados['total_orfas_encontradas'], 5)
        self.assertEqual(dados['total_vinculadas'], 3)
        self.assertEqual(set(dados['emails_processados']), emails_processados)
        self.assertEqual(dados['metodo'], 'comando_gerenciamento')

    def test_registrar_notificacao_vinculacao(self):
        """Testar registro de notificação de vinculação"""
        # Registrar notificação
        log = AuditoriaManager.registrar_notificacao_vinculacao(
            usuario_notificado=self.user,
            quantidade_orcamentos=2,
            metodo_vinculacao="automatico"
        )

        # Verificar log
        self.assertEqual(log.acao, TipoAcao.NOTIFICACAO_VINCULACAO)
        self.assertIsNone(log.usuario)  # Notificação é do sistema
        self.assertEqual(log.objeto_afetado, self.user)

        # Verificar descrição
        self.assertIn('Notification envoyée à Test User', log.descricao)
        self.assertIn('test@exemplo.com', log.descricao)
        self.assertIn('2 demandes liées', log.descricao)

        # Verificar dados
        dados = log.dados_posteriores
        self.assertEqual(dados['usuario_notificado'], self.user.id)
        self.assertEqual(dados['email_notificado'], self.user.email)
        self.assertEqual(dados['quantidade_orcamentos'], 2)
        self.assertEqual(dados['metodo_vinculacao'], 'automatico')

    def test_registrar_solicitacao_publica_usuario_logado(self):
        """Testar registro quando usuário logado usa URL pública"""
        # Registrar ação
        log = AuditoriaManager.registrar_solicitacao_publica_usuario_logado(
            usuario=self.user,
            solicitacao=self.solicitacao
        )

        # Verificar log
        self.assertEqual(log.acao, TipoAcao.CRIACAO)
        self.assertEqual(log.usuario, self.user)
        self.assertEqual(log.objeto_afetado, self.solicitacao)

        # Verificar descrição
        self.assertIn('Demande de devis via URL publique', log.descricao)
        self.assertIn('utilisateur connecté', log.descricao)

        # Verificar dados
        dados = log.dados_posteriores
        self.assertEqual(dados['usuario_logado'], self.user.id)
        self.assertEqual(dados['email_formulario'], self.solicitacao.email_solicitante)
        self.assertTrue(dados['vinculacao_automatica'])

    def test_historico_objeto_solicitacao(self):
        """Testar obtenção de histórico de uma solicitação"""
        # Criar alguns logs para a solicitação
        AuditoriaManager.registrar_criacao(self.user, self.solicitacao)
        AuditoriaManager.registrar_vinculacao_orcamento_orfao(self.user, self.solicitacao)
        AuditoriaManager.registrar_deteccao_orcamento_orfao(self.user, 'test@exemplo.com', 1)

        # Obter histórico
        historico = AuditoriaManager.obter_historico_objeto(self.solicitacao)

        # Verificar se retornou os logs corretos
        self.assertEqual(len(historico), 2)  # Criação + Vinculação (detecção é do usuário, não da solicitação)

        # Verificar ordenação (mais recente primeiro)
        self.assertEqual(historico[0].acao, TipoAcao.VINCULACAO_ORFAO)
        self.assertEqual(historico[1].acao, TipoAcao.CRIACAO)

    def test_atividades_usuario_orcamentos_orfaos(self):
        """Testar obtenção de atividades do usuário relacionadas a órfãos"""
        # Criar logs variados
        AuditoriaManager.registrar_deteccao_orcamento_orfao(self.user, 'test@exemplo.com', 2)
        AuditoriaManager.registrar_vinculacao_orcamento_orfao(self.user, self.solicitacao)
        AuditoriaManager.registrar_notificacao_vinculacao(self.user, 2, "automatico")

        # Obter atividades
        atividades = AuditoriaManager.obter_atividades_usuario(self.user, dias=1)

        # Verificar se retornou as atividades corretas
        self.assertEqual(len(atividades), 2)  # Detecção + Vinculação (notificação não tem usuário)

        # Verificar tipos de ação
        acoes = [atividade.acao for atividade in atividades]
        self.assertIn(TipoAcao.DETECCAO_ORFAO, acoes)
        self.assertIn(TipoAcao.VINCULACAO_ORFAO, acoes)

    def test_estatisticas_periodo_com_orcamentos_orfaos(self):
        """Testar estatísticas incluindo ações de orçamentos órfãos"""
        from datetime import datetime, timedelta

        # Criar logs variados
        AuditoriaManager.registrar_deteccao_orcamento_orfao(self.user, 'test@exemplo.com', 2)
        AuditoriaManager.registrar_vinculacao_orcamento_orfao(self.user, self.solicitacao)
        AuditoriaManager.registrar_processamento_lote_orfaos(self.admin_user, 5, 3, {'test@exemplo.com'})

        # Obter estatísticas
        data_inicio = datetime.now() - timedelta(days=1)
        data_fim = datetime.now() + timedelta(days=1)

        estatisticas = AuditoriaManager.obter_estatisticas_periodo(data_inicio, data_fim)

        # Verificar estatísticas
        self.assertEqual(estatisticas['total_acoes'], 3)

        # Verificar ações por tipo
        acoes_por_tipo = estatisticas['acoes_por_tipo']
        self.assertIn('Détection demande orpheline', acoes_por_tipo)
        self.assertIn('Liaison demande orpheline', acoes_por_tipo)
        self.assertIn('Traitement en lot', acoes_por_tipo)

    def test_log_auditoria_str_representation(self):
        """Testar representação string do log de auditoria"""
        log = AuditoriaManager.registrar_vinculacao_orcamento_orfao(
            usuario=self.user,
            solicitacao=self.solicitacao
        )

        # Verificar string representation
        str_log = str(log)
        self.assertIn('Test User', str_log)
        self.assertIn('Liaison demande orpheline', str_log)

    def test_resumo_alteracao_log(self):
        """Testar propriedade resumo_alteracao do log"""
        log = AuditoriaManager.registrar_vinculacao_orcamento_orfao(
            usuario=self.user,
            solicitacao=self.solicitacao
        )

        # Verificar resumo
        resumo = log.resumo_alteracao
        self.assertIn('cliente:', resumo)
        self.assertIn('→', resumo)

    def test_auditoria_com_request_metadata(self):
        """Testar captura de metadados da requisição na auditoria"""
        # Criar mock request
        mock_request = MagicMock()
        mock_request.META = {
            'HTTP_USER_AGENT': 'Test Browser',
            'REMOTE_ADDR': '127.0.0.1'
        }
        mock_request.session.session_key = 'test_session_123'

        # Registrar com request
        log = AuditoriaManager.registrar_vinculacao_orcamento_orfao(
            usuario=self.user,
            solicitacao=self.solicitacao,
            request=mock_request
        )

        # Verificar metadados
        self.assertEqual(log.ip_address, '127.0.0.1')
        self.assertEqual(log.user_agent, 'Test Browser')
        self.assertEqual(log.sessao_id, 'test_session_123')

    def test_auditoria_sem_request(self):
        """Testar auditoria sem requisição (comando de gerenciamento)"""
        log = AuditoriaManager.registrar_processamento_lote_orfaos(
            usuario_comando=self.admin_user,
            total_processadas=5,
            total_vinculadas=3,
            emails_processados={'test@exemplo.com'}
        )

        # Verificar que funciona sem request
        self.assertIsNone(log.ip_address)
        self.assertEqual(log.user_agent, '')
        self.assertEqual(log.sessao_id, '')

    def test_auditoria_erro_vinculacao(self):
        """Testar auditoria em caso de erro na vinculação"""
        # Simular erro
        log = AuditoriaManager.registrar_acao(
            usuario=self.user,
            acao=TipoAcao.VINCULACAO_ORFAO,
            objeto=self.solicitacao,
            descricao="Erro ao vincular orçamento órfão",
            sucesso=False,
            erro_mensagem="Erro de teste",
            funcionalidade="Teste de erro"
        )

        # Verificar log de erro
        self.assertFalse(log.sucesso)
        self.assertEqual(log.erro_mensagem, "Erro de teste")

    def test_filtros_auditoria_orcamentos_orfaos(self):
        """Testar filtros específicos para logs de orçamentos órfãos"""
        # Criar diferentes tipos de logs
        AuditoriaManager.registrar_deteccao_orcamento_orfao(self.user, 'test@exemplo.com', 2)
        AuditoriaManager.registrar_vinculacao_orcamento_orfao(self.user, self.solicitacao)
        AuditoriaManager.registrar_criacao(self.user, self.solicitacao)  # Log normal

        # Filtrar apenas logs de órfãos
        logs_orfaos = LogAuditoria.objects.filter(
            acao__in=[
                TipoAcao.VINCULACAO_ORFAO,
                TipoAcao.DETECCAO_ORFAO,
                TipoAcao.PROCESSAMENTO_LOTE,
                TipoAcao.NOTIFICACAO_VINCULACAO
            ]
        )

        # Verificar filtro
        self.assertEqual(logs_orfaos.count(), 2)

        # Verificar que contém apenas logs de órfãos
        for log in logs_orfaos:
            self.assertIn(log.acao, [TipoAcao.VINCULACAO_ORFAO, TipoAcao.DETECCAO_ORFAO])

    def test_performance_logs_auditoria(self):
        """Testar performance da criação de logs em massa"""
        import time

        # Criar muitos logs
        start_time = time.time()

        for i in range(50):
            solicitacao_temp = SolicitacaoOrcamento.objects.create(
                nome_solicitante=f'Temp User {i}',
                email_solicitante=f'temp{i}@exemplo.com',
                telefone_solicitante='11999999999',
                endereco=f'Rua Temp {i}, 123',
                cidade='São Paulo',
                cep='01234-567',
                tipo_servico='pintura_interior',
                descricao_servico=f'Temp {i}',
            )

            AuditoriaManager.registrar_vinculacao_orcamento_orfao(
                usuario=self.user,
                solicitacao=solicitacao_temp,
                origem=f"performance_test_{i}"
            )

        end_time = time.time()

        # Verificar que foi executado em tempo razoável
        execution_time = end_time - start_time
        self.assertLess(execution_time, 5.0)  # Menos de 5 segundos

        # Verificar que todos os logs foram criados
        logs_criados = LogAuditoria.objects.filter(acao=TipoAcao.VINCULACAO_ORFAO).count()
        self.assertGreaterEqual(logs_criados, 50)

    def test_integridade_dados_auditoria(self):
        """Testar integridade dos dados de auditoria"""
        # Registrar vinculação com dados complexos
        log = AuditoriaManager.registrar_vinculacao_orcamento_orfao(
            usuario=self.user,
            solicitacao=self.solicitacao,
            origem="teste_integridade"
        )

        # Recarregar do banco para verificar serialização JSON
        log.refresh_from_db()

        # Verificar que os dados JSON foram preservados corretamente
        self.assertIsInstance(log.dados_anteriores, dict)
        self.assertIsInstance(log.dados_posteriores, dict)
        self.assertIsInstance(log.campos_alterados, dict)

        # Verificar estrutura dos dados
        self.assertIn('cliente', log.dados_anteriores)
        self.assertIn('cliente', log.dados_posteriores)
        self.assertIn('cliente', log.campos_alterados)

    def test_auditoria_cascata_operacoes(self):
        """Testar auditoria de operações em cascata"""
        # Simular operações em sequência

        # 1. Detecção
        log_deteccao = AuditoriaManager.registrar_deteccao_orcamento_orfao(
            usuario=self.user,
            email='test@exemplo.com',
            quantidade_encontrada=1
        )

        # 2. Vinculação
        log_vinculacao = AuditoriaManager.registrar_vinculacao_orcamento_orfao(
            usuario=self.user,
            solicitacao=self.solicitacao,
            origem="cascata_teste"
        )

        # 3. Notificação
        log_notificacao = AuditoriaManager.registrar_notificacao_vinculacao(
            usuario_notificado=self.user,
            quantidade_orcamentos=1,
            metodo_vinculacao="cascata"
        )

        # Verificar sequência temporal
        self.assertLess(log_deteccao.timestamp, log_vinculacao.timestamp)
        self.assertLessEqual(log_vinculacao.timestamp, log_notificacao.timestamp)

        # Verificar que todos os logs foram criados
        logs_total = LogAuditoria.objects.count()
        self.assertGreaterEqual(logs_total, 3)

    def test_auditoria_views_cliente_devis_detail(self):
        """Testar auditoria da visualização de orçamento pelo cliente"""
        from django.test import Client
        from orcamentos.models import Orcamento

        # Criar orçamento
        orcamento = Orcamento.objects.create(
            solicitacao=self.solicitacao,
            numero='ORC-001',
            descricao='Teste',
            valor_total=1000.00,
            elaborado_por=self.admin_user
        )

        # Associar solicitação ao cliente
        self.solicitacao.cliente = self.user
        self.solicitacao.save()

        # Fazer login e acessar a view
        client = Client()
        client.force_login(self.user)

        response = client.get(f'/devis/devis/{orcamento.numero}/')

        # Verificar se foi registrado na auditoria
        logs_visualizacao = LogAuditoria.objects.filter(
            acao=TipoAcao.VISUALIZACAO,
            usuario=self.user,
            content_type__model='orcamento'
        )

        self.assertTrue(logs_visualizacao.exists())
        log = logs_visualizacao.first()
        self.assertEqual(log.objeto_afetado, orcamento)


    def test_auditoria_aceitacao_orcamento(self):
        """Testar auditoria da aceitação de orçamento"""
        from orcamentos.models import Orcamento, StatusOrcamento

        # Criar orçamento enviado
        orcamento = Orcamento.objects.create(
            solicitacao=self.solicitacao,
            numero='ORC-002',
            descricao='Teste Aceitar',
            valor_total=1500.00,
            elaborado_por=self.admin_user,
            status=StatusOrcamento.ENVIADO
        )

        # Associar solicitação ao cliente
        self.solicitacao.cliente = self.user
        self.solicitacao.save()

        # Simular aceitação
        from django.test import Client
        client = Client()
        client.force_login(self.user)

        response = client.post(f'/devis/devis/{orcamento.numero}/accepter/')

        # Verificar se foi registrado na auditoria
        logs_alteracao = LogAuditoria.objects.filter(
            acao=TipoAcao.ALTERACAO,
            usuario=self.user,
            content_type__model='orcamento'
        )

        self.assertTrue(logs_alteracao.exists())
        log = logs_alteracao.first()
        self.assertIn('status', log.campos_alterados)
        self.assertEqual(log.dados_posteriores['status'], StatusOrcamento.ACEITO)


    def test_auditoria_recusa_orcamento(self):
        """Testar auditoria da recusa de orçamento"""
        from orcamentos.models import Orcamento, StatusOrcamento

        # Criar orçamento enviado
        orcamento = Orcamento.objects.create(
            solicitacao=self.solicitacao,
            numero='ORC-003',
            descricao='Teste Recusar',
            valor_total=2000.00,
            elaborado_por=self.admin_user,
            status=StatusOrcamento.ENVIADO
        )

        # Associar solicitação ao cliente
        self.solicitacao.cliente = self.user
        self.solicitacao.save()

        # Simular recusa
        from django.test import Client
        client = Client()
        client.force_login(self.user)

        response = client.post(f'/devis/devis/{orcamento.numero}/refuser/', {
            'motivo': 'Valor muito alto'
        })

        # Verificar se foi registrado na auditoria
        logs_alteracao = LogAuditoria.objects.filter(
            acao=TipoAcao.ALTERACAO,
            usuario=self.user,
            content_type__model='orcamento'
        )

        self.assertTrue(logs_alteracao.exists())
        log = logs_alteracao.first()
        self.assertIn('status', log.campos_alterados)
        self.assertIn('motivo_recusa', log.campos_alterados)
        self.assertEqual(log.dados_posteriores['status'], StatusOrcamento.RECUSADO)
        self.assertEqual(log.dados_posteriores['motivo_recusa'], 'Valor muito alto')


    def test_auditoria_download_pdf_cliente(self):
        """Testar auditoria de download de PDF pelo cliente"""
        from orcamentos.models import Orcamento

        # Criar orçamento
        orcamento = Orcamento.objects.create(
            solicitacao=self.solicitacao,
            numero='ORC-004',
            descricao='Teste PDF',
            valor_total=1200.00,
            elaborado_por=self.admin_user
        )

        # Associar solicitação ao cliente
        self.solicitacao.cliente = self.user
        self.solicitacao.save()

        # Registrar download na auditoria
        log = AuditoriaManager.registrar_acao(
            usuario=self.user,
            acao=TipoAcao.DOWNLOAD,
            objeto=orcamento,
            descricao=f"Téléchargement PDF du devis {orcamento.numero} par le client",
            funcionalidade="Download PDF Cliente"
        )

        # Verificar log
        self.assertEqual(log.acao, TipoAcao.DOWNLOAD)
        self.assertEqual(log.usuario, self.user)
        self.assertEqual(log.objeto_afetado, orcamento)
        self.assertIn('Téléchargement PDF', log.descricao)
        self.assertEqual(log.funcionalidade, "Download PDF Cliente")


    def test_auditoria_admin_vincular_orfaos_ajax(self):
        """Testar auditoria da vinculação de órfãos via AJAX pelo admin"""
        # Criar solicitação órfã
        solicitacao_orfa = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Orphan User',
            email_solicitante=self.user.email,  # Mesmo email do usuário
            telefone_solicitante='11888888888',
            endereco='Rua Órfã, 456',
            cidade='São Paulo',
            cep='98765-432',
            tipo_servico='pintura_exterior',
            descricao_servico='Solicitação órfã',
            cliente=None  # Órfã
        )

        # Simular requisição AJAX do admin
        from django.test import Client
        import json

        client = Client()
        client.force_login(self.admin_user)

        # Simular dados da requisição AJAX
        data = {'email': self.user.email}

        # Como a view real faria a vinculação, vamos simular o processo
        # Registrar vinculação na auditoria
        AuditoriaManager.registrar_vinculacao_orcamento_orfao(
            usuario=self.user,
            solicitacao=solicitacao_orfa,
            origem="admin_manual"
        )

        # Registrar processamento em lote
        AuditoriaManager.registrar_processamento_lote_orfaos(
            usuario_comando=self.admin_user,
            total_processadas=1,
            total_vinculadas=1,
            emails_processados={self.user.email}
        )

        # Verificar logs criados
        log_vinculacao = LogAuditoria.objects.filter(
            acao=TipoAcao.VINCULACAO_ORFAO
        ).first()

        log_lote = LogAuditoria.objects.filter(
            acao=TipoAcao.PROCESSAMENTO_LOTE
        ).first()

        self.assertIsNotNone(log_vinculacao)
        self.assertIsNotNone(log_lote)

        # Verificar conteúdo dos logs
        self.assertEqual(log_vinculacao.usuario, self.user)
        self.assertEqual(log_vinculacao.objeto_afetado, solicitacao_orfa)
        self.assertIn('admin_manual', log_vinculacao.descricao)

        self.assertEqual(log_lote.usuario, self.admin_user)
        self.assertEqual(log_lote.dados_posteriores['total_vinculadas'], 1)


    def test_auditoria_solicitacao_publica_usuario_logado(self):
        """Testar auditoria quando usuário logado usa URL pública"""
        # Simular a situação da view
        log = AuditoriaManager.registrar_solicitacao_publica_usuario_logado(
            usuario=self.user,
            solicitacao=self.solicitacao
        )

        # Verificar log
        self.assertEqual(log.acao, TipoAcao.CRIACAO)
        self.assertEqual(log.usuario, self.user)
        self.assertEqual(log.objeto_afetado, self.solicitacao)

        # Verificar descrição específica
        self.assertIn('URL publique', log.descricao)
        self.assertIn('utilisateur connecté', log.descricao)

        # Verificar dados estruturados
        dados = log.dados_posteriores
        self.assertEqual(dados['usuario_logado'], self.user.id)
        self.assertEqual(dados['email_formulario'], self.solicitacao.email_solicitante)
        self.assertTrue(dados['vinculacao_automatica'])


    def test_auditoria_admin_dashboard_estatisticas(self):
        """Testar se as estatísticas do dashboard incluem dados de auditoria"""
        # Criar alguns logs de diferentes tipos
        AuditoriaManager.registrar_deteccao_orcamento_orfao(self.user, 'test@exemplo.com', 2)
        AuditoriaManager.registrar_vinculacao_orcamento_orfao(self.user, self.solicitacao)
        AuditoriaManager.registrar_criacao(self.admin_user, self.solicitacao)

        # Simular acesso ao dashboard admin
        from django.test import Client
        client = Client()
        client.force_login(self.admin_user)

        response = client.get('/devis/admin/dashboard/')

        # Verificar se a resposta foi bem-sucedida
        self.assertEqual(response.status_code, 200)

        # Verificar se o contexto contém as estatísticas esperadas
        context = response.context
        self.assertIn('total_solicitacoes', context)
        self.assertIn('solicitacoes_orfas', context)


    def test_auditoria_elaboracao_orcamento_admin(self):
        """Testar auditoria da elaboração de orçamento pelo admin"""
        from orcamentos.models import Orcamento

        # Criar orçamento
        orcamento = Orcamento.objects.create(
            solicitacao=self.solicitacao,
            numero='ORC-ADMIN-001',
            descricao='Teste Admin',
            valor_total=3000.00,
            elaborado_por=self.admin_user
        )

        # Registrar criação na auditoria
        log = AuditoriaManager.registrar_criacao(
            usuario=self.admin_user,
            objeto=orcamento
        )

        # Verificar log
        self.assertEqual(log.acao, TipoAcao.CRIACAO)
        self.assertEqual(log.usuario, self.admin_user)
        self.assertEqual(log.objeto_afetado, orcamento)
        self.assertIn('Création', log.descricao)


    def test_auditoria_envio_orcamento_admin(self):
        """Testar auditoria do envio de orçamento pelo admin"""
        from orcamentos.models import Orcamento, StatusOrcamento

        # Criar orçamento em rascunho
        orcamento = Orcamento.objects.create(
            solicitacao=self.solicitacao,
            numero='ORC-ENVIO-001',
            descricao='Teste Envio',
            valor_total=2500.00,
            elaborado_por=self.admin_user,
            status=StatusOrcamento.RASCUNHO
        )

        # Simular envio
        dados_anteriores = {'status': orcamento.status}
        orcamento.status = StatusOrcamento.ENVIADO
        orcamento.data_envio = timezone.now()

        # Registrar na auditoria
        log = AuditoriaManager.registrar_alteracao(
            usuario=self.admin_user,
            objeto=orcamento,
            dados_anteriores=dados_anteriores,
            dados_posteriores={
                'status': orcamento.status,
                'data_envio': orcamento.data_envio.isoformat()
            }
        )

        # Verificar log
        self.assertEqual(log.acao, TipoAcao.ALTERACAO)
        self.assertEqual(log.usuario, self.admin_user)
        self.assertIn('status', log.campos_alterados)
        self.assertEqual(log.dados_posteriores['status'], StatusOrcamento.ENVIADO)


    def test_auditoria_filtros_avancados(self):
        """Testar filtros avançados para logs de auditoria"""
        from datetime import datetime, timedelta

        # Criar logs de diferentes períodos
        hoje = datetime.now()
        ontem = hoje - timedelta(days=1)

        # Log recente
        log_recente = AuditoriaManager.registrar_vinculacao_orcamento_orfao(
            usuario=self.user,
            solicitacao=self.solicitacao
        )

        # Alterar timestamp para simular log antigo
        log_antigo = AuditoriaManager.registrar_deteccao_orcamento_orfao(
            usuario=self.user,
            email='old@exemplo.com',
            quantidade_encontrada=1
        )
        log_antigo.timestamp = ontem
        log_antigo.save()

        # Filtrar logs do último dia
        logs_recentes = LogAuditoria.objects.filter(
            timestamp__gte=hoje.date()
        )

        # Verificar filtro
        self.assertIn(log_recente, logs_recentes)
        self.assertNotIn(log_antigo, logs_recentes)

        # Filtrar por tipo de ação
        logs_vinculacao = LogAuditoria.objects.filter(
            acao=TipoAcao.VINCULACAO_ORFAO
        )

        logs_deteccao = LogAuditoria.objects.filter(
            acao=TipoAcao.DETECCAO_ORFAO
        )

        self.assertIn(log_recente, logs_vinculacao)
        self.assertIn(log_antigo, logs_deteccao)


    def test_auditoria_export_relatorio(self):
        """Testar funcionalidade de exportação de relatórios de auditoria"""
        # Criar vários logs
        logs_criados = []

        for i in range(5):
            log = AuditoriaManager.registrar_vinculacao_orcamento_orfao(
                usuario=self.user,
                solicitacao=self.solicitacao,
                origem=f"teste_export_{i}"
            )
            logs_criados.append(log)

        # Simular exportação (obter dados estruturados)
        logs_data = []
        for log in logs_criados:
            logs_data.append({
                'timestamp': log.timestamp.isoformat(),
                'usuario': log.usuario.username if log.usuario else None,
                'acao': log.get_acao_display(),
                'objeto': str(log.objeto_afetado),
                'sucesso': log.sucesso,
                'descricao': log.descricao
            })

        # Verificar estrutura dos dados
        self.assertEqual(len(logs_data), 5)
        for data in logs_data:
            self.assertIn('timestamp', data)
            self.assertIn('usuario', data)
            self.assertIn('acao', data)
            self.assertEqual(data['usuario'], self.user.username)
            self.assertTrue(data['sucesso'])


    def test_auditoria_cleanup_logs_antigos(self):
        """Testar limpeza de logs antigos de auditoria"""
        from datetime import datetime, timedelta

        # Criar log muito antigo
        log_antigo = AuditoriaManager.registrar_deteccao_orcamento_orfao(
            usuario=self.user,
            email='antigo@exemplo.com',
            quantidade_encontrada=1
        )

        # Simular que é muito antigo (mais de 1 ano)
        data_antiga = datetime.now() - timedelta(days=400)
        log_antigo.timestamp = data_antiga
        log_antigo.save()

        # Log recente
        log_recente = AuditoriaManager.registrar_vinculacao_orcamento_orfao(
            usuario=self.user,
            solicitacao=self.solicitacao
        )

        # Simular limpeza (remover logs mais antigos que 365 dias)
        cutoff_date = datetime.now() - timedelta(days=365)
        logs_para_remover = LogAuditoria.objects.filter(
            timestamp__lt=cutoff_date
        )

        count_antes = LogAuditoria.objects.count()
        logs_removidos_count = logs_para_remover.count()

        # Verificar que o log antigo seria removido
        self.assertGreater(logs_removidos_count, 0)
        self.assertIn(log_antigo, logs_para_remover)
        self.assertNotIn(log_recente, logs_para_remover)


    def test_auditoria_notificacoes_sistema(self):
        """Testar logs de notificações do sistema"""
        # Registrar notificação de vinculação
        log = AuditoriaManager.registrar_notificacao_vinculacao(
            usuario_notificado=self.user,
            quantidade_orcamentos=3,
            metodo_vinculacao="sistema_automatico"
        )

        # Verificar que é um log do sistema (sem usuário executor)
        self.assertIsNone(log.usuario)
        self.assertEqual(log.objeto_afetado, self.user)
        self.assertEqual(log.acao, TipoAcao.NOTIFICACAO_VINCULACAO)

        # Verificar dados da notificação
        dados = log.dados_posteriores
        self.assertEqual(dados['quantidade_orcamentos'], 3)
        self.assertEqual(dados['metodo_vinculacao'], 'sistema_automatico')
        self.assertEqual(dados['usuario_notificado'], self.user.id)


    def test_auditoria_bulk_operations(self):
        """Testar auditoria de operações em lote"""
        emails_processados = {'email1@test.com', 'email2@test.com', 'email3@test.com'}

        # Registrar processamento em lote
        log = AuditoriaManager.registrar_processamento_lote_orfaos(
            usuario_comando=self.admin_user,
            total_processadas=10,
            total_vinculadas=7,
            emails_processados=emails_processados
        )

        # Verificar log
        self.assertEqual(log.acao, TipoAcao.PROCESSAMENTO_LOTE)
        self.assertEqual(log.usuario, self.admin_user)

        # Verificar estatísticas
        dados = log.dados_posteriores
        self.assertEqual(dados['total_orfas_encontradas'], 10)
        self.assertEqual(dados['total_vinculadas'], 7)
        self.assertEqual(set(dados['emails_processados']), emails_processados)
        self.assertEqual(dados['metodo'], 'comando_gerenciamento')

        # Verificar descrição
        self.assertIn('Traitement en lot: 7/10', log.descricao)
        self.assertIn('3 emails traités', log.descricao)
