from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from .models import Contato, PieceJointe
from .serializers import (
    ContatoListSerializer,
    ContatoDetailSerializer,
    ContatoCreateSerializer,
    ContatoUpdateSerializer,
    PieceJointeSerializer,
)


def contato(request):
    """Página de contato"""
    if request.method == "POST":
        # Processar formulário de contato
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        mensagem = request.POST.get("mensagem")

        Contato.objects.create(nome=nome, email=email, mensagem=mensagem)

        return JsonResponse({"success": True})

    return render(request, "pages/contato.html")


class ContatoViewSet(viewsets.ModelViewSet):
    queryset = Contato.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["type_contact", "status", "ville_projet"]
    search_fields = ["nom", "prenom", "email", "sujet", "message"]
    ordering_fields = ["date_creation", "date_traitement"]
    ordering = ["-date_creation"]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == "create":
            # Permitir criação sem autenticação (formulário público)
            permission_classes = [permissions.AllowAny]
        else:
            # Outras ações requerem autenticação de staff
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "create":
            return ContatoCreateSerializer
        elif self.action == "list":
            return ContatoListSerializer
        elif self.action in ["update", "partial_update"]:
            return ContatoUpdateSerializer
        return ContatoDetailSerializer

    def create(self, request, *args, **kwargs):
        """Criar novo contato e enviar notificação por email"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Adicionar metadados da requisição
        validated_data = serializer.validated_data
        validated_data["ip_address"] = self.get_client_ip(request)
        validated_data["user_agent"] = request.META.get("HTTP_USER_AGENT", "")

        contato = serializer.save(**validated_data)

        # Enviar email de notificação
        self.enviar_notificacao_email(contato)

        return Response(
            {
                "message": "Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais."
            },
            status=status.HTTP_201_CREATED,
        )

    def get_client_ip(self, request):
        """Obter IP do cliente"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def enviar_notificacao_email(self, contato):
        """Enviar email de notificação para a empresa"""
        try:
            subject = f"Nouveau contact: {contato.sujet}"
            message = f"""
            Nouveau message reçu sur le site web:

            Nom: {contato.nom} {contato.prenom}
            Email: {contato.email}
            Téléphone: {contato.telephone}
            Type: {contato.get_type_contact_display()}
            Sujet: {contato.sujet}

            Message:
            {contato.message}

            Informations du projet:
            Adresse: {contato.adresse_projet}
            Ville: {contato.ville_projet}
            Surface estimée: {contato.surface_estimee} m²
            Budget estimé: {contato.budget_estime} €

            Date: {contato.date_creation.strftime('%d/%m/%Y %H:%M')}
            IP: {contato.ip_address}
            """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            # Log do erro, mas não falhar a criação do contato
            print(f"Erro ao enviar email: {e}")

    @action(detail=True, methods=["post"])
    def marquer_traite(self, request, pk=None):
        """Marcar contato como tratado"""
        contato = self.get_object()
        contato.marquer_como_traite()
        return Response({"status": "Contato marcado como tratado"})

    @action(detail=False, methods=["get"])
    def estatisticas(self, request):
        """Retornar estatísticas dos contatos"""
        total = Contato.objects.count()
        novos = Contato.objects.filter(status="nouveau").count()
        em_curso = Contato.objects.filter(status="en_cours").count()
        tratados = Contato.objects.filter(status="traite").count()

        # Contatos por tipo
        por_tipo = {}
        for tipo, label in Contato.TipoContato.choices:
            por_tipo[tipo] = Contato.objects.filter(type_contact=tipo).count()

        return Response(
            {
                "total": total,
                "por_status": {
                    "novos": novos,
                    "em_curso": em_curso,
                    "tratados": tratados,
                },
                "por_tipo": por_tipo,
            }
        )


class PieceJointeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PieceJointe.objects.all()
    serializer_class = PieceJointeSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["contato"]
