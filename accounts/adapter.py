from allauth.socialaccount.adapter import DefaultSocialAccountAdapter  # type: ignore
import uuid

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        Personaliza a criação do usuário quando fizer login com Facebook.
        Gera username único com UUID pra evitar conflito se o Facebook não mandar.
        """
        user = super().populate_user(request, sociallogin, data)

        # Gera username único sempre com UUID pra não dar conflito
        if not user.username or user.username.strip() == '':
            user.username = f"fb_{uuid.uuid4().hex[:10]}"
        
        # Email fake válido caso o Facebook não mande
        if not user.email:
            user.email = f"{user.username}@users.noreply.localhost"
            
        return user