import pytest
from django.urls import reverse
from django.test import override_settings
from django.core import mail
from accounts.models import User, AccountType


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_admin_creates_user_sends_password_definition_email(client):
    # Loga como administrador
    admin = User.objects.create_user(
        email="superadmin@example.com",
        password="pass123456",
        first_name="Super",
        last_name="Admin",
        account_type=AccountType.ADMINISTRATOR,
        is_staff=True,
    )
    client.force_login(admin)

    # Dados do novo usuário
    form_data = {
        "email": "novo.usuario@example.com",
        "first_name": "Novo",
        "last_name": "Usuario",
        "account_type": AccountType.COLLABORATOR,
        "is_active": "on",  # manter ativo
        # is_staff e grupos são opcionais e podem ser omitidos
    }

    # POST para criar
    resp = client.post(reverse("accounts:user_create"), data=form_data, follow=True)
    assert resp.status_code == 200  # após follow redirect para lista

    # Verifica que o usuário foi criado
    user = User.objects.get(email="novo.usuario@example.com")

    # Senha deve ser inutilizável (fluxo seguro)
    assert not user.has_usable_password()

    # Um email deve ter sido enviado com o link de definição de senha
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert "Réinitialisation de mot de passe" in email.subject or "Réinitialisation" in email.subject
    assert "novo.usuario@example.com" in email.to
    # Link deve conter a rota de confirm reset
    assert "/comptes/password_reset/" in email.body or "/comptes/password_reset/" in email.alternatives[0][0]

