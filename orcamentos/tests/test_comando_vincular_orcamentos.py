import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO
from unittest.mock import patch
from orcamentos.models import SolicitacaoOrcamento, StatusOrcamento
from orcamentos.management.commands.vincular_orcamentos_orfaos import Command

User = get_user_model()

class VincularOrcamentosOrfaosCommandTestCase(TestCase):
    """
    Testes para o comando de gerenciamento vincular_orcamentos_orfaos
    """

    def setUp(self):
        """Configurar dados para os testes"""
        # Criar usuários
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@exemplo.com',
            first_name='User',
            last_name='One',
            password='pass123'
        )

        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@exemplo.com',
            first_name='User',
            last_name='Two',
            password='pass123'
        )

        # Criar solicitações órfãs
        self.solicitacao_user1_1 = SolicitacaoOrcamento.objects.create(
            nome_solicitante='User One',
            email_solicitante='user1@exemplo.com',
            telefone_solicitante='11999999999',
            endereco='Rua User1, 123',
            cidade='São Paulo',
            cep='01234-567',
            tipo_servico='pintura_interior',
            descricao_servico='Pintura interior user1',
        )

        self.solicitacao_user1_2 = SolicitacaoOrcamento.objects.create(
            nome_solicitante='User One',
            email_solicitante='user1@exemplo.com',
            telefone_solicitante='11999999999',
            endereco='Rua User1, 456',
            cidade='São Paulo',
            cep='01234-567',
            tipo_servico='pintura_exterior',
            descricao_servico='Pintura exterior user1',
        )

        self.solicitacao_user2 = SolicitacaoOrcamento.objects.create(
            nome_solicitante='User Two',
            email_solicitante='user2@exemplo.com',
            telefone_solicitante='11888888888',
            endereco='Rua User2, 789',
            cidade='Rio de Janeiro',
            cep='12345-678',
            tipo_servico='renovacao_completa',
            descricao_servico='Renovação user2',
        )

        # Solicitação sem usuário
        self.solicitacao_sem_user = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Sem Usuario',
            email_solicitante='semuser@exemplo.com',
            telefone_solicitante='11777777777',
            endereco='Rua Sem User, 999',
            cidade='Brasília',
            cep='98765-432',
            tipo_servico='decoracao',
            descricao_servico='Decoração sem user',
        )

    def test_comando_sem_argumentos(self):
        """Testar comando sem argumentos (processamento normal)"""
        # Capturar output
        out = StringIO()

        # Executar comando
        call_command('vincular_orcamentos_orfaos', stdout=out)

        # Verificar output
        output = out.getvalue()
        self.assertIn('Iniciando busca por orçamentos órfãos', output)
        self.assertIn('Encontradas 4 solicitações órfãs', output)
        self.assertIn('Solicitações vinculadas: 3', output)
        self.assertIn('Usuários únicos beneficiados: 2', output)

        # Verificar vinculações no banco
        self.solicitacao_user1_1.refresh_from_db()
        self.solicitacao_user1_2.refresh_from_db()
        self.solicitacao_user2.refresh_from_db()
        self.solicitacao_sem_user.refresh_from_db()

        self.assertEqual(self.solicitacao_user1_1.cliente, self.user1)
        self.assertEqual(self.solicitacao_user1_2.cliente, self.user1)
        self.assertEqual(self.solicitacao_user2.cliente, self.user2)
        self.assertIsNone(self.solicitacao_sem_user.cliente)

    def test_comando_dry_run(self):
        """Testar comando com --dry-run"""
        # Capturar output
        out = StringIO()

        # Executar comando em dry-run
        call_command('vincular_orcamentos_orfaos', '--dry-run', stdout=out)

        # Verificar output
        output = out.getvalue()
        self.assertIn('[DRY-RUN]', output)
        self.assertIn('MODO DRY-RUN: Nenhuma alteração foi feita', output)

        # Verificar que nada foi alterado no banco
        self.solicitacao_user1_1.refresh_from_db()
        self.solicitacao_user1_2.refresh_from_db()
        self.solicitacao_user2.refresh_from_db()

        self.assertIsNone(self.solicitacao_user1_1.cliente)
        self.assertIsNone(self.solicitacao_user1_2.cliente)
        self.assertIsNone(self.solicitacao_user2.cliente)

    def test_comando_email_especifico(self):
        """Testar comando com --email específico"""
        # Capturar output
        out = StringIO()

        # Executar comando para email específico
        call_command('vincular_orcamentos_orfaos', '--email', 'user1@exemplo.com', stdout=out)

        # Verificar output
        output = out.getvalue()
        self.assertIn('Processando apenas email: user1@exemplo.com', output)
        self.assertIn('Encontradas 2 solicitações órfãs', output)
        self.assertIn('Solicitações vinculadas: 2', output)

        # Verificar vinculações
        self.solicitacao_user1_1.refresh_from_db()
        self.solicitacao_user1_2.refresh_from_db()
        self.solicitacao_user2.refresh_from_db()

        self.assertEqual(self.solicitacao_user1_1.cliente, self.user1)
        self.assertEqual(self.solicitacao_user1_2.cliente, self.user1)
        self.assertIsNone(self.solicitacao_user2.cliente)  # Não deve ser vinculada

    @patch('orcamentos.services.NotificationService.notificar_orcamentos_vinculados')
    def test_comando_com_notificacoes(self, mock_notificar):
        """Testar comando com --notify"""
        # Executar comando com notificações
        call_command('vincular_orcamentos_orfaos', '--notify')

        # Verificar se as notificações foram enviadas
        self.assertEqual(mock_notificar.call_count, 2)  # Para user1 e user2

        # Verificar argumentos das chamadas
        calls = mock_notificar.call_args_list

        # Primeira chamada (user1 com 2 orçamentos)
        call1_args = calls[0][0]
        self.assertIn(call1_args[0], [self.user1, self.user2])
        self.assertIn(call1_args[1], [1, 2])

        # Segunda chamada (user2 com 1 orçamento)
        call2_args = calls[1][0]
        self.assertIn(call2_args[0], [self.user1, self.user2])
        self.assertIn(call2_args[1], [1, 2])

    def test_comando_sem_orcamentos_orfaos(self):
        """Testar comando quando não há orçamentos órfãos"""
        # Vincular todas as solicitações
        SolicitacaoOrcamento.objects.filter(
            email_solicitante='user1@exemplo.com'
        ).update(cliente=self.user1)

        SolicitacaoOrcamento.objects.filter(
            email_solicitante='user2@exemplo.com'
        ).update(cliente=self.user2)

        SolicitacaoOrcamento.objects.filter(
            email_solicitante='semuser@exemplo.com'
        ).delete()

        # Capturar output
        out = StringIO()

        # Executar comando
        call_command('vincular_orcamentos_orfaos', stdout=out)

        # Verificar output
        output = out.getvalue()
        self.assertIn('Nenhum orçamento órfão encontrado', output)

    def test_comando_email_inexistente(self):
        """Testar comando com email que não existe"""
        # Capturar output
        out = StringIO()

        # Executar comando para email inexistente
        call_command('vincular_orcamentos_orfaos', '--email', 'inexistente@exemplo.com', stdout=out)

        # Verificar output
        output = out.getvalue()
        self.assertIn('Nenhum orçamento órfão encontrado', output)

    def test_comando_email_sem_usuario(self):
        """Testar comando com email que não tem usuário correspondente"""
        # Capturar output
        out = StringIO()

        # Executar comando para email sem usuário
        call_command('vincular_orcamentos_orfaos', '--email', 'semuser@exemplo.com', stdout=out)

        # Verificar output
        output = out.getvalue()
        self.assertIn('Usuário não encontrado para email: semuser@exemplo.com', output)
        self.assertIn('Solicitações vinculadas: 0', output)

    def test_comando_argumentos_combinados(self):
        """Testar comando com múltiplos argumentos"""
        # Capturar output
        out = StringIO()

        # Executar comando com dry-run e email específico
        call_command(
            'vincular_orcamentos_orfaos',
            '--dry-run',
            '--email',
            'user1@exemplo.com',
            stdout=out
        )

        # Verificar output
        output = out.getvalue()
        self.assertIn('[DRY-RUN]', output)
        self.assertIn('Processando apenas email: user1@exemplo.com', output)
        self.assertIn('MODO DRY-RUN', output)

        # Verificar que nada foi alterado
        self.solicitacao_user1_1.refresh_from_db()
        self.assertIsNone(self.solicitacao_user1_1.cliente)

    def test_comando_com_erro_na_vinculacao(self):
        """Testar comando com erro durante vinculação"""
        # Capturar output
        out = StringIO()

        # Simular erro deletando o usuário durante o teste
        with patch.object(SolicitacaoOrcamento, 'save', side_effect=Exception('Erro de banco')):
            call_command('vincular_orcamentos_orfaos', stdout=out)

        # Verificar que o erro foi capturado no output
        output = out.getvalue()
        self.assertIn('Erro ao processar', output)

    def test_comando_help(self):
        """Testar help do comando"""
        # Capturar output do help
        out = StringIO()

        try:
            call_command('vincular_orcamentos_orfaos', '--help', stdout=out)
        except SystemExit:
            pass  # Help command faz sys.exit

        # Verificar se o help foi exibido
        output = out.getvalue()
        self.assertIn('Vincular orçamentos órfãos', output)
        self.assertIn('--dry-run', output)
        self.assertIn('--email', output)
        self.assertIn('--notify', output)

    def test_performance_comando_muitos_orcamentos(self):
        """Testar performance do comando com muitos orçamentos"""
        import time

        # Criar muitas solicitações órfãs
        solicitacoes_bulk = []
        for i in range(100):
            solicitacoes_bulk.append(
                SolicitacaoOrcamento(
                    nome_solicitante=f'Bulk User {i}',
                    email_solicitante=f'bulk{i}@exemplo.com',
                    telefone_solicitante='11999999999',
                    endereco=f'Rua Bulk {i}, 123',
                    cidade='São Paulo',
                    cep='01234-567',
                    tipo_servico='pintura_interior',
                    descricao_servico=f'Pintura bulk {i}',
                )
            )

        SolicitacaoOrcamento.objects.bulk_create(solicitacoes_bulk)

        # Medir tempo de execução
        start_time = time.time()
        call_command('vincular_orcamentos_orfaos', verbosity=0)
        end_time = time.time()

        # Verificar que executou em tempo razoável (menos de 5 segundos)
        execution_time = end_time - start_time
        self.assertLess(execution_time, 5.0)

    def test_comando_output_formatacao(self):
        """Testar formatação do output do comando"""
        out = StringIO()

        # Executar comando
        call_command('vincular_orcamentos_orfaos', stdout=out)

        output = out.getvalue()

        # Verificar elementos da formatação
        self.assertIn('🔍', output)  # Emoji de busca
        self.assertIn('✅', output)  # Emoji de sucesso
        self.assertIn('⚠️', output)   # Emoji de aviso
        self.assertIn('📊', output)  # Emoji de estatísticas
        self.assertIn('📋', output)  # Emoji de resumo
        self.assertIn('=' * 50, output)  # Separadores

        # Verificar estrutura do resumo
        self.assertIn('RESUMO DA OPERAÇÃO', output)
        self.assertIn('Total de solicitações órfãs encontradas', output)
        self.assertIn('Solicitações vinculadas', output)
        self.assertIn('Usuários únicos beneficiados', output)


class CommandIntegrationTestCase(TestCase):
    """
    Testes de integração do comando com outros componentes do sistema
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='integration_user',
            email='integration@exemplo.com',
            password='pass123'
        )

    @patch('orcamentos.services.NotificationService.notificar_orcamentos_vinculados')
    def test_integracao_comando_com_notification_service(self, mock_notificar):
        """Testar integração do comando com NotificationService"""
        # Criar solicitações órfãs
        for i in range(3):
            SolicitacaoOrcamento.objects.create(
                nome_solicitante=f'Integration User {i}',
                email_solicitante='integration@exemplo.com',
                telefone_solicitante='11999999999',
                endereco=f'Rua Integration {i}, 123',
                cidade='São Paulo',
                cep='01234-567',
                tipo_servico='pintura_interior',
                descricao_servico=f'Pintura integration {i}',
            )

        # Executar comando com notificações
        call_command('vincular_orcamentos_orfaos', '--notify')

        # Verificar se o NotificationService foi chamado
        mock_notificar.assert_called_once_with(self.user, 3)

    def test_integracao_comando_com_auditoria(self):
        """Testar se o comando gera logs de auditoria"""
        with patch('orcamentos.management.commands.vincular_orcamentos_orfaos.logger') as mock_logger:
            # Criar solicitação órfã
            SolicitacaoOrcamento.objects.create(
                nome_solicitante='Audit User',
                email_solicitante='integration@exemplo.com',
                telefone_solicitante='11999999999',
                endereco='Rua Audit, 123',
                cidade='São Paulo',
                cep='01234-567',
                tipo_servico='pintura_interior',
                descricao_servico='Pintura audit',
            )

            # Executar comando
            call_command('vincular_orcamentos_orfaos')

            # Verificar se houve logging (será implementado na auditoria)
            # Este teste será expandido quando implementarmos os logs

    def test_comando_com_orcamentos_relacionados(self):
        """Testar comando quando solicitações órfãs já têm orçamentos elaborados"""
        # Criar solicitação órfã
        solicitacao = SolicitacaoOrcamento.objects.create(
            nome_solicitante='User Com Orcamento',
            email_solicitante='integration@exemplo.com',
            telefone_solicitante='11999999999',
            endereco='Rua Com Orcamento, 123',
            cidade='São Paulo',
            cep='01234-567',
            tipo_servico='pintura_interior',
            descricao_servico='Pintura com orçamento',
        )

        # Criar orçamento para a solicitação órfã
        orcamento = Orcamento.objects.create(
            solicitacao=solicitacao,
            titulo='Orçamento teste',
            descricao='Orçamento para teste',
            prazo_execucao=30,
            elaborado_por=self.user
        )

        # Executar comando
        call_command('vincular_orcamentos_orfaos')

        # Verificar se foi vinculada
        solicitacao.refresh_from_db()
        orcamento.refresh_from_db()

        self.assertEqual(solicitacao.cliente, self.user)
        self.assertEqual(orcamento.solicitacao.cliente, self.user)


class CommandErrorHandlingTestCase(TestCase):
    """
    Testes para tratamento de erros no comando
    """

    def test_comando_com_email_malformado(self):
        """Testar comando com email malformado"""
        out = StringIO()

        # Executar comando com email malformado
        call_command('vincular_orcamentos_orfaos', '--email', 'email_invalido', stdout=out)

        output = out.getvalue()
        self.assertIn('Nenhum orçamento órfão encontrado', output)

    def test_comando_resiliente_a_erros_database(self):
        """Testar se o comando é resiliente a erros de banco de dados"""
        # Criar usuário e solicitação
        user = User.objects.create_user(
            username='error_user',
            email='error@exemplo.com',
            password='pass123'
        )

        solicitacao = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Error User',
            email_solicitante='error@exemplo.com',
            telefone_solicitante='11999999999',
            endereco='Rua Error, 123',
            cidade='São Paulo',
            cep='01234-567',
            tipo_servico='pintura_interior',
            descricao_servico='Pintura error',
        )

        out = StringIO()

        # Simular erro na operação save
        with patch.object(SolicitacaoOrcamento, 'save', side_effect=Exception('Database error')):
            # Comando deve continuar executando mesmo com erros
            call_command('vincular_orcamentos_orfaos', stdout=out)

        output = out.getvalue()
        self.assertIn('Erro ao processar', output)

    def test_comando_verbosidade_diferente(self):
        """Testar comando com diferentes níveis de verbosidade"""
        # Criar dados de teste
        user = User.objects.create_user(
            username='verbose_user',
            email='verbose@exemplo.com',
            password='pass123'
        )

        SolicitacaoOrcamento.objects.create(
            nome_solicitante='Verbose User',
            email_solicitante='verbose@exemplo.com',
            telefone_solicitante='11999999999',
            endereco='Rua Verbose, 123',
            cidade='São Paulo',
            cep='01234-567',
            tipo_servico='pintura_interior',
            descricao_servico='Pintura verbose',
        )

        # Testar verbosidade 0 (silencioso)
        out = StringIO()
        call_command('vincular_orcamentos_orfaos', verbosity=0, stdout=out)
        output = out.getvalue()
        # Com verbosidade 0, deve ter menos output
        self.assertNotIn('🔍', output)

        # Testar verbosidade 2 (detalhado)
        out = StringIO()
        call_command('vincular_orcamentos_orfaos', verbosity=2, stdout=out)
        output = out.getvalue()
        # Com verbosidade 2, deve ter output detalhado
        self.assertIn('Iniciando busca', output)
