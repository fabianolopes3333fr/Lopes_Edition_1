import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from unittest.mock import patch, MagicMock
from orcamentos.models import SolicitacaoOrcamento, StatusOrcamento, Orcamento
from orcamentos.services import NotificationService

User = get_user_model()

class AdminOrcamentosOrfaosViewsTestCase(TestCase):
    """
    Testes para as views administrativas de gestão de orçamentos órfãos
    """

    def setUp(self):
        """Configurar dados para os testes"""
        self.client = Client()

        # Criar admin
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@exemplo.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )

        # Criar usuário cliente
        self.user = User.objects.create_user(
            username='cliente',
            email='cliente@exemplo.com',
            first_name='Cliente',
            last_name='Teste',
            password='clientepass123'
        )

        # Criar solicitações órfãs
        self.solicitacao_orfa_1 = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Cliente Teste',
            email_solicitante='cliente@exemplo.com',
            telefone_solicitante='11999999999',
            endereco='Rua Cliente, 123',
            cidade='São Paulo',
            cep='01234-567',
            tipo_servico='pintura_interior',
            descricao_servico='Pintura sala cliente',
        )

        self.solicitacao_orfa_2 = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Cliente Teste',
            email_solicitante='cliente@exemplo.com',
            telefone_solicitante='11999999999',
            endereco='Rua Cliente, 456',
            cidade='São Paulo',
            cep='01234-567',
            tipo_servico='pintura_exterior',
            descricao_servico='Pintura fachada cliente',
        )

        # Solicitação sem usuário correspondente
        self.solicitacao_sem_usuario = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Sem Usuario',
            email_solicitante='semcliente@exemplo.com',
            telefone_solicitante='11888888888',
            endereco='Rua Sem Cliente, 789',
            cidade='Rio de Janeiro',
            cep='12345-678',
            tipo_servico='renovacao_completa',
            descricao_servico='Renovação sem cliente',
        )

    def test_admin_orcamentos_orfaos_view_acesso_negado_nao_staff(self):
        """Testar que usuários não-staff não podem acessar a view de órfãos"""
        # Tentar acessar como usuário comum
        self.client.login(username='cliente', password='clientepass123')
        response = self.client.get(reverse('orcamentos:admin_orcamentos_orfaos'))

        # Deve redirecionar para login (acesso negado)
        self.assertEqual(response.status_code, 302)

    def test_admin_orcamentos_orfaos_view_carrega_corretamente(self):
        """Testar se a view de órfãos carrega corretamente para admin"""
        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Acessar a view
        response = self.client.get(reverse('orcamentos:admin_orcamentos_orfaos'))

        # Verificar se carregou com sucesso
        self.assertEqual(response.status_code, 200)

        # Verificar se o template correto foi usado
        self.assertTemplateUsed(response, 'orcamentos/admin_orcamentos_orfaos.html')

        # Verificar contexto
        context = response.context
        self.assertIn('stats', context)
        self.assertIn('emails_com_usuarios', context)
        self.assertIn('emails_sem_usuarios', context)
        self.assertIn('solicitacoes_orfas', context)

        # Verificar estatísticas
        stats = context['stats']
        self.assertEqual(stats['total_orfas'], 3)
        self.assertEqual(stats['emails_unicos'], 2)
        self.assertEqual(stats['podem_ser_vinculadas'], 1)
        self.assertEqual(stats['sem_usuario'], 1)

    def test_admin_orcamentos_orfaos_agrupamento_emails(self):
        """Testar agrupamento correto de emails na view de órfãos"""
        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Acessar a view
        response = self.client.get(reverse('orcamentos:admin_orcamentos_orfaos'))

        context = response.context
        emails_com_usuarios = context['emails_com_usuarios']
        emails_sem_usuarios = context['emails_sem_usuarios']

        # Verificar agrupamento
        self.assertEqual(len(emails_com_usuarios), 1)
        self.assertEqual(len(emails_sem_usuarios), 1)

        # Verificar email com usuário
        email_com_usuario = emails_com_usuarios[0]
        self.assertEqual(email_com_usuario['email_solicitante'], 'cliente@exemplo.com')
        self.assertEqual(email_com_usuario['count'], 2)
        self.assertTrue(email_com_usuario['pode_vincular'])
        self.assertEqual(email_com_usuario['usuario'], self.user)

        # Verificar email sem usuário
        email_sem_usuario = emails_sem_usuarios[0]
        self.assertEqual(email_sem_usuario['email_solicitante'], 'semcliente@exemplo.com')
        self.assertEqual(email_sem_usuario['count'], 1)
        self.assertFalse(email_sem_usuario['pode_vincular'])

    def test_admin_vincular_orcamentos_orfaos_ajax_sucesso(self):
        """Testar vinculação via AJAX com sucesso"""
        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Fazer requisição AJAX
        response = self.client.post(
            reverse('orcamentos:admin_vincular_orcamentos_orfaos'),
            {'email': 'cliente@exemplo.com'},
            content_type='application/x-www-form-urlencoded'
        )

        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data['success'])
        self.assertIn('2 demande', data['message'])
        self.assertEqual(len(data['vinculadas']), 2)
        self.assertIn(self.solicitacao_orfa_1.numero, data['vinculadas'])
        self.assertIn(self.solicitacao_orfa_2.numero, data['vinculadas'])
        self.assertIn('Cliente Teste', data['usuario'])

        # Verificar vinculações no banco
        self.solicitacao_orfa_1.refresh_from_db()
        self.solicitacao_orfa_2.refresh_from_db()

        self.assertEqual(self.solicitacao_orfa_1.cliente, self.user)
        self.assertEqual(self.solicitacao_orfa_2.cliente, self.user)

    def test_admin_vincular_orcamentos_orfaos_ajax_email_inexistente(self):
        """Testar AJAX com email que não tem usuário correspondente"""
        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Fazer requisição AJAX com email sem usuário
        response = self.client.post(
            reverse('orcamentos:admin_vincular_orcamentos_orfaos'),
            {'email': 'semcliente@exemplo.com'}
        )

        # Verificar resposta de erro
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertFalse(data['success'])
        self.assertIn('Aucun utilisateur trouvé', data['error'])

    def test_admin_vincular_orcamentos_orfaos_ajax_email_vazio(self):
        """Testar AJAX sem fornecer email"""
        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Fazer requisição AJAX sem email
        response = self.client.post(
            reverse('orcamentos:admin_vincular_orcamentos_orfaos'),
            {}
        )

        # Verificar resposta de erro
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertFalse(data['success'])
        self.assertIn('Email não fornecido', data['error'])

    def test_admin_vincular_orcamentos_orfaos_ajax_nao_staff(self):
        """Testar que usuários não-staff não podem usar AJAX de vinculação"""
        # Login como usuário comum
        self.client.login(username='cliente', password='clientepass123')

        # Tentar fazer requisição AJAX
        response = self.client.post(
            reverse('orcamentos:admin_vincular_orcamentos_orfaos'),
            {'email': 'cliente@exemplo.com'}
        )

        # Deve redirecionar (acesso negado)
        self.assertEqual(response.status_code, 302)

    def test_admin_vincular_orcamentos_orfaos_ajax_apenas_post(self):
        """Testar que a view AJAX só aceita POST"""
        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Tentar fazer GET
        response = self.client.get(reverse('orcamentos:admin_vincular_orcamentos_orfaos'))

        # Deve retornar 405 Method Not Allowed
        self.assertEqual(response.status_code, 405)

    @patch('orcamentos.services.NotificationService.notificar_orcamentos_vinculados')
    def test_admin_vincular_orcamentos_orfaos_ajax_com_notificacao(self, mock_notificar):
        """Testar se a notificação é enviada após vinculação via AJAX"""
        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Fazer requisição AJAX
        response = self.client.post(
            reverse('orcamentos:admin_vincular_orcamentos_orfaos'),
            {'email': 'cliente@exemplo.com'}
        )

        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

        # Verificar se a notificação foi chamada
        mock_notificar.assert_called_once_with(self.user, 2)

    def test_admin_dashboard_estatisticas_orfaos(self):
        """Testar estatísticas de órfãos no dashboard administrativo"""
        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Acessar dashboard
        response = self.client.get(reverse('orcamentos:admin_dashboard'))

        # Verificar se carregou com sucesso
        self.assertEqual(response.status_code, 200)

        # Verificar contexto
        context = response.context
        self.assertIn('solicitacoes_orfas', context)
        self.assertIn('orfaos_vincuLaveis', context)

        # Verificar valores
        self.assertEqual(context['solicitacoes_orfas'], 3)
        self.assertEqual(context['orfaos_vincuLaveis'], 1)

    def test_admin_dashboard_com_orcamentos_ja_vinculados(self):
        """Testar dashboard após vinculação de órfãos"""
        # Vincular orçamentos órfãos
        self.solicitacao_orfa_1.cliente = self.user
        self.solicitacao_orfa_1.save()
        self.solicitacao_orfa_2.cliente = self.user
        self.solicitacao_orfa_2.save()

        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Acessar dashboard
        response = self.client.get(reverse('orcamentos:admin_dashboard'))

        # Verificar estatísticas atualizadas
        context = response.context
        self.assertEqual(context['solicitacoes_orfas'], 1)  # Apenas a sem usuário
        self.assertEqual(context['orfaos_vincuLaveis'], 0)  # Nenhuma pode ser vinculada

    def test_view_admin_orcamentos_orfaos_html_content(self):
        """Testar conteúdo HTML da view de órfãos"""
        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Acessar a view
        response = self.client.get(reverse('orcamentos:admin_orcamentos_orfaos'))

        # Verificar conteúdo HTML
        self.assertContains(response, 'Gestion des Demandes Orphelines')
        self.assertContains(response, 'cliente@exemplo.com')
        self.assertContains(response, 'semcliente@exemplo.com')
        self.assertContains(response, 'Total Orphelines')
        self.assertContains(response, 'Peuvent être liées')
        self.assertContains(response, 'Sans utilisateur')
        self.assertContains(response, 'Lier maintenant')

    def test_multiple_vinculacao_mesmo_email(self):
        """Testar vinculação múltipla para o mesmo email via AJAX"""
        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Primeira vinculação
        response1 = self.client.post(
            reverse('orcamentos:admin_vincular_orcamentos_orfaos'),
            {'email': 'cliente@exemplo.com'}
        )

        data1 = response1.json()
        self.assertTrue(data1['success'])

        # Segunda tentativa de vinculação (não deve encontrar órfãos)
        response2 = self.client.post(
            reverse('orcamentos:admin_vincular_orcamentos_orfaos'),
            {'email': 'cliente@exemplo.com'}
        )

        data2 = response2.json()
        self.assertFalse(data2['success'])
        self.assertIn('Aucune demande orpheline trouvée', data2['error'])

    def test_admin_orcamentos_orfaos_paginacao(self):
        """Testar paginação na lista de solicitações órfãs"""
        # Criar mais solicitações órfãs para testar paginação
        for i in range(25):
            SolicitacaoOrcamento.objects.create(
                nome_solicitante=f'Usuario {i}',
                email_solicitante=f'user{i}@exemplo.com',
                telefone_solicitante='11999999999',
                endereco=f'Rua {i}, 123',
                cidade='São Paulo',
                cep='01234-567',
                tipo_servico='pintura_interior',
                descricao_servico=f'Pintura {i}',
            )

        # Login como admin
        self.client.login(username='admin', password='adminpass123')

        # Acessar a view
        response = self.client.get(reverse('orcamentos:admin_orcamentos_orfaos'))

        # Verificar se limitou a 20 itens na exibição
        solicitacoes_exibidas = response.context['solicitacoes_orfas']
        self.assertEqual(len(solicitacoes_exibidas), 20)


class NotificationServiceOrcamentosOrfaosTestCase(TestCase):
    """
    Testes para o serviço de notificações relacionado a orçamentos órfãos
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@exemplo.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )

    @patch('orcamentos.services.render_to_string')
    @patch('orcamentos.services.send_mail')
    def test_notificar_orcamentos_vinculados_email_enviado(self, mock_send_mail, mock_render):
        """Testar se o email de notificação é enviado corretamente"""
        # Configurar mocks
        mock_render.return_value = '<html>Email content</html>'
        mock_send_mail.return_value = True

        # Chamar serviço
        NotificationService.notificar_orcamentos_vinculados(self.user, 3)

        # Verificar se render_to_string foi chamado
        mock_render.assert_called_once()

        # Verificar se send_mail foi chamado
        mock_send_mail.assert_called_once()

        # Verificar argumentos do send_mail
        args, kwargs = mock_send_mail.call_args
        self.assertIn('3 demandes', args[0])  # Subject
        self.assertIn('Bienvenue', args[0])
        self.assertEqual(kwargs['recipient_list'], [self.user.email])
        self.assertTrue(kwargs['fail_silently'])

    @patch('orcamentos.services.render_to_string')
    @patch('orcamentos.services.send_mail')
    def test_notificar_orcamentos_vinculados_singular(self, mock_send_mail, mock_render):
        """Testar notificação com apenas 1 orçamento vinculado"""
        mock_render.return_value = '<html>Email content</html>'
        mock_send_mail.return_value = True

        # Chamar serviço com 1 orçamento
        NotificationService.notificar_orcamentos_vinculados(self.user, 1)

        # Verificar plural/singular no subject
        args, kwargs = mock_send_mail.call_args
        self.assertIn('1 demande', args[0])
        self.assertNotIn('demandes', args[0])

    @patch('orcamentos.services.send_mail')
    def test_notificar_orcamentos_vinculados_erro_email(self, mock_send_mail):
        """Testar tratamento de erro no envio de email"""
        # Simular erro no envio
        mock_send_mail.side_effect = Exception('Erro de email')

        # Chamar serviço (não deve levantar exceção)
        try:
            NotificationService.notificar_orcamentos_vinculados(self.user, 2)
        except Exception:
            self.fail("NotificationService não deve levantar exceção em caso de erro de email")

    @patch('orcamentos.services.NotificationService.criar_notificacao')
    def test_notificar_orcamentos_vinculados_notificacao_sistema(self, mock_criar_notificacao):
        """Testar criação de notificação no sistema"""
        # Chamar serviço
        NotificationService.notificar_orcamentos_vinculados(self.user, 2)

        # Verificar se a notificação foi criada
        mock_criar_notificacao.assert_called_once()

        # Verificar argumentos
        args, kwargs = mock_criar_notificacao.call_args
        self.assertEqual(args[0], self.user)  # usuário
        self.assertIn('Demandes retrouvées', args[2])  # título
        self.assertIn('2 demande', args[3])  # mensagem
        self.assertEqual(args[4], '/devis/mes-devis/')  # URL

    def test_verificar_e_processar_orcamentos_orfaos_service(self):
        """Testar função utilitária do serviço"""
        # Criar solicitações órfãs
        SolicitacaoOrcamento.objects.create(
            nome_solicitante='Test User',
            email_solicitante='test@exemplo.com',
            telefone_solicitante='11999999999',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            cep='01234-567',
            tipo_servico='pintura_interior',
            descricao_servico='Pintura teste',
        )

        SolicitacaoOrcamento.objects.create(
            nome_solicitante='Sem Usuario',
            email_solicitante='semuser@exemplo.com',
            telefone_solicitante='11888888888',
            endereco='Rua Sem User, 456',
            cidade='Rio de Janeiro',
            cep='12345-678',
            tipo_servico='pintura_exterior',
            descricao_servico='Pintura sem user',
        )

        # Chamar função utilitária
        processadas = NotificationService.verificar_e_processar_orcamentos_orfaos()

        # Verificar resultado
        self.assertEqual(processadas, 1)  # Apenas 1 pode ser vinculada

        # Verificar vinculação no banco
        solicitacao = SolicitacaoOrcamento.objects.get(email_solicitante='test@exemplo.com')
        self.assertEqual(solicitacao.cliente, self.user)

        # Verificar que a sem usuário continua órfã
        solicitacao_sem_user = SolicitacaoOrcamento.objects.get(email_solicitante='semuser@exemplo.com')
        self.assertIsNone(solicitacao_sem_user.cliente)
