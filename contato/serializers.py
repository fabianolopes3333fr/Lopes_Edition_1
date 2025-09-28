from rest_framework import serializers
from .models import Contato, PieceJointe


class PieceJointeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PieceJointe
        fields = ["id", "fichier", "nom_original", "taille", "date_upload"]
        read_only_fields = ["id", "taille", "date_upload"]


class ContatoListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de contatos (admin)"""

    pieces_jointes_count = serializers.SerializerMethodField()

    class Meta:
        model = Contato
        fields = [
            "id",
            "nom",
            "prenom",
            "email",
            "telephone",
            "type_contact",
            "sujet",
            "status",
            "date_creation",
            "pieces_jointes_count",
        ]

    def get_pieces_jointes_count(self, obj):
        return obj.pieces_jointes.count()


class ContatoDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalhes do contato (admin)"""

    pieces_jointes = PieceJointeSerializer(many=True, read_only=True)

    class Meta:
        model = Contato
        fields = "__all__"


class ContatoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de contato (público)"""

    pieces_jointes = serializers.ListField(
        child=serializers.FileField(), required=False, write_only=True
    )

    class Meta:
        model = Contato
        fields = [
            "nom",
            "prenom",
            "email",
            "telephone",
            "type_contact",
            "sujet",
            "message",
            "adresse_projet",
            "ville_projet",
            "surface_estimee",
            "budget_estime",
            "pieces_jointes",
        ]

    def validate_email(self, value):
        """Validar formato do email"""
        if not value:
            raise serializers.ValidationError("L'email est obligatoire.")
        return value.lower()

    def validate_pieces_jointes(self, value):
        """Validar arquivos anexados"""
        if value:
            # Limitar número de arquivos
            if len(value) > 5:
                raise serializers.ValidationError("Maximum 5 fichiers autorisés.")

            # Limitar tamanho dos arquivos
            for file in value:
                if file.size > 10 * 1024 * 1024:  # 10MB
                    raise serializers.ValidationError(
                        f"Le fichier {file.name} est trop volumineux (max 10MB)."
                    )

                # Verificar extensões permitidas
                allowed_extensions = [
                    ".pdf",
                    ".doc",
                    ".docx",
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".gif",
                ]
                if not any(
                    file.name.lower().endswith(ext) for ext in allowed_extensions
                ):
                    raise serializers.ValidationError(
                        f"Type de fichier non autorisé: {file.name}"
                    )

        return value

    def create(self, validated_data):
        pieces_jointes_data = validated_data.pop("pieces_jointes", [])

        # Criar o contato
        contato = Contato.objects.create(**validated_data)

        # Criar as peças anexas
        for file in pieces_jointes_data:
            PieceJointe.objects.create(
                contato=contato, fichier=file, nom_original=file.name, taille=file.size
            )

        return contato


class ContatoUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de contato (admin)"""

    class Meta:
        model = Contato
        fields = ["status", "notes_internes", "date_traitement"]
