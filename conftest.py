import os
import sys
import django
import pytest
from pathlib import Path

# Adicionar o diretório do projeto ao Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))


def pytest_configure(config):
    """Configurar Django para os testes"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

    try:
        django.setup()
        print("Django configurado com sucesso para testes")
    except Exception as e:
        print(f"Erro ao configurar Django: {e}")
        raise


@pytest.fixture(scope="session")
def django_db_setup():
    """Configuração da base de dados para testes"""
    from django.conf import settings

    # Configuração completa da base de dados para testes
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": False,
        "OPTIONS": {},
        "TIME_ZONE": None,
        "CONN_MAX_AGE": 0,
        "AUTOCOMMIT": True,
        "TEST": {
            "CHARSET": None,
            "COLLATION": None,
            "NAME": None,
            "MIRROR": None,
        },
    }


@pytest.fixture(autouse=True)
def clear_contenttype_cache(db):
    """Limpar cache do ContentType antes de cada teste"""
    from django.contrib.contenttypes.models import ContentType

    ContentType.objects.clear_cache()
    yield
    # Limpar novamente após o teste
    ContentType.objects.clear_cache()


@pytest.fixture
def user_factory():
    """Factory para criar usuários nos testes"""
    from django.contrib.auth import get_user_model

    User = get_user_model()

    def _create_user(**kwargs):
        defaults = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    return _create_user


@pytest.fixture
def profile_factory(user_factory):
    """Factory para criar perfis nos testes"""
    from profiles.models import Profile

    def _create_profile(**kwargs):
        user = kwargs.pop("user", user_factory())
        defaults = {
            "phone": "+33123456789",
            "address": "123 Test Street",
            "city": "Paris",
            "postal_code": "75001",
            "country": "France",
        }
        defaults.update(kwargs)

        # Obter ou criar perfil
        profile, created = Profile.objects.get_or_create(user=user, defaults=defaults)

        if not created:
            # Atualizar perfil existente
            for key, value in defaults.items():
                setattr(profile, key, value)
            profile.save()

        return profile

    return _create_profile


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Permitir acesso à base de dados em todos os testes"""
    pass
