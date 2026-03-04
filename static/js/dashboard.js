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

    // 1. Fetch Global Metrics (Financiero)
    fetch('/api/metricas_globales')
        .then(res => res.json())
        .then(data => {
            const benEl = document.getElementById('g-beneficio');
            benEl.textContent = `$${data.Beneficio_Total.toFixed(2)}`;
            if (data.Beneficio_Total < 0) {
                benEl.classList.remove('positive');
                benEl.classList.add('negative');
            }

            const yieldEl = document.getElementById('g-yield');
            yieldEl.textContent = `${data.Yield}%`;
            if (data.Yield < 0) yieldEl.classList.add('negative');
            else if (data.Yield > 0) yieldEl.classList.add('positive');

            const winRateEl = document.getElementById('g-winrate');
            winRateEl.textContent = `${data.WinRate}%`;
            if (data.WinRate >= 50) winRateEl.classList.add('positive');

            document.getElementById('g-balance').textContent = `${data.Aciertos} W - ${data.Fallos} L`;
        });

    // 2. Fetch Today's Predictions & Set Filters
    let rawPredictions = [];

    fetch('/api/predicciones_hoy')
        .then(res => res.json())
        .then(data => {
            rawPredictions = data;
            renderPredictions(rawPredictions);
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
                <td><strong style="color:var(--text-primary)">${p.HomeTeam}</strong> <span style="color:var(--text-muted)">vs</span> <strong>${p.AwayTeam}</strong></td>
                <td><span style="font-family:'Outfit', sans-serif; font-size:1.1rem; font-weight:700;">${p.Cuota}</span></td>
                <td><span style="color:var(--brand-color); font-weight:700;">${(p.Probabilidad * 100).toFixed(1)}%</span></td>
                <td><span style="${colorEV}">${p.EV.toFixed(2)}</span></td>
                <td><span style="color:var(--text-muted); font-size:0.9rem;">${p.Proj_Goles_L} - ${p.Proj_Goles_V}</span></td>
                <td><strong style="color: var(--text-primary); border: 1px solid var(--border-color); padding: 4px 10px; border-radius: 6px; background:white;">${p.Marcador_Exacto}</strong></td>
                <td>${isInvest ? `<span class="badge invest">Apostar (Stake ${(p.Kelly_Stake * 100).toFixed(1)}%)</span>` : `<span class="badge pass">Evitar (No-Bet)</span>`}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Buscador Inteligente en vivo
    const searchInput = document.getElementById('global-search');
    const filterSelect = document.getElementById('filter-market');

    function applyFilters() {
        const searchTerm = searchInput.value.toLowerCase();
        const filterVal = filterSelect.value;

        let filtered = rawPredictions.filter(p => {
            const matchText = `${p.HomeTeam.toLowerCase()} ${p.AwayTeam.toLowerCase()}`;
            return matchText.includes(searchTerm);
        });

        if (filterVal === 'value') {
            filtered = filtered.filter(p => p.Recomendacion !== 'No Bet');
        } else if (filterVal === 'pass') {
            filtered = filtered.filter(p => p.Recomendacion === 'No Bet');
        }

        renderPredictions(filtered);
    }

    searchInput.addEventListener('input', () => {
        const navTarget = document.querySelector('[data-target="view-predictions"]');
        if (!navTarget.classList.contains('active')) navTarget.click();
        applyFilters();
    });

    filterSelect.addEventListener('change', applyFilters);

    // 3. Fetch Teams Stats
    fetch('/api/stats_equipos')
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('stats-body');
            const sortedTeams = Object.keys(data).sort((a, b) => data[b].Pts_Totales - data[a].Pts_Totales);

            sortedTeams.slice(0, 20).forEach(team => {
                const s = data[team];
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
        });

    // 4. Render Bankroll Chart
    fetch('/api/grafico_bankroll')
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById('bankrollChart').getContext('2d');

            Chart.defaults.color = '#6B6A68';
            Chart.defaults.font.family = "'Inter', sans-serif";

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Capital Acumulado ($)',
                        data: data.data,
                        borderColor: '#0E8E42',
                        backgroundColor: 'rgba(14, 142, 66, 0.05)',
                        borderWidth: 3,
                        pointBackgroundColor: '#FFFFFF',
                        pointBorderColor: '#0E8E42',
                        pointHoverBackgroundColor: '#000000',
                        pointHoverBorderColor: '#FFFFFF',
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        fill: true,
                        tension: 0.3
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
                            borderColor: '#333',
                            borderWidth: 1,
                            padding: 12,
                            displayColors: false,
                            callbacks: {
                                label: function (context) {
                                    return 'Balance: $' + context.parsed.y.toFixed(2);
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(0,0,0,0.03)', drawBorder: false }
                        },
                        y: {
                            grid: { color: 'rgba(0,0,0,0.03)', drawBorder: false },
                            ticks: { callback: function (value) { return '$' + value; } }
                        }
                    }
                }
            });
        });

    // 5. Fetch Insights
    fetch('/api/insights')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('insights-container');
            container.innerHTML = '';

            if (data.length === 0) {
                container.innerHTML = `<div class="insight-card"><p>No hay alertas de rentabilidad notables hoy.</p></div>`;
                return;
            }

            data.forEach(ins => {
                container.innerHTML += `
                <div class="insight-card">
                    <div class="insight-icon" style="color:var(--brand-color)"><i class="fa-solid fa-bolt"></i></div>
                    <div class="insight-body">
                        <h3>${ins.titulo}</h3>
                        <p>${ins.mensaje}</p>
                        <p style="margin-top:0.5rem; font-weight:600; font-size:0.85rem; color:var(--text-primary)">Confianza IA: ${(ins.confianza * 100).toFixed(1)}%</p>
                    </div>
                </div>`;
            });
        })
        .catch(err => {
            console.error("No se pudo cargar los insights", err);
        });
});
