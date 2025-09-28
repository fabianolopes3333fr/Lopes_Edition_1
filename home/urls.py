from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.sobre, name="about"),
    path("servicos/", views.servicos, name="services"),
    path("contact/", views.contato_view, name="contact"),
    path("realisations/", views.realisations, name="projets"),
    path("devis/", views.contato_view, name="devis"),
    path("nos-couleurs/", views.nos_couleurs, name="nuancier"),
    path("api/couleurs/", views.api_couleurs, name="api_nuancier"),
]
