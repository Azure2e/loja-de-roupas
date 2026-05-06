from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        Personaliza a criação do usuário quando fizer login com Facebook.
        Se o Facebook não retornar username, cria um automático usando o ID do Facebook.
        """
        user = super().populate_user(request, sociallogin, data)

        # Gera username único se não existir
        if not user.username or user.username.strip() == '':
            user.username = f"fb_{sociallogin.account.uid}"

        return user