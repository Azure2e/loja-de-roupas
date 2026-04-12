from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Produto, Variante

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug']
    prepopulated_fields = {'slug': ('nome',)}

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'preco', 'disponivel', 'imagem_preview']
    list_filter = ['categoria', 'disponivel']
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ['nome', 'descricao']

    # Preview da imagem no admin
    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" style="height: 80px; width: auto; object-fit: cover; border-radius: 8px;">',
                obj.imagem.url
            )
        return "Sem imagem"
    imagem_preview.short_description = 'Imagem' # pyright: ignore[reportFunctionMemberAccess]
    imagem_preview.allow_tags = True # pyright: ignore[reportFunctionMemberAccess]

@admin.register(Variante)
class VarianteAdmin(admin.ModelAdmin):
    list_display = ['produto', 'tamanho', 'cor', 'estoque', 'preco_final']
    list_filter = ['tamanho', 'cor']