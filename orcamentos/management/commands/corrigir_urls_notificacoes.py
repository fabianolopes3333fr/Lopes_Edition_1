from django.core.management.base import BaseCommand
from django.db import transaction
from orcamentos.models import Notificacao
import re

class Command(BaseCommand):
    help = 'Corrige URLs incorretas nas notificações existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostra o que seria corrigido sem fazer alterações',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Executando em modo de teste (dry-run)'))
        
        # Buscar todas as notificações com URLs incorretas
        notificacoes = Notificacao.objects.filter(
            url_acao__isnull=False
        ).exclude(url_acao='')
        
        corrigidas = 0
        
        with transaction.atomic():
            for notif in notificacoes:
                url_original = notif.url_acao
                url_corrigida = self.corrigir_url(url_original)
                
                if url_original != url_corrigida:
                    self.stdout.write(
                        f'ID {notif.id}: {url_original} -> {url_corrigida}'
                    )
                    
                    if not dry_run:
                        notif.url_acao = url_corrigida
                        notif.save()
                    
                    corrigidas += 1
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Encontradas {corrigidas} notificações que precisam ser corrigidas')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Corrigidas {corrigidas} notificações')
            )

    def corrigir_url(self, url):
        """Corrige uma URL incorreta"""
        if not url:
            return url
        
        # Corrigir URLs que começam com /orcamentos/ para /devis/
        if url.startswith('/orcamentos/'):
            url = url.replace('/orcamentos/', '/devis/', 1)
        
        # Corrigir endpoints específicos
        url = re.sub(r'/devis/admin/demandes/', '/devis/admin/solicitacoes/', url)
        url = re.sub(r'/devis/admin/orcamento/', '/devis/admin/orcamentos/', url)
        url = re.sub(r'/devis/admin/solicitacao/', '/devis/admin/solicitacoes/', url)  # Corrigir singular para plural
        
        # Garantir que URLs de projetos estejam corretas
        url = re.sub(r'/devis/admin/projeto/', '/devis/admin/projetos/', url)
        
        return url
