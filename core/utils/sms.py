# core/utils/sms.py
import requests
from django.conf import settings

def enviar_sms(numero_destino: str, mensagem: str):
    """Envia SMS via Brevo"""
    url = "https://api.brevo.com/v3/transactionalSMS/sms"
    
    headers = {
        "api-key": settings.BREVO_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "sender": "SuaLoja",
        "recipient": numero_destino,
        "content": mensagem
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            print(f"✅ SMS enviado para {numero_destino}")
            return True
        else:
            print(f"❌ Erro SMS: {response.text}")
            return False
    except Exception as e:
        print(f"Erro de conexão SMS: {e}")
        return False


def enviar_whatsapp(numero_destino: str, mensagem: str):
    """Envia WhatsApp via Brevo"""
    url = "https://api.brevo.com/v3/whatsapp/sendMessage"
    
    headers = {
        "api-key": settings.BREVO_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "senderNumber": settings.WHATSAPP_SENDER,
        "recipientNumber": numero_destino,
        "content": mensagem
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            print(f"✅ WhatsApp enviado para {numero_destino}")
            return True
        else:
            print(f"❌ Erro WhatsApp: {response.text}")
            return False
    except Exception as e:
        print(f"Erro de conexão WhatsApp: {e}")
        return False