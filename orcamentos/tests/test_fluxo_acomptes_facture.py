from decimal import Decimal
from datetime import date, timedelta

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from orcamentos.models import (
    Projeto, SolicitacaoOrcamento, Orcamento, ItemOrcamento,
    AcompteOrcamento, StatusAcompte, TipoServico, TipoUnidade, TipoAtividade, TipoTVA,
    CondicoesPagamento, TipoPagamento, StatusOrcamento, Facture
)
from orcamentos.auditoria import LogAuditoria, TipoAcao


User = get_user_model()


class FluxoAcomptesDevisFactureTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.cliente = User.objects.create_user(
            username='cliente2@test.com', email='cliente2@test.com', password='testpass',
            first_name='Ana', last_name='Pereira', account_type='CLIENT'
        )
        self.admin = User.objects.create_user(
            username='admin2@test.com', email='admin2@test.com', password='testpass',
            first_name='Admin', last_name='Deux', account_type='ADMINISTRATOR', is_staff=True, is_superuser=True
        )

    def _criar_orcamento_com_itens(self):
        projeto = Projeto.objects.create(
            cliente=self.cliente,
            titulo='Projeto Acomptes',
            descricao='Desc',
            tipo_servico=TipoServico.PINTURA_INTERIOR,
            endereco_projeto='End', cidade_projeto='Paris', cep_projeto='75000'
        )
        solicitacao = SolicitacaoOrcamento.objects.create(
            cliente=self.cliente,
            projeto=projeto,
            nome_solicitante=f"{self.cliente.first_name} {self.cliente.last_name}",
            email_solicitante=self.cliente.email,
            telefone_solicitante='0102030405',
            endereco='End', cidade='Paris', cep='75000',
            tipo_servico=TipoServico.PINTURA_INTERIOR,
            descricao_servico='Serviço'
        )
        orc = Orcamento.objects.create(
            solicitacao=solicitacao,
            elaborado_por=self.admin,
            titulo='Devis Acomptes', descricao='Desc',
            prazo_execucao=10, validade_orcamento=date.today() + timedelta(days=30),
            condicoes_pagamento=CondicoesPagamento.ACOMPTE_30,
            tipo_pagamento=TipoPagamento.VIREMENT,
            status=StatusOrcamento.ENVIADO, data_envio=timezone.now()
        )
        ItemOrcamento.objects.create(
            orcamento=orc,
            referencia='REF-AC', descricao='Prestação', unidade=TipoUnidade.UNITE,
            atividade=TipoAtividade.SERVICE, quantidade=Decimal('10'), preco_unitario_ht=Decimal('100.00'),
            taxa_tva=TipoTVA.TVA_20
        )
        orc.calcular_totais()
        return orc

    def test_fluxo_acomptes_devis_facture(self):
        # Criar orcamento com itens
        orc = self._criar_orcamento_com_itens()

        # Criar acomptes: 30% pago, 20% pendente
        acompte_pago = AcompteOrcamento.objects.create(
            orcamento=orc,
            criado_por=self.admin,
            tipo='inicial', descricao='Acompte 30%', percentual=Decimal('30.00'),
            valor_ht=Decimal('0.00'), valor_ttc=Decimal('0.00'), data_vencimento=date.today() + timedelta(days=7),
            status=StatusAcompte.PAGO
        )
        acompte_pago.calcular_valores(); acompte_pago.save()

        acompte_pendente = AcompteOrcamento.objects.create(
            orcamento=orc,
            criado_por=self.admin,
            tipo='intermediario', descricao='Acompte 20%', percentual=Decimal('20.00'),
            valor_ht=Decimal('0.00'), valor_ttc=Decimal('0.00'), data_vencimento=date.today() + timedelta(days=20),
            status=StatusAcompte.PENDENTE
        )
        acompte_pendente.calcular_valores(); acompte_pendente.save()

        # Aceitar orçamento
        orc.status = StatusOrcamento.ACEITO
        orc.data_resposta_cliente = timezone.now()
        orc.save()

        # Admin abre página de criar fatura a partir do orcamento
        self.client.login(username='admin2@test.com', password='testpass')
        resp_get = self.client.get(reverse('orcamentos:admin_criar_fatura_from_orcamento', args=[orc.numero]))
        self.assertEqual(resp_get.status_code, 200)
        self.assertContains(resp_get, 'Informations de la Facture')

        # Postar criação de fatura, usando fallback para copiar itens (enviar JSON inválido)
        post_data = {
            'titulo': 'Facture Devis Acomptes',
            'descricao': 'Fatura baseada em devis com acomptes',
            'data_emissao': date.today().isoformat(),
            'data_vencimento': (date.today() + timedelta(days=30)).isoformat(),
            'condicoes_pagamento': CondicoesPagamento.ACOMPTE_30,
            'tipo_pagamento': TipoPagamento.VIREMENT,
            'desconto': '0',
            'observacoes': '',
            'itens_json': 'INVALID_JSON_TRIGGER_FALLBACK',
            'action': 'draft',
            # Campo cliente hidden é renderizado no template, mas o view força fatura.cliente = cliente; então opcional aqui
        }
        resp_post = self.client.post(
            reverse('orcamentos:admin_criar_fatura_from_orcamento', args=[orc.numero]),
            data=post_data,
            follow=True
        )
        self.assertEqual(resp_post.status_code, 200)

        # Verificar fatura criada
        fatura = Facture.objects.filter(orcamento=orc).first()
        self.assertIsNotNone(fatura)
        self.assertGreater(fatura.total, Decimal('0.00'))

        # Gerar HTML do PDF e verificar linhas de acomptes e saldo
        resp_pdf = self.client.get(reverse('orcamentos:admin_fatura_pdf', args=[fatura.numero]) + '?debug=1')
        self.assertEqual(resp_pdf.status_code, 200)
        html = resp_pdf.content.decode('utf-8')
        self.assertIn('Acomptes payés', html)
        self.assertIn('Solde TTC à payer', html)

        # Cálculos esperados
        total_ttc = orc.total_ttc
        total_acomptes_pagos = orc.total_acomptes_pagos
        solde_esperado = total_ttc - total_acomptes_pagos
        # Deve aparecer o valor formatado com 2 casas decimais
        self.assertIn(f"{total_acomptes_pagos:.2f}", html)
        self.assertIn(f"{solde_esperado:.2f}", html)

        # Auditoria: deve existir log de criação de fatura
        logs = LogAuditoria.objects.filter(acao=TipoAcao.CRIACAO_FATURA)
        self.assertTrue(logs.exists())

