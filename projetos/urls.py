from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"", views.ProjetoViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("projetos/", views.projetos, name="projetos"),
    path("projetos/<int:pk>/", views.projeto_detail, name="projeto_detail"),
]
