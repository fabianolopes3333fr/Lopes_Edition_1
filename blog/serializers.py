from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CategorieBlog, ArticleBlog, CommentaireBlog, NewsletterSubscriber


class AuteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


class CategorieBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorieBlog
        fields = ["id", "nom", "slug", "description", "couleur", "actif", "ordre"]


class CommentaireBlogSerializer(serializers.ModelSerializer):
    reponses = serializers.SerializerMethodField()

    class Meta:
        model = CommentaireBlog
        fields = [
            "id",
            "nom",
            "email",
            "site_web",
            "contenu",
            "status",
            "date_creation",
            "parent",
            "reponses",
        ]
        read_only_fields = ["status", "date_creation"]

    def get_reponses(self, obj):
        if obj.reponses.exists():
            return CommentaireBlogSerializer(
                obj.reponses.filter(status="approuve"), many=True
            ).data
        return []


class ArticleBlogListSerializer(serializers.ModelSerializer):
    auteur = AuteurSerializer(read_only=True)
    categorie = CategorieBlogSerializer(read_only=True)
    tags_list = serializers.ReadOnlyField()
    nombre_commentaires = serializers.SerializerMethodField()

    class Meta:
        model = ArticleBlog
        fields = [
            "id",
            "titre",
            "slug",
            "resume",
            "auteur",
            "categorie",
            "tags_list",
            "image",
            "text_alt",
            "status",
            "date_publication",
            "vues",
            "featured",
            "nombre_commentaires",
        ]

    def get_nombre_commentaires(self, obj):
        return obj.commentaires.filter(status="approuve").count()


class ArticleBlogDetailSerializer(serializers.ModelSerializer):
    auteur = AuteurSerializer(read_only=True)
    categorie = CategorieBlogSerializer(read_only=True)
    tags_list = serializers.ReadOnlyField()
    commentaires = serializers.SerializerMethodField()

    class Meta:
        model = ArticleBlog
        fields = [
            "id",
            "titre",
            "slug",
            "resume",
            "contenu",
            "auteur",
            "categorie",
            "tags",
            "tags_list",
            "image",
            "text_alt",
            "status",
            "date_creation",
            "date_modification",
            "date_publication",
            "meta_description",
            "meta_keywords",
            "vues",
            "featured",
            "commentaires",
        ]

    def get_commentaires(self, obj):
        commentaires_parents = obj.commentaires.filter(status="approuve", parent=None)
        return CommentaireBlogSerializer(commentaires_parents, many=True).data


class ArticleBlogCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleBlog
        fields = [
            "titre",
            "resume",
            "contenu",
            "categorie",
            "tags",
            "image",
            "text_alt",
            "status",
            "date_publication",
            "meta_description",
            "meta_keywords",
            "featured",
        ]

    def create(self, validated_data):
        validated_data["auteur"] = self.context["request"].user
        return super().create(validated_data)


class NewsletterSerializer(serializers.ModelSerializer):
    interests_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = NewsletterSubscriber
        fields = ["prenom", "email", "interests", "rgpd_consent", "interests_display"]
        extra_kwargs = {
            "email": {
                "error_messages": {
                    "required": "L'adresse email est requise.",
                    "invalid": "Veuillez entrer une adresse email valide.",
                    "unique": "Cette adresse email est déjà inscrite à notre newsletter.",
                }
            },
            "rgpd_consent": {
                "error_messages": {
                    "required": "Le consentement RGPD est requis pour l'inscription."
                }
            },
        }

    def get_interests_display(self, obj):
        """Retourne les intérêts en format lisible"""
        return obj.get_interests_display()

    def validate_email(self, value):
        """Validation personnalisée pour l'email"""
        if not value:
            raise serializers.ValidationError("L'adresse email est requise.")

        # Normaliser l'email
        email = value.lower().strip()

        # Vérifier la longueur
        if len(email) > 254:
            raise serializers.ValidationError("L'adresse email est trop longue.")

        # Vérifier les domaines interdits (optionnel)
        forbidden_domains = ["tempmail.com", "10minutemail.com", "guerrillamail.com"]
        domain = email.split("@")[-1] if "@" in email else ""
        if domain in forbidden_domains:
            raise serializers.ValidationError(
                "Les adresses email temporaires ne sont pas autorisées."
            )

        return email

    def validate_prenom(self, value):
        """Validation pour le prénom"""
        if value:
            # Nettoyer le prénom
            prenom = value.strip().title()

            # Vérifier la longueur
            if len(prenom) > 100:
                raise serializers.ValidationError(
                    "Le prénom est trop long (maximum 100 caractères)."
                )

            # Vérifier les caractères autorisés (lettres, espaces, tirets, apostrophes)
            import re

            if not re.match(r"^[a-zA-ZÀ-ÿ\s\-']+$", prenom):
                raise serializers.ValidationError(
                    "Le prénom ne peut contenir que des lettres, espaces, tirets et apostrophes."
                )

            return prenom
        return value

    def validate_interests(self, value):
        """Validation pour les intérêts"""
        if value:
            # Nettoyer et valider les intérêts
            interests_list = [
                interest.strip() for interest in value.split(",") if interest.strip()
            ]

            # Vérifier que les intérêts sont valides
            valid_interests = [
                choice[0] for choice in NewsletterSubscriber.INTEREST_CHOICES
            ]
            invalid_interests = [
                interest
                for interest in interests_list
                if interest not in valid_interests
            ]

            if invalid_interests:
                raise serializers.ValidationError(
                    f"Intérêts non valides: {', '.join(invalid_interests)}. "
                    f"Intérêts disponibles: {', '.join(valid_interests)}"
                )

            return ",".join(interests_list)
        return value

    def validate_rgpd_consent(self, value):
        """Validation pour le consentement RGPD"""
        if not value:
            raise serializers.ValidationError(
                "Vous devez accepter notre politique de confidentialité pour vous inscrire à la newsletter."
            )
        return value

    def validate(self, attrs):
        """Validation globale"""
        # Vérifier si l'email existe déjà (pour les créations)
        if not self.instance:  # Création
            email = attrs.get("email")
            if email and NewsletterSubscriber.objects.filter(email=email).exists():
                raise serializers.ValidationError(
                    {
                        "email": "Cette adresse email est déjà inscrite à notre newsletter."
                    }
                )

        return attrs

    def create(self, validated_data):
        """Création personnalisée avec gestion du token de confirmation"""
        # Ajouter l'adresse IP si disponible dans le contexte
        request = self.context.get("request")
        if request:
            validated_data["ip_address"] = self.get_client_ip(request)

        # Créer l'assinante
        subscriber = super().create(validated_data)

        # Associer à une liste par défaut si elle existe
        try:
            from .models import NewsletterList

            default_list = NewsletterList.objects.filter(
                name="Newsletter Générale"
            ).first()
            if default_list:
                subscriber.lists.add(default_list)
        except:
            pass  # Ignorar se não houver lista padrão

        return subscriber

    def get_client_ip(self, request):
        """Obter IP do cliente"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def to_representation(self, instance):
        """Personalizar a representação de saída"""
        data = super().to_representation(instance)

        # Adicionar informações úteis na resposta
        data["date_joined"] = (
            instance.date_joined.isoformat() if instance.date_joined else None
        )
        data["confirmed"] = getattr(instance, "confirmed", False)
        data["active"] = getattr(instance, "active", True)

        return data
