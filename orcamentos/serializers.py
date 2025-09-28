from rest_framework import serializers
from .models import Cliente, Orcamento, ItemOrcamento, HistoricoOrcamento


class ClienteSerializer(serializers.ModelSerializer):
    nom_complet = serializers.ReadOnlyField()

    class Meta:
        model = Cliente
        fields = [
            "id",
            "nom",
            "prenom",
            "nom_complet",
            "email",
            "telephone",
            "adresse",
            "ville",
            "code_postal",
            "nom_entreprise",
            "siret",
            "date_creation",
            "date_modification",
            "notes",
        ]
        read_only_fields = ["date_creation", "date_modification"]

    def validate_email(self, value):
        """Validar formato do email"""
        return value.lower()


class ItemOrcamentoSerializer(serializers.ModelSerializer):
    total = serializers.ReadOnlyField()

    class Meta:
        model = ItemOrcamento
        fields = [
            "id",
            "type_service",
            "description",
            "details",
            "quantite",
            "unite",
            "prix_unitaire",
            "total",
            "ordre",
        ]
        read_only_fields = ["total"]


class HistoricoOrcamentoSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = HistoricoOrcamento
        fields = [
            "id",
            "acao",
            "descricao",
            "data",
            "usuario",
            "usuario_nome",
            "ip_address",
        ]
        read_only_fields = ["data"]


class OrcamentoListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de orçamentos"""

    cliente_nome = serializers.CharField(source="cliente.nom_complet", read_only=True)
    auteur_nome = serializers.CharField(source="auteur.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = Orcamento
        fields = [
            "id",
            "numero",
            "uuid",
            "titre",
            "cliente",
            "cliente_nome",
            "status",
            "status_display",
            "date_creation",
            "date_expiration",
            "total",
            "auteur",
            "auteur_nome",
            "is_expired",
        ]


class OrcamentoDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalhes do orçamento"""

    cliente = ClienteSerializer(read_only=True)
    itens = ItemOrcamentoSerializer(many=True, read_only=True)
    historico = HistoricoOrcamentoSerializer(many=True, read_only=True)
    auteur_nome = serializers.CharField(source="auteur.get_full_name", read_only=True)
    is_expired = serializers.ReadOnlyField()
    url_publica = serializers.ReadOnlyField()

    class Meta:
        model = Orcamento
        fields = [
            "id",
            "numero",
            "uuid",
            "cliente",
            "titre",
            "description",
            "adresse_projet",
            "ville_projet",
            "status",
            "date_creation",
            "date_envoi",
            "date_expiration",
            "date_reponse",
            "sous_total",
            "taux_tva",
            "montant_tva",
            "total",
            "conditions_paiement",
            "validite",
            "auteur",
            "auteur_nome",
            "notes_internes",
            "itens",
            "historico",
            "is_expired",
            "url_publica",
        ]


class OrcamentoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de orçamento"""

    itens = ItemOrcamentoSerializer(many=True, required=False)

    class Meta:
        model = Orcamento
        fields = [
            "cliente",
            "titre",
            "description",
            "adresse_projet",
            "ville_projet",
            "date_expiration",
            "taux_tva",
            "conditions_paiement",
            "validite",
            "notes_internes",
            "itens",
        ]

    def create(self, validated_data):
        # Corrigir: usar pop com valor padrão para evitar KeyError
        itens_data = validated_data.pop("itens", [])

        # Definir o autor como o usuário da requisição
        validated_data["auteur"] = self.context["request"].user

        # Criar orçamento
        orcamento = Orcamento.objects.create(**validated_data)

        # Criar itens se fornecidos
        for item_data in itens_data:
            ItemOrcamento.objects.create(orcamento=orcamento, **item_data)

        # Criar histórico
        HistoricoOrcamento.objects.create(
            orcamento=orcamento,
            acao="creation",
            descricao="Devis créé",
            usuario=self.context["request"].user,
        )

        return orcamento


class OrcamentoUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de orçamento"""

    itens = ItemOrcamentoSerializer(many=True, required=False)

    class Meta:
        model = Orcamento
        fields = [
            "titre",
            "description",
            "adresse_projet",  # Corrigido: removido espaço extra
            "ville_projet",
            "date_expiration",
            "taux_tva",
            "conditions_paiement",
            "validite",
            "notes_internes",
            "itens",
        ]

    def update(self, instance, validated_data):
        itens_data = validated_data.pop("itens", None)

        # Atualizar orçamento
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Atualizar itens se fornecidos
        if itens_data is not None:
            # Remover itens existentes
            instance.itens.all().delete()

            # Criar novos itens
            for item_data in itens_data:
                ItemOrcamento.objects.create(orcamento=instance, **item_data)

        # Criar histórico
        HistoricoOrcamento.objects.create(
            orcamento=instance,
            acao="modification",
            descricao="Devis modifié",
            usuario=self.context["request"].user,
        )

        return instance


class OrcamentoPublicoSerializer(serializers.ModelSerializer):
    """Serializer para visualização pública do orçamento"""

    cliente = ClienteSerializer(read_only=True)
    itens = ItemOrcamentoSerializer(many=True, read_only=True)
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = Orcamento
        fields = [
            "numero",
            "titre",
            "description",
            "adresse_projet",
            "ville_projet",
            "cliente",
            "date_creation",
            "date_expiration",
            "sous_total",
            "taux_tva",
            "montant_tva",
            "total",
            "conditions_paiement",
            "validite",
            "itens",
            "is_expired",
        ]
