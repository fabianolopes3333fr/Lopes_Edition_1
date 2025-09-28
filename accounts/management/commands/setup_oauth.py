from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from decouple import config


class Command(BaseCommand):
    help = 'Configura automaticamente Google e Microsoft OAuth'

    def handle(self, *args, **options):
        # Obter credenciais do Google OAuth do .env
        google_client_id = config('GOOGLE_OAUTH2_CLIENT_ID', default='')
        google_client_secret = config('GOOGLE_OAUTH2_CLIENT_SECRET', default='')

        # Obter credenciais do Microsoft OAuth do .env
        microsoft_client_id = config('MICROSOFT_CLIENT_ID', default='')
        microsoft_client_secret = config('MICROSOFT_CLIENT_SECRET', default='')

        # Obter ou criar o site
        site = Site.objects.get_or_create(
            pk=2,
            defaults={
                'domain': 'localhost:8000',
                'name': 'Lopes Peinture - Desenvolvimento'
            }
        )[0]

        # Configurar Google OAuth se as credenciais estiverem disponíveis
        if google_client_id and google_client_secret:
            google_app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Google OAuth - Lopes Peinture',
                    'client_id': google_client_id,
                    'secret': google_client_secret,
                }
            )

            if not created:
                google_app.client_id = google_client_id
                google_app.secret = google_client_secret
                google_app.save()

            google_app.sites.add(site)

            action = 'criada' if created else 'atualizada'
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Aplicação Google OAuth {action} com sucesso!'
                )
            )
            self.stdout.write(f'   Client ID: {google_client_id[:20]}...')
        else:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Google OAuth: Credenciais não encontradas no .env'
                )
            )

        # Configurar Microsoft OAuth se as credenciais estiverem disponíveis
        if microsoft_client_id and microsoft_client_secret and microsoft_client_id != 'your-microsoft-client-id':
            microsoft_app, created = SocialApp.objects.get_or_create(
                provider='microsoft',
                defaults={
                    'name': 'Microsoft OAuth - Lopes Peinture',
                    'client_id': microsoft_client_id,
                    'secret': microsoft_client_secret,
                }
            )

            if not created:
                microsoft_app.client_id = microsoft_client_id
                microsoft_app.secret = microsoft_client_secret
                microsoft_app.save()

            microsoft_app.sites.add(site)

            action = 'criada' if created else 'atualizada'
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Aplicação Microsoft OAuth {action} com sucesso!'
                )
            )
            self.stdout.write(f'   Client ID: {microsoft_client_id[:20]}...')
        else:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Microsoft OAuth: Credenciais não encontradas ou são valores padrão'
                )
            )
            self.stdout.write(
                self.style.HTTP_INFO(
                    '   Para configurar Microsoft OAuth:'
                )
            )
            self.stdout.write('   1. Vá para https://portal.azure.com/')
            self.stdout.write('   2. Registre uma nova aplicação')
            self.stdout.write('   3. Configure a URI de redirecionamento: http://localhost:8000/accounts/microsoft/login/callback/')
            self.stdout.write('   4. Adicione MICROSOFT_CLIENT_ID e MICROSOFT_CLIENT_SECRET no .env')

        self.stdout.write(f'📍 Site configurado: {site.domain}')
