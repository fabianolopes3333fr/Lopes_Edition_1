import pytest
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_password_reset_confirm_valid_link(client):
    user = User.objects.create_user(
        email="reset.user@example.com",
        password="initialPass123",
        first_name="Reset",
        last_name="User",
        account_type="CLIENT",
    )
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    url = reverse("accounts:password_reset_confirm", kwargs={"uidb64": uidb64, "token": token})
    resp = client.get(url)

    assert resp.status_code == 200
    # Deve renderizar o formulário (validlink True)
    assert "Nouveau mot de passe" in resp.content.decode("utf-8")
    assert "Lien invalide" not in resp.content.decode("utf-8")


@pytest.mark.django_db
def test_password_reset_confirm_invalid_link(client):
    user = User.objects.create_user(
        email="reset.invalid@example.com",
        password="initialPass123",
        first_name="Reset",
        last_name="Invalid",
        account_type="CLIENT",
    )
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    invalid_token = "invalid-token"

    url = reverse("accounts:password_reset_confirm", kwargs={"uidb64": uidb64, "token": invalid_token})
    resp = client.get(url)

    assert resp.status_code == 200
    # Deve renderizar a tela de link inválido (validlink False)
    html = resp.content.decode("utf-8")
    assert "Lien invalide" in html
    assert "Demander un nouveau lien" in html

