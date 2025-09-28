import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Setup social applications for allauth'

    def handle(self, *args, **options):
        site = Site.objects.get_current()

        # Pegar credenciais do .env
        google_client_id = os.getenv('GOOGLE_OAUTH2_CLIENT_ID', 'temporary-google-client-id')
        google_secret = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET', 'temporary-google-secret')

        # Criar aplicação Google
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            name='Google',
            defaults={
                'client_id': google_client_id,
                'secret': google_secret,
            }
        )

        # Se já existe, atualizar com as credenciais do .env
        if not created:
            google_app.client_id = google_client_id
            google_app.secret = google_secret
            google_app.save()

        google_app.sites.add(site)

        if created:
            self.stdout.write(
                self.style.SUCCESS('✓ Google social app created successfully')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✓ Google social app updated successfully')
            )

        # Criar aplicação Facebook (com credenciais temporárias)
        facebook_app, created = SocialApp.objects.get_or_create(
            provider='facebook',
            name='Facebook',
            defaults={
                'client_id': 'temporary-facebook-client-id',
                'secret': 'temporary-facebook-secret',
            }
        )
        facebook_app.sites.add(site)

        if created:
            self.stdout.write(
                self.style.SUCCESS('✓ Facebook social app created successfully')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠ Facebook social app already exists')
            )

        self.stdout.write(
            self.style.SUCCESS('\n🎉 Social apps setup completed!')
        )

        if google_client_id != 'temporary-google-client-id':
            self.stdout.write(
                self.style.SUCCESS('✓ Google credentials loaded from .env file')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠ Using temporary Google credentials')
            )