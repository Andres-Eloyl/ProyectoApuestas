// Función global para mostrar notificaciones tipo Toast
window.showToast = function (message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        // Create container if it doesn't exist
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed top-20 right-6 z-50 flex flex-col gap-2';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const bgColors = {
        'info': 'bg-primary/90 border-primary',
        'warning': 'bg-yellow-500/90 border-yellow-400',
        'error': 'bg-red-500/90 border-red-400',
        'success': 'bg-emerald-500/90 border-emerald-400'
    };

    const iconMap = {
        'info': 'info',
        'warning': 'warning',
        'error': 'error',
        'success': 'check_circle'
    };

    toast.className = `flex items-center gap-3 px-4 py-3 rounded shadow-lg border-l-4 text-white text-xs font-bold transform transition-all duration-300 translate-x-full opacity-0 ${bgColors[type]}`;

    toast.innerHTML = `
        <span class="material-symbols-outlined text-sm">${iconMap[type]}</span>
        <span>${message}</span>
    `;

    document.getElementById('toast-container').appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
        toast.classList.remove('translate-x-full', 'opacity-0');
        toast.classList.add('translate-x-0', 'opacity-100');
    });

    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('translate-x-0', 'opacity-100');
        toast.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

// --- MODAL SYSTEM LOGIC ---
window.openModal = function (templateId) {
    const globalModal = document.getElementById('global-modal');
    const modalBody = document.getElementById('modal-body');
    const template = document.getElementById('tpl-' + templateId);

    if (globalModal && modalBody && template) {
        // Cargar el contenido
        modalBody.innerHTML = template.innerHTML;

        // Mostrar
        globalModal.classList.remove('hidden');
        globalModal.classList.add('flex');

        // Animacion entrada
        requestAnimationFrame(() => {
            globalModal.classList.remove('opacity-0');
            globalModal.classList.add('opacity-100');
            const wrapper = document.getElementById('modal-content-wrapper');
            if (wrapper) {
                wrapper.classList.remove('scale-95');
                wrapper.classList.add('scale-100');
            }
        });
    } else {
        showToast('Ventana no disponible aún.', 'warning');
    }
};

window.closeModal = function () {
    const globalModal = document.getElementById('global-modal');
    if (globalModal) {
        // Animacion salida
        globalModal.classList.remove('opacity-100');
        globalModal.classList.add('opacity-0');
        const wrapper = document.getElementById('modal-content-wrapper');
        if (wrapper) {
            wrapper.classList.remove('scale-100');
            wrapper.classList.add('scale-95');
        }

        setTimeout(() => {
            globalModal.classList.add('hidden');
            globalModal.classList.remove('flex');
            document.getElementById('modal-body').innerHTML = '';
        }, 300);
    }
};

// Cerrar modal con Escape o Clic fuera
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});
document.addEventListener('click', (e) => {
    if (e.target.id === 'global-modal') closeModal();
});

// --- FULLSCREEN LOGIC ---
window.toggleFullScreen = function () {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch((err) => {
            showToast(`Error al intentar pantalla completa: ${err.message}`, 'error');
        });
        showToast('Pantalla Completa Activada', 'success');
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
};

// --- INTERACTIVE TUTORIAL LOGIC ---
const tutorialSteps = [
    {
        badge: 'Live Analysis',
        badgeClass: 'bg-red-600',
        title: 'EL PODER DEL <br /><span class="text-primary italic">DATO PURO.</span>',
        description: 'Transformamos la pasión del estadio en métricas de alta precisión. Analítica avanzada para decisiones en milisegundos.',
        actions: `
            <a href="#terminal" onclick="smoothScrollTo(event, 'terminal')" class="h-12 px-8 bg-primary text-white font-black rounded hover:brightness-110 transition-all shadow-xl shadow-primary/20 flex items-center gap-2">
                ABRIR TERMINAL <span class="material-symbols-outlined text-sm">terminal</span>
            </a>
            <a href="#alertavalor" onclick="smoothScrollTo(event, 'alertavalor')" class="h-12 px-8 bg-white/5 backdrop-blur-md border border-white/10 text-white font-black rounded hover:bg-white/10 transition-all flex items-center justify-center">
                EXPLORAR MERCADOS
            </a>
        `
    },
    {
        badge: 'Monitor',
        badgeClass: 'bg-emerald-600',
        title: 'MONITOR<br /><span class="text-emerald-500 italic">EN VIVO.</span>',
        description: 'Observa en tiempo real la rentabilidad operativa. El ROI, Win Rate y Accuracy definen la salud actual de tu estrategia frente a la Inteligencia Artificial.',
        actions: `
            <a href="#livexg" onclick="smoothScrollTo(event, 'livexg')" class="h-12 px-8 bg-emerald-600 text-white font-black rounded hover:brightness-110 transition-all shadow-xl shadow-emerald-500/20 flex items-center justify-center">
                IR AL MONITOR
            </a>
        `
    },
    {
        badge: 'Value Picks',
        badgeClass: 'bg-orange-500',
        title: 'ALERTAS DE<br /><span class="text-orange-500 italic">VALOR EXTREMO.</span>',
        description: 'El motor audita contantemente discrepancias entre la casa de apuestas y nuestra probabilidad predicha. Descubre los mercados con EV+ (Expected Value Positivo) al instante.',
        actions: `
            <a href="#alertavalor" onclick="smoothScrollTo(event, 'alertavalor')" class="h-12 px-8 bg-orange-600 text-white font-black rounded hover:brightness-110 transition-all shadow-xl shadow-orange-500/20 flex items-center justify-center">
                VER ALERTAS
            </a>
        `
    },
    {
        badge: 'Terminal',
        badgeClass: 'bg-purple-600',
        title: 'TERMINAL<br /><span class="text-purple-500 italic">MULTICANAL.</span>',
        description: 'Todas las ligas cruzadas con variables de xG, confianza del modelo y ratings IA. Revisa al detalle cada partido disponible.',
        actions: `
            <a href="#terminal" onclick="smoothScrollTo(event, 'terminal')" class="h-12 px-8 bg-purple-600 text-white font-black rounded hover:brightness-110 transition-all shadow-xl shadow-purple-500/20 flex items-center justify-center">
                DWH TERMINAL
            </a>
        `
    },
    {
        badge: 'Precisión',
        badgeClass: 'bg-slate-600',
        title: 'AUDITORÍA<br /><span class="text-slate-400 italic">Y PRECISIÓN.</span>',
        description: 'Visualiza la confiabilidad por liga y el historial reciente de predicciones. Transparencia total sobre los aciertos y fallos de la red neuronal.',
        actions: `
            <a href="#rendimiento" onclick="smoothScrollTo(event, 'rendimiento')" class="h-12 px-8 bg-slate-700 text-white font-black rounded hover:brightness-110 transition-all shadow-xl flex items-center justify-center">
                EVALUAR RESULTADOS
            </a>
        `
    }
];

let currentGuideStep = 0;

function updateGuideCarousel() {
    const container = document.getElementById('hero-carousel-content');
    const badgeContainer = document.getElementById('hero-badge-container');
    const title = document.getElementById('hero-title');
    const desc = document.getElementById('hero-description');
    const actions = document.getElementById('hero-actions');
    const indicators = document.getElementById('hero-indicators');

    if (!container) return;

    // Fade out
    container.classList.add('opacity-0');

    setTimeout(() => {
        const step = tutorialSteps[currentGuideStep];

        // Update content
        badgeContainer.innerHTML = `<span class="px-2 py-1 text-white text-[10px] font-black uppercase tracking-tighter shadow-sm ${step.badgeClass}">${step.badge}</span>`;
        title.innerHTML = step.title;
        desc.innerHTML = step.description;
        actions.innerHTML = step.actions;

        // Update indicators
        indicators.innerHTML = tutorialSteps.map((_, index) => `
            <div class="h-1.5 rounded-full transition-all duration-300 ${index === currentGuideStep ? 'w-6 bg-primary' : 'w-1.5 bg-white/20 hover:bg-white/40 cursor-pointer'}" 
                 onclick="goToGuideStep(${index})"></div>
        `).join('');

        // Fade in
        container.classList.remove('opacity-0');
    }, 300); // 300ms matches the transition-opacity duration-300 class
}

window.nextGuideStep = function () {
    currentGuideStep = (currentGuideStep + 1) % tutorialSteps.length;
    updateGuideCarousel();
};

window.prevGuideStep = function () {
    currentGuideStep = (currentGuideStep - 1 + tutorialSteps.length) % tutorialSteps.length;
    updateGuideCarousel();
};

window.goToGuideStep = function (stepIndex) {
    if (stepIndex !== currentGuideStep) {
        currentGuideStep = stepIndex;
        updateGuideCarousel();
    }
};

window.smoothScrollTo = function (event, targetId) {
    if (event) event.preventDefault();
    const target = document.getElementById(targetId);
    if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
    }
};

document.addEventListener("DOMContentLoaded", () => {
    // Initialize guide indicators
    updateGuideCarousel();

    // 1. Fetch Precision Metrics
    fetch('/api/metricas_globales')
        .then(res => res.json())
        .then(data => {
            const elPrecision = document.getElementById('ui-precision');
            const elAciertos = document.getElementById('ui-aciertos');
            const elFallos = document.getElementById('ui-fallos');
            const elEficiencia = document.getElementById('ui-eficiencia-ligas');
            const elRoi = document.getElementById('ui-roi');
            const elWr = document.getElementById('ui-wr');
            const elAcc = document.getElementById('ui-acc');

            if (elPrecision) elPrecision.textContent = `${data.Precision_Global.toFixed(1)}% `;
            if (elAciertos) elAciertos.textContent = `+ ${data.Aciertos} `;
            if (elFallos) elFallos.textContent = `- ${data.Fallos} `;

            // Stats en header superior
            if (elRoi) elRoi.textContent = `+ ${(data.Precision_Global / 10).toFixed(1)}% ROI`; // Estimado
            if (elWr) elWr.textContent = `${data.Precision_Global.toFixed(1)}% WR`;
            if (elAcc) elAcc.textContent = `${data.Precision_Global.toFixed(0)}% ACC`;

            if (elEficiencia && data.Desglose_Ligas) {
                elEficiencia.innerHTML = '';
                const ligasObj = data.Desglose_Ligas;

                // Colors map
                const colorMap = { "Premier League": "emerald-500", "La Liga": "primary", "Serie A": "orange-500", "Bundesliga": "yellow-500", "Ligue 1": "blue-400" };
                const shortMap = { "Premier League": "PL", "La Liga": "LL", "Serie A": "SA", "Bundesliga": "BL", "Ligue 1": "L1", "Champions League": "UCL" };

                for (const liga in ligasObj) {
                    const stats = ligasObj[liga];
                    const color = colorMap[liga] || "primary";
                    const shortName = shortMap[liga] || liga.substring(0, 2).toUpperCase();

                    elEficiencia.innerHTML += `
            <div class="flex items-center gap-3">
                        <span class="text-[10px] font-black text-white w-6">${shortName}</span>
                        <div class="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                            <div class="h-full bg-${color}" style="width: ${stats.precision}%"></div>
                        </div>
                        <span class="text-[10px] font-bold text-${color}">${stats.precision.toFixed(0)}%</span>
                    </div>`;
                }
            }

            // Draw Precision Chart
            const ctx = document.getElementById('precisionChart');
            if (ctx && data.Desglose_Ligas) {
                Chart.defaults.color = '#94a3b8'; // text-slate-400
                Chart.defaults.font.family = "'Inter', sans-serif";

                const ligasObj = data.Desglose_Ligas;
                const ligas = Object.keys(ligasObj);
                const winRates = ligas.map(l => ligasObj[l].precision);
                const bgColors = winRates.map(w => w >= 50 ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)'); // emerald-500 or red-500
                const borderColors = winRates.map(w => w >= 50 ? '#10b981' : '#ef4444');

                new Chart(ctx.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: ligas,
                        datasets: [{
                            label: 'Precisión IA (%)',
                            data: winRates,
                            backgroundColor: bgColors,
                            borderColor: borderColors,
                            borderWidth: 2,
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { grid: { display: false, drawBorder: false } },
                            y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.05)', drawBorder: false } }
                        }
                    }
                });
            }
        });

    // 2. Fetch Real-time Predictions & Terminal
    const tbodyTerminal = document.getElementById('ui-terminal-body');
    const alertasValors = document.getElementById('ui-alertas');
    const marquee = document.getElementById('ui-marquee');

    if (tbodyTerminal) {
        tbodyTerminal.innerHTML = `<tr><td colspan="7" class="text-center p-4">Iniciando oráculo neuronal neuronal...</td></tr>`;
    }

    fetch('/api/predicciones_hoy')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                if (tbodyTerminal) tbodyTerminal.innerHTML = `<tr><td colspan="7" class="text-center text-red-500 p-4">Error: ${data.error}</td></tr>`;
                return;
            }
            renderTerminalAndAlertas(data);
        })
        .catch(err => {
            if (tbodyTerminal) tbodyTerminal.innerHTML = `<tr><td colspan="7" class="text-center text-red-500 p-4">Falla de conexión con el backend.</td></tr>`;
        });

    function renderTerminalAndAlertas(predictions) {
        if (tbodyTerminal) tbodyTerminal.innerHTML = '';
        if (alertasValors) alertasValors.innerHTML = '';

        const partidosCriticosContainer = document.getElementById('ui-partidos-criticos');
        if (partidosCriticosContainer) {
            partidosCriticosContainer.innerHTML = '';
            const criticos = [...predictions].filter(p => p.Recomendacion !== 'No Bet').sort((a, b) => b.Probabilidad - a.Probabilidad).slice(0, 2);
            while (criticos.length < 2 && predictions.length > criticos.length) {
                const p = predictions.find(pred => !criticos.includes(pred));
                if (p) criticos.push(p);
            }
            criticos.forEach((p, index) => {
                const totalG = (p.Proj_Goles_L + p.Proj_Goles_V) || 1;
                const pctL = Math.round((p.Proj_Goles_L / totalG) * 100);
                const pctV = 100 - pctL;
                const posL = Math.round(p.Probabilidad * 100);
                const posV = 100 - posL;
                partidosCriticosContainer.innerHTML += `
            <div class="p-3 bg-slate-900/40 border border-slate-800 rounded hover:border-primary/50 transition-colors cursor-pointer group">
                                <div class="flex justify-between items-center mb-2">
                                    <span class="text-[9px] text-slate-500 font-bold uppercase">Predicción • Carga Actual</span>
                                    <span class="text-[9px] px-1 ${index === 0 ? 'bg-primary text-white' : 'bg-slate-800 text-slate-400'} rounded">${index === 0 ? 'DESTACADO' : 'SEGUIMIENTO'}</span>
                                </div>
                                <div class="grid grid-cols-3 items-center gap-2 mb-3 text-center">
                                    <div class="text-[11px] font-bold text-white uppercase truncate">${p.HomeTeam}</div>
                                    <div class="text-xs font-black text-primary">${p.Proj_Goles_L} - ${p.Proj_Goles_V}</div>
                                    <div class="text-[11px] font-bold text-white uppercase truncate">${p.AwayTeam}</div>
                                </div>
                                <div class="space-y-1.5">
                                    <div class="flex justify-between text-[10px]">
                                        <span class="text-slate-500 uppercase">xG (Proyectado)</span>
                                        <span class="text-white font-bold">${p.Proj_Goles_L} - ${p.Proj_Goles_V}</span>
                                    </div>
                                    <div class="h-1 bg-slate-800 rounded-full overflow-hidden flex">
                                        <div class="h-full bg-primary" style="width: ${pctL}%"></div>
                                        <div class="h-full bg-slate-700" style="width: ${pctV}%"></div>
                                    </div>
                                    <div class="flex justify-between text-[10px]">
                                        <span class="text-slate-500 uppercase">Probabilidad (H-A)</span>
                                        <span class="text-white font-bold">${posL}% - ${posV}%</span>
                                    </div>
                                </div>
                            </div>`;
            });
        }

        let marqueeText = "";

        // Ordenamos las alertas de valor (solo EV > 1.0) por EV
        const valuePicks = [...predictions].filter(p => parseFloat(p.EV) > 1.0).sort((a, b) => b.EV - a.EV);

        // Render Alertas de Valor (Top 4)
        valuePicks.slice(0, 4).forEach((p, index) => {
            const colors = ['primary', 'emerald-500', 'orange-500', 'slate-400'];
            const color = colors[index % colors.length];
            const ev = parseFloat(p.EV);
            const valueStr = ev > 1.0 ? `+ ${(ev - 1.0).toFixed(2)} v` : '0.00v';

            alertasValors.innerHTML += `
            <div class="p-2 border-l-2 border-${color} bg-slate-900/40 flex items-center justify-between group cursor-pointer hover:bg-slate-900">
                <div>
                    <p class="text-[9px] text-slate-500 font-bold uppercase">${p.HomeTeam} vs ${p.AwayTeam}</p>
                    <p class="text-[11px] font-black text-white">${p.Recomendacion !== 'No Bet' ? p.Recomendacion : 'Revisión Manual'}</p>
                </div>
                <div class="text-right">
                    <p class="text-[10px] font-black text-${color}">${valueStr}</p>
                    <p class="text-[9px] text-slate-500 font-bold">@${p.Cuota}</p>
                </div>
            </div>`;
        });

        // Render Terminal Body
        predictions.forEach(p => {
            const isInvest = p.Recomendacion !== 'No Bet';
            const colorClass = isInvest ? 'emerald-500' : 'slate-500';
            const bgClass = isInvest ? 'emerald-500/10' : 'slate-500/10';
            const ev = parseFloat(p.EV);
            const valueStr = ev > 1.0 ? `+ ${((ev - 1.0) * 100).toFixed(1)}% ` : '0.0%';



            tbodyTerminal.innerHTML += `
            <tr class="border-b border-slate-800/50 hover:bg-slate-900/30 transition-colors">
                <td class="p-4">
                    <span class="text-white font-bold block">${p.HomeTeam} vs ${p.AwayTeam}</span> 
                    <span class="text-[9px] text-slate-600 font-black uppercase tracking-widest">${p.Recomendacion !== 'No Bet' ? 'EV+ Detectado' : 'Sin Valor'}</span>
                </td>
                <td class="p-4"><span class="px-2 py-0.5 bg-${bgClass} text-${colorClass} rounded font-black">${(p.Probabilidad * 10).toFixed(1)}</span></td>
                <td class="p-4">${p.Proj_Goles_L} / ${p.Proj_Goles_V}</td>
                <td class="p-4">
                    <div class="flex gap-0.5">
                        <div class="h-4 w-1 bg-${colorClass}"></div>
                        <div class="h-4 w-1 bg-${colorClass}"></div>
                        <div class="h-4 w-1 bg-${colorClass}/${isInvest ? '50' : '100'}"></div>
                        <div class="h-4 w-1 bg-${colorClass}/${isInvest ? '30' : '100'}"></div>
                    </div>
                </td>
                <td class="p-4">${p.Cuota}</td>
                <td class="p-4 text-${colorClass} font-bold">${valueStr}</td>
                <td class="p-4">
                    <div class="h-1 w-12 bg-slate-800 rounded-full overflow-hidden">
                        <div class="h-full bg-primary" style="width: ${(p.Probabilidad * 100).toFixed(0)}%"></div>
                    </div>
                </td>
            </tr>`;
        });

        if (marquee) {
            if (valuePicks.length > 0) {
                const top3 = valuePicks.slice(0, 3);
                marqueeText = top3.map(p => `STRONG PICK: ${p.HomeTeam.toUpperCase()} vs ${p.AwayTeam.toUpperCase()} | VALOR(EV): ${p.EV} | CUOTA: ${p.Cuota} | SUGERENCIA: ${p.Recomendacion} (Confianza: ${(p.Probabilidad * 100).toFixed(0)
                    }%)`).join('   ✦   ');
            } else {
                marqueeText = "Buscando valor en los mercados globales... No se detectaron anomalías EV+ en la sesión actual.";
            }
            marquee.textContent = marqueeText + "   ✦   " + marqueeText; // Duplicate for smooth looping
        }
    }

    // 3. Fetch Insights para Sugerencia del Sistema
    fetch('/api/insights')
        .then(res => res.json())
        .then(data => {
            const elSugerencia = document.getElementById('ui-sugerencia');
            if (elSugerencia && data.length > 0) {
                // Use the first insight
                elSugerencia.textContent = `"${data[0].mensaje}"`;
            } else if (elSugerencia) {
                elSugerencia.textContent = "Sin anomalías detectadas en mercados primarios de la sesión.";
            }
        });

    // 4. Fetch Historial Auditoria
    fetch('/api/historial_evaluado')
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('ui-auditoria-body');
            if (!tbody) return;
            tbody.innerHTML = '';
            if (!data || data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" class="p-4 text-center">Sin datos recientes</td></tr>';
                return;
            }

            // Limit to last 5
            const recent = data.slice(-5).reverse();
            recent.forEach(p => {
                const isHit = p.Acierto === "ACIERTO";
                const isPending = p.Acierto === "PENDIENTE";
                const color = isHit ? 'emerald-500' : (isPending ? 'slate-400' : 'red-500');
                tbody.innerHTML += `
                <tr class="border-b border-slate-800/50 hover:bg-slate-900/30 transition-colors">
                    <td class="p-4">${p.Fecha}</td>
                    <td class="p-4"><strong class="text-white">${p.Partido}</strong></td>
                    <td class="p-4 text-primary font-bold">${p.Prediccion_IA}</td>
                    <td class="p-4 text-${color} font-black">${p.Resultado_Real !== '-' ? p.Resultado_Real : ''} ${p.Acierto}</td>
                </tr>`;
            });
        });

    // 5. Lógica del Asistente Analista (Chatbot)
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    const chatMessages = document.getElementById('chat-messages');

    function appendMessage(sender, text) {
        if (!chatMessages) return;

        const isUser = sender === 'user';
        const iconClasses = isUser ? 'person text-slate-400' : 'smart_toy text-primary';
        const bgClasses = isUser ? 'bg-primary/20 text-white border-primary/30 rounded-tr-none' : 'bg-slate-800/80 text-slate-300 border-slate-700/50 rounded-tl-none';

        // Parsear markdown básico (negritas)
        const parsedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Convertir saltos de línea a <br>
        const formattedText = parsedText.replace(/\n/g, '<br>');

        const msgHTML = `
        <div class="flex gap-2 text-sm max-w-[90%] ${isUser ? 'ml-auto flex-row-reverse' : ''}">
            <span class="material-symbols-outlined text-sm mt-0.5" class="${iconClasses}">${isUser ? 'person' : 'smart_toy'}</span>
            <div class="${bgClasses} p-2 rounded-lg border text-xs leading-relaxed" style="word-break: break-word;">
                ${formattedText}
            </div>
        </div>`;

        chatMessages.insertAdjacentHTML('beforeend', msgHTML);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll
    }

    function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Limpiar input y mostrar msj del usuario
        chatInput.value = '';
        appendMessage('user', text);

        // Indicador de "escribiendo" (opcional, simplificado por ahora)

        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mensaje: text })
        })
            .then(res => res.json())
            .then(data => {
                appendMessage('bot', data.respuesta);
            })
            .catch(err => {
                console.error("Error en chat:", err);
                appendMessage('bot', `<span class="text-red-400"> Error de conexión con el núcleo analítico.</span>`);
            });
    }

    if (chatSend && chatInput) {
        chatSend.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    // 6. Lógica de toggle para el Chatbot Flotante
    const chatbotContainer = document.getElementById('floating-chatbot');
    const chatbotToggleBtn = document.getElementById('chatbot-toggle');
    const chatbotIcon = document.getElementById('chatbot-icon');

    if (chatbotContainer && chatbotToggleBtn && chatbotIcon) {
        let isChatbotOpen = false;

        chatbotToggleBtn.addEventListener('click', () => {
            isChatbotOpen = !isChatbotOpen;

            if (isChatbotOpen) {
                chatbotContainer.classList.remove('translate-y-[calc(100%-48px)]');
                chatbotContainer.classList.add('translate-y-0');
                chatbotIcon.classList.add('rotate-180');
                // Auto-focus the input after a short delay
                setTimeout(() => chatInput && chatInput.focus(), 300);
            } else {
                chatbotContainer.classList.remove('translate-y-0');
                chatbotContainer.classList.add('translate-y-[calc(100%-48px)]');
                chatbotIcon.classList.remove('rotate-180');
            }
        });
    }

});
