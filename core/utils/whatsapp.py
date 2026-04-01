# core/utils/whatsapp.py
import requests
from django.conf import settings

def enviar_whatsapp(numero_destino: str, mensagem: str):
    """
    Envia mensagem via WhatsApp usando Brevo
    numero_destino deve vir com DDI (ex: 556881178014 ou 59171234567)
    """
    url = "https://api.brevo.com/v3/whatsapp/sendMessage"

    headers = {
        "api-key": settings.BREVO_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "senderNumber": settings.WHATSAPP_SENDER,   # Número aprovado no Brevo
        "recipientNumber": numero_destino,
        "text": mensagem                            # ← Campo correto é "text"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            print(f"✅ WhatsApp enviado com sucesso para {numero_destino}")
            return True
        else:
            print(f"❌ Erro ao enviar WhatsApp: {response.text}")
            return False

    except Exception as e:
        print(f"Erro de conexão com Brevo: {e}")
        return False