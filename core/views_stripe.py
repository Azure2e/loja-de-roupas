import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

# ===================== VIEW PARA CRIAR CHECKOUT SESSION =====================
def create_checkout_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Exemplo: você pode passar valor, descrição, etc.
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'brl',
                        'product_data': {
                            'name': data.get('product_name', 'Produto da Loja'),
                        },
                        'unit_amount': int(float(data.get('amount', 0)) * 100),  # valor em centavos
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/pagamento/sucesso/'),
                cancel_url=request.build_absolute_uri('/pagamento/cancelado/'),
                metadata={
                    'user_id': request.user.id if request.user.is_authenticated else None,
                }
            )
            return JsonResponse({'id': session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método não permitido'}, status=405)


# ===================== PÁGINAS DE SUCESSO E CANCELAMENTO =====================
class PaymentSuccessView(TemplateView):
    template_name = 'core/payment_success.html'

class PaymentCancelView(TemplateView):
    template_name = 'core/payment_cancel.html'


# ===================== WEBHOOK DO STRIPE (MUITO IMPORTANTE) =====================
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # ==================== TRATAMENTO DE EVENTOS ====================
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Aqui você pode salvar o pedido como pago
        print(f"✅ Pagamento confirmado! Session ID: {session.id}")
        # Exemplo: atualizar pedido no banco
        # Pedido.objects.filter(stripe_session_id=session.id).update(pago=True)

    elif event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print(f"💰 Pagamento via PaymentIntent confirmado: {payment_intent.id}")

    return HttpResponse(status=200)