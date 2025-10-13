from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

from orcamentos.models import Projeto, SolicitacaoOrcamento, Orcamento
from orcamentos.auditoria import AuditoriaManager, LogAuditoria, TipoAcao
from orcamentos.monitor_auditoria import MonitorOrcamentos

User = get_user_model()


class AuditoriaTestCase(TestCase):
    """Testes para o sistema de auditoria"""

    def setUp(self):
        # Limpar cache do ContentType antes de cada teste
        ContentType.objects.clear_cache()
        
        self.user = User.objects.create_user(
            username='test@test.com',
            email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            account_type='CLIENT'
        )

        self.admin = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='Test',
            account_type='ADMIN',
            is_staff=True
        )

    def test_registrar_criacao_objeto(self):
        """Teste registro de criação de objeto"""
        projeto = Projeto.objects.create(
            cliente=self.user,
            titulo='Projeto Test',
            descricao='Descrição test',
            tipo_servico='pintura_interior',
            endereco_projeto='Endereço test',
            cidade_projeto='Paris',
            cep_projeto='75001'
        )

        # Registrar criação manualmente
        log = AuditoriaManager.registrar_criacao(
            usuario=self.user,
            objeto=projeto,
            dados_objeto={'titulo': 'Projeto Test', 'descricao': 'Descrição test'}
        )

        self.assertIsNotNone(log)
        self.assertEqual(log.usuario, self.user)
        self.assertEqual(log.acao, TipoAcao.CRIACAO)
        self.assertEqual(log.object_id, projeto.pk)
        self.assertTrue(log.sucesso)

        print(f"✓ Criação registrada: {log}")

    def test_registrar_edicao_objeto(self):
        """Teste registro de edição de objeto"""
        projeto = Projeto.objects.create(
            cliente=self.user,
            titulo='Projeto Original',
            descricao='Descrição original',
            tipo_servico='pintura_interior',
            endereco_projeto='Endereço test',
            cidade_projeto='Paris',
            cep_projeto='75001'
        )

        dados_anteriores = {
            'titulo': 'Projeto Original',
            'descricao': 'Descrição original'
        }

        # Alterar projeto
        projeto.titulo = 'Projeto Alterado'
        projeto.descricao = 'Descrição alterada'
        projeto.save()

        dados_posteriores = {
            'titulo': 'Projeto Alterado',
            'descricao': 'Descrição alterada'
        }

        # Registrar edição
        log = AuditoriaManager.registrar_edicao(
            usuario=self.admin,
            objeto=projeto,
            dados_anteriores=dados_anteriores,
            dados_posteriores=dados_posteriores
        )

        self.assertIsNotNone(log)
        self.assertEqual(log.acao, TipoAcao.EDICAO)
        self.assertIsNotNone(log.campos_alterados)
        self.assertIn('titulo', log.campos_alterados)
        self.assertIn('descricao', log.campos_alterados)

        print(f"✓ Edição registrada: {log.resumo_alteracao}")

    def test_registrar_exclusao_objeto(self):
        """Teste registro de exclusão de objeto"""
        projeto = Projeto.objects.create(
            cliente=self.user,
            titulo='Projeto Para Deletar',
            descricao='Será deletado',
            tipo_servico='pintura_interior',
            endereco_projeto='Endereço test',
            cidade_projeto='Paris',
            cep_projeto='75001'
        )

        projeto_id = projeto.pk
        dados_objeto = {'titulo': projeto.titulo, 'descricao': projeto.descricao}

        # Registrar exclusão antes de deletar
        log = AuditoriaManager.registrar_exclusao(
            usuario=self.admin,
            objeto=projeto,
            dados_objeto=dados_objeto
        )

        # Deletar projeto
        projeto.delete()

        self.assertIsNotNone(log)
        self.assertEqual(log.acao, TipoAcao.EXCLUSAO)
        self.assertEqual(log.object_id, projeto_id)
        self.assertIsNotNone(log.dados_anteriores)

        print(f"✓ Exclusão registrada: {log}")

    def test_monitor_automatico(self):
        """Teste do monitor automático de alterações"""
        monitor = MonitorOrcamentos()

        # Simular criação de projeto (o monitor deve capturar automaticamente)
        projeto = Projeto.objects.create(
            cliente=self.user,
            titulo='Projeto Monitorado',
            descricao='Teste de monitoramento',
            tipo_servico='pintura_interior',
            endereco_projeto='Endereço test',
            cidade_projeto='Paris',
            cep_projeto='75001'
        )

        # Verificar se dados foram serializados corretamente
        dados = monitor.serializar_objeto(projeto)

        self.assertIn('titulo', dados)
        self.assertIn('_modelo', dados)
        self.assertEqual(dados['titulo'], 'Projeto Monitorado')
        self.assertEqual(dados['_modelo'], 'Projeto')

        print(f"✓ Monitoramento automático funcionando")

    def test_detectar_alteracoes(self):
        """Teste detecção de alterações"""
        monitor = MonitorOrcamentos()

        dados_anteriores = {
            'titulo': 'Título Original',
            'descricao': 'Descrição Original',
            'status': 'planejando'
        }

        dados_posteriores = {
            'titulo': 'Título Alterado',
            'descricao': 'Descrição Original',  # Não alterado
            'status': 'em_andamento'
        }

        alteracoes = monitor.detectar_alteracoes(dados_anteriores, dados_posteriores)

        self.assertEqual(len(alteracoes), 2)  # titulo e status alterados
        self.assertIn('titulo', alteracoes)
        self.assertIn('status', alteracoes)
        self.assertNotIn('descricao', alteracoes)  # Não alterado

        print(f"✓ Detecção de alterações: {list(alteracoes.keys())}")

    def test_historico_objeto(self):
        """Teste obtenção de histórico de um objeto"""
        projeto = Projeto.objects.create(
            cliente=self.user,
            titulo='Projeto Histórico',
            descricao='Teste histórico',
            tipo_servico='pintura_interior',
            endereco_projeto='Endereço test',
            cidade_projeto='Paris',
            cep_projeto='75001'
        )

        # Criar alguns logs
        AuditoriaManager.registrar_criacao(self.user, projeto)
        AuditoriaManager.registrar_visualizacao(self.admin, projeto)

        # Obter histórico
        historico = AuditoriaManager.obter_historico_objeto(projeto)

        self.assertGreater(len(historico), 0)

        for log in historico:
            self.assertEqual(log.object_id, projeto.pk)

        print(f"✓ Histórico obtido: {len(historico)} registros")

    def test_atividades_usuario(self):
        """Teste obtenção de atividades de um usuário"""
        projeto = Projeto.objects.create(
            cliente=self.user,
            titulo='Projeto Atividade',
            descricao='Teste atividade',
            tipo_servico='pintura_interior',
            endereco_projeto='Endereço test',
            cidade_projeto='Paris',
            cep_projeto='75001'
        )

        # Registrar atividades
        AuditoriaManager.registrar_criacao(self.user, projeto)
        AuditoriaManager.registrar_visualizacao(self.user, projeto)

        # Obter atividades
        atividades = AuditoriaManager.obter_atividades_usuario(self.user, dias=1)

        self.assertGreater(len(atividades), 0)

        for atividade in atividades:
            self.assertEqual(atividade.usuario, self.user)

        print(f"✓ Atividades do usuário: {len(atividades)} registros")

    def test_estatisticas_periodo(self):
        """Teste geração de estatísticas por período"""
        hoje = timezone.now()
        ontem = hoje - timedelta(days=1)

        projeto = Projeto.objects.create(
            cliente=self.user,
            titulo='Projeto Estatística',
            descricao='Teste estatística',
            tipo_servico='pintura_interior',
            endereco_projeto='Endereço test',
            cidade_projeto='Paris',
            cep_projeto='75001'
        )

        # Registrar algumas ações
        AuditoriaManager.registrar_criacao(self.user, projeto)
        AuditoriaManager.registrar_visualizacao(self.admin, projeto)

        # Obter estatísticas
        stats = AuditoriaManager.obter_estatisticas_periodo(ontem, hoje)

        self.assertIn('total_acoes', stats)
        self.assertIn('acoes_por_tipo', stats)
        self.assertIn('usuarios_mais_ativos', stats)
        self.assertGreater(stats['total_acoes'], 0)

        print(f"✓ Estatísticas: {stats['total_acoes']} ações no período")

    def test_relatorio_diario(self):
        """Teste geração de relatório diário"""
        monitor = MonitorOrcamentos()

        # Criar alguns dados de teste
        projeto = Projeto.objects.create(
            cliente=self.user,
            titulo='Projeto Relatório',
            descricao='Teste relatório',
            tipo_servico='pintura_interior',
            endereco_projeto='Endereço test',
            cidade_projeto='Paris',
            cep_projeto='75001'
        )

        AuditoriaManager.registrar_criacao(self.user, projeto)

        # Gerar relatório
        relatorio = monitor.gerar_relatorio_diario()

        self.assertIn('data', relatorio)
        self.assertIn('total_atividades', relatorio)
        self.assertIn('atividades_por_tipo', relatorio)
        self.assertIn('usuarios_ativos', relatorio)

        print(f"✓ Relatório diário: {relatorio['total_atividades']} atividades")

    def test_relatorio_semanal(self):
        """Teste geração de relatório semanal"""
        monitor = MonitorOrcamentos()

        # Criar alguns dados de teste
        projeto = Projeto.objects.create(
            cliente=self.user,
            titulo='Projeto Semanal',
            descricao='Teste semanal',
            tipo_servico='pintura_interior',
            endereco_projeto='Endereço test',
            cidade_projeto='Paris',
            cep_projeto='75001'
        )

        AuditoriaManager.registrar_criacao(self.user, projeto)
        AuditoriaManager.registrar_visualizacao(self.admin, projeto)

        # Gerar relatório
        relatorio = monitor.gerar_relatorio_semanal()

        self.assertIn('periodo', relatorio)
        self.assertIn('total_atividades', relatorio)
        self.assertIn('estatisticas_diarias', relatorio)
        self.assertIn('usuarios_mais_ativos', relatorio)

        print(f"✓ Relatório semanal: {relatorio['total_atividades']} atividades")

    @patch('orcamentos.auditoria.AuditoriaManager._get_client_ip')
    def test_metadados_requisicao(self, mock_get_ip):
        """Teste captura de metadados da requisição"""
        mock_get_ip.return_value = '192.168.1.1'

        # Simular request
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        request.META['HTTP_USER_AGENT'] = 'Test Browser'
        request.session = MagicMock()
        request.session.session_key = 'test_session_123'

        projeto = Projeto.objects.create(
            cliente=self.user,
            titulo='Projeto Request',
            descricao='Teste request',
            tipo_servico='pintura_interior',
            endereco_projeto='Endereço test',
            cidade_projeto='Paris',
            cep_projeto='75001'
        )

        # Registrar com request
        log = AuditoriaManager.registrar_criacao(
            usuario=self.user,
            objeto=projeto,
            request=request
        )

        self.assertEqual(log.ip_address, '192.168.1.1')
        self.assertEqual(log.user_agent, 'Test Browser')
        self.assertEqual(log.sessao_id, 'test_session_123')

        print(f"✓ Metadados capturados: IP={log.ip_address}")

    def test_auditoria_com_erro(self):
        """Teste registro de auditoria com erro"""
        projeto = Projeto.objects.create(
            cliente=self.user,
            titulo='Projeto Erro',
            descricao='Teste erro',
            tipo_servico='pintura_interior',
            endereco_projeto='Endereço test',
            cidade_projeto='Paris',
            cep_projeto='75001'
        )

        # Registrar erro
        log = AuditoriaManager.registrar_acao(
            usuario=self.user,
            acao=TipoAcao.EDICAO,
            objeto=projeto,
            descricao='Teste de erro',
            sucesso=False,
            erro_mensagem='Erro simulado para teste'
        )

        self.assertFalse(log.sucesso)
        self.assertEqual(log.erro_mensagem, 'Erro simulado para teste')

        print(f"✓ Erro registrado: {log.erro_mensagem}")

    def test_performance_consultas(self):
        """Teste performance das consultas de auditoria"""
        from django.test.utils import override_settings
        from django.db import connection

        # Criar múltiplos projetos para testar performance
        projetos = []
        for i in range(20):
            projeto = Projeto.objects.create(
                cliente=self.user,
                titulo=f'Projeto {i}',
                descricao=f'Descrição {i}',
                tipo_servico='pintura_interior',
                endereco_projeto=f'Endereço {i}',
                cidade_projeto='Paris',
                cep_projeto='75001'
            )
            projetos.append(projeto)
            AuditoriaManager.registrar_criacao(self.user, projeto)

        # Testar consulta de histórico
        initial_queries = len(connection.queries)

        for projeto in projetos[:5]:  # Testar apenas 5 para não sobrecarregar
            historico = AuditoriaManager.obter_historico_objeto(projeto, limit=10)
            list(historico)  # Força execução da query

        final_queries = len(connection.queries)
        queries_executadas = final_queries - initial_queries

        # Deve ser eficiente (não mais que 10 queries para 5 objetos)
        self.assertLessEqual(queries_executadas, 10)

        print(f"✓ Performance OK: {queries_executadas} queries para 5 consultas")

    def tearDown(self):
        """Limpeza após cada teste"""
        LogAuditoria.objects.all().delete()
        Projeto.objects.all().delete()
        User.objects.all().delete()


if __name__ == '__main__':
    import django
    import os

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

    import unittest
    unittest.main()
