// ==================== DETALHE DO PRODUTO - SELEÇÃO DE TAMANHO E COR ====================
document.addEventListener('DOMContentLoaded', function () {
    const selectTamanho = document.getElementById('select-tamanho');
    const selectCor = document.getElementById('select-cor');
    const btnAdicionar = document.getElementById('btn-adicionar');
    const precoAtual = document.getElementById('preco-atual');
    const infoEstoque = document.getElementById('info-estoque');

    if (!selectTamanho) return; // Sai se não estiver na página de detalhe

    const basePreco = parseFloat(precoAtual.textContent.replace('R$', '').trim()) || 0;

    // Quando o usuário escolhe o tamanho
    selectTamanho.addEventListener('change', function () {
        const tamanhoId = this.value;
        selectCor.innerHTML = '<option value="">Escolha a cor</option>';

        if (!tamanhoId) {
            btnAdicionar.disabled = true;
            return;
        }

        // Adiciona as cores disponíveis para o tamanho escolhido
        {% for v in variantes %}
        if ("{{ v.id }}" === tamanhoId) {
            const opt = document.createElement('option');
            opt.value = "{{ v.id }}";
            opt.textContent = "{{ v.cor }}";
            opt.dataset.precoExtra = "{{ v.preco_extra }}";
            opt.dataset.estoque = "{{ v.estoque }}";
            selectCor.appendChild(opt);
        }
        {% endfor %}
    });

    // Quando o usuário escolhe a cor
    selectCor.addEventListener('change', function () {
        const option = this.options[this.selectedIndex];
        if (!option.value) {
            btnAdicionar.disabled = true;
            return;
        }

        const precoExtra = parseFloat(option.dataset.precoExtra) || 0;
        const estoque = parseInt(option.dataset.estoque) || 0;
        const precoFinal = basePreco + precoExtra;

        precoAtual.textContent = `R$ ${precoFinal.toFixed(2)}`;
        infoEstoque.innerHTML = `Estoque disponível: <strong>${estoque}</strong> unidades`;

        btnAdicionar.disabled = false;
        btnAdicionar.dataset.varianteId = option.value;
    });

    // Clique no botão "Adicionar ao Carrinho"
    btnAdicionar.addEventListener('click', function () {
        const varianteId = this.dataset.varianteId;
        if (varianteId) {
            window.location.href = `{% url 'core:adicionar_carrinho' 999 %}`.replace('999', varianteId);
        }
    });
});