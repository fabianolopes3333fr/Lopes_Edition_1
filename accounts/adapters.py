"""
Adaptadores customizados para django-allauth
Integração com sistema de usuários customizado
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from .models import User


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Adaptador customizado para contas normais
    """

    def get_login_redirect_url(self, request):
        """
        Define para onde redirecionar após login
        """
        if hasattr(request.user, 'profile') and request.user.profile:
            return reverse('profiles:detail')
        return reverse('home:home')

    def save_user(self, request, user, form, commit=True):
        """
        Personaliza o salvamento do usuário
        """
        user = super().save_user(request, user, form, commit=False)

        # Configurações específicas para novos usuários
        user.is_active = False  # Requer verificação de email

        if commit:
            user.save()

        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adaptador customizado para login social (Google, Microsoft)
    """

    def pre_social_login(self, request, sociallogin):
        """
        Executado antes do login social
        Conecta conta social a conta existente se email coincidir
        """
        # Obtém o email da conta social
        email = sociallogin.account.extra_data.get('email')

        if email:
            try:
                # Verifica se já existe um usuário com este email
                existing_user = User.objects.get(email=email)

                # Se o usuário existe mas não está conectado à conta social
                if not sociallogin.is_existing:
                    # Conecta a conta social ao usuário existente
                    sociallogin.connect(request, existing_user)
                    messages.info(
                        request,
                        f"Sua conta {sociallogin.account.provider.title()} foi conectada com sucesso à sua conta existente."
                    )

            except User.DoesNotExist:
                # Usuário não existe, prossegue com criação normal
                pass

    def populate_user(self, request, sociallogin, data):
        """
        Popula dados do usuário a partir da conta social
        """
        user = super().populate_user(request, sociallogin, data)

        # Dados específicos do Google
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data

            # Define nome e sobrenome se disponível
            if not user.first_name and extra_data.get('given_name'):
                user.first_name = extra_data.get('given_name')

            if not user.last_name and extra_data.get('family_name'):
                user.last_name = extra_data.get('family_name')

        # Dados específicos do Microsoft
        elif sociallogin.account.provider == 'microsoft':
            extra_data = sociallogin.account.extra_data

            # Define nome e sobrenome se disponível
            if not user.first_name and extra_data.get('givenName'):
                user.first_name = extra_data.get('givenName')

            if not user.last_name and extra_data.get('surname'):
                user.last_name = extra_data.get('surname')

        # Usuários de login social são ativados automaticamente
        user.is_active = True

        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Salva o usuário criado via login social
        """
        user = super().save_user(request, sociallogin, form)

        # Define tipo de conta padrão para usuários sociais
        if not hasattr(user, 'account_type') or not user.account_type:
            user.account_type = 'CLIENT'
            user.save()

        # Cria mensagem de boas-vindas
        provider_name = sociallogin.account.provider.title()
        messages.success(
            request,
            f"Bem-vindo à Lopes Peinture! Sua conta foi criada com sucesso usando {provider_name}."
        )

        return user

    def get_connect_redirect_url(self, request, socialaccount):
        """
        URL de redirecionamento após conectar conta social
        """
        messages.success(
            request,
            f"Sua conta {socialaccount.provider.title()} foi conectada com sucesso!"
        )
        return reverse('profiles:detail')

    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """
        Trata erros de autenticação social
        """
        error_messages = {
            'google': "Erro na autenticação com Google. Tente novamente ou use outro método de login.",
            'microsoft': "Erro na autenticação com Microsoft. Tente novamente ou use outro método de login.",
        }

        message = error_messages.get(provider_id, "Erro na autenticação social. Tente novamente.")
        messages.error(request, message)

        # Redireciona para página de login
        return redirect('accounts:login')

    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Determina se o cadastro automático é permitido
        """
        # Permite cadastro automático para provedores confiáveis
        trusted_providers = ['google', 'microsoft']
        return sociallogin.account.provider in trusted_providers
