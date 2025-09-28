from django.core.management.base import BaseCommand
from orcamentos.models import Orcamento
import secrets


class Command(BaseCommand):
    help = "Gerar tokens únicos para orçamentos existentes"

    def handle(self, *args, **options):
        orcamentos_sem_token = Orcamento.objects.filter(token_publico="")
        count = 0

        for orcamento in orcamentos_sem_token:
            # Gerar token único
            while True:
                token = secrets.token_urlsafe(16)
                if not Orcamento.objects.filter(token_publico=token).exists():
                    orcamento.token_publico = token
                    orcamento.save()
                    count += 1
                    break

        self.stdout.write(self.style.SUCCESS(f"Tokens gerados para {count} orçamentos"))
