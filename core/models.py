from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from django.conf import settings   

# ==================== CLOUDINARY ====================
from cloudinary.models import CloudinaryField


# ==================== CATEGORIAS ====================
class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Categorias"


# ==================== PRODUTOS ====================
class Produto(models.Model):
    nome = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    descricao = models.TextField()
    preco = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='produtos')
    
    imagem = models.ImageField(
        upload_to='produtos/',
        blank=True,
        null=True,
        verbose_name="Imagem do Produto"
    )
    disponivel = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['-criado_em']
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"


# ==================== VARIANTES ====================
class Variante(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='variantes')
    tamanho = models.CharField(max_length=10, choices=[
        ('PP', 'PP'), ('P', 'P'), ('M', 'M'), ('G', 'G'), ('GG', 'GG')
    ])
    cor = models.CharField(max_length=50)
    estoque = models.PositiveIntegerField(default=10)
    preco_extra = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=Decimal('0.00')
    )

    def __str__(self):
        return f"{self.produto.nome} - {self.tamanho} - {self.cor}"

    @property
    def preco_final(self):
        return self.produto.preco + self.preco_extra

    class Meta:
        verbose_name = "Variante"
        verbose_name_plural = "Variantes"


# ==================== CUPONS ====================
class Cupom(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=20, choices=[
        ('welcome', 'Bem-vindo'),
        ('loyalty', 'Fidelidade'),
        ('general', 'Geral')
    ])
    desconto_tipo = models.CharField(max_length=10, choices=[('percent', '%'), ('fixed', 'R$')])
    desconto_valor = models.DecimalField(max_digits=8, decimal_places=2)
    valido_ate = models.DateTimeField()
    uso_maximo = models.PositiveIntegerField(default=1)
    minimo_compra = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=Decimal('0.00')
    )

    def __str__(self):
        return self.codigo


# ==================== PEDIDO (ATUALIZADO) ====================
class Pedido(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('cancelado', 'Cancelado'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    
    external_reference = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        unique=True
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.user} - {self.status}"

    class Meta:
        ordering = ['-criado_em']
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"


# ==================== DEPOIMENTOS (TESTIMONIAL) ====================
class Testimonial(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Cliente"
    )
    nome = models.CharField(max_length=100, verbose_name="Nome do cliente")
    cidade = models.CharField(max_length=100, blank=True, verbose_name="Cidade/Estado")
    texto = models.TextField(verbose_name="Depoimento")
    
    # ⭐ ESTRELAS DE AVALIAÇÃO
    rating = models.PositiveSmallIntegerField(
        default=5,
        choices=[(i, f'{i} ⭐') for i in range(1, 6)],
        verbose_name="Avaliação"
    )
    
    foto = CloudinaryField(
        blank=True,
        null=True,
        verbose_name="Foto do cliente"
    )
    
    data = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True, verbose_name="Ativo no site")
    aprovado = models.BooleanField(default=False, verbose_name="Aprovado pelo admin")

    class Meta:
        verbose_name = "Depoimento"
        verbose_name_plural = "Depoimentos"
        ordering = ['-data']

    def __str__(self):
        return f"{self.nome} - {self.rating}⭐"

    @property
    def rating_stars(self):
        """Mostra só as estrelas preenchidas (usado no template)"""
        return '⭐' * self.rating

    @property
    def rating_stars_complete(self):
        """Mostra 5 estrelas completas (preenchidas + vazias) - mais bonito"""
        full = '⭐' * self.rating
        empty = '☆' * (5 - self.rating)
        return full + empty


# ==================== PERFIL DO USUÁRIO (Fidelidade) ====================
# (Este fica em accounts/models.py - não mexa aqui)