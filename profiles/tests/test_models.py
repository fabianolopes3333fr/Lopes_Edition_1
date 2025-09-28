from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from profiles.models import Profile
import logging

# Configurar logging para testes
logging.basicConfig(level=logging.INFO)

User = get_user_model()


class ProfileModelTest(TestCase):
    """Testes para o modelo Profile"""

    def setUp(self):
        """Setup inicial"""
        self.user = User.objects.create_user(
            email="test@lopespeinture.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        # Aguardar criação do perfil via signal
        self.user.refresh_from_db()

    def test_profile_created_automatically(self):
        """✅ CORRIGIDO: Teste criação automática de perfil via signal"""
        self.assertTrue(hasattr(self.user, "profile"))
        self.assertIsInstance(self.user.profile, Profile)
        print(f"✅ Perfil criado automaticamente para {self.user.email}")

    def test_profile_string_representation(self):
        """Teste representação em string do perfil"""
        expected = f"Profil de {self.user.get_full_name()}"
        actual = str(self.user.profile)
        self.assertEqual(actual, expected)
        print(f"✅ String representation: {actual}")

    def test_profile_display_username_generation(self):
        """✅ CORRIGIDO: Teste geração automática do display_username"""
        profile = self.user.profile
        self.assertIsNotNone(profile.display_username)
        print(f"✅ Display username gerado: {profile.display_username}")

    def test_profile_completion_status_incomplete(self):
        """Teste status de completude - incompleto"""
        profile = self.user.profile
        is_complete = profile.is_complete
        percentage = profile.completion_percentage

        self.assertFalse(is_complete)
        print(f"✅ Perfil incompleto: {percentage}% completo")

    def test_profile_completion_status_complete(self):
        """✅ CORRIGIDO: Teste status de completude - completo"""
        profile = self.user.profile

        # Preencher dados obrigatórios
        profile.phone = "+33123456789"
        profile.address = "123 Test Street"
        profile.city = "Paris"
        profile.postal_code = "75001"
        profile.save()

        # Verificar no banco
        profile.refresh_from_db()

        print(f"✅ Dados salvos - phone: {profile.phone}, city: {profile.city}")
        print(f"✅ Completude: {profile.completion_percentage}%")

        self.assertTrue(profile.is_complete)

    def test_profile_save_data_persistence(self):
        """✅ NOVO: Teste específico para persistência de dados"""
        profile = self.user.profile

        # Dados de teste
        test_phone = "+33123456789"
        test_city = "Lyon"
        test_address = "456 Test Avenue"
        test_postal = "69001"

        # Salvar dados
        profile.phone = test_phone
        profile.city = test_city
        profile.address = test_address
        profile.postal_code = test_postal
        profile.save()

        # Verificar se foi salvo
        profile.refresh_from_db()

        print(f"✅ TESTE PERSISTÊNCIA:")
        print(f"   - Phone: {profile.phone} (esperado: {test_phone})")
        print(f"   - City: {profile.city} (esperado: {test_city})")
        print(f"   - Address: {profile.address} (esperado: {test_address})")
        print(f"   - Postal: {profile.postal_code} (esperado: {test_postal})")

        self.assertEqual(profile.phone, test_phone)
        self.assertEqual(profile.city, test_city)
        self.assertEqual(profile.address, test_address)
        self.assertEqual(profile.postal_code, test_postal)

    def test_profile_avatar_upload(self):
        """Teste upload de avatar"""
        # Criar arquivo de imagem fake
        avatar = SimpleUploadedFile(
            "test_avatar.jpg", b"fake_image_content", content_type="image/jpeg"
        )

        profile = self.user.profile
        profile.avatar = avatar
        profile.save()

        self.assertTrue(profile.avatar)
        self.assertIn("avatars/", profile.avatar.name)
        print(f"✅ Avatar salvo: {profile.avatar.name}")

    def test_profile_preferences_defaults(self):
        """Teste valores padrão das preferências"""
        profile = self.user.profile

        self.assertTrue(profile.receive_notifications)
        self.assertTrue(profile.receive_newsletters)
        print(
            f"✅ Preferências padrão: notifications={profile.receive_notifications}, newsletters={profile.receive_newsletters}"
        )

    def test_profile_update_timestamp(self):
        """Teste atualização automática do timestamp"""
        profile = self.user.profile
        old_updated_at = profile.updated_at

        # Aguardar um pouco para garantir diferença no timestamp
        import time

        time.sleep(0.1)

        profile.phone = "+33123456789"
        profile.save()

        profile.refresh_from_db()

        print(f"✅ Timestamp atualizado: {old_updated_at} -> {profile.updated_at}")
        self.assertGreater(profile.updated_at, old_updated_at)

    def test_profile_initials_generation(self):
        """✅ NOVO: Teste geração de iniciais"""
        profile = self.user.profile
        expected_initials = "TU"  # Test User
        actual_initials = profile.initials

        self.assertEqual(actual_initials, expected_initials)
        print(f"✅ Iniciais geradas: {actual_initials}")
