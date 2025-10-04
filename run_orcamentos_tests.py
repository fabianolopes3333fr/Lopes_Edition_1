#!/usr/bin/env python
"""
Script principal para executar testes do fluxo de orçamentos e sistema de auditoria
Uso: python run_orcamentos_tests.py [opções]
"""

import os
import sys
import django
import subprocess
from datetime import datetime
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test.utils import get_runner
from django.conf import settings
from django.core.management import call_command
from orcamentos.monitor_auditoria import MonitorOrcamentos


class TestRunner:
    """Executor de testes para o sistema de orçamentos"""

    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.relatorio_pasta = 'logs/testes'
        self.criar_diretorios()

    def criar_diretorios(self):
        """Cria diretórios necessários"""
        os.makedirs(self.relatorio_pasta, exist_ok=True)
        os.makedirs('logs', exist_ok=True)

    def executar_testes_fluxo(self):
        """Executa testes de fluxo de orçamentos"""
        print("🧪 Executando testes de fluxo de orçamentos...")

        # Configurar runner de testes
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=2, interactive=False)

        # Executar testes específicos do fluxo - corrigir caminho
        failures = test_runner.run_tests([
            "orcamentos.tests.test_fluxo_orcamentos.FluxoOrcamentosTestCase",
        ])

        if failures:
            print("❌ Alguns testes falharam!")
            return False
        else:
            print("✅ Todos os testes de fluxo passaram!")
            return True

    def executar_testes_unitarios(self):
        """Executa testes unitários do app orcamentos"""
        print("🔬 Executando testes unitários...")

        try:
            # Executar todos os testes do app orcamentos
            result = subprocess.run([
                sys.executable, 'manage.py', 'test', 'orcamentos',
                '--verbosity=2', '--keepdb'
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Testes unitários passaram!")
                return True
            else:
                print("❌ Testes unitários falharam!")
                print(result.stdout)
                print(result.stderr)
                return False

        except Exception as e:
            print(f"❌ Erro ao executar testes unitários: {e}")
            return False

    def validar_migrações(self):
        """Valida se todas as migrações estão aplicadas"""
        print("📋 Validando migrações...")

        try:
            # Verificar migrações pendentes
            result = subprocess.run([
                sys.executable, 'manage.py', 'showmigrations', '--plan'
            ], capture_output=True, text=True)

            if '[X]' in result.stdout and '[ ]' not in result.stdout:
                print("✅ Todas as migrações estão aplicadas!")
                return True
            else:
                print("⚠️ Existem migrações pendentes!")
                print(result.stdout)
                return False

        except Exception as e:
            print(f"❌ Erro ao verificar migrações: {e}")
            return False

    def executar_collectstatic(self):
        """Executa collectstatic para validar arquivos estáticos"""
        print("📁 Validando arquivos estáticos...")

        try:
            result = subprocess.run([
                sys.executable, 'manage.py', 'collectstatic',
                '--noinput', '--dry-run'
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Arquivos estáticos válidos!")
                return True
            else:
                print("❌ Problemas com arquivos estáticos!")
                print(result.stderr)
                return False

        except Exception as e:
            print(f"❌ Erro ao validar arquivos estáticos: {e}")
            return False

    def gerar_relatorio_auditoria(self):
        """Gera relatório de auditoria"""
        print("📊 Gerando relatório de auditoria...")

        try:
            monitor = MonitorOrcamentos()

            # Relatório diário
            relatorio_diario = monitor.gerar_relatorio_diario()
            arquivo_diario = monitor.salvar_relatorio(
                relatorio_diario,
                f"auditoria_diario_{self.timestamp}.json"
            )

            # Relatório semanal
            relatorio_semanal = monitor.gerar_relatorio_semanal()
            arquivo_semanal = monitor.salvar_relatorio(
                relatorio_semanal,
                f"auditoria_semanal_{self.timestamp}.json"
            )

            print(f"✅ Relatórios de auditoria gerados!")
            print(f"   - Diário: {arquivo_diario}")
            print(f"   - Semanal: {arquivo_semanal}")

            return True

        except Exception as e:
            print(f"❌ Erro ao gerar relatórios de auditoria: {e}")
            return False

    def verificar_integridade_dados(self):
        """Verifica integridade dos dados"""
        print("🔍 Verificando integridade dos dados...")

        try:
            from orcamentos.models import Projeto, SolicitacaoOrcamento, Orcamento

            # Verificar projetos órfãos
            projetos_sem_cliente = Projeto.objects.filter(cliente__isnull=True).count()

            # Verificar solicitações órfãs
            solicitacoes_sem_referencia = SolicitacaoOrcamento.objects.filter(
                cliente__isnull=True,
                projeto__isnull=True
            ).count()

            # Verificar orçamentos sem solicitação
            orcamentos_orfaos = Orcamento.objects.filter(solicitacao__isnull=True).count()

            problemas = []
            if projetos_sem_cliente > 0:
                problemas.append(f"{projetos_sem_cliente} projetos sem cliente")

            if solicitacoes_sem_referencia > 0:
                problemas.append(f"{solicitacoes_sem_referencia} solicitações sem referência")

            if orcamentos_orfaos > 0:
                problemas.append(f"{orcamentos_orfaos} orçamentos órfãos")

            if problemas:
                print("⚠️ Problemas de integridade encontrados:")
                for problema in problemas:
                    print(f"   - {problema}")
                return False
            else:
                print("✅ Integridade dos dados OK!")
                return True

        except Exception as e:
            print(f"❌ Erro ao verificar integridade: {e}")
            return False

    def executar_linting(self):
        """Executa verificações de código"""
        print("🔧 Executando verificações de código...")

        try:
            # Verificar se flake8 está disponível
            result = subprocess.run(['flake8', '--version'],
                                  capture_output=True, text=True)

            if result.returncode != 0:
                print("⚠️ flake8 não encontrado, pulando verificação de código")
                return True

            # Executar flake8 no app orcamentos
            result = subprocess.run([
                'flake8', 'orcamentos/', '--max-line-length=100',
                '--exclude=migrations,__pycache__'
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Código em conformidade com PEP8!")
                return True
            else:
                print("⚠️ Problemas de estilo encontrados:")
                print(result.stdout)
                return True  # Não falhar por problemas de estilo

        except Exception as e:
            print(f"⚠️ Erro ao executar linting: {e}")
            return True  # Não falhar se linting não funcionar

    def gerar_relatorio_completo(self, resultados):
        """Gera relatório completo da execução"""
        relatorio = {
            'timestamp': self.timestamp,
            'data_execucao': datetime.now().isoformat(),
            'resultados': resultados,
            'resumo': {
                'total_verificacoes': len(resultados),
                'sucessos': sum(1 for r in resultados.values() if r),
                'falhas': sum(1 for r in resultados.values() if not r),
                'taxa_sucesso': sum(1 for r in resultados.values() if r) / len(resultados) * 100
            }
        }

        arquivo_relatorio = os.path.join(
            self.relatorio_pasta,
            f"relatorio_completo_{self.timestamp}.json"
        )

        with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)

        print(f"\n📋 Relatório completo salvo em: {arquivo_relatorio}")
        return arquivo_relatorio

    def executar_suite_completa(self):
        """Executa suite completa de testes e verificações"""
        print("🚀 Iniciando suite completa de testes do sistema de orçamentos")
        print("=" * 60)

        resultados = {}

        # 1. Validar migrações
        resultados['migracoes'] = self.validar_migrações()

        # 2. Verificar integridade dos dados
        resultados['integridade_dados'] = self.verificar_integridade_dados()

        # 3. Executar testes de fluxo
        resultados['testes_fluxo'] = self.executar_testes_fluxo()

        # 4. Executar testes unitários
        resultados['testes_unitarios'] = self.executar_testes_unitarios()

        # 5. Validar arquivos estáticos
        resultados['arquivos_estaticos'] = self.executar_collectstatic()

        # 6. Verificações de código
        resultados['linting'] = self.executar_linting()

        # 7. Gerar relatórios de auditoria
        resultados['relatorio_auditoria'] = self.gerar_relatorio_auditoria()

        # Gerar relatório final
        arquivo_relatorio = self.gerar_relatorio_completo(resultados)

        # Mostrar resumo
        print("\n" + "=" * 60)
        print("📊 RESUMO DA EXECUÇÃO")
        print("=" * 60)

        for verificacao, sucesso in resultados.items():
            status = "✅ PASSOU" if sucesso else "❌ FALHOU"
            print(f"{verificacao.replace('_', ' ').title()}: {status}")

        taxa_sucesso = sum(1 for r in resultados.values() if r) / len(resultados) * 100
        print(f"\nTaxa de sucesso: {taxa_sucesso:.1f}%")

        if all(resultados.values()):
            print("\n🎉 Todos os testes e verificações passaram!")
            return True
        else:
            print("\n⚠️ Algumas verificações falharam. Verifique os logs acima.")
            return False


def main():
    """Função principal"""
    import argparse

    parser = argparse.ArgumentParser(description='Executor de testes do sistema de orçamentos')
    parser.add_argument('--fluxo', action='store_true',
                        help='Executar apenas testes de fluxo')
    parser.add_argument('--unitarios', action='store_true',
                        help='Executar apenas testes unitários')
    parser.add_argument('--auditoria', action='store_true',
                        help='Gerar apenas relatórios de auditoria')
    parser.add_argument('--integridade', action='store_true',
                        help='Verificar apenas integridade dos dados')
    parser.add_argument('--completo', action='store_true',
                        help='Executar suite completa (padrão)')

    args = parser.parse_args()

    runner = TestRunner()

    try:
        if args.fluxo:
            success = runner.executar_testes_fluxo()
        elif args.unitarios:
            success = runner.executar_testes_unitarios()
        elif args.auditoria:
            success = runner.gerar_relatorio_auditoria()
        elif args.integridade:
            success = runner.verificar_integridade_dados()
        else:
            # Executar suite completa por padrão
            success = runner.executar_suite_completa()

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
