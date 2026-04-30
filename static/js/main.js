// static/js/main.js
document.addEventListener('DOMContentLoaded', function () {

    // ==================== reCAPTCHA v3 ====================
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

    // ==================== LÓGICA DE PRODUTOS ====================
    const selectTamanho = document.getElementById('select-tamanho');
    const selectCor = document.getElementById('select-cor');
    const btnAdicionar = document.getElementById('btn-adicionar');
    const precoAtual = document.getElementById('preco-atual');
    const infoEstoque = document.getElementById('info-estoque');

    if (selectTamanho) {
        const basePreco = parseFloat(precoAtual?.dataset.basePreco) || 0;

        selectTamanho.addEventListener('change', function () {
            const tamanhoId = this.value;
            selectCor.innerHTML = '<option value="">Escolha a cor</option>';

            if (!tamanhoId) {
                btnAdicionar.disabled = true;
                return;
            }

            const variantes = JSON.parse(document.getElementById('variantes-data')?.textContent || '[]');

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
            if (varianteId) window.location.href = `/adicionar/${varianteId}/`;
        });
    }

    // ==================== UPLOAD E PREVIEW DE FOTO NO PERFIL ====================
    const fileInput = document.getElementById('foto-upload');
    const previewImg = document.getElementById('preview-img');
    const btnRemover = document.getElementById('btn-remover-foto');

    if (fileInput && previewImg) {
        previewImg.parentElement.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = e => previewImg.src = e.target.result;
                reader.readAsDataURL(file);
            }
        });

        if (btnRemover) {
            btnRemover.addEventListener('click', function () {
                fileInput.value = '';
                previewImg.src = 'https://via.placeholder.com/160x160/1a0033/00d4ff?text=👤';
            });
        }
    }

    // ==================== NOTIFICAÇÕES ====================
    function carregarNotificacoes() {
        fetch('/accounts/notifications/')
            .then(res => res.json())
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

    // ==================== STATUS ONLINE - BOLINHA ====================
    function connectOnlineStatus() {
        const container = document.getElementById('profile-pic-container');
        if (!container) return;
        const userId = container.getAttribute('data-user-id');
        if (!userId) return;

        const socket = new WebSocket('wss://' + window.location.host + '/ws/online/');

        socket.onopen = () => console.log("✅ Status Online conectado");

        socket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            if (data.type === 'online_status' && String(data.user_id) === userId) {
                updateStatusDot(data.status);
            }
        };

        socket.onclose = () => {
            console.log("❌ Status Online desconectado");
            setTimeout(connectOnlineStatus, 3000);
        };
    }

    function updateStatusDot(status) {
        const dot = document.getElementById('online-dot');
        if (!dot) return;

        if (status === 'online') {
            dot.style.backgroundColor = '#22c55e';
            dot.style.display = 'block';
        } else if (status === 'ausente') {
            dot.style.backgroundColor = '#eab308';
            dot.style.display = 'block';
        } else {
            dot.style.display = 'none';
        }
    }

    // ==================== ESTRELAS CLICÁVEIS (Depoimento) ====================
    function initStarRating() {
        document.querySelectorAll('.star').forEach(star => {
            star.addEventListener('click', function () {
                const value = this.getAttribute('data-value');
                const ratingInput = document.getElementById('rating-input');
                if (ratingInput) ratingInput.value = value;

                document.querySelectorAll('.star').forEach(s => {
                    if (parseInt(s.getAttribute('data-value')) <= parseInt(value)) {
                        s.textContent = '★';
                    } else {
                        s.textContent = '☆';
                    }
                });
            });
        });
    }

    // ==================== CHAT ONLINE ====================
    let chatSocket = null;

    window.toggleChat = function() {
        const windowEl = document.getElementById('chat-window');
        windowEl.classList.toggle('d-none');

        if (!windowEl.classList.contains('d-none') && !chatSocket) {
            connectChat();
        }
    };

    function connectChat() {
        const userId = "{{ user.id }}";
        if (!userId) return;

        chatSocket = new WebSocket('wss://' + window.location.host + '/ws/chat/');

        chatSocket.onopen = () => console.log("✅ Chat conectado");

        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            if (data.type === 'chat_history' || data.type === 'chat_message') {
                renderMessages(data.messages || [data]);
            }
        };

        chatSocket.onclose = () => {
            console.log("Chat desconectado");
            setTimeout(connectChat, 3000);
        };
    }

    function renderMessages(messages) {
        const body = document.getElementById('chat-body');
        body.innerHTML = '';

        messages.forEach(msg => {
            const div = document.createElement('div');
            div.className = msg.is_from_store ? 'text-end mb-2' : 'text-start mb-2';
            div.innerHTML = `
                <div class="d-inline-block px-3 py-2 rounded-3 ${msg.is_from_store ? 'bg-primary text-white' : 'bg-secondary text-white'}">
                    ${msg.message}
                    <small class="d-block text-light opacity-75">${msg.time}</small>
                </div>`;
            body.appendChild(div);
        });
        body.scrollTop = body.scrollHeight;
    }

    window.sendChatMessage = function() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (!message || !chatSocket) return;

        chatSocket.send(JSON.stringify({ message: message }));
        input.value = '';
    };

    // ==================== INICIALIZAÇÃO ====================
    connectOnlineStatus();
    initStarRating();   // ← Ativa as estrelas do formulário de depoimento

});