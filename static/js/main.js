// static/js/main.js
document.addEventListener('DOMContentLoaded', function () {

    // ==================== reCAPTCHA v3 (invisível) ====================
    const RECAPTCHA_SITE_KEY = '6LcUda0sAAAAAMqlx5RebYZ-F-OIEnnqPzXsYM7x';

    function loadRecaptcha() {
        if (window.grecaptcha) return;
        const script = document.createElement('script');
        script.src = `https://www.google.com/recaptcha/api.js?render=${RECAPTCHA_SITE_KEY}`;
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
    }
    loadRecaptcha();

    // ==================== LÓGICA DE PRODUTOS (tamanho / cor) ====================
    const selectTamanho = document.getElementById('select-tamanho');
    const selectCor = document.getElementById('select-cor');
    const btnAdicionar = document.getElementById('btn-adicionar');
    const precoAtual = document.getElementById('preco-atual');
    const infoEstoque = document.getElementById('info-estoque');

    if (selectTamanho) {
        const basePreco = parseFloat(precoAtual.dataset.basePreco) || 0;

        selectTamanho.addEventListener('change', function () {
            const tamanhoId = this.value;
            selectCor.innerHTML = '<option value="">Escolha a cor</option>';

            if (!tamanhoId) {
                btnAdicionar.disabled = true;
                return;
            }

            const variantes = JSON.parse(document.getElementById('variantes-data').textContent || '[]');

            variantes.forEach(v => {
                if (String(v.tamanho_id) === tamanhoId) {
                    const opt = document.createElement('option');
                    opt.value = v.id;
                    opt.textContent = v.cor;
                    opt.dataset.precoExtra = v.preco_extra;
                    opt.dataset.estoque = v.estoque;
                    selectCor.appendChild(opt);
                }
            });
        });

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

        btnAdicionar.addEventListener('click', function () {
            const varianteId = this.dataset.varianteId;
            if (varianteId) {
                window.location.href = `/adicionar/${varianteId}/`;
            }
        });
    }

    // ==================== reCAPTCHA NO FORMULÁRIO DE LOGIN ====================
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', function (e) {
            e.preventDefault();

            if (!window.grecaptcha) {
                alert('reCAPTCHA não carregou. Recarregue a página e tente novamente.');
                return;
            }

            grecaptcha.execute(RECAPTCHA_SITE_KEY, { action: 'login' })
                .then(function (token) {
                    let tokenInput = document.getElementById('recaptcha-token');
                    if (!tokenInput) {
                        tokenInput = document.createElement('input');
                        tokenInput.type = 'hidden';
                        tokenInput.name = 'g-recaptcha-response';
                        tokenInput.id = 'recaptcha-token';
                        loginForm.appendChild(tokenInput);
                    }
                    tokenInput.value = token;
                    loginForm.submit();
                })
                .catch(function (error) {
                    console.error('Erro no reCAPTCHA:', error);
                    alert('Erro ao verificar reCAPTCHA. Tente novamente.');
                });
        });
    }

    // ==================== UPLOAD E PREVIEW DE FOTO NO PERFIL ====================
    const fileInput  = document.getElementById('foto-upload');
    const previewImg = document.getElementById('preview-img');
    const btnRemover = document.getElementById('btn-remover-foto');

    if (fileInput && previewImg) {
        previewImg.parentElement.addEventListener('click', function () {
            fileInput.click();
        });

        fileInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    previewImg.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });

        if (btnRemover) {
            btnRemover.addEventListener('click', function () {
                fileInput.value = '';
                previewImg.src = 'https://via.placeholder.com/160x160/1a0033/00d4ff?text=👤';
                
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-info rounded-4 text-center mt-3';
                alertDiv.textContent = 'Foto removida. Salve as alterações para confirmar.';
                document.querySelector('.card-body').insertBefore(alertDiv, document.querySelector('form'));
                setTimeout(() => alertDiv.remove(), 4000);
            });
        }
    }

    // ==================== NOTIFICAÇÕES (Bell) ====================
    function carregarNotificacoes() {
        fetch('/accounts/notifications/')
            .then(response => response.json())
            .then(data => {
                const countEl = document.getElementById('notification-count');
                const listEl = document.getElementById('notification-list');

                if (countEl) countEl.textContent = data.unread_count || 0;

                let html = '';
                if (data.notifications && data.notifications.length > 0) {
                    data.notifications.forEach(notif => {
                        html += `
                            <li class="dropdown-item border-bottom border-secondary py-2">
                                <strong>${notif.title}</strong><br>
                                <small class="text-light">${notif.message}</small><br>
                                <small class="text-muted">${notif.time}</small>
                            </li>`;
                    });
                } else {
                    html = '<li class="dropdown-item text-center text-muted py-3">Nenhuma notificação</li>';
                }
                listEl.innerHTML = html;
            })
            .catch(() => {});
    }

    setInterval(carregarNotificacoes, 8000);
    carregarNotificacoes();

    // ==================== STATUS ONLINE - BOLINHA (Verde / Amarelo) ====================
    function connectOnlineStatus() {
        const userId = document.getElementById('profile-pic-container')?.dataset.userId;
        if (!userId) return;

        const socket = new WebSocket('wss://' + window.location.host + '/ws/online/');

        socket.onopen = function () {
            console.log("✅ Status Online conectado");
        };

        socket.onmessage = function (e) {
            const data = JSON.parse(e.data);
            if (data.type === 'online_status' && String(data.user_id) === userId) {
                updateStatusDot(data.status);
            }
        };

        socket.onclose = function () {
            console.log("❌ Status Online desconectado");
            setTimeout(connectOnlineStatus, 3000);
        };
    }

    function updateStatusDot(status) {
        const dot = document.getElementById('online-dot');
        if (!dot) return;

        if (status === 'online') {
            dot.style.backgroundColor = '#22c55e';   // Verde
            dot.style.display = 'block';
        } 
        else if (status === 'ausente') {
            dot.style.backgroundColor = '#eab308';   // Amarelo
            dot.style.display = 'block';
        } 
        else {
            dot.style.display = 'none';              // Offline
        }
    }

    // Inicia o status online
    connectOnlineStatus();

});