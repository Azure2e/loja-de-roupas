from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Produto, Variante, Cupom, Pedido, Testimonial


# ==================== DEPOIMENTOS ====================
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cidade', 'rating_stars', 'ativo', 'aprovado', 'data']
    list_filter = ['ativo', 'aprovado', 'rating', 'data']
    search_fields = ['nome', 'texto', 'cidade']
    list_editable = ['ativo', 'aprovado']
    ordering = ['-data']
    readonly_fields = ['data']

    # Ações rápidas no admin
    actions = ['aprovar_depoimentos', 'reprovar_depoimentos']

    def rating_stars(self, obj):
        return format_html('⭐' * obj.rating)
    rating_stars.short_description = 'Avaliação'

    def aprovar_depoimentos(self, request, queryset):
        queryset.update(aprovado=True)
    aprovar_depoimentos.short_description = '✅ Aprovar selecionados'

    def reprovar_depoimentos(self, request, queryset):
        queryset.update(aprovado=False)
    reprovar_depoimentos.short_description = '❌ Reprovar selecionados'


# ==================== OUTROS MODELOS ====================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug']
    prepopulated_fields = {'slug': ('nome',)}


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'preco', 'disponivel', 'imagem_preview']
    list_filter = ['categoria', 'disponivel']
    search_fields = ['nome', 'descricao']
    prepopulated_fields = {'slug': ('nome',)}

    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" style="height: 80px; width: auto; object-fit: cover; border-radius: 8px;">',
                obj.imagem.url
            )
        return "Sem imagem"
    imagem_preview.short_description = 'Imagem'


@admin.register(Variante)
class VarianteAdmin(admin.ModelAdmin):
    list_display = ['produto', 'tamanho', 'cor', 'estoque', 'preco_final']
    list_filter = ['tamanho', 'cor']


@admin.register(Cupom)
class CupomAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'tipo', 'desconto_tipo', 'desconto_valor', 'valido_ate']
    list_filter = ['tipo', 'desconto_tipo']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total', 'status', 'criado_em']
    list_filter = ['status', 'criado_em']
    search_fields = ['external_reference', 'user__username']


# ==================== FIM ====================
# Não precisa registrar manualmente aqui (todos já estão com @admin.register)