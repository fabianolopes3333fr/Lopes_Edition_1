"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.admin_dashboard import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),  # Admin personalizado com dashboard de projetos

    # Apps principais
    path('', include('home.urls')),
    # Expor as mesmas URLs de home sob o namespace 'pages' para compatibilidade de testes
    path('', include(('home.urls', 'pages'), namespace='pages')),
    path('comptes/', include('accounts.urls')),
    path('profiles/', include('profiles.urls')),

    # Sistema de orçamentos e projetos
    path('devis/', include('orcamentos.urls')),
    path('clients/', include('clientes.urls')),  # URL da app de clientes

    # Outros apps
    path('contact/', include('contato.urls')),
    path('conseil-et-inspiration/', include('blog.urls')),
    path('projects/', include('projetos.urls')),

    # Allauth URLs
    path('auth/', include('allauth.urls')),
]

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)