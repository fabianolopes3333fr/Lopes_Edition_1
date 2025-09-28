#!/usr/bin/env python
"""
Script para configurar os provedores de login social no Django Admin
Execute este script após configurar as credenciais OAuth2
"""

import os
import django
import sys

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from decouple import config

def setup_social_providers():
    """
    Configura os provedores sociais automaticamente
    """
    print("🔧 Configurando provedores de login social...")

    # Obter o site atual
    try:
        site = Site.objects.get(pk=2)  # SITE_ID = 2 no settings
    except Site.DoesNotExist:
        print("❌ Site não encontrado. Criando site...")
        site = Site.objects.create(
            pk=2,
            domain='localhost:8000',
            name='Lopes Peinture - Local'
        )
        print(f"✅ Site criado: {site.domain}")

    # Configurar Google OAuth2
    google_client_id = config('GOOGLE_OAUTH2_CLIENT_ID', default='')
    google_client_secret = config('GOOGLE_OAUTH2_CLIENT_SECRET', default='')

    if google_client_id and google_client_secret:
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth2',
                'client_id': google_client_id,
                'secret': google_client_secret,
            }
        )

        # Adicionar site à aplicação
        google_app.sites.add(site)

        if created:
            print("✅ Google OAuth2 configurado com sucesso!")
        else:
            print("ℹ️ Google OAuth2 já estava configurado.")
            # Atualizar credenciais se necessário
            google_app.client_id = google_client_id
            google_app.secret = google_client_secret
            google_app.save()
    else:
        print("⚠️ Credenciais do Google não encontradas no .env")

    # Configurar Microsoft OAuth2
    microsoft_client_id = config('MICROSOFT_OAUTH2_CLIENT_ID', default='')
    microsoft_client_secret = config('MICROSOFT_OAUTH2_CLIENT_SECRET', default='')

    if microsoft_client_id and microsoft_client_secret:
        microsoft_app, created = SocialApp.objects.get_or_create(
            provider='microsoft',
            defaults={
                'name': 'Microsoft OAuth2',
                'client_id': microsoft_client_id,
                'secret': microsoft_client_secret,
            }
        )

        # Adicionar site à aplicação
        microsoft_app.sites.add(site)

        if created:
            print("✅ Microsoft OAuth2 configurado com sucesso!")
        else:
            print("ℹ️ Microsoft OAuth2 já estava configurado.")
            # Atualizar credenciais se necessário
            microsoft_app.client_id = microsoft_client_id
            microsoft_app.secret = microsoft_client_secret
            microsoft_app.save()
    else:
        print("⚠️ Credenciais do Microsoft não encontradas no .env")

    print("\n🎉 Configuração concluída!")
    print("\n📋 Próximos passos:")
    print("1. Configure as credenciais OAuth2 no arquivo .env")
    print("2. Execute as migrações: python manage.py migrate")
    print("3. Execute este script novamente se necessário")
    print("4. Teste os botões de login social nos templates")

    return True

def show_callback_urls():
    """
    Mostra as URLs de callback que devem ser configuradas nos provedores
    """
    site_url = config('SITE_URL', default='http://localhost:8000')

    print("\n🔗 URLs de Callback para configurar nos provedores:")
    print("\n📍 GOOGLE OAuth2:")
    print(f"   • {site_url}/accounts/google/login/callback/")

    print("\n📍 MICROSOFT OAuth2:")
    print(f"   • {site_url}/accounts/microsoft/login/callback/")

    print("\n💡 Configure estas URLs nos respectivos consoles de desenvolvedor!")

if __name__ == '__main__':
    try:
        setup_social_providers()
        show_callback_urls()
    except Exception as e:
        print(f"❌ Erro durante a configuração: {e}")
        sys.exit(1)
