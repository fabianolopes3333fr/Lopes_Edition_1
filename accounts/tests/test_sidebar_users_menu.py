import pytest
from django.urls import reverse
from accounts.models import User, AccountType


@pytest.mark.django_db
class TestSidebarUsersMenuVisibility:
    def test_menu_not_visible_for_client(self, client):
        user = User.objects.create_user(
            email="client@example.com",
            password="pass123456",
            first_name="Cli",
            last_name="Ent",
            account_type=AccountType.CLIENT,
        )
        client.force_login(user)
        url = reverse("accounts:dashboard")
        resp = client.get(url)
        assert resp.status_code == 200
        # link para Utilisateurs não deve aparecer
        assert b'/comptes/users/' not in resp.content
        assert b'Utilisateurs' not in resp.content

    def test_menu_not_visible_for_collaborator(self, client):
        user = User.objects.create_user(
            email="collab@example.com",
            password="pass123456",
            first_name="Col",
            last_name="Lab",
            account_type=AccountType.COLLABORATOR,
        )
        client.force_login(user)
        url = reverse("accounts:dashboard")
        resp = client.get(url)
        assert resp.status_code == 200
        # link para Utilisateurs não deve aparecer
        assert b'/comptes/users/' not in resp.content
        assert b'Utilisateurs' not in resp.content

    def test_menu_visible_for_administrator(self, client):
        user = User.objects.create_user(
            email="admin@example.com",
            password="pass123456",
            first_name="Ad",
            last_name="Min",
            account_type=AccountType.ADMINISTRATOR,
            is_staff=True,
        )
        client.force_login(user)
        url = reverse("accounts:dashboard")
        resp = client.get(url)
        assert resp.status_code == 200
        # link e label devem aparecer
        assert b'/comptes/users/' in resp.content
        assert b'Utilisateurs' in resp.content

