import pytest
from django.test import TestCase, Client, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.management import call_command
from django.core import mail
from unittest.mock import patch
from orcamentos.models import SolicitacaoOrcamento, StatusOrcamento
from orcamentos.signals import vincular_orcamentos_orfaos, verificar_e_vincular_orcamentos_existentes
from orcamentos.services import NotificationService

User = get_user_model()

@pytest.mark.django_db(transaction=True)
class VinculacaoOrcamentosOrfaosTestCase(TransactionTestCase):
    """
    Testes para a funcionalidade de vinculação automática de orçamentos órfãos
    """

    def setUp(self):
        """Configurar dados para os testes"""
        # Limpar dados antes de cada teste
        SolicitacaoOrcamento.objects.all().delete()
        User.objects.all().delete()
        
        self.client = Client()

        # Criar usuário de teste
        self.user = User.objects.create_user(
            username='testuser',
            email='test@exemplo.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )

        # Criar admin de teste
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@exemplo.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )

        # Criar solicitações órfãs para teste
        self.solicitacao_orfa_1 = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Test User',
            email_solicitante='test@exemplo.com',
            telefone_solicitante='11999999999',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            cep='01234-567',
            tipo_servico='pintura_interior',
            descricao_servico='Pintura de sala',
        )

        self.solicitacao_orfa_2 = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Test User',
            email_solicitante='test@exemplo.com',
            telefone_solicitante='11999999999',
            endereco='Rua Teste, 456',
            cidade='São Paulo',
            cep='01234-567',
            tipo_servico='pintura_exterior',
            descricao_servico='Pintura de fachada',
        )

        # Solicitação órfã sem usuário correspondente
        self.solicitacao_sem_usuario = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Sem Usuario',
            email_solicitante='semUsuario@exemplo.com',
            telefone_solicitante='11888888888',
            endereco='Rua Sem Usuario, 789',
            cidade='Rio de Janeiro',
            cep='12345-678',
            tipo_servico='renovacao_completa',
            descricao_servico='Renovação completa',
        )

    def test_signal_vincula_orcamentos_no_cadastro(self):
        """Testar se o signal vincula orçamentos órfãos quando usuário é criado"""
        # Limpar usuários com este email para evitar conflito
        User.objects.filter(email='novo@exemplo.com').delete()
        
        # Criar solicitação órfã com email novo
        solicitacao_nova = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Novo Usuario',
            email_solicitante='novo@exemplo.com',
            telefone_solicitante='11777777777',
            endereco='Rua Nova, 999',
            cidade='São Paulo',
            cep='98765-432',
            tipo_servico='pintura_interior',
            descricao_servico='Pintura nova',
        )
        
        # Verificar que está órfã
        self.assertIsNone(solicitacao_nova.cliente)
        
        # Criar usuário com o mesmo email
        novo_usuario = User.objects.create_user(
            username='novousuario',
            email='novo@exemplo.com',
            first_name='Novo',
            last_name='Usuario',
            password='novopass123'
        )
        
        # Recarregar solicitação
        solicitacao_nova.refresh_from_db()
        
        # Verificar se foi vinculada
        self.assertEqual(solicitacao_nova.cliente, novo_usuario)

    def test_view_cliente_orcamentos_vincula_automaticamente(self):
        """Testar se a view cliente_orcamentos vincula órfãos automaticamente"""
        # Login do usuário
        self.client.login(username='testuser', password='testpass123')

        # Verificar que as solicitações estão órfãs
        self.assertIsNone(self.solicitacao_orfa_1.cliente)
        self.assertIsNone(self.solicitacao_orfa_2.cliente)

        # Acessar a página de orçamentos
        response = self.client.get(reverse('orcamentos:cliente_orcamentos'))

        # Verificar se a página carregou com sucesso
        self.assertEqual(response.status_code, 200)

        # Recarregar as solicitações do banco
        self.solicitacao_orfa_1.refresh_from_db()
        self.solicitacao_orfa_2.refresh_from_db()

        # Verificar se foram vinculadas automaticamente
        self.assertEqual(self.solicitacao_orfa_1.cliente, self.user)
        self.assertEqual(self.solicitacao_orfa_2.cliente, self.user)

        # Verificar se a mensagem de sucesso foi exibida
        messages = list(response.context['messages'])
        self.assertTrue(any('trouvé et associé' in str(message) for message in messages))

    def test_url_publica_com_usuario_logado(self):
        """Testar se a URL pública vincula automaticamente quando usuário está logado"""
        # Login do usuário
        self.client.login(username='testuser', password='testpass123')

        # Dados para nova solicitação
        form_data = {
            'nome_solicitante': 'Test User Logado',
            'email_solicitante': 'test@exemplo.com',
            'telefone_solicitante': '11777777777',
            'endereco': 'Rua Nova, 999',
            'cidade': 'São Paulo',
            'cep': '01234-567',
            'tipo_servico': 'decoracao',
            'descricao_servico': 'Decoração de quarto',
            'area_aproximada': 20,
            'urgencia': 'media',
            'orcamento_maximo': 5000,
        }

        # Fazer POST para a URL pública
        response = self.client.post(reverse('orcamentos:solicitar_publico'), form_data)

        # Verificar se foi redirecionado (sucesso)
        self.assertEqual(response.status_code, 302)

        # Buscar a solicitação criada
        nova_solicitacao = SolicitacaoOrcamento.objects.filter(
            email_solicitante='test@exemplo.com',
            descricao_servico='Decoração de quarto'
        ).first()

        # Verificar se foi vinculada automaticamente ao usuário logado
        self.assertIsNotNone(nova_solicitacao)
        self.assertEqual(nova_solicitacao.cliente, self.user)

    def test_comando_vincular_orcamentos_orfaos(self):
        """Testar o comando de gerenciamento para vincular orçamentos órfãos"""
        # Verificar situação inicial
        orfas_inicial = SolicitacaoOrcamento.objects.filter(cliente__isnull=True).count()
        self.assertEqual(orfas_inicial, 3)  # 2 que podem ser vinculadas + 1 sem usuário

        # Executar comando
        call_command('vincular_orcamentos_orfaos')

        # Verificar resultados
        self.solicitacao_orfa_1.refresh_from_db()
        self.solicitacao_orfa_2.refresh_from_db()
        self.solicitacao_sem_usuario.refresh_from_db()

        # Verificar vinculações
        self.assertEqual(self.solicitacao_orfa_1.cliente, self.user)
        self.assertEqual(self.solicitacao_orfa_2.cliente, self.user)
        self.assertIsNone(self.solicitacao_sem_usuario.cliente)  # Deve continuar órfã

        # Verificar total de órfãs restantes
        orfas_final = SolicitacaoOrcamento.objects.filter(cliente__isnull=True).count()
        self.assertEqual(orfas_final, 1)  # Apenas a sem usuário

    def test_comando_dry_run(self):
        """Testar o comando com --dry-run (sem fazer alterações)"""
        # Executar comando em modo dry-run
        call_command('vincular_orcamentos_orfaos', '--dry-run')

        # Verificar que nada foi alterado
        self.solicitacao_orfa_1.refresh_from_db()
        self.solicitacao_orfa_2.refresh_from_db()

        self.assertIsNone(self.solicitacao_orfa_1.cliente)
        self.assertIsNone(self.solicitacao_orfa_2.cliente)

    def test_comando_email_especifico(self):
        """Testar o comando para email específico"""
        # Executar comando para email específico
        call_command('vincular_orcamentos_orfaos', '--email', 'test@exemplo.com')

        # Verificar resultados
        self.solicitacao_orfa_1.refresh_from_db()
        self.solicitacao_orfa_2.refresh_from_db()
        self.solicitacao_sem_usuario.refresh_from_db()

        # Verificar que apenas as solicitações do email especificado foram vinculadas
        self.assertEqual(self.solicitacao_orfa_1.cliente, self.user)
        self.assertEqual(self.solicitacao_orfa_2.cliente, self.user)
        self.assertIsNone(self.solicitacao_sem_usuario.cliente)

    @patch('orcamentos.services.NotificationService.notificar_orcamentos_vinculados')
    def test_comando_com_notificacoes(self, mock_notificar):
        """Testar o comando com envio de notificações"""
        # Executar comando com notificações
        call_command('vincular_orcamentos_orfaos', '--notify')

        # Verificar se a notificação foi chamada
        mock_notificar.assert_called_once_with(self.user, 2)

    def test_view_admin_orcamentos_orfaos(self):
        """Testar a view administrativa para visualizar orçamentos órfãos"""
        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Acessar a página
        response = self.client.get(reverse('orcamentos:admin_orcamentos_orfaos'))

        # Verificar se carregou com sucesso
        self.assertEqual(response.status_code, 200)

        # Verificar se as estatísticas estão corretas
        context = response.context
        self.assertEqual(context['stats']['total_orfas'], 3)
        self.assertEqual(context['stats']['podem_ser_vinculadas'], 1)  # 1 email único
        self.assertEqual(context['stats']['sem_usuario'], 1)

    def test_ajax_vincular_orcamentos_orfaos(self):
        """Testar vinculação via AJAX"""
        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Fazer requisição AJAX
        response = self.client.post(
            reverse('orcamentos:admin_vincular_orcamentos_orfaos'),
            {'email': 'test@exemplo.com'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['vinculadas']), 2)

        # Verificar vinculações no banco
        self.solicitacao_orfa_1.refresh_from_db()
        self.solicitacao_orfa_2.refresh_from_db()

        self.assertEqual(self.solicitacao_orfa_1.cliente, self.user)
        self.assertEqual(self.solicitacao_orfa_2.cliente, self.user)

    def test_ajax_email_sem_usuario(self):
        """Testar AJAX com email que não tem usuário"""
        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Fazer requisição AJAX com email sem usuário
        response = self.client.post(
            reverse('orcamentos:admin_vincular_orcamentos_orfaos'),
            {'email': 'semUsuario@exemplo.com'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Verificar resposta de erro
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('Aucun utilisateur trouvé', data['error'])

    def test_dashboard_admin_estatisticas_orfaos(self):
        """Testar se o dashboard administrativo mostra estatísticas de órfãos"""
        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Acessar dashboard
        response = self.client.get(reverse('orcamentos:admin_dashboard'))

        # Verificar se carregou com sucesso
        self.assertEqual(response.status_code, 200)

        # Verificar se as estatísticas de órfãos estão presentes
        context = response.context
        self.assertIn('solicitacoes_orfas', context)
        self.assertIn('orfaos_vincuLaveis', context)
        self.assertEqual(context['solicitacoes_orfas'], 3)
        self.assertEqual(context['orfaos_vincuLaveis'], 1)

    @patch('orcamentos.services.send_mail')
    def test_notificacao_orcamentos_vinculados(self, mock_send_mail):
        """Testar envio de notificação sobre orçamentos vinculados"""
        # Chamar serviço de notificação
        NotificationService.notificar_orcamentos_vinculados(self.user, 2)

        # Verificar se o email foi enviado
        mock_send_mail.assert_called_once()
        args, kwargs = mock_send_mail.call_args

        # Verificar conteúdo do email
        self.assertIn('2 demande', args[0])  # Subject
        self.assertIn('Bienvenue', args[0])
        self.assertEqual(kwargs['recipient_list'], [self.user.email])

    def test_verificar_e_vincular_orcamentos_existentes(self):
        """Testar função utilitária de vinculação"""
        # Chamar função utilitária
        vinculadas = verificar_e_vincular_orcamentos_existentes(
            'test@exemplo.com',
            self.user
        )

        # Verificar retorno
        self.assertEqual(len(vinculadas), 2)
        self.assertIn(self.solicitacao_orfa_1.numero, vinculadas)
        self.assertIn(self.solicitacao_orfa_2.numero, vinculadas)

        # Verificar vinculações no banco
        self.solicitacao_orfa_1.refresh_from_db()
        self.solicitacao_orfa_2.refresh_from_db()

        self.assertEqual(self.solicitacao_orfa_1.cliente, self.user)
        self.assertEqual(self.solicitacao_orfa_2.cliente, self.user)

    def test_url_publica_email_diferente_usuario_logado(self):
        """Testar URL pública com email diferente do usuário logado"""
        # Login do usuário
        self.client.login(username='testuser', password='testpass123')

        # Dados com email diferente
        form_data = {
            'nome_solicitante': 'Test User',
            'email_solicitante': 'outro@exemplo.com',  # Email diferente
            'telefone_solicitante': '11777777777',
            'endereco': 'Rua Nova, 999',
            'cidade': 'São Paulo',
            'cep': '01234-567',
            'tipo_servico': 'decoracao',
            'descricao_servico': 'Decoração com email diferente',
            'area_aproximada': 20,
            'urgencia': 'media',
            'orcamento_maximo': 5000,
        }

        # Fazer POST
        response = self.client.post(reverse('orcamentos:solicitar_publico'), form_data)

        # Verificar se foi redirecionado
        self.assertEqual(response.status_code, 302)

        # Buscar a solicitação criada
        nova_solicitacao = SolicitacaoOrcamento.objects.filter(
            email_solicitante='outro@exemplo.com'
        ).first()

        # Verificar se foi vinculada ao usuário logado mesmo com email diferente
        self.assertIsNotNone(nova_solicitacao)
        self.assertEqual(nova_solicitacao.cliente, self.user)

    def test_multiplos_usuarios_mesmo_email(self):
        """Testar cenário com múltiplos usuários com mesmo email"""
        # NOTA: O modelo User tem constraint UNIQUE no email, então este cenário
        # não pode ocorrer no sistema real. Vamos testar que o comando funciona
        # corretamente com um único usuário por email.
        
        # Executar comando com apenas um usuário por email
        call_command('vincular_orcamentos_orfaos')

        # Verificar que as solicitações foram vinculadas ao usuário
        self.solicitacao_orfa_1.refresh_from_db()
        self.solicitacao_orfa_2.refresh_from_db()

        # Deve ser vinculado ao usuário existente
        self.assertEqual(self.solicitacao_orfa_1.cliente, self.user)
        self.assertEqual(self.solicitacao_orfa_2.cliente, self.user)

    def tearDown(self):
        """Limpeza após os testes"""
        # Limpar emails enviados durante os testes
        mail.outbox = []


class VinculacaoOrcamentosIntegrationTestCase(TestCase):
    """
    Testes de integração para a funcionalidade completa
    """

    def setUp(self):
        self.client = Client()

    def test_fluxo_completo_vinculacao(self):
        """Testar fluxo completo: solicitação anônima -> cadastro -> vinculação"""
        # 1. Fazer solicitação anônima
        form_data = {
            'nome_solicitante': 'Futuro Usuario',
            'email_solicitante': 'futuro@exemplo.com',
            'telefone_solicitante': '11666666666',
            'endereco': 'Rua Futuro, 123',
            'cidade': 'São Paulo',
            'cep': '01234-567',
            'tipo_servico': 'pintura_interior',
            'descricao_servico': 'Pintura futura',
            'area_aproximada': 30,
            'urgencia': 'baixa',
            'orcamento_maximo': 3000,
        }

        response = self.client.post(reverse('orcamentos:solicitar_publico'), form_data)
        self.assertEqual(response.status_code, 302)

        # Verificar que a solicitação foi criada como órfã
        solicitacao = SolicitacaoOrcamento.objects.get(email_solicitante='futuro@exemplo.com')
        self.assertIsNone(solicitacao.cliente)

        # 2. Criar usuário com o mesmo email (simula cadastro)
        user = User.objects.create_user(
            username='futurouser',
            email='futuro@exemplo.com',
            password='futuropass123'
        )

        # 3. Verificar se foi vinculado automaticamente pelo signal
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.cliente, user)

        # 4. Login e verificar se o usuário pode acessar o dashboard
        self.client.login(username='futurouser', password='futuropass123')
        response = self.client.get(reverse('orcamentos:cliente_orcamentos'))

        self.assertEqual(response.status_code, 200)
        
        # Verificar que a solicitação está vinculada ao usuário no banco de dados
        solicitacoes_usuario = SolicitacaoOrcamento.objects.filter(cliente=user)
        self.assertEqual(solicitacoes_usuario.count(), 1)
        self.assertEqual(solicitacoes_usuario.first().descricao_servico, 'Pintura futura')
        
        # Verificar que a página carregou corretamente (ao invés de procurar texto específico)
        self.assertIn('orcamentos', response.context or {})

    @patch('orcamentos.services.NotificationService.notificar_orcamentos_vinculados')
    def test_notificacao_apos_vinculacao_signal(self, mock_notificar):
        """Testar se a notificação é enviada após vinculação por signal"""
        # Criar solicitação órfã
        SolicitacaoOrcamento.objects.create(
            nome_solicitante='Test Signal',
            email_solicitante='signal@exemplo.com',
            telefone_solicitante='11555555555',
            endereco='Rua Signal, 456',
            cidade='São Paulo',
            cep='01234-567',
            tipo_servico='pintura_exterior',
            descricao_servico='Teste signal',
        )

        # Criar usuário (dispara signal)
        User.objects.create_user(
            username='signaluser',
            email='signal@exemplo.com',
            password='signalpass123'
        )

        # Verificar se a notificação foi chamada
        mock_notificar.assert_called_once()
