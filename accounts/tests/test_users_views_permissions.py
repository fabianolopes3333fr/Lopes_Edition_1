import pytest
from django.urls import reverse
from accounts.models import User, AccountType


@pytest.mark.django_db
class TestUsersViewsPermissions:
    def test_users_list_forbidden_for_client(self, client):
        user = User.objects.create_user(
            email="client2@example.com",
            password="pass123456",
            first_name="Cli2",
            last_name="Ent2",
            account_type=AccountType.CLIENT,
        )
        client.force_login(user)
        resp = client.get(reverse("accounts:users_list"))
        assert resp.status_code == 403

    def test_users_list_forbidden_for_collaborator(self, client):
        user = User.objects.create_user(
            email="collab2@example.com",
            password="pass123456",
            first_name="Col2",
            last_name="Lab2",
            account_type=AccountType.COLLABORATOR,
        )
        client.force_login(user)
        resp = client.get(reverse("accounts:users_list"))
        assert resp.status_code == 403

    def test_users_list_allowed_for_admin(self, client):
        user = User.objects.create_user(
            email="admin2@example.com",
            password="pass123456",
            first_name="Ad2",
            last_name="Min2",
            account_type=AccountType.ADMINISTRATOR,
            is_staff=True,
        )
        client.force_login(user)
        resp = client.get(reverse("accounts:users_list"))
        assert resp.status_code == 200

