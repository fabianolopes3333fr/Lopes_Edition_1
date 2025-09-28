from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

User = get_user_model()


class UserModelTest(TestCase):
    """Testes para o modelo User"""

    def setUp(self):
        """Setup inicial para os testes"""
        self.user_data = {
            "email": "test@lopespeinture.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "account_type": "CLIENT",
        }

    def test_create_user_success(self):
        """✅ CORRIGIDO: Teste criação de usuário válido"""
        user = User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"],
            account_type=self.user_data["account_type"],
        )

        self.assertEqual(user.email, "test@lopespeinture.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.account_type, "CLIENT")
        self.assertTrue(user.check_password("testpass123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        # Verificar se username foi gerado
        self.assertIsNotNone(user.username)

    def test_create_user_without_email(self):
        """✅ CORRIGIDO: Teste criação de usuário sem email"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="",  # Email vazio
                password="testpass123",
                first_name="Test",
                last_name="User",
            )

    def test_create_user_invalid_email(self):
        """Teste criação de usuário com email inválido"""
        user = User(
            email="invalid-email",
            first_name="Test",
            last_name="User",
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_create_user_duplicate_email(self):
        """✅ CORRIGIDO: Teste criação de usuário com email duplicado"""
        # Criar primeiro usuário
        User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"],
        )

        # Tentar criar segundo usuário com mesmo email
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email=self.user_data["email"],  # Mesmo email
                password="otherpass123",
                first_name="Other",
                last_name="User",
            )

    def test_create_superuser(self):
        """✅ CORRIGIDO: Teste criação de superusuário"""
        superuser = User.objects.create_superuser(
            email="admin@lopespeinture.com",
            password="adminpass123",
            first_name="Admin",
            last_name="User",
        )

        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
        self.assertEqual(superuser.account_type, "ADMINISTRATOR")

    def test_username_generation(self):
        """✅ CORRIGIDO: Teste geração automática de username"""
        user = User.objects.create_user(
            email="test.user@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        # Username deve ser gerado automaticamente
        self.assertIsNotNone(user.username)
        self.assertTrue(user.username.startswith("test.user"))

    def test_get_full_name(self):
        """✅ CORRIGIDO: Teste método get_full_name"""
        user = User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"],
        )

        self.assertEqual(user.get_full_name(), "Test User")

    def test_get_short_name(self):
        """✅ CORRIGIDO: Teste método get_short_name"""
        user = User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"],
        )

        self.assertEqual(user.get_short_name(), "Test")

    def test_account_type_choices(self):
        """✅ CORRIGIDO: Teste tipos de conta válidos"""
        valid_types = ["CLIENT", "COLLABORATOR", "ADMINISTRATOR"]

        for i, account_type in enumerate(valid_types):
            email = f"test{i}@lopespeinture.com"

            user = User.objects.create_user(
                email=email,
                password="testpass123",
                first_name="Test",
                last_name="User",
                account_type=account_type,
            )
            self.assertEqual(user.account_type, account_type)

    def test_string_representation(self):
        """✅ CORRIGIDO: Teste representação em string do usuário"""
        user = User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"],
        )

        self.assertEqual(str(user), "test@lopespeinture.com")

    def test_email_normalization(self):
        """Teste normalização de email"""
        user = User.objects.create_user(
            email="TEST@LOPESPEINTURE.COM",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        self.assertEqual(user.email, "test@lopespeinture.com")

    def test_username_uniqueness(self):
        """Teste unicidade de username gerado"""
        # Criar dois usuários com emails similares
        user1 = User.objects.create_user(
            email="test@example.com",
            password="pass1",
            first_name="Test1",
            last_name="User1",
        )

        user2 = User.objects.create_user(
            email="test@different.com",
            password="pass2",
            first_name="Test2",
            last_name="User2",
        )

        # Usernames devem ser diferentes
        self.assertNotEqual(user1.username, user2.username)
