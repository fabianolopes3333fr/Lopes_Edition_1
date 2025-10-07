from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404
from .models import Projeto
from .serializers import ProjetoSerializer


def projetos(request):
    """Página de projetos"""
    projetos = Projeto.objects.all()
    context = {
        "projetos": projetos,
    }
    return render(request, "pages/projetos.html", context)

def projeto_detail(request, pk):
    """Detalhes do projeto"""
    projeto = get_object_or_404(Projeto, pk=pk)
    context = {
        'projeto': projeto,
    }
    return render(request, 'pages/projeto_detail.html', context)


class ProjetoViewSet(viewsets.ModelViewSet):
    queryset = Projeto.objects.filter(visible_site=True)
    serializer_class = ProjetoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type_projet', 'status', 'ville']
    search_fields = ['titre', 'description', 'ville']
    ordering_fields = ['date_creation', 'date_debut']
    ordering = ['-date_creation']
