from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import NewsletterSubscribeView

router = DefaultRouter()
router.register(r"categories", views.CategorieBlogViewSet)
router.register(r"articles", views.ArticleBlogViewSet)
router.register(r"commentaires", views.CommentaireBlogViewSet)

app_name = "blog"

urlpatterns = [
    # APIs REST
    path("api/", include(router.urls), name='api_root'),
    path(
        "api/newsletter/subscribe/",
        NewsletterSubscribeView.as_view(),
        name="newsletter_subscribe",
    ),
    # Views de template (se você tiver)
    path("Conseils/et/Inspiration", views.blog_list_view, name="blog_list"),
    path("<slug:slug>/", views.blog_detail_view, name="blog_detail"),
]
