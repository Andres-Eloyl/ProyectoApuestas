document.addEventListener("DOMContentLoaded", () => {
    // Top Date
    const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('currentDate').textContent = new Date().toLocaleDateString('es-ES', dateOptions);

    // Initial Status Check Simulation
    setTimeout(() => {
        const titleEl = document.getElementById('data-status-title');
        titleEl.textContent = "Datos Sincronizados";
        titleEl.style.color = "var(--success)";
    }, 1200);

    // Navigation Logic
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.view-section');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            navItems.forEach(nav => nav.classList.remove('active'));
            sections.forEach(sec => sec.classList.remove('active'));

            item.classList.add('active');
            const target = item.getAttribute('data-target');
            document.getElementById(target).classList.add('active');
        });
    });

    // 1. Fetch Precision Metrics & Chart (IA vs Realidad)
    fetch('/api/metricas_globales')
        .then(res => res.json())
        .then(data => {
            document.getElementById('g-partidos').textContent = data.Total_Partidos;
            document.getElementById('g-aciertos').textContent = data.Aciertos;
            document.getElementById('g-fallos').textContent = data.Fallos;
            document.getElementById('g-precision').textContent = `${data.Precision_Global.toFixed(1)}%`;

            // Draw Precision Bar Chart
            const ctx = document.getElementById('precisionChart');
            if (ctx) {
                Chart.defaults.color = '#6B6A68';
                Chart.defaults.font.family = "'Inter', sans-serif";

                const ligasObj = data.Desglose_Ligas || {};
                const ligas = Object.keys(ligasObj);
                const winRates = ligas.map(l => ligasObj[l].precision);
                const bgColors = winRates.map(w => w >= 50 ? 'rgba(14, 142, 66, 0.7)' : 'rgba(215, 38, 61, 0.7)');
                const borderColors = winRates.map(w => w >= 50 ? '#0E8E42' : '#D7263D');

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
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                backgroundColor: '#111111',
                                titleColor: '#fff',
                                bodyColor: '#F5F4F0',
                                padding: 12,
                                displayColors: false,
                                callbacks: {
                                    label: function (context) {
                                        return context.parsed.y + '% de Acierto';
                                    }
                                }
                            }
                        },
                        scales: {
                            x: { grid: { display: false, drawBorder: false } },
                            y: {
                                beginAtZero: true,
                                max: 100,
                                grid: { color: 'rgba(0,0,0,0.03)', drawBorder: false },
                                ticks: { callback: function (value) { return value + '%'; } }
                            }
                        }
                    }
                });
            }
        });

    // 2. Fetch Real-time Predictions & Set Filters
    let rawPredictions = [];

    const tbodyPredictions = document.getElementById('predictions-body');
    if (tbodyPredictions) {
        tbodyPredictions.innerHTML = `<tr><td colspan="7" class="text-center" style="color:var(--brand-color); padding: 2rem;"><i class="fa-solid fa-circle-notch fa-spin" style="margin-right: 8px;"></i>Sincronizando Oráculo en Vivo (Tomará entre 5 y 10 segundos)...</td></tr>`;
    }

    fetch('/api/sync_predicciones')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                tbodyPredictions.innerHTML = `<tr><td colspan="7" class="text-center text-danger"><i class="fa-solid fa-triangle-exclamation"></i> Error sincronizando IA: ${data.error}</td></tr>`;
                return;
            }
            rawPredictions = data;
            renderPredictions(rawPredictions);
            generateLiveInsights(rawPredictions);
        })
        .catch(err => {
            tbodyPredictions.innerHTML = `<tr><td colspan="7" class="text-center text-danger"><i class="fa-solid fa-triangle-exclamation"></i> Falla de conexión con el backend neuronal.</td></tr>`;
        });

    function renderPredictions(dataToRender) {
        const tbody = document.getElementById('predictions-body');
        tbody.innerHTML = '';

        if (dataToRender.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">No se encontraron resultados.</td></tr>`;
            return;
        }

        dataToRender.forEach(p => {
            const tr = document.createElement('tr');
            const isInvest = p.Recomendacion !== 'No Bet';
            const colorEV = p.EV > 1.10 ? 'color: var(--success); font-weight:700;' : 'color: var(--text-primary);';

            tr.innerHTML = `
                <td><strong style="color:var(--text-primary); font-size: 1.05rem;">${p.HomeTeam}</strong> <span style="color:var(--text-muted); padding: 0 4px;">vs</span> <strong>${p.AwayTeam}</strong></td>
                <td><span style="font-family:'Outfit', sans-serif; font-size:1.15rem; font-weight:800; color:var(--text-primary)">${p.Cuota}</span></td>
                <td><span style="color:var(--brand-color); font-weight:700; background: var(--success-bg); padding: 4px 8px; border-radius: 6px;">${(p.Probabilidad * 100).toFixed(1)}%</span></td>
                <td><span style="${colorEV}; font-size:1.1rem">${p.EV.toFixed(2)}</span></td>
                <td><span style="color:var(--text-muted); font-size:0.95rem; font-weight: 500;">${p.Proj_Goles_L} - ${p.Proj_Goles_V}</span></td>
                <td><span class="highlight-box">${p.Marcador_Exacto}</span></td>
                <td>${isInvest ? `<span class="badge invest"><i class="fa-solid fa-arrow-trend-up"></i> Apostar (Stake ${(p.Kelly_Stake * 100).toFixed(1)}%)</span>` : `<span class="badge pass">Evitar (No-Bet)</span>`}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Buscador Inteligente en vivo
    const searchInput = document.getElementById('global-search');
    const filterSelect = document.getElementById('filter-market');

    // Filtros por Liga en el Dashboard Principal
    const leagueBadges = document.querySelectorAll('.filter-league');
    leagueBadges.forEach(badge => {
        badge.addEventListener('click', (e) => {
            e.preventDefault();
            // Ir a la vista de predicciones si no estamos ahí
            document.querySelector('[data-target="view-predictions"]').click();
            // Llenar el buscador y disparar
            searchInput.value = badge.getAttribute('data-league');
            applyFilters();
        });
    });

    function applyFilters() {
        const searchTerm = searchInput.value.toLowerCase();
        const filterVal = filterSelect.value;

        // Mapa de ligas expandido para habilitar el filtrado inteligente
        const LEAGUES_MAP = {
            "La Liga": ["real madrid", "barcelona", "ath madrid", "sociedad", "betis", "valencia", "athletic", "osasuna", "celta", "alaves", "levante", "vallecano", "elche", "girona", "mallorca", "las palmas", "sevilla", "villarreal"],
            "Premier League": ["man city", "man united", "newcastle", "tottenham", "aston villa", "west ham", "brighton", "wolves", "nott'm forest", "sheffield united", "arsenal", "liverpool", "chelsea", "everton", "crystal palace", "fulham", "brentford", "bournemouth"],
            "Serie A": ["inter", "milan", "juventus", "roma", "napoli", "lazio", "atalanta", "fiorentina", "bologna", "torino", "monza", "genoa", "lecce", "empoli"],
            "Bundesliga": ["bayern munich", "dortmund", "leverkusen", "rb leipzig", "ein frankfurt", "stuttgart", "hoffenheim", "freiburg", "wolfsburg", "heidenheim"]
        };

        let filtered = rawPredictions.filter(p => {
            const h = p.HomeTeam.toLowerCase();
            const a = p.AwayTeam.toLowerCase();
            const matchText = `${h} ${a}`;

            // Verifica si el texto está en el nombre de los equipos
            const matchesName = matchText.includes(searchTerm);

            // Verifica si el término coincide parcialmente con el nombre de alguna liga (ej: "premier")
            let matchesLeague = false;
            if (searchTerm.trim() !== '') {
                for (const [leagueName, teams] of Object.entries(LEAGUES_MAP)) {
                    if (leagueName.toLowerCase().includes(searchTerm)) {
                        if (teams.some(team => h.includes(team) || a.includes(team))) {
                            matchesLeague = true;
                            break;
                        }
                    }
                }
            }

            return matchesName || matchesLeague;
        });

        if (filterVal === 'value') {
            filtered = filtered.filter(p => p.Recomendacion !== 'No Bet');
        } else if (filterVal === 'pass') {
            filtered = filtered.filter(p => p.Recomendacion === 'No Bet');
        }

        renderPredictions(filtered);
    }

    searchInput.addEventListener('input', () => {
        applyFilters();
    });

    filterSelect.addEventListener('change', applyFilters);

    // 2.5 Fetch Historial Auditoria (Temporada Actual)
    fetch('/api/historial_evaluado')
        .then(res => res.json())
        .then(data => {
            renderAuditoria(data);
        });

    function renderAuditoria(dataToRender) {
        const tbody = document.getElementById('auditoria-body');
        tbody.innerHTML = '';

        if (!dataToRender || dataToRender.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">Aún no hay datos de auditoría generados.</td></tr>`;
            return;
        }

        dataToRender.forEach(p => {
            const tr = document.createElement('tr');

            // Colores por acierto
            const isHit = p.Acierto === "✅";
            const rowClass = isHit ? "row-success-subtle" : "row-fail-subtle";
            const iconBadge = isHit ? `<span style="font-size:1.2rem;" title="Acierto">🎯</span>` : `<span style="font-size:1.2rem;" opacity="0.6" title="Fallo">❌</span>`;

            tr.innerHTML = `
                <td><span class="badge" style="background:var(--bg-secondary); color:var(--text-primary); border: 1px solid var(--border-color);">${p.Liga}</span></td>
                <td style="color:var(--text-muted); font-size:0.85rem">${p.Fecha}</td>
                <td><strong style="color:var(--text-primary);">${p.Partido}</strong></td>
                <td><strong style="color:var(--brand-color); font-size:1.1rem">${p.Prediccion_IA}</strong></td>
                <td><strong style="color:var(--text-primary); font-size:1.1rem">${p.Resultado_Real}</strong></td>
                <td class="text-center">${iconBadge}</td>
                <td class="desktop-only text-muted" style="font-size:0.8rem;">${p.Info_Extra}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // 3. Fetch Teams Stats (Virtual Scrolling)
    let rawStats = {};
    let sortedFilteredTeams = [];
    let currentRenderCount = 0;
    const CHUNK_SIZE = 20;

    fetch('/api/stats_equipos')
        .then(res => res.json())
        .then(data => {
            rawStats = data;
            initStatsDisplay("");
        });

    function initStatsDisplay(searchTerm) {
        let teams = Object.keys(rawStats);
        if (searchTerm) {
            teams = teams.filter(t => t.toLowerCase().includes(searchTerm.toLowerCase()));
        }

        // Sort by Pts_Totales descending
        teams.sort((a, b) => rawStats[b].Pts_Totales - rawStats[a].Pts_Totales);

        sortedFilteredTeams = teams;
        currentRenderCount = 0;

        const tbody = document.getElementById('stats-body');
        tbody.innerHTML = '';

        if (sortedFilteredTeams.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No se encontraron equipos en xG Analytics.</td></tr>`;
            return;
        }

        renderNextChunk();
    }

    function renderNextChunk() {
        const tbody = document.getElementById('stats-body');
        const nextBatch = sortedFilteredTeams.slice(currentRenderCount, currentRenderCount + CHUNK_SIZE);

        nextBatch.forEach(team => {
            const s = rawStats[team];
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong style="color:var(--text-primary)">${team}</strong></td>
                <td><span class="badge">${s.Pts_Totales} pts</span></td>
                <td>${s.Racha} pts / Últ. 3</td>
                <td><span style="color:var(--brand-color); font-weight:700;">${s.xG_Favor.toFixed(2)}</span></td>
                <td><span style="color:var(--danger); font-weight:700;">${s.xG_Contra.toFixed(2)}</span></td>
            `;
            tbody.appendChild(tr);
        });
        currentRenderCount += nextBatch.length;
    }

    // Detector de scroll para Virtual Scrolling
    const xgContainer = document.getElementById('xg-scroll-container');
    if (xgContainer) {
        xgContainer.addEventListener('scroll', () => {
            // Cuando se esté cerca del fondo (50px de margen)
            if (xgContainer.scrollTop + xgContainer.clientHeight >= xgContainer.scrollHeight - 50) {
                if (currentRenderCount < sortedFilteredTeams.length) {
                    renderNextChunk();
                }
            }
        });
    }

    // Ampliar la función original de ApplyFilters de arriba para que incluya las Stats
    const originalApplyFilters = applyFilters;
    applyFilters = function () {
        originalApplyFilters();
        const searchTerm = searchInput.value.toLowerCase();
        if (Object.keys(rawStats).length > 0) {
            initStatsDisplay(searchTerm);
        }
    };

    // 4. (Migrado Arriba) Render Bankroll Chart fue reemplazado por Precision Chart


    // 6. Fetch Results Dashboard (Auditoría)
    fetch('/api/dashboard_resultados')
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('results-body');
            tbody.innerHTML = '';

            if (!data || data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">No hay histórico de resultados auditados.</td></tr>`;
                return;
            }

            // Invertimos para ver primero los más recientes
            data.reverse().forEach(r => {
                const tr = document.createElement('tr');
                let balanceElement = `<span style="color:var(--text-muted)">Pendiente</span>`;

                if (r.Ganancia_Perdida > 0) {
                    balanceElement = `<span class="badge invest">+ $${r.Ganancia_Perdida.toFixed(2)}</span>`;
                } else if (r.Ganancia_Perdida < 0) {
                    balanceElement = `<span class="badge" style="background:var(--danger-bg); color:var(--danger);">- $${Math.abs(r.Ganancia_Perdida).toFixed(2)}</span>`;
                } else if (r.Resultado_Real && r.Resultado_Real !== "-") {
                    balanceElement = `<span style="color:var(--text-muted)">$0.00</span>`;
                }

                // Recomendation text formatter
                let recText = r.Recomendacion;
                if (recText === 'H') recText = 'Gana Local';
                if (recText === 'A') recText = 'Gana Visita';
                if (recText === 'D') recText = 'Empate';

                tr.innerHTML = `
                    <td>${r.Fecha_Partido}</td>
                    <td><strong style="color:var(--text-primary)">${r.HomeTeam}</strong> <span style="font-size:0.85rem">vs</span> <strong>${r.AwayTeam}</strong></td>
                    <td><span class="badge" style="background:#f1f3f5; color:#555">${recText}</span></td>
                    <td><strong style="color:var(--brand-color)">${(r.Probabilidad * 100).toFixed(1)}%</strong> <span style="opacity:0.6">/ @${r.Cuota}</span></td>
                    <td><span style="font-size:1.15rem; font-weight:800; font-family:'Outfit'">${r.Resultado_Real || '-'}</span></td>
                    <td>${balanceElement}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error cargando auditoria:", err));

    // 7. Mascot Speech Bubble Rotation (Duolingo-style)
    const mascotSpeech = document.getElementById('mascot-speech');
    if (mascotSpeech) {
        const frases = [
            "¡Hola! Soy Predicto 🎯 Tu asistente de apuestas inteligentes.",
            "💡 Recuerda: Solo apuesta cuando el EV sea mayor a 1.10.",
            "📊 El modelo cubre 5 ligas + Champions League.",
            "🔔 Recibes 3 alertas diarias por Telegram.",
            "⚽ El criterio Kelly protege tu bankroll.",
            "🧠 El motor usa HistGradient Boosting + Poisson.",
            "📈 Revisa el rendimiento para validar la IA."
        ];
        let fraseIndex = 0;
        setInterval(() => {
            fraseIndex = (fraseIndex + 1) % frases.length;
            mascotSpeech.textContent = frases[fraseIndex];
        }, 8000);
    }

    function generateLiveInsights(predictions) {
        const container = document.getElementById('insights-container');
        if (!container) return;
        container.innerHTML = '';

        const evPicks = predictions.filter(p => p.Recomendacion !== 'No Bet');
        if (evPicks.length === 0) {
            container.innerHTML = `<div class="insight-card"><p>El radar neuronal no detectó cuotas desbalanceadas notables para emitir alertas globales en este momento.</p></div>`;
            return;
        }

        const LEAGUES_MAP = {
            "La Liga": ["real madrid", "barcelona", "ath madrid", "sociedad", "betis", "valencia", "athletic", "osasuna", "celta", "alaves", "levante", "vallecano", "elche", "girona", "mallorca", "las palmas", "sevilla", "villarreal"],
            "Premier League": ["man city", "man united", "newcastle", "tottenham", "aston villa", "west ham", "brighton", "wolves", "nott'm forest", "sheffield united", "arsenal", "liverpool", "chelsea", "everton", "crystal palace", "fulham", "brentford", "bournemouth"],
            "Serie A": ["inter", "milan", "juventus", "roma", "napoli", "lazio", "atalanta", "fiorentina", "bologna", "torino", "monza", "genoa", "lecce", "empoli"],
            "Bundesliga": ["bayern munich", "dortmund", "leverkusen", "rb leipzig", "ein frankfurt", "stuttgart", "hoffenheim", "freiburg", "wolfsburg", "heidenheim"]
        };

        const bestPicksByLeague = {};

        evPicks.forEach(p => {
            const h = p.HomeTeam.toLowerCase();
            const a = p.AwayTeam.toLowerCase();
            let assignedLeague = "Champions / Otras";

            for (const [leagueName, teams] of Object.entries(LEAGUES_MAP)) {
                if (teams.some(team => h.includes(team) || a.includes(team))) {
                    assignedLeague = leagueName;
                    break;
                }
            }

            if (!bestPicksByLeague[assignedLeague] || p.EV > bestPicksByLeague[assignedLeague].EV) {
                bestPicksByLeague[assignedLeague] = p;
            }
        });

        const sortedLeagues = Object.keys(bestPicksByLeague).sort((a, b) => bestPicksByLeague[b].EV - bestPicksByLeague[a].EV);

        sortedLeagues.forEach(league => {
            const fila = bestPicksByLeague[league];
            const msj = `En la jornada de <strong>${league}</strong>, el radar detecta una oportunidad de valor respaldando a ${fila.HomeTeam}. Al encontrar una cuota de <strong>${fila.Cuota}</strong> y un Edge matemático de ${fila.EV.toFixed(2)}, el motor de Poisson calcula un marcador probable de ${fila.Marcador_Exacto}. Se sugiere invertir ${(fila.Kelly_Stake * 100).toFixed(1)}% del pool.`;

            container.innerHTML += `
            <div class="insight-card">
                <div class="insight-icon" style="color:var(--brand-color)"><i class="fa-solid fa-bolt"></i></div>
                <div class="insight-body">
                    <h3 style="margin-bottom:0.5rem; color:var(--text-primary); font-size: 1.1rem;">Pick ${league}: ${fila.HomeTeam}</h3>
                    <p style="color:var(--text-muted); line-height:1.6; font-size:0.95rem;">${msj}</p>
                    <div style="margin-top:0.8rem; font-size:0.85rem; font-weight:600; color:var(--success)">Convicción IA: ${(fila.Probabilidad * 100).toFixed(1)}%</div>
                </div>
            </div>`;
        });
    }
});
