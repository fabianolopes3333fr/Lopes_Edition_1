from rest_framework import serializers
from .models import Projeto, ImageProjeto


class ImageProjetoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProjeto
        fields = ["id", "image", "legende", "ordre"]


class ProjetoSerializer(serializers.ModelSerializer):
    images = ImageProjetoSerializer(many=True, read_only=True)

    class Meta:
        model = Projeto
        fields = [
            "id",
            "titre",
            "description",
            "ville",
            "adresse",
            "type_projet",
            "status",
            "date_debut",
            "date_fin",
            "surface_m2",
            "prix_estime",
            "image_principale",
            "images",
            "date_creation",
        ]
