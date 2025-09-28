from rest_framework.views import APIView
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .models import CategorieBlog, ArticleBlog, CommentaireBlog, NewsletterSubscriber
from .serializers import (
    CategorieBlogSerializer,
    ArticleBlogListSerializer,
    ArticleBlogDetailSerializer,
    ArticleBlogCreateUpdateSerializer,
    CommentaireBlogSerializer,
    NewsletterSerializer,
)


class CategorieBlogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CategorieBlog.objects.filter(actif=True)
    serializer_class = CategorieBlogSerializer
    lookup_field = "slug"


class ArticleBlogViewSet(viewsets.ModelViewSet):
    queryset = ArticleBlog.objects.all()  # Definir queryset base
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["categorie", "status", "featured", "auteur"]
    search_fields = ["titre", "resume", "contenu", "tags"]
    ordering_fields = ["date_publication", "date_creation", "vues", "titre"]
    ordering = ["-date_publication"]
    lookup_field = "slug"

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return ArticleBlog.objects.all()
        return ArticleBlog.objects.filter(
            status="publie", date_publication__lte=timezone.now()
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ArticleBlogListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return ArticleBlogCreateUpdateSerializer
        return ArticleBlogDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Incrementar visualizações apenas para usuários não autenticados ou não staff
        if not request.user.is_authenticated or not request.user.is_staff:
            instance.incrementer_vues()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Retorna artigos em destaque"""
        articles = self.get_queryset().filter(featured=True)[:5]
        serializer = ArticleBlogListSerializer(articles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """Retorna artigos recentes"""
        articles = self.get_queryset()[:10]
        serializer = ArticleBlogListSerializer(articles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def add_comment(self, request, slug=None):
        """Adicionar comentário a um artigo"""
        article = self.get_object()
        serializer = CommentaireBlogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(article=article, ip_address=request.META.get("REMOTE_ADDR"))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentaireBlogViewSet(viewsets.ModelViewSet):
    queryset = CommentaireBlog.objects.all()
    serializer_class = CommentaireBlogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["article", "status"]
    ordering = ["-date_creation"]

    def get_queryset(self):
        if self.request.user.is_staff:
            return CommentaireBlog.objects.all()
        return CommentaireBlog.objects.filter(status="approuve")

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """Aprovar comentário (apenas staff)"""
        if not request.user.is_staff:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        comment = self.get_object()
        comment.status = "approuve"
        comment.date_moderation = timezone.now()
        comment.save()
        return Response({"status": "approved"})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """Rejeitar comentário (apenas staff)"""
        if not request.user.is_staff:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        comment = self.get_object()
        comment.status = "rejete"
        comment.date_moderation = timezone.now()
        comment.save()
        return Response({"status": "rejected"})


# Views de template HTML
def blog_list_view(request):
    """View para listar artigos (template HTML)"""
    # Carregar dados iniciais para SEO e primeira renderização
    articles = ArticleBlog.objects.filter(
        status="publie", date_publication__lte=timezone.now()
    ).select_related("categorie", "auteur")[:6]

    categories = CategorieBlog.objects.filter(actif=True)

    # Artigo em destaque
    featured_article = ArticleBlog.objects.filter(
        status="publie", featured=True, date_publication__lte=timezone.now()
    ).first()

    context = {
        "articles": articles,
        "categories": categories,
        "featured_article": featured_article,
        "page_title": "Blog - Lopes Peinture",
        "page_description": "Découvrez nos conseils, astuces et actualités sur la peinture intérieure et extérieure.",
    }

    return render(request, "pages/blog.html", context)


def blog_detail_view(request, slug):
    """View para detalhe do artigo (template HTML)"""
    try:
        article = get_object_or_404(
            ArticleBlog.objects.select_related("categorie", "auteur"),
            slug=slug,
            status="publie",
            date_publication__lte=timezone.now(),
        )

        # Incrementar visualizações
        article.incrementer_vues()

        # Artigos relacionados
        related_articles = ArticleBlog.objects.filter(
            categorie=article.categorie,
            status="publie",
            date_publication__lte=timezone.now(),
        ).exclude(id=article.id)[:3]

        # Comentários aprovados
        comments = (
            CommentaireBlog.objects.filter(
                article=article,
                status="approuve",
                parent__isnull=True,  # Apenas comentários principais
            )
            .select_related("parent")
            .order_by("-date_creation")
        )

        context = {
            "article": article,
            "related_articles": related_articles,
            "comments": comments,
            "page_title": f"{article.titre} - Blog Lopes Peinture",
            "page_description": article.resume or article.contenu[:160],
            "page_image": article.image.url if article.image else None,
        }

        return render(request, "pages/blog-detail.html", context)

    except ArticleBlog.DoesNotExist:
        raise Http404("Article non trouvé")


@method_decorator(csrf_exempt, name="dispatch")
class NewsletterSubscribeView(APIView):
    permission_classes = [AllowAny]  # Permitir acesso público

    def post(self, request, *args, **kwargs):
        # Verificar se os dados são JSON ou form-data
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return Response(
                    {"message": "Données JSON invalides."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            data = request.data

        serializer = NewsletterSerializer(data=data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")

            # 1. Verifica se o e-mail já existe
            if NewsletterSubscriber.objects.filter(email=email).exists():
                return Response(
                    {"message": "Cet e-mail est déjà abonné."},
                    status=status.HTTP_409_CONFLICT,
                )

            # 2. Salva o assinante no banco de dados
            subscriber = serializer.save()

            # 3. Envia o e-mail de confirmação
            try:
                subject = "Confirmation de votre inscription à la newsletter"
                html_message = render_to_string(
                    "emails/newsletter_confirmation.html", {"subscriber": subscriber}
                )
                plain_message = strip_tags(html_message)
                from_email = "contact@lopespeinture.fr"
                to = email

                send_mail(
                    subject, plain_message, from_email, [to], html_message=html_message
                )

            except Exception as e:
                # Opcional: registrar o erro de envio de e-mail
                print(f"Erro ao enviar e-mail: {e}")
                # A requisição ainda será bem-sucedida, pois o assinante foi salvo

            return Response(
                {"success": True, "message": "Merci pour votre inscription !"},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Données invalides.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get(self, request, *args, **kwargs):
        """Método GET para verificar se a API está funcionando"""
        return Response(
            {"message": "Newsletter subscription endpoint is working."},
            status=status.HTTP_200_OK,
        )
