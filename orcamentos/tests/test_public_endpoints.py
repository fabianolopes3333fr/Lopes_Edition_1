from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.signing import TimestampSigner

from orcamentos.models import SolicitacaoOrcamento, Orcamento, StatusOrcamento

User = get_user_model()


class PublicDevisEndpointsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create an admin (elaborado_por needs a user)
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='testpass123',
            is_staff=True, is_superuser=True
        )
        # Create a public solicitation (no linked client)
        self.solicitacao = SolicitacaoOrcamento.objects.create(
            nome_solicitante='Public User',
            email_solicitante='public@example.com',
            telefone_solicitante='0102030405',
            endereco='Rue A',
            cidade='Paris',
            cep='75001',
            tipo_servico='pintura_interior',
            descricao_servico='Teste',
        )
        # Create an orcamento in ENVIADO status
        self.orcamento = Orcamento.objects.create(
            solicitacao=self.solicitacao,
            elaborado_por=self.admin,
            titulo='Devis Test',
            descricao='Desc',
            prazo_execucao=10,
            validade_orcamento=date.today() + timedelta(days=15),
            condicoes_pagamento='comptant',
            observacoes='-',
            status=StatusOrcamento.ENVIADO,
        )
        self.signer = TimestampSigner()

    def test_public_accept(self):
        url = reverse('orcamentos:orcamento_publico_aceitar', kwargs={'uuid': self.orcamento.uuid})
        token = self.signer.sign(f"{self.orcamento.uuid}:accept")
        resp = self.client.post(url, data={'token': token})
        self.assertEqual(resp.status_code, 200)
        # Expect HTML page confirmation
        self.assertIn('text/html', resp.headers.get('Content-Type', ''))
        self.assertIn('Devis Accepté', resp.content.decode('utf-8'))
        # Refresh from DB
        self.orcamento.refresh_from_db()
        self.solicitacao.refresh_from_db()
        self.assertEqual(self.orcamento.status, StatusOrcamento.ACEITO)
        self.assertEqual(self.solicitacao.status, StatusOrcamento.ACEITO)

    def test_public_refuse(self):
        # Reset to ENVIADO in case previous test ran first
        self.orcamento.status = StatusOrcamento.ENVIADO
        self.orcamento.save()
        url = reverse('orcamentos:orcamento_publico_recusar', kwargs={'uuid': self.orcamento.uuid})
        token = self.signer.sign(f"{self.orcamento.uuid}:refuse")
        resp = self.client.post(url, data={'token': token})
        self.assertEqual(resp.status_code, 200)
        # Expect HTML page confirmation
        self.assertIn('text/html', resp.headers.get('Content-Type', ''))
        self.assertIn('Devis Refusé', resp.content.decode('utf-8'))
        # Refresh from DB
        self.orcamento.refresh_from_db()
        self.solicitacao.refresh_from_db()
        self.assertEqual(self.orcamento.status, StatusOrcamento.RECUSADO)
        self.assertEqual(self.solicitacao.status, StatusOrcamento.RECUSADO)
