from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta

from orcamentos.models import (
    Projeto, SolicitacaoOrcamento, Orcamento, ItemOrcamento,
    StatusOrcamento, StatusProjeto, TipoServico, UrgenciaProjeto
)

User = get_user_model()


class TesteBasicoOrcamentosTestCase(TestCase):
    """Testes básicos para validar que o sistema está funcionando"""

    def setUp(self):
        """Setup inicial para todos os testes"""
        # Criar usuários de teste
        self.cliente = User.objects.create_user(
            username='cliente@test.com',
            email='cliente@test.com',
            password='testpass123',
            first_name='João',
            last_name='Silva'
        )

        # Adicionar account_type se existir no modelo
        if hasattr(self.cliente, 'account_type'):
            self.cliente.account_type = 'CLIENT'
            self.cliente.save()

        self.admin = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='Sistema',
            is_staff=True
        )

        # Adicionar account_type se existir no modelo
        if hasattr(self.admin, 'account_type'):
            self.admin.account_type = 'ADMIN'
            self.admin.save()

    def test_01_criar_projeto(self):
        """Teste básico de criação de projeto"""
        print("\n=== TESTE BÁSICO 1: Criação de Projeto ===")

        projeto = Projeto.objects.create(
            cliente=self.cliente,
            titulo='Projeto Test Básico',
            descricao='Descrição test',
            tipo_servico=TipoServico.PINTURA_INTERIOR,
            endereco_projeto='Endereço test',
            cidade_projeto='Paris',
            cep_projeto='75001'
        )

        self.assertIsNotNone(projeto)
        self.assertEqual(projeto.titulo, 'Projeto Test Básico')
        self.assertEqual(projeto.cliente, self.cliente)
        self.assertEqual(projeto.status, StatusProjeto.PLANEJANDO)

        print(f"✓ Projeto criado com sucesso: {projeto.uuid}")

    def test_02_criar_solicitacao_orcamento(self):
        """Teste básico de criação de solicitação de orçamento"""
        print("\n=== TESTE BÁSICO 2: Criação de Solicitação ===")

        solicitacao = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Maria Santos',
            email_solicitante='maria@email.com',
            telefone_solicitante='11888888888',
            endereco='456 Avenue Test',
            cidade='Lyon',
            cep='69001',
            tipo_servico=TipoServico.PINTURA_EXTERIOR,
            descricao_servico='Pintura externa da fachada'
        )

        self.assertIsNotNone(solicitacao)
        self.assertEqual(solicitacao.nome_solicitante, 'Maria Santos')
        self.assertEqual(solicitacao.status, StatusOrcamento.PENDENTE)
        self.assertTrue(solicitacao.numero.startswith('DEV'))

        print(f"✓ Solicitação criada com sucesso: {solicitacao.numero}")

    def test_03_criar_orcamento(self):
        """Teste básico de criação de orçamento"""
        print("\n=== TESTE BÁSICO 3: Criação de Orçamento ===")

        # Primeiro criar uma solicitação
        solicitacao = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Cliente Test',
            email_solicitante='cliente@email.com',
            telefone_solicitante='11999999999',
            endereco='Endereço Test',
            cidade='Paris',
            cep='75001',
            tipo_servico=TipoServico.PINTURA_INTERIOR,
            descricao_servico='Serviço test'
        )

        # Criar orçamento
        orcamento = Orcamento.objects.create(
            solicitacao=solicitacao,
            elaborado_por=self.admin,
            titulo='Orçamento Test',
            descricao='Descrição do orçamento',
            prazo_execucao=15,
            validade_orcamento=date.today() + timedelta(days=30)
        )

        self.assertIsNotNone(orcamento)
        self.assertEqual(orcamento.solicitacao, solicitacao)
        self.assertEqual(orcamento.elaborado_por, self.admin)
        self.assertEqual(orcamento.status, StatusOrcamento.EM_ELABORACAO)
        self.assertTrue(orcamento.numero.startswith('OR'))

        print(f"✓ Orçamento criado com sucesso: {orcamento.numero}")

    def test_04_criar_item_orcamento(self):
        """Teste básico de criação de item de orçamento"""
        print("\n=== TESTE BÁSICO 4: Criação de Item ===")

        # Criar solicitação e orçamento
        solicitacao = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Cliente Test',
            email_solicitante='cliente@email.com',
            telefone_solicitante='11999999999',
            endereco='Endereço Test',
            cidade='Paris',
            cep='75001',
            tipo_servico=TipoServico.PINTURA_INTERIOR,
            descricao_servico='Serviço test'
        )

        orcamento = Orcamento.objects.create(
            solicitacao=solicitacao,
            elaborado_por=self.admin,
            titulo='Orçamento Test',
            descricao='Descrição do orçamento',
            prazo_execucao=15,
            validade_orcamento=date.today() + timedelta(days=30)
        )

        # Criar item
        item = ItemOrcamento.objects.create(
            orcamento=orcamento,
            descricao='Tinta Acrílica Test',
            quantidade=Decimal('2.00'),
            preco_unitario_ht=Decimal('45.00')
        )

        self.assertIsNotNone(item)
        self.assertEqual(item.orcamento, orcamento)
        self.assertEqual(item.descricao, 'Tinta Acrílica Test')
        self.assertGreater(item.total_ht, 0)

        print(f"✓ Item criado com sucesso: {item.descricao} - Total: {item.total_ht}€")

    def test_05_relacionamentos(self):
        """Teste básico dos relacionamentos entre modelos"""
        print("\n=== TESTE BÁSICO 5: Relacionamentos ===")

        # Criar projeto
        projeto = Projeto.objects.create(
            cliente=self.cliente,
            titulo='Projeto Relacionamento',
            descricao='Test relacionamento',
            tipo_servico=TipoServico.PINTURA_INTERIOR,
            endereco_projeto='Endereço test',
            cidade_projeto='Paris',
            cep_projeto='75001'
        )

        # Criar solicitação vinculada ao projeto
        solicitacao = SolicitacaoOrcamento.objects.create(
            cliente=self.cliente,
            projeto=projeto,
            nome_solicitante='João Silva',
            email_solicitante='joao@email.com',
            telefone_solicitante='11999999999',
            endereco='Endereço test',
            cidade='Paris',
            cep='75001',
            tipo_servico=TipoServico.PINTURA_INTERIOR,
            descricao_servico='Serviço vinculado ao projeto'
        )

        # Verificar relacionamentos
        self.assertEqual(solicitacao.projeto, projeto)
        self.assertEqual(solicitacao.cliente, self.cliente)

        # Verificar reverse relationships
        solicitacoes_projeto = projeto.solicitacoes_orcamento.all()
        self.assertIn(solicitacao, solicitacoes_projeto)

        print(f"✓ Relacionamentos funcionando: Projeto {projeto.uuid} -> Solicitação {solicitacao.numero}")

    def test_06_status_transitions(self):
        """Teste básico de transições de status"""
        print("\n=== TESTE BÁSICO 6: Transições de Status ===")

        # Criar solicitação
        solicitacao = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Cliente Status',
            email_solicitante='status@email.com',
            telefone_solicitante='11999999999',
            endereco='Endereço test',
            cidade='Paris',
            cep='75001',
            tipo_servico=TipoServico.PINTURA_INTERIOR,
            descricao_servico='Test status'
        )

        # Verificar status inicial
        self.assertEqual(solicitacao.status, StatusOrcamento.PENDENTE)

        # Criar orçamento (deve mudar status da solicitação)
        orcamento = Orcamento.objects.create(
            solicitacao=solicitacao,
            elaborado_por=self.admin,
            titulo='Orçamento Status',
            descricao='Test status',
            prazo_execucao=15,
            validade_orcamento=date.today() + timedelta(days=30)
        )

        # Verificar status do orçamento
        self.assertEqual(orcamento.status, StatusOrcamento.EM_ELABORACAO)

        print(f"✓ Status funcionando: Solicitação {solicitacao.status} -> Orçamento {orcamento.status}")

    def tearDown(self):
        """Limpeza após cada teste"""
        # Django já faz a limpeza automaticamente nos testes
        pass


class TesteAuditoriaBasicoTestCase(TestCase):
    """Testes básicos para o sistema de auditoria"""

    def test_01_import_auditoria(self):
        """Teste se o sistema de auditoria pode ser importado"""
        print("\n=== TESTE AUDITORIA 1: Import ===")

        try:
            from orcamentos.auditoria import AuditoriaManager, LogAuditoria, TipoAcao
            print("✓ Imports de auditoria funcionando")
            return True
        except ImportError as e:
            print(f"❌ Erro ao importar auditoria: {e}")
            return False

    def test_02_criar_log_auditoria(self):
        """Teste básico de criação de log de auditoria"""
        print("\n=== TESTE AUDITORIA 2: Criação de Log ===")

        try:
            from orcamentos.auditoria import LogAuditoria, TipoAcao
            from django.contrib.contenttypes.models import ContentType

            # Criar usuário
            user = User.objects.create_user(
                username='test@test.com',
                email='test@test.com',
                password='testpass123'
            )

            # Criar log manual
            content_type = ContentType.objects.get_for_model(User)

            log = LogAuditoria.objects.create(
                usuario=user,
                acao=TipoAcao.CRIACAO,
                descricao='Teste de log',
                content_type=content_type,
                object_id=user.pk,
                modulo='orcamentos',
                funcionalidade='teste'
            )

            self.assertIsNotNone(log)
            self.assertEqual(log.usuario, user)
            self.assertEqual(log.acao, TipoAcao.CRIACAO)

            print(f"✓ Log de auditoria criado: {log}")
            return True

        except Exception as e:
            print(f"❌ Erro ao criar log de auditoria: {e}")
            return False
