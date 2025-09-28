from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.forms import (
    UserRegistrationForm,
    EmailLoginForm,
)  # ✅ CORRIGIDO: Nomes corretos

User = get_user_model()


class UserRegistrationFormTest(TestCase):
    """✅ CORRIGIDO: Testes para formulário de criação de usuário"""

    def test_form_valid_data(self):
        """Teste formulário com dados válidos"""
        form_data = {
            "email": "test@lopespeinture.com",
            "first_name": "Test",
            "last_name": "User",
            "account_type": "CLIENT",
            "password1": "complexpass123",
            "password2": "complexpass123",
        }

        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_passwords_dont_match(self):
        """Teste senhas não coincidem"""
        form_data = {
            "email": "test@lopespeinture.com",
            "first_name": "Test",
            "last_name": "User",
            "account_type": "CLIENT",
            "password1": "complexpass123",
            "password2": "differentpass123",
        }

        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_form_invalid_email(self):
        """Teste email inválido"""
        form_data = {
            "email": "invalid-email",
            "first_name": "Test",
            "last_name": "User",
            "account_type": "CLIENT",
            "password1": "complexpass123",
            "password2": "complexpass123",
        }

        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_duplicate_email(self):
        """Teste email duplicado"""
        # Criar usuário existente
        User.objects.create_user(
            email="existing@lopespeinture.com",
            password="pass123",
            first_name="Existing",
            last_name="User",
        )

        form_data = {
            "email": "existing@lopespeinture.com",
            "first_name": "Test",
            "last_name": "User",
            "account_type": "CLIENT",
            "password1": "complexpass123",
            "password2": "complexpass123",
        }

        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_save(self):
        """Teste salvar formulário"""
        form_data = {
            "email": "test@lopespeinture.com",
            "first_name": "Test",
            "last_name": "User",
            "account_type": "CLIENT",
            "password1": "complexpass123",
            "password2": "complexpass123",
        }

        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertEqual(user.email, "test@lopespeinture.com")
        self.assertEqual(user.account_type, "CLIENT")
        self.assertTrue(user.check_password("complexpass123"))


class EmailLoginFormTest(TestCase):
    """✅ CORRIGIDO: Testes para formulário de autenticação"""

    def setUp(self):
        """Setup inicial"""
        self.user = User.objects.create_user(
            email="test@lopespeinture.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_form_valid_credentials(self):
        """Teste credenciais válidas"""
        form_data = {
            "username": "test@lopespeinture.com",  # ✅ O campo é username mas contém email
            "password": "testpass123",
        }

        form = EmailLoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_credentials(self):
        """Teste credenciais inválidas"""
        form_data = {
            "username": "test@lopespeinture.com",
            "password": "wrongpassword",
        }

        form = EmailLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_form_inactive_user(self):
        """Teste usuário inativo"""
        self.user.is_active = False
        self.user.save()

        form_data = {
            "username": "test@lopespeinture.com",
            "password": "testpass123",
        }

        form = EmailLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
