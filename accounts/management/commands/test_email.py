"""
Comando para testar o sistema de envio de emails.
Uso: python manage.py test_email seu.email@teste.com
"""
from django.core.management.base import BaseCommand
from django.http import HttpRequest
from utils.emails.sistema_email import _send_mail, _get_smtp_connection, _get_from_email, _get_active_email_settings
from django.conf import settings


class Command(BaseCommand):
    help = 'Testa o sistema de envio de emails e exibe configurações ativas'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, nargs='?', help='Email destinatário para teste')
        parser.add_argument('--info', action='store_true', help='Apenas exibe informações de configuração')

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('🔍 DIAGNÓSTICO DO SISTEMA DE EMAIL'))
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write('')

        # 1. Verificar Backend
        backend = getattr(settings, 'EMAIL_BACKEND', 'Não configurado')
        self.stdout.write(self.style.HTTP_INFO('📧 Backend Ativo:'))
        self.stdout.write(f'   {backend}')
        
        if 'console' in backend.lower():
            self.stdout.write(self.style.WARNING('   ⚠️  Backend CONSOLE - emails não são enviados, apenas exibidos no console'))
        elif 'locmem' in backend.lower():
            self.stdout.write(self.style.WARNING('   ⚠️  Backend LOCMEM - emails armazenados em memória (testes)'))
        elif 'smtp' in backend.lower():
            self.stdout.write(self.style.SUCCESS('   ✅ Backend SMTP - pronto para enviar emails reais'))
        else:
            self.stdout.write(self.style.WARNING('   ⚠️  Backend desconhecido'))
        
        self.stdout.write('')

        # 2. Verificar EmailSettings do DB
        self.stdout.write(self.style.HTTP_INFO('🗄️  Configuração do Banco de Dados:'))
        cfg = _get_active_email_settings()
        
        if cfg:
            self.stdout.write(self.style.SUCCESS('   ✅ EmailSettings encontrado e ATIVO'))
            self.stdout.write(f'   Host: {cfg.host}')
            self.stdout.write(f'   Port: {cfg.port}')
            self.stdout.write(f'   Username: {cfg.username}')
            self.stdout.write(f'   Password: {"*" * len(cfg.password) if cfg.password else "Não configurado"}')
            self.stdout.write(f'   Use TLS: {cfg.use_tls}')
            self.stdout.write(f'   Use SSL: {cfg.use_ssl}')
            self.stdout.write(f'   From Email: {cfg.from_email or "Não configurado"}')
            self.stdout.write(f'   Ativo: {cfg.actif}')
        else:
            self.stdout.write(self.style.ERROR('   ❌ Nenhum EmailSettings ativo encontrado'))
            self.stdout.write('   Configure em: /admin/system_config/emailsettings/')
        
        self.stdout.write('')

        # 3. Verificar settings.py fallback
        self.stdout.write(self.style.HTTP_INFO('⚙️  Configuração do settings.py (fallback):'))
        self.stdout.write(f'   EMAIL_HOST: {getattr(settings, "EMAIL_HOST", "Não configurado")}')
        self.stdout.write(f'   EMAIL_PORT: {getattr(settings, "EMAIL_PORT", "Não configurado")}')
        self.stdout.write(f'   EMAIL_HOST_USER: {getattr(settings, "EMAIL_HOST_USER", "Não configurado")}')
        self.stdout.write(f'   EMAIL_USE_TLS: {getattr(settings, "EMAIL_USE_TLS", "Não configurado")}')
        self.stdout.write(f'   EMAIL_USE_SSL: {getattr(settings, "EMAIL_USE_SSL", "Não configurado")}')
        self.stdout.write(f'   DEFAULT_FROM_EMAIL: {getattr(settings, "DEFAULT_FROM_EMAIL", "Não configurado")}')
        self.stdout.write('')

        # 4. Verificar from_email resolvido
        from_email = _get_from_email()
        self.stdout.write(self.style.HTTP_INFO('📮 From Email Resolvido:'))
        if from_email:
            self.stdout.write(self.style.SUCCESS(f'   ✅ {from_email}'))
        else:
            self.stdout.write(self.style.ERROR('   ❌ Nenhum from_email configurado'))
        self.stdout.write('')

        # 5. Se --info, parar aqui
        if options['info']:
            return

        # 6. Testar envio se email fornecido
        email = options.get('email')
        if not email:
            self.stdout.write(self.style.WARNING('ℹ️  Para testar envio de email, forneça um destinatário:'))
            self.stdout.write('   python manage.py test_email seu.email@teste.com')
            self.stdout.write('')
            self.stdout.write('   Ou use --info para apenas ver configurações:')
            self.stdout.write('   python manage.py test_email --info')
            return

        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING(f'📨 TESTANDO ENVIO PARA: {email}'))
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write('')

        try:
            result = _send_mail(
                subject="Teste - LOPES PEINTURE Sistema de Email",
                plain_message="Este é um email de teste do sistema LOPES PEINTURE.\n\nSe você recebeu este email, o sistema está funcionando corretamente!",
                html_message="""
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h1 style="color: #dc2626;">✅ Teste de Email - LOPES PEINTURE</h1>
                    <p>Este é um email de teste do sistema.</p>
                    <p><strong>Se você recebeu este email, o sistema está funcionando corretamente!</strong></p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">Sistema de Email Centralizado - LOPES PEINTURE</p>
                </body>
                </html>
                """,
                recipients=[email]
            )
            
            if result:
                self.stdout.write(self.style.SUCCESS(f'✅ Email enviado com sucesso para {email}'))
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('Verifique a caixa de entrada do destinatário.'))
                self.stdout.write(self.style.WARNING('⚠️  Se não chegou, verifique também a pasta de SPAM/LIXO'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Falha ao enviar email para {email}'))
                self.stdout.write('')
                self.stdout.write('Verifique os logs em logs/accounts.log para mais detalhes')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ ERRO ao enviar email: {str(e)}'))
            self.stdout.write('')
            self.stdout.write('Possíveis causas:')
            self.stdout.write('1. Credenciais SMTP incorretas')
            self.stdout.write('2. Firewall bloqueando conexão')
            self.stdout.write('3. Configuração TLS/SSL incorreta')
            self.stdout.write('4. Host/Port incorretos')

