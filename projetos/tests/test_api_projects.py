import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from projetos.models import Projeto

User = get_user_model()


@pytest.mark.django_db
def test_projects_api_smoke():
    client = APIClient()

    # 1) GET lista deve responder 200 mesmo sem projetos
    resp = client.get('/projects/')
    assert resp.status_code == 200

    # 2) GET detalhe inexistente deve responder 404
    resp = client.get('/projects/999999/')
    assert resp.status_code == 404

    # 3) Criar um projeto via ORM para testar detalhe 200
    p = Projeto.objects.create(
        titre='Projet Test',
        description='Desc',
        ville='Paris',
        adresse='1 Rue Test',
        type_projet='interieur',
        status='nouveau',
        date_debut=timezone.now().date(),
        prix_estime=1000,
        visible_site=True,
    )
    resp = client.get(f'/projects/{p.id}/')
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == p.id
    assert data['titre'] == 'Projet Test'

    # 4) POST criação requer autenticação -> autenticar e criar
    user = User.objects.create_user(username='tester', email='tester@example.com', password='pass12345')
    client.force_authenticate(user=user)

    payload = {
        'titre': 'Projet API',
        'description': 'Criado via API',
        'ville': 'Lyon',
        'adresse': '2 Rue API',
        'type_projet': 'exterieur',
        'status': 'en_cours',
        'prix_estime': 2500.50,
    }

    resp = client.post('/projects/', payload, format='json')
    assert resp.status_code == 201
    data = resp.json()
    assert data['titre'] == 'Projet API'


@pytest.mark.django_db
def test_projects_api_validation_errors():
    """Testar que erros de validação são tratados corretamente"""
    client = APIClient()
    
    # Criar usuário para autenticação
    user = User.objects.create_user(username='validator', email='validator@example.com', password='pass12345')
    client.force_authenticate(user=user)

    # Payload inválido: faltando campos obrigatórios
    payload = {
        'titre': '',  # vazio
        'description': 'Test',
    }

    resp = client.post('/projects/', payload, format='json')
    # Deve retornar 400 (Bad Request) para dados inválidos
    assert resp.status_code == 400
