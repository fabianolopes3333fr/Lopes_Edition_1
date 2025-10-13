"""
Script para limpar todas as migrações do projeto
Execute com: python limpar_migracoes.py
"""
import os
import shutil
from pathlib import Path

# Cores para terminal Windows
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    RESET = '\033[0m'
    NEGRITO = '\033[1m'

def print_colorido(texto, cor):
    """Imprime texto colorido"""
    print(f"{cor}{texto}{Cores.RESET}")

def confirmar_acao():
    """Pede confirmação do usuário"""
    print_colorido("\n⚠️  ATENÇÃO: Esta ação irá deletar TODAS as migrações!", Cores.VERMELHO + Cores.NEGRITO)
    print_colorido("Isso apagará:", Cores.AMARELO)
    print("  • Todas as migrações de todos os apps")
    print("  • Arquivos __pycache__ relacionados")
    print("  • O banco de dados (db.sqlite3)")
    print()
    print_colorido("Você precisará:", Cores.AZUL)
    print("  1. Criar novas migrações (python manage.py makemigrations)")
    print("  2. Aplicar as migrações (python manage.py migrate)")
    print("  3. Criar novo superusuário (python manage.py createsuperuser)")
    print()
    
    resposta = input("Deseja continuar? Digite 'SIM' para confirmar: ")
    return resposta.strip().upper() == 'SIM'

def encontrar_apps_django():
    """Encontra todos os apps Django no projeto"""
    apps = []
    base_dir = Path(__file__).parent
    
    # Lista de apps conhecidos
    apps_conhecidos = [
        'accounts',
        'blog',
        'clientes',
        'contato',
        'home',
        'orcamentos',
        'profiles',
        'projetos'
    ]
    
    for app in apps_conhecidos:
        app_path = base_dir / app
        if app_path.exists() and app_path.is_dir():
            migrations_path = app_path / 'migrations'
            if migrations_path.exists():
                apps.append({
                    'nome': app,
                    'path': app_path,
                    'migrations_path': migrations_path
                })
    
    return apps

def deletar_arquivos_migracao(migrations_path):
    """Deleta arquivos de migração, mantendo __init__.py"""
    arquivos_deletados = []
    
    if not migrations_path.exists():
        return arquivos_deletados
    
    for arquivo in migrations_path.iterdir():
        # Manter __init__.py
        if arquivo.name == '__init__.py':
            continue
        
        # Deletar arquivos de migração (*.py)
        if arquivo.is_file() and arquivo.suffix == '.py':
            try:
                arquivo.unlink()
                arquivos_deletados.append(arquivo.name)
            except Exception as e:
                print_colorido(f"  ✗ Erro ao deletar {arquivo.name}: {e}", Cores.VERMELHO)
        
        # Deletar __pycache__
        elif arquivo.is_dir() and arquivo.name == '__pycache__':
            try:
                shutil.rmtree(arquivo)
                arquivos_deletados.append('__pycache__/')
            except Exception as e:
                print_colorido(f"  ✗ Erro ao deletar __pycache__: {e}", Cores.VERMELHO)
    
    return arquivos_deletados

def deletar_banco_dados():
    """Deleta o banco de dados SQLite"""
    base_dir = Path(__file__).parent
    db_path = base_dir / 'db.sqlite3'
    
    if db_path.exists():
        try:
            db_path.unlink()
            print_colorido("  ✓ Banco de dados deletado", Cores.VERDE)
            return True
        except Exception as e:
            print_colorido(f"  ✗ Erro ao deletar banco: {e}", Cores.VERMELHO)
            return False
    else:
        print_colorido("  ℹ Banco de dados não encontrado", Cores.AMARELO)
        return True

def main():
    """Função principal"""
    print_colorido("=" * 80, Cores.AZUL)
    print_colorido("LIMPEZA DE MIGRAÇÕES DO DJANGO", Cores.AZUL + Cores.NEGRITO)
    print_colorido("=" * 80, Cores.AZUL)
    
    # Confirmar ação
    if not confirmar_acao():
        print_colorido("\n✗ Operação cancelada pelo usuário", Cores.AMARELO)
        return
    
    print()
    print_colorido("=" * 80, Cores.AZUL)
    print_colorido("INICIANDO LIMPEZA...", Cores.AZUL + Cores.NEGRITO)
    print_colorido("=" * 80, Cores.AZUL)
    print()
    
    # Encontrar apps
    apps = encontrar_apps_django()
    print_colorido(f"📦 Encontrados {len(apps)} apps Django", Cores.AZUL)
    print()
    
    # Deletar migrações de cada app
    total_arquivos = 0
    for app in apps:
        print_colorido(f"🔧 Processando app: {app['nome']}", Cores.AZUL)
        arquivos = deletar_arquivos_migracao(app['migrations_path'])
        
        if arquivos:
            for arquivo in arquivos:
                print_colorido(f"  ✓ Deletado: {arquivo}", Cores.VERDE)
            total_arquivos += len(arquivos)
        else:
            print_colorido(f"  ℹ Nenhuma migração encontrada", Cores.AMARELO)
        print()
    
    # Deletar banco de dados
    print_colorido("🗄️  Deletando banco de dados...", Cores.AZUL)
    deletar_banco_dados()
    print()
    
    # Resumo
    print_colorido("=" * 80, Cores.VERDE)
    print_colorido("✓ LIMPEZA CONCLUÍDA!", Cores.VERDE + Cores.NEGRITO)
    print_colorido("=" * 80, Cores.VERDE)
    print()
    print_colorido(f"Total de arquivos deletados: {total_arquivos}", Cores.VERDE)
    print()
    
    # Próximos passos
    print_colorido("📝 PRÓXIMOS PASSOS:", Cores.AZUL + Cores.NEGRITO)
    print()
    print_colorido("1. Criar novas migrações:", Cores.AZUL)
    print("   python manage.py makemigrations")
    print()
    print_colorido("2. Aplicar migrações:", Cores.AZUL)
    print("   python manage.py migrate")
    print()
    print_colorido("3. Criar superusuário:", Cores.AZUL)
    print("   python manage.py createsuperuser")
    print()
    print_colorido("4. (Opcional) Carregar dados iniciais:", Cores.AZUL)
    print("   python manage.py loaddata fixtures/initial_data.json")
    print()
    print_colorido("=" * 80, Cores.VERDE)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_colorido("\n✗ Operação cancelada pelo usuário (Ctrl+C)", Cores.AMARELO)
    except Exception as e:
        print()
        print_colorido(f"\n✗ Erro inesperado: {e}", Cores.VERMELHO)
        import traceback
        traceback.print_exc()

