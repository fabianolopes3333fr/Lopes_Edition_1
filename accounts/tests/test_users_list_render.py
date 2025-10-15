import pytest
from django.urls import reverse
from django.contrib.auth.models import Group
from accounts.models import User, AccountType


@pytest.mark.django_db
def test_users_list_renders_user_data(client):
    # Admin
    admin = User.objects.create_user(
        email="admin.view@example.com",
        password="pass123456",
        first_name="Admin",
        last_name="View",
        account_type=AccountType.ADMINISTRATOR,
        is_staff=True,
    )
    client.force_login(admin)

    # Groups
    g1 = Group.objects.create(name="Managers")
    g2 = Group.objects.create(name="Equipe A")

    # Outros usuários
    collab = User.objects.create_user(
        email="colab.view@example.com",
        password="pass123456",
        first_name="Colab",
        last_name="One",
        account_type=AccountType.COLLABORATOR,
        is_active=True,
    )
    collab.groups.add(g1)

    client_user = User.objects.create_user(
        email="client.view@example.com",
        password="pass123456",
        first_name="Cli",
        last_name="Ent",
        account_type=AccountType.CLIENT,
        is_active=False,
    )
    client_user.groups.add(g2)

    # Request
    resp = client.get(reverse("accounts:users_list"))
    assert resp.status_code == 200

    content = resp.content

    # Emails
    assert b"admin.view@example.com" in content
    assert b"colab.view@example.com" in content
    assert b"client.view@example.com" in content

    # Tipos (labels de display)
    assert b"Administrateur" in content
    assert b"Collaborateur" in content
    assert b"Client" in content

    # Grupos
    assert b"Managers" in content
    assert b"Equipe A" in content

    # Status badges
    assert b"Actif" in content  # collab
    assert b"Inactif" in content  # client_user

    # Blocos de estatísticas presentes
    assert b"Total" in content
    assert b"Actifs" in content
    assert b"Admins" in content
    assert b"Clients" in content
