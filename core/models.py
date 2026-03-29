from django.db import models

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Categorias"


class Produto(models.Model):
    nome = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='produtos')
    
    # ==================== IMAGEM DO PRODUTO (MELHORADO) ====================
    imagem = models.ImageField(
        upload_to='produtos/',           # pasta onde as imagens serão salvas
        blank=True,                      # permite deixar sem imagem
        null=True,                       # permite valor nulo no banco
        verbose_name="Imagem do Produto"
    )
    
    disponivel = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['-criado_em']        # mais novos primeiro
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"


class Variante(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='variantes')
    tamanho = models.CharField(max_length=10, choices=[
        ('PP', 'PP'), ('P', 'P'), ('M', 'M'), ('G', 'G'), ('GG', 'GG')
    ])
    cor = models.CharField(max_length=50)
    estoque = models.PositiveIntegerField(default=10)
    preco_extra = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.produto.nome} - {self.tamanho} - {self.cor}"

    @property
    def preco_final(self):
        return self.produto.preco + self.preco_extra

    class Meta:
        verbose_name = "Variante"
        verbose_name_plural = "Variantes"