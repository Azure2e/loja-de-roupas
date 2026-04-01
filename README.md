# 🛍️ SuaLoja - Loja de Roupas Online

Loja de roupas completa desenvolvida em **Django 6.0** com design moderno, carrinho de compras, pagamento real via Mercado Pago, autenticação avançada, OTP via WhatsApp e sistema de fidelidade.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)

## ✨ Funcionalidades Implementadas

- ✅ Catálogo de produtos com variantes (tamanhos e cores)
- ✅ Carrinho de compras persistente (session)
- ✅ Sistema completo de cupons e descontos
- ✅ **Pagamento real com Mercado Pago** (Checkout)
- ✅ Autenticação completa (login, registro, reset de senha)
- ✅ **Verificação de telefone por OTP via WhatsApp** (Brevo)
- ✅ **Proteção contra força bruta** (django-axes)
- ✅ **Senha master + URL secreta** para o Admin
- ✅ Sistema de fidelidade (pontos automáticos + níveis Iniciante / Fiel / VIP)
- ✅ Design responsivo e moderno (Bootstrap + tema dark)
- ✅ Upload de imagens de produtos
- ✅ Admin seguro e personalizado

## 🚀 Como Rodar Localmente

```bash
# 1. Clone o projeto
git clone https://github.com/Azure2e/loja-de-roupas.git
cd loja-de-roupas

# 2. Ative o ambiente virtual
.\.venv\Scripts\Activate.ps1

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o .env (crie na raiz)
cp .env.example .env

# 5. Rode as migrações
python manage.py makemigrations
python manage.py migrate

# 6. Crie um superusuário
python manage.py createsuperuser

# 7. Rode o servidor
python manage.py runserver
